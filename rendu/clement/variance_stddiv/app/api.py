import hashlib
import json
import os
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, make_asgi_app
import redis

from statistiques import ecart_type, variance_population

app = FastAPI(
    title="Clement Enterprise Population Statistics API",
    version="1.0.0",
    description="Surcouche volontairement enterprise autour des fonctions 7 et 9 du CDC.",
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
    nombres: list[float]


class StatisticsResponse(BaseModel):
    operation: Literal["variance_population", "ecart_type"]
    resultat: float | None
    cached: bool


def _cache_key(operation: str, nombres: list[float]) -> str:
    payload = json.dumps(nombres, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"stats:{operation}:{digest}"


def _execute(operation: str, nombres: list[float]) -> StatisticsResponse:
    key = _cache_key(operation, nombres)
    try:
        cached = redis_client.get(key)
    except redis.RedisError:
        cached = None

    if cached is not None:
        REQUESTS.labels(operation=operation, cache="hit").inc()
        return StatisticsResponse(
            operation=operation,
            resultat=json.loads(cached),
            cached=True,
        )

    with LATENCY.labels(operation=operation).time():
        if operation == "variance_population":
            resultat = variance_population(nombres)
        else:
            resultat = ecart_type(nombres)

    try:
        redis_client.setex(key, 300, json.dumps(resultat))
    except redis.RedisError:
        pass

    REQUESTS.labels(operation=operation, cache="miss").inc()
    return StatisticsResponse(
        operation=operation,
        resultat=resultat,
        cached=False,
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


app.mount("/metrics", make_asgi_app())
