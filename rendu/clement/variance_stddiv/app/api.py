import hashlib
import json
import math
import os
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, make_asgi_app
import redis

if __package__:
    from .statistiques import ecart_type, moyenne_population, variance_population
else:
    from statistiques import ecart_type, moyenne_population, variance_population

app = FastAPI(
    title="Clement Enterprise Population Statistics API",
    version="1.0.0",
    description="Surcouche volontairement enterprise autour des fonctions 3, 7 et 9 du CDC.",
)

REQUESTS = Counter(
    "statistics_requests_total",
    "Nombre de requetes statistiques",
    ["operation", "cache"],
)
LATENCY = Histogram(
    "statistics_request_duration_seconds",
    "Duree de traitement",
    ["operation"],
)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
    socket_connect_timeout=0.2,
    socket_timeout=0.2,
)


class StatisticsRequest(BaseModel):
    nombres: list[Annotated[float, Field(allow_inf_nan=False)]]


class StatisticsResponse(BaseModel):
    operation: Literal["moyenne_population", "variance_population", "ecart_type"]
    resultat: float | None
    cached: bool
    mode: Literal["standard", "ilian"] | None = None


def _cache_key(
    operation: str,
    nombres: list[float],
    mode: str | None = None,
) -> str:
    payload = json.dumps(nombres, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    mode_key = f":{mode}" if mode is not None else ""
    return f"stats:{operation}{mode_key}:{digest}"


def _execute(
    operation: str,
    nombres: list[float],
    mode: Literal["standard", "ilian"] | None = None,
) -> StatisticsResponse:
    key = _cache_key(operation, nombres, mode)
    try:
        cached = redis_client.get(key)
    except redis.RedisError:
        cached = None

    if cached is not None:
        try:
            cachedResult = json.loads(cached)
            isValidCachedResult = cachedResult is None or math.isfinite(
                float(cachedResult)
            )
        except (TypeError, ValueError, OverflowError):
            isValidCachedResult = False

        if isValidCachedResult:
            REQUESTS.labels(operation=operation, cache="hit").inc()
            return StatisticsResponse(
                operation=operation,
                resultat=cachedResult,
                cached=True,
                mode=mode,
            )

    try:
        with LATENCY.labels(operation=operation).time():
            if operation == "variance_population":
                resultat = variance_population(nombres)
            elif operation == "ecart_type":
                resultat = ecart_type(nombres)
            else:
                resultat = moyenne_population(
                    nombres,
                    utiliser_code_ilian=mode == "ilian",
                )
    except RuntimeError as error:
        if operation != "moyenne_population" or mode != "ilian":
            raise
        raise HTTPException(
            status_code=503,
            detail="Mode Ilian indisponible ; vérifiez ILIAN_MOYENNE_FILE.",
        ) from error
    except OverflowError as error:
        raise HTTPException(
            status_code=422,
            detail="Le résultat dépasse la plage numérique prise en charge.",
        ) from error

    if resultat is not None and not math.isfinite(resultat):
        raise HTTPException(
            status_code=422,
            detail="Le résultat dépasse la plage numérique prise en charge.",
        )

    try:
        redis_client.setex(key, 300, json.dumps(resultat))
    except redis.RedisError:
        pass

    REQUESTS.labels(operation=operation, cache="miss").inc()
    return StatisticsResponse(
        operation=operation,
        resultat=resultat,
        cached=False,
        mode=mode,
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/variance", response_model=StatisticsResponse)
def variance(payload: StatisticsRequest):
    return _execute("variance_population", payload.nombres)


@app.post("/ecart-type", response_model=StatisticsResponse)
def standard_deviation(payload: StatisticsRequest):
    return _execute("ecart_type", payload.nombres)


@app.post("/moyenne", response_model=StatisticsResponse)
def mean(
    payload: StatisticsRequest,
    mode: Literal["standard", "ilian"] = "standard",
):
    return _execute("moyenne_population", payload.nombres, mode)


app.mount("/metrics", make_asgi_app())
