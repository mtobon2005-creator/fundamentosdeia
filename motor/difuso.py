"""Sprint 4 · Lógica difusa: prioridad difusa (Mamdani) y capa de decisión de carga (Sugeno)."""
import numpy as np

U = np.linspace(0, 100, 1001)  # universo de la urgencia


def trap(x, a, b, c, d):
    """Pertenencia trapezoidal. a==b o c==d dan un 'hombro' (pertenencia 1 desde/hasta ese punto)."""
    x = np.asarray(x, dtype=float)
    subida = (x - a) / (b - a) if b > a else np.where(x >= a, 1.0, 0.0)
    bajada = (d - x) / (d - c) if d > c else np.where(x <= d, 1.0, 0.0)
    return np.clip(np.minimum(subida, bajada), 0.0, 1.0)


# ---------------------------------------------------------------------------
# 1) PRIORIDAD DIFUSA
# Cada conjunto se centra en el umbral de las reglas clásicas (en el umbral la pertenencia es 0,5).
# ---------------------------------------------------------------------------
def conjuntos_entrada(fin_de_semana):
    return {
        "Inventario": {
            "muy bajo": (0, 0, 4, 16), "bajo": (0, 0, 10, 30),
            "moderado": (0, 0, 20, 40), "alto": (70, 130, 200, 200),
        },
        "Ventas semanales": {
            "altas": (20, 60, 200, 200) if fin_de_semana else (30, 70, 200, 200),
            "muy altas": (50, 90, 200, 200),
        },
        "Días sin reabastecer": {"varios": (8, 20, 22, 32), "muchos": (15, 35, 60, 60)},
        "Quejas": {"muchas": (2, 5, 10, 10)},
    }


RANGOS = {"Inventario": 150, "Ventas semanales": 120, "Días sin reabastecer": 45, "Quejas": 8}
SALIDA = {"baja": (0, 0, 20, 45), "media": (30, 50, 50, 70), "alta": (55, 80, 100, 100)}
CURVAS = {k: trap(U, *p) for k, p in SALIDA.items()}
CENTROIDE = {k: float((U * c).sum() / c.sum()) for k, c in CURVAS.items()}
S_MIN, S_MAX = CENTROIDE["baja"], CENTROIDE["alta"]

# (id, texto, conclusión) — versión difusa de las 10 reglas del experto.
REGLAS_DIFUSAS = [
    ("R1", "inventario muy bajo", "alta"),
    ("R2", "quejas muchas", "alta"),
    ("R3", "días sin reabastecer muchos", "alta"),
    ("R4", "inventario bajo Y ventas altas", "alta"),
    ("R5", "inventario bajo", "media"),
    ("R6", "días sin reabastecer varios", "media"),
    ("R7", "ventas muy altas (rotación)", "media"),
    ("R8", "fin de semana Y inventario moderado", "media"),
    ("R9", "inventario alto (sobrante)", "baja"),
    ("R10", "ninguna anterior aplica", "baja"),
]


def evaluar(inv, ventas, dias, quejas, fin_de_semana):
    """Fuzzifica, activa las 10 reglas, agrega (máx) y desfuzzifica por centroide."""
    cs = conjuntos_entrada(fin_de_semana)
    valores = {"Inventario": inv, "Ventas semanales": ventas, "Días sin reabastecer": dias, "Quejas": quejas}
    mu = {v: {n: float(trap(valores[v], *p)) for n, p in sets.items()} for v, sets in cs.items()}
    i, v, d, q = mu["Inventario"], mu["Ventas semanales"], mu["Días sin reabastecer"], mu["Quejas"]
    act = [
        i["muy bajo"], q["muchas"], d["muchos"], min(i["bajo"], v["altas"]),
        i["bajo"], d["varios"], v["muy altas"],
        min(1.0 if fin_de_semana else 0.0, i["moderado"]), i["alto"],
    ]
    act.append(max(0.0, 1.0 - max(act)))  # R10: nada de lo anterior aplica
    # El orden de las reglas importa (gana la primera que se cumple): una regla más urgente
    # que se activa "apaga" en proporción a las reglas de menor urgencia.
    rango = {"alta": 2, "media": 1, "baja": 0}
    fuerza = []
    for k, ((_, _, salida), a) in enumerate(zip(REGLAS_DIFUSAS, act)):
        mayor = max([act[j] for j in range(k) if rango[REGLAS_DIFUSAS[j][2]] > rango[salida]] or [0.0])
        fuerza.append(a * (1.0 - mayor))
    agregada = np.zeros_like(U)
    for (_, _, salida), f in zip(REGLAS_DIFUSAS, fuerza):
        agregada = np.maximum(agregada, np.minimum(f, CURVAS[salida]))
    score = float((U * agregada).sum() / agregada.sum())
    valor = 1.0 + 2.0 * min(1.0, max(0.0, (score - S_MIN) / (S_MAX - S_MIN)))
    return {
        "score": score, "valor": valor, "prioridad": etiqueta(valor),
        "mu": mu, "activaciones": act, "fuerza": fuerza, "agregada": agregada,
    }


def etiqueta(valor):
    return "urgente" if valor >= 2.5 else "media" if valor >= 1.5 else "baja"


# ---------------------------------------------------------------------------
# 2) CAPA DE DECISIÓN DE CARGA (cuántas unidades enviar) — sistema tipo Sugeno
# Entradas: urgencia (0-100) y déficit (% del nivel objetivo que falta).
# Salida: % del faltante que conviene enviar.
# ---------------------------------------------------------------------------
URGENCIA = {"baja": (0, 0, 25, 50), "media": (25, 50, 50, 75), "alta": (50, 75, 100, 100)}
DEFICIT = {"pequeño": (0, 0, 15, 40), "medio": (20, 45, 45, 70), "grande": (50, 75, 100, 100)}
ENVIO = {"mínimo": 25.0, "moderado": 60.0, "completo": 100.0}
MATRIZ_CARGA = {
    ("alta", "grande"): "completo", ("alta", "medio"): "completo", ("alta", "pequeño"): "moderado",
    ("media", "grande"): "completo", ("media", "medio"): "moderado", ("media", "pequeño"): "mínimo",
    ("baja", "grande"): "moderado", ("baja", "medio"): "mínimo", ("baja", "pequeño"): "mínimo",
}


def porcentaje_envio(valor_prioridad, deficit_pct):
    """Devuelve (% del faltante a enviar, lista de (urgencia, déficit, salida, fuerza))."""
    urgencia = (valor_prioridad - 1.0) / 2.0 * 100.0
    mu_u = {k: float(trap(urgencia, *p)) for k, p in URGENCIA.items()}
    mu_d = {k: float(trap(deficit_pct, *p)) for k, p in DEFICIT.items()}
    reglas, num, den = [], 0.0, 0.0
    for (u, d), salida in MATRIZ_CARGA.items():
        w = min(mu_u[u], mu_d[d])
        reglas.append((u, d, salida, w))
        num += w * ENVIO[salida]
        den += w
    return (num / den if den > 0 else 0.0), reglas


def repartir(solicitud, pesos, capacidad):
    """Reparte 'capacidad' unidades: proporcional a pesos, sin pasar de lo solicitado."""
    envio = {k: 0.0 for k in solicitud}
    activos = {k for k, v in solicitud.items() if v > 0}
    restante = float(capacidad)
    while activos and restante > 1e-9:
        sw = sum(pesos[k] for k in activos)
        prop = {k: restante * pesos[k] / sw for k in activos}
        llenos = [k for k in activos if solicitud[k] - envio[k] <= prop[k] + 1e-9]
        if not llenos:
            for k in activos:
                envio[k] += prop[k]
            break
        for k in llenos:
            restante -= solicitud[k] - envio[k]
            envio[k] = solicitud[k]
            activos.discard(k)
    # a unidades enteras sin pasar de la capacidad
    base = {k: int(np.floor(v + 1e-9)) for k, v in envio.items()}
    faltan = int(round(min(capacidad, sum(envio.values())))) - sum(base.values())
    for k in sorted(envio, key=lambda k: envio[k] - base[k], reverse=True)[: max(0, faltan)]:
        base[k] += 1
    return base
