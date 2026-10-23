"""Puente entre el estado de la app y el motor (con caché)."""
from io import BytesIO

import pandas as pd
import streamlit as st

from estado import COLUMNAS
from motor import difuso, experto, genetico
from motor.red import EN_DISPUTA, TIENDAS


def hechos_tupla(df):
    df = df.fillna(0)
    return tuple((t, *[int(r[c]) for c in COLUMNAS]) for t, r in df.iterrows())


def _a_dict(h):
    return {t: tuple(v) for t, *v in h}


@st.cache_data(show_spinner=False)
def clasica(h, finde):
    """{tienda: (prioridad, regla)} con las 10 reglas del experto."""
    return experto.razonar(_a_dict(h), finde)


@st.cache_data(show_spinner=False)
def difusa(h, finde):
    """{tienda: resultado difuso}."""
    return {t: difuso.evaluar(*v, finde) for t, v in _a_dict(h).items()}


def valores_base(h, finde, modo):
    if modo == "Difusa":
        return {t: r["valor"] for t, r in difusa(h, finde).items()}
    return {t: experto.VALOR_PRIORIDAD[p] for t, (p, _) in clasica(h, finde).items()}


@st.cache_data(show_spinner=False)
def resolver(h, finde, tiempo, modo, ac, rv, mult, minuto, castigo, semilla):
    """Escenario → algoritmo genético → ruta, más el control exhaustivo."""
    p = {"mult": mult, "minuto": minuto, "castigo": castigo}
    esc = genetico.construir_escenario(ac, rv, valores_base(h, finde, modo), p)
    mejor, hist, prom = genetico.algoritmo_genetico(esc, tiempo, semilla)
    ruta, llegadas, total = genetico.decodificar(mejor, tiempo)
    _, opt = genetico.busqueda_exhaustiva(esc, tiempo)
    return {
        "esc": esc, "ruta": ruta, "llegadas": llegadas, "total": total,
        "fitness": genetico.calcular_fitness(mejor, esc, tiempo),
        "hist": hist, "prom": prom, "optimo": opt,
        "tarde": [t for t, m in llegadas.items() if genetico.llega_tarde(esc, t, m)],
    }


def plan_de_carga(llegadas, valores, hechos, capacidad, objetivo, concentrar, mult):
    """Capa de decisión de carga: cuántas unidades lleva el camión a cada tienda de la ruta."""
    filas, solicitud, pesos = [], {}, {}
    for t in llegadas:
        inv = hechos[t][0]
        faltante = max(0, objetivo - inv)
        pct_def = faltante / objetivo * 100 if objetivo else 0
        pct, reglas = difuso.porcentaje_envio(valores[t], pct_def)
        solicitud[t] = pct / 100 * faltante
        pesos[t] = solicitud[t] * (mult if concentrar and t in EN_DISPUTA else 1)
        filas.append({"Tienda": t, "Inventario": inv, "Faltante": faltante,
                      "% a enviar": round(pct, 1), "Solicitud": round(solicitud[t], 1), "_reglas": reglas})
    envio = difuso.repartir(solicitud, pesos, capacidad)
    for f in filas:
        f["Envío"] = envio[f["Tienda"]]
        f["Inventario final"] = f["Inventario"] + f["Envío"]
    return filas


def exportar_excel(hojas):
    """hojas: {nombre: DataFrame} → bytes de un .xlsx con encabezado y anchos ajustados."""
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for nombre, df in hojas.items():
            df.to_excel(w, sheet_name=nombre[:31], index=False)
            ws = w.sheets[nombre[:31]]
            for celda in ws[1]:
                celda.font = celda.font.copy(bold=True)
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(
                    42, max(len(str(c.value)) if c.value is not None else 0 for c in col) + 3)
    return buf.getvalue()
