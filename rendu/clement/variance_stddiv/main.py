import os
import requests


API_URL = "http://localhost:8080"

def init() -> None:
    os.system("clear")

def variance_population_enterprise(nombres: list[float]) -> float | None:
    response = requests.post(
        f"{API_URL}/variance",
        json={"nombres": nombres},
        timeout=5,
    )

    response.raise_for_status()

    data = response.json()
    return data["resultat"]


def ecart_type_enterprise(nombres: list[float]) -> float | None:
    response = requests.post(
        f"{API_URL}/ecart-type",
        json={"nombres": nombres},
        timeout=5,
    )

    response.raise_for_status()

    data = response.json()
    return data["resultat"]


def moyenne_population_enterprise(
    nombres: list[float],
    mode: str = "standard",
) -> float | None:
    response = requests.post(
        f"{API_URL}/moyenne",
        params={"mode": mode},
        json={"nombres": nombres},
        timeout=5,
    )

    response.raise_for_status()

    data = response.json()
    return data["resultat"]
