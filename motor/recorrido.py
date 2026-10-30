"""Recorrido del camión minuto a minuto sobre la red (para animar la ruta)."""
from .red import ORIGEN, POS, RED, TIEMPO_ATENCION, camino

_PESO = {(a, b): w for a, vs in RED.items() for b, w in vs}


def segmentos(ruta):
    """Lista de (t0, t1, tipo, desde, hasta): 'viaje' entre nodos vecinos y 'atención' en cada tienda."""
    segs, t = [], 0
    for i in range(len(ruta) - 1):
        nodos = camino(ruta[i], ruta[i + 1])
        for a, b in zip(nodos, nodos[1:]):
            segs.append((t, t + _PESO[(a, b)], "viaje", a, b))
            t += _PESO[(a, b)]
        if ruta[i + 1] != ORIGEN:
            segs.append((t, t + TIEMPO_ATENCION, "atención", ruta[i + 1], ruta[i + 1]))
            t += TIEMPO_ATENCION
    return segs


def posicion(segs, minuto):
    """(x, y, texto del estado, puntos recorridos hasta ese minuto)."""
    puntos = [POS[segs[0][3]]]
    for t0, t1, tipo, a, b in segs:
        if minuto >= t1:
            if tipo == "viaje":
                puntos.append(POS[b])
            continue
        if tipo == "atención":
            return (*POS[a], f"Descargando en {a.replace('C.C. ', '')}", puntos)
        f = (minuto - t0) / (t1 - t0)
        x = POS[a][0] + f * (POS[b][0] - POS[a][0])
        y = POS[a][1] + f * (POS[b][1] - POS[a][1])
        return x, y, f"En camino a {b.replace('C.C. ', '')}", puntos + [(x, y)]
    return (*POS[segs[-1][4]], "De vuelta en la bodega", puntos)
