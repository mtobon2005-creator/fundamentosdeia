"""Sprint 1 · Red logística, Dijkstra y A* (TSP)."""
from heapq import heappop, heappush

# Costo de cada tramo = minutos estimados en hora pico.
RED = {
    "Bodega Itagüí": [("Sabaneta Plaza", 8), ("Los Molinos Envigado", 12), ("C.C. Oviedo", 10)],
    "Sabaneta Plaza": [("Bodega Itagüí", 8)],
    "Los Molinos Envigado": [("Bodega Itagüí", 12), ("C.C. Premium Plaza", 9)],
    "C.C. Oviedo": [("Bodega Itagüí", 10), ("C.C. El Tesoro", 5), ("Unicentro", 9)],
    "C.C. El Tesoro": [("C.C. Oviedo", 5), ("C.C. Premium Plaza", 7), ("C.C. San Diego", 11)],
    "C.C. Premium Plaza": [("Los Molinos Envigado", 9), ("C.C. El Tesoro", 7)],
    "Unicentro": [("C.C. Oviedo", 9), ("C.C. San Diego", 8), ("C.C. Mayorca", 13)],
    "C.C. San Diego": [("C.C. El Tesoro", 11), ("Unicentro", 8), ("Puerta del Norte", 10)],
    "C.C. Mayorca": [("Unicentro", 13), ("Puerta del Norte", 7)],
    "Puerta del Norte": [("C.C. San Diego", 10), ("C.C. Mayorca", 7)],
}
ORIGEN = "Bodega Itagüí"
TIENDAS = [n for n in RED if n != ORIGEN]

# Posición esquemática para dibujar el mapa (x, y).
POS = {
    "Puerta del Norte": (285, 48), "C.C. Mayorca": (455, 120), "C.C. San Diego": (205, 150),
    "Unicentro": (350, 215), "C.C. El Tesoro": (150, 262), "C.C. Oviedo": (300, 312),
    "C.C. Premium Plaza": (75, 340), "Los Molinos Envigado": (95, 438),
    "Bodega Itagüí": (255, 452), "Sabaneta Plaza": (410, 478),
}

ZONAS = {
    "Sur": ["Sabaneta Plaza", "Los Molinos Envigado"],
    "El Poblado": ["C.C. Oviedo", "C.C. El Tesoro", "C.C. Premium Plaza"],
    "Centro": ["Unicentro", "C.C. San Diego"],
    "Norte": ["C.C. Mayorca", "Puerta del Norte"],
}
ZONAS_EN_DISPUTA = ["El Poblado", "Centro"]
EN_DISPUTA = [t for z in ZONAS_EN_DISPUTA for t in ZONAS[z]]

TIEMPO_ATENCION = 15  # minutos de descarga y revisión por tienda


def dijkstra(red, origen):
    """Tiempo mínimo desde 'origen' a todos los nodos, y predecesores."""
    dist = {n: float("inf") for n in red}
    prev = {n: None for n in red}
    dist[origen] = 0
    cola = [(0, origen)]
    visitados = set()
    while cola:
        d, nodo = heappop(cola)
        if nodo in visitados:
            continue
        visitados.add(nodo)
        for vecino, peso in red[nodo]:
            nuevo = d + peso
            if nuevo < dist[vecino]:
                dist[vecino] = nuevo
                prev[vecino] = nodo
                heappush(cola, (nuevo, vecino))
    return dist, prev


_TODO = {n: dijkstra(RED, n) for n in RED}
DIST = {n: _TODO[n][0] for n in RED}
_PREV = {n: _TODO[n][1] for n in RED}


def camino(a, b):
    """Nodos recorridos en la ruta más corta de a hasta b."""
    out = [b]
    while out[0] != a:
        out.insert(0, _PREV[a][out[0]])
    return out


def aristas():
    """Tramos únicos (a, b, minutos) para dibujar la red."""
    vistos, out = set(), []
    for a, vecinos in RED.items():
        for b, w in vecinos:
            clave = tuple(sorted((a, b)))
            if clave not in vistos:
                vistos.add(clave)
                out.append((a, b, w))
    return out


def heuristica_tsp(actual, faltantes, dist, origen, cerrada):
    if not faltantes:
        return dist[actual][origen] if cerrada else 0
    return min(dist[actual][t] for t in faltantes)


def a_estrella_tsp(dist, origen, tiendas, cerrada=False):
    """A* sobre el estado (nodo actual, tiendas visitadas). Devuelve (ruta, costo)."""
    todas = frozenset(tiendas)
    cola = [(heuristica_tsp(origen, todas, dist, origen, cerrada), 0, origen, frozenset(), [origen])]
    mejor_costo = {}
    while cola:
        _, g, nodo, visitadas, ruta = heappop(cola)
        if visitadas == todas:
            if not cerrada or nodo == origen:
                return ruta, g
            nuevo_g = g + dist[nodo][origen]
            heappush(cola, (nuevo_g, nuevo_g, origen, visitadas, ruta + [origen]))
            continue
        clave = (nodo, visitadas)
        if clave in mejor_costo and mejor_costo[clave] <= g:
            continue
        mejor_costo[clave] = g
        for sig in todas - visitadas:
            nuevo_g = g + dist[nodo][sig]
            nv = visitadas | {sig}
            h = heuristica_tsp(sig, todas - nv, dist, origen, cerrada)
            heappush(cola, (nuevo_g + h, nuevo_g, sig, nv, ruta + [sig]))
    return None, None
