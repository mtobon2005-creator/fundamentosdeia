"""Sprint 3 · Escenario competitivo y algoritmo genético (mismo diseño que el notebook)."""
import random

from .red import DIST, EN_DISPUTA, ORIGEN, TIEMPO_ATENCION, TIENDAS

PARAMS_NOTEBOOK = {"mult": 2.0, "minuto": 45, "castigo": 0.5, "semilla": 42}


def construir_escenario(estrategia_ac, estrategia_rival, valores, p):
    """Traduce el juego en valor por tienda y carrera. valores: {tienda: valor base de prioridad}."""
    valor = {}
    for t, v in valores.items():
        if estrategia_ac == "Concentrar" and t in EN_DISPUTA:
            v = v * p["mult"]
        valor[t] = v
    return {"valor_tienda": valor, "hay_carrera": estrategia_rival == "Expandirse",
            "minuto": p["minuto"], "castigo": p["castigo"]}


def decodificar(crom, tiempo):
    """Una tienda entra solo si alcanza el tiempo para ir, atenderla y volver a la bodega."""
    ruta, llegadas, usado = [ORIGEN], {}, 0
    for t in crom:
        ir, volver = DIST[ruta[-1]][t], DIST[t][ORIGEN]
        if usado + ir + TIEMPO_ATENCION + volver <= tiempo:
            usado += ir
            llegadas[t] = usado
            usado += TIEMPO_ATENCION
            ruta.append(t)
    total = usado + DIST[ruta[-1]][ORIGEN]
    ruta.append(ORIGEN)
    return ruta, llegadas, total


def llega_tarde(esc, tienda, minuto):
    return esc["hay_carrera"] and tienda in EN_DISPUTA and minuto > esc["minuto"]


def calcular_fitness(crom, esc, tiempo):
    """fitness = valor entregado − 0,01 × minutos usados."""
    _, llegadas, total = decodificar(crom, tiempo)
    valor = 0.0
    for t, m in llegadas.items():
        v = esc["valor_tienda"][t]
        if llega_tarde(esc, t, m):
            v *= esc["castigo"]
        valor += v
    return valor - 0.01 * total


def algoritmo_genetico(esc, tiempo, semilla, pob=30, generaciones=60, pm=0.20, elitismo=2):
    """Evaluar → elitismo → ruleta → cruce por orden → mutación por intercambio."""
    rng = random.Random(semilla)
    memo = {}

    def fit(ind):
        k = tuple(ind)
        if k not in memo:
            memo[k] = calcular_fitness(ind, esc, tiempo)
        return memo[k]

    poblacion = []
    for _ in range(pob):
        ind = list(TIENDAS)
        rng.shuffle(ind)
        poblacion.append(ind)

    mejor_hist, prom_hist = [], []
    for _ in range(generaciones):
        poblacion.sort(key=fit, reverse=True)
        mejor_hist.append(fit(poblacion[0]))
        prom_hist.append(sum(fit(i) for i in poblacion) / len(poblacion))
        nueva = poblacion[:elitismo]
        pesos = [max(fit(i), 0.01) for i in poblacion]
        while len(nueva) < pob:
            p1 = rng.choices(poblacion, weights=pesos, k=1)[0]
            p2 = rng.choices(poblacion, weights=pesos, k=1)[0]
            hijo = p1[: len(p1) // 2]
            hijo = hijo + [t for t in p2 if t not in hijo]
            if rng.random() < pm:
                i, j = rng.randrange(len(hijo)), rng.randrange(len(hijo))
                hijo[i], hijo[j] = hijo[j], hijo[i]
            nueva.append(hijo)
        poblacion = nueva
    poblacion.sort(key=fit, reverse=True)
    mejor_hist.append(fit(poblacion[0]))
    prom_hist.append(sum(fit(i) for i in poblacion) / len(poblacion))
    return poblacion[0], mejor_hist, prom_hist


def busqueda_exhaustiva(esc, tiempo):
    """Control: mejor fitness entre todas las secuencias de paradas factibles."""
    mejor = [float("-inf"), []]

    def rec(ultimo, usado, valor, visitadas, orden):
        total = usado + DIST[ultimo][ORIGEN]
        f = valor - 0.01 * total
        if f > mejor[0]:
            mejor[0], mejor[1] = f, list(orden)
        for t in TIENDAS:
            if t in visitadas:
                continue
            ir, volver = DIST[ultimo][t], DIST[t][ORIGEN]
            if usado + ir + TIEMPO_ATENCION + volver <= tiempo:
                llegada = usado + ir
                v = esc["valor_tienda"][t]
                if llega_tarde(esc, t, llegada):
                    v *= esc["castigo"]
                visitadas.add(t)
                orden.append(t)
                rec(t, llegada + TIEMPO_ATENCION, valor + v, visitadas, orden)
                orden.pop()
                visitadas.discard(t)

    rec(ORIGEN, 0, 0.0, set(), [])
    return mejor[1], mejor[0]
