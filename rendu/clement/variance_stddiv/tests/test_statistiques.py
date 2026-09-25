import math

from app.statistiques import ecart_type, variance_population


def test_variance_reference_cdc():
    nombres = [12.0, 4.5, 3.0]
    snapshot = nombres.copy()
    assert variance_population(nombres) == 15.5
    assert nombres == snapshot


def test_ecart_type_reference_cdc():
    nombres = [12.0, 4.5, 3.0]
    snapshot = nombres.copy()
    assert math.isclose(ecart_type(nombres), math.sqrt(15.5))
    assert round(ecart_type(nombres), 2) == 3.94
    assert nombres == snapshot


def test_liste_vide_cdc():
    assert variance_population([]) is None
    assert ecart_type([]) is None


def test_valeurs_negatives_et_decimales():
    nombres = [-2.5, 0.0, 2.5]
    assert math.isclose(variance_population(nombres), 25 / 6)
    assert math.isclose(ecart_type(nombres), math.sqrt(25 / 6))
