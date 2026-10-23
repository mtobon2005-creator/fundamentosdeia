"""Estado compartido entre páginas (st.session_state)."""
import pandas as pd
import streamlit as st

from motor.experto import HECHOS_NOTEBOOK
from motor.genetico import PARAMS_NOTEBOOK

COLUMNAS = ["Inventario", "Ventas/sem", "Días sin reabastecer", "Quejas"]
PAGINAS = [
    "Inicio",
    "1 · Red logística",
    "2 · Base de conocimiento",
    "3 · Sistema experto",
    "4 · Competencia y ruta",
    "5 · Prioridad difusa",
    "6 · Carga por tienda",
]


def hechos_notebook():
    df = pd.DataFrame.from_dict(HECHOS_NOTEBOOK, orient="index", columns=COLUMNAS)
    df.index.name = "Tienda"
    return df


def iniciar():
    ss = st.session_state
    ss.setdefault("pagina", PAGINAS[0])
    ss.setdefault("hechos", hechos_notebook())
    ss.setdefault("finde", True)
    ss.setdefault("tiempo", 90)
    ss.setdefault("params", dict(PARAMS_NOTEBOOK))
    ss.setdefault("escenario", "Concentrar|Expandirse")
    ss.setdefault("modo_ruta", "Clásica")
    ss.setdefault("carga", {"capacidad": 150, "objetivo": 100})


def ir_a(pagina):
    st.session_state["pagina"] = pagina
