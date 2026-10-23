"""Sprint 2 · Sistema experto de 10 reglas (prioridad clásica)."""
from .red import DIST, ORIGEN, TIEMPO_ATENCION

UMBRALES = {
    "INVENTARIO_MUY_BAJO": 10,
    "UMBRAL_INVENTARIO_CRITICO": 20,
    "INVENTARIO_SOBRANTE": 100,
    "UMBRAL_VENTAS_ALTAS_NORMAL": 50,
    "UMBRAL_VENTAS_ALTAS_FIN_DE_SEMANA": 40,
    "UMBRAL_ROTACION_MUY_ALTA": 70,
    "LIMITE_DIAS_SIN_REABASTECER": 14,
    "LIMITE_DIAS_MUY_URGENTE": 25,
    "LIMITE_QUEJAS": 3,
    "TIEMPO_ATENCION_POR_TIENDA": TIEMPO_ATENCION,
}

# (id, condición en lenguaje natural, conclusión)
REGLAS = [
    ("R1", "inventario < 10", "urgente"),
    ("R2", "quejas de clientes > 3", "urgente"),
    ("R3", "más de 25 días sin reabastecer", "urgente"),
    ("R4", "inventario < 20 Y ventas altas (> 50; > 40 si llega el fin de semana)", "urgente"),
    ("R5", "inventario < 20 (sin cumplir R4)", "media"),
    ("R6", "más de 14 días sin reabastecer", "media"),
    ("R7", "rotación muy alta (ventas > 70)", "media"),
    ("R8", "se acerca el fin de semana Y inventario < 30", "media"),
    ("R9", "inventario sobrante (> 100)", "baja"),
    ("R10", "ninguna condición anterior aplica", "baja"),
]
ORDEN_PRIORIDAD = {"urgente": 0, "media": 1, "baja": 2}
VALOR_PRIORIDAD = {"urgente": 3, "media": 2, "baja": 1}

# Memoria de trabajo del notebook (Entrega 2): inventario, ventas/sem, días sin reabastecer, quejas.
HECHOS_NOTEBOOK = {
    "C.C. Oviedo": (15, 60, 5, 1),
    "C.C. El Tesoro": (45, 30, 18, 0),
    "Unicentro": (18, 40, 9, 4),
    "C.C. Mayorca": (80, 20, 3, 0),
    "Puerta del Norte": (10, 55, 12, 0),
    "C.C. San Diego": (60, 25, 7, 0),
    "C.C. Premium Plaza": (22, 15, 20, 0),
    "Los Molinos Envigado": (90, 10, 2, 0),
    "Sabaneta Plaza": (12, 35, 30, 0),
}


def regla_prioridad(inv, ventas, dias, quejas, fin_de_semana):
    """Devuelve (prioridad, id de la regla que se disparó). Gana la primera que se cumple."""
    u = UMBRALES
    umbral_ventas = u["UMBRAL_VENTAS_ALTAS_FIN_DE_SEMANA"] if fin_de_semana else u["UMBRAL_VENTAS_ALTAS_NORMAL"]
    if inv < u["INVENTARIO_MUY_BAJO"]:
        return "urgente", "R1"
    if quejas > u["LIMITE_QUEJAS"]:
        return "urgente", "R2"
    if dias > u["LIMITE_DIAS_MUY_URGENTE"]:
        return "urgente", "R3"
    if inv < u["UMBRAL_INVENTARIO_CRITICO"] and ventas > umbral_ventas:
        return "urgente", "R4"
    if inv < u["UMBRAL_INVENTARIO_CRITICO"]:
        return "media", "R5"
    if dias > u["LIMITE_DIAS_SIN_REABASTECER"]:
        return "media", "R6"
    if ventas > u["UMBRAL_ROTACION_MUY_ALTA"]:
        return "media", "R7"
    if fin_de_semana and inv < 30:
        return "media", "R8"
    if inv > u["INVENTARIO_SOBRANTE"]:
        return "baja", "R9"
    return "baja", "R10"


def razonar(hechos, fin_de_semana):
    """3.1 Razonamiento. hechos: {tienda: (inv, ventas, dias, quejas)} -> {tienda: (prioridad, regla)}."""
    return {t: regla_prioridad(*h, fin_de_semana) for t, h in hechos.items()}


def plan_del_dia(prioridades, tiempo_disponible):
    """3.2 Solución: tiendas por urgencia mientras alcance el tiempo (ir + atender + volver)."""
    orden = sorted(prioridades, key=lambda t: ORDEN_PRIORIDAD[prioridades[t]])
    ruta, usado, llegadas, pendientes = [ORIGEN], 0, {}, []
    for t in orden:
        ir, volver = DIST[ruta[-1]][t], DIST[t][ORIGEN]
        if usado + ir + TIEMPO_ATENCION + volver <= tiempo_disponible:
            usado += ir
            llegadas[t] = usado
            usado += TIEMPO_ATENCION
            ruta.append(t)
        else:
            pendientes.append(t)
    total = usado + DIST[ruta[-1]][ORIGEN]
    ruta.append(ORIGEN)
    return {"ruta": ruta, "llegadas": llegadas, "total": total, "pendientes": pendientes}
