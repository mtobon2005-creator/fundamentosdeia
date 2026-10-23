"""Sprint 3 · Teoría de juegos: matriz de pagos, mejores respuestas, Nash y minimax."""

ESTRATEGIAS_AC = ["Concentrar", "Distribuir"]
ESTRATEGIAS_RIVAL = ["Expandirse", "Mantener"]

# (pago Arturo Calle, pago rival): participación de mercado esperada, escala 0 a 10 (supuestos del modelo).
PAGOS = {
    ("Concentrar", "Expandirse"): (6, 5),
    ("Concentrar", "Mantener"): (5, 4),
    ("Distribuir", "Expandirse"): (3, 8),
    ("Distribuir", "Mantener"): (7, 6),
}
NOTAS = {
    ("Concentrar", "Expandirse"): "AC defiende; el rival entra pero gana poco",
    ("Concentrar", "Mantener"): "AC invierte de más donde nadie lo ataca",
    ("Distribuir", "Expandirse"): "El rival le quita clientes en las zonas en disputa",
    ("Distribuir", "Mantener"): "Todo sigue como está",
}


def mejor_respuesta_ac(rival):
    return max(ESTRATEGIAS_AC, key=lambda a: PAGOS[(a, rival)][0])


def mejor_respuesta_rival(ac):
    return max(ESTRATEGIAS_RIVAL, key=lambda r: PAGOS[(ac, r)][1])


def encontrar_nash():
    return [
        (a, r) for a in ESTRATEGIAS_AC for r in ESTRATEGIAS_RIVAL
        if mejor_respuesta_ac(r) == a and mejor_respuesta_rival(a) == r
    ]


def minimax_ac():
    peor = {a: min(PAGOS[(a, r)][0] for r in ESTRATEGIAS_RIVAL) for a in ESTRATEGIAS_AC}
    return max(peor, key=peor.get), peor


NASH = encontrar_nash()
