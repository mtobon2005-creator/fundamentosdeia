import pandas as pd
import streamlit as st

from motor.experto import ORDEN_PRIORIDAD, REGLAS, UMBRALES
from motor.red import ORIGEN, RED
from ui import COLOR_PRIORIDAD, encabezado, navegacion, nota, pastilla

USO = {
    "INVENTARIO_MUY_BAJO": ("Inventario muy bajo", "< 10 u.", "R1"),
    "UMBRAL_INVENTARIO_CRITICO": ("Inventario crítico", "< 20 u.", "R4, R5"),
    "INVENTARIO_SOBRANTE": ("Inventario sobrante", "> 100 u.", "R9"),
    "UMBRAL_VENTAS_ALTAS_NORMAL": ("Ventas altas (normal)", "> 50 /sem.", "R4"),
    "UMBRAL_VENTAS_ALTAS_FIN_DE_SEMANA": ("Ventas altas (fin de semana)", "> 40 /sem.", "R4"),
    "UMBRAL_ROTACION_MUY_ALTA": ("Rotación muy alta", "> 70 /sem.", "R7"),
    "LIMITE_DIAS_SIN_REABASTECER": ("Días sin reabastecer (media)", "> 14 días", "R6"),
    "LIMITE_DIAS_MUY_URGENTE": ("Días sin reabastecer (urgente)", "> 25 días", "R3"),
    "LIMITE_QUEJAS": ("Quejas de clientes", "> 3", "R2"),
    "TIEMPO_ATENCION_POR_TIENDA": ("Atención por tienda", "15 min", "Plan del día"),
}

ARQUITECTURA = """
digraph G {
  rankdir=TB; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, color="#1c2e4a", fillcolor="#eef1f6", fontcolor="#1c2e4a"];
  edge [color="#b8892f"];
  bc [label="Base de conocimiento\\nred + umbrales + 10 reglas"];
  mt [label="Memoria de trabajo\\ndatos de hoy: 9 tiendas + tiempo"];
  r  [label="Motor de inferencia 3.1\\nRazonamiento: reglas → prioridad", fillcolor="#fbf3df"];
  s  [label="Motor de inferencia 3.2\\nSolución: ruta del día", fillcolor="#fbf3df"];
  bc -> r; mt -> r; r -> s;
}
"""


def render():
    encabezado("Sprint 2 · Base de conocimiento", "Lo que el experto sabe de antemano",
               "Base de conocimiento + memoria de trabajo + motor de inferencia.")
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("#### Cómo se conectan")
        st.graphviz_chart(ARQUITECTURA)
    with c2:
        st.markdown("#### La base tiene tres piezas")
        st.markdown("1. **Relaciones:** red de calles y jerarquía de prioridades.\n"
                    "2. **Hechos:** umbrales del negocio.\n"
                    "3. **Reglas:** 10 SI-ENTONCES; gana la primera que se cumple.")

    st.markdown("#### 1 · Relaciones")
    r1, r2 = st.columns(2)
    with r1:
        filas = [{"Desde": a, "Hasta": b, "Minutos": w} for a, vs in RED.items() for b, w in vs if a < b]
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch", height=240)
    with r2:
        st.markdown(" ".join(pastilla(f"{p} · orden {o}", COLOR_PRIORIDAD[p]) for p, o in ORDEN_PRIORIDAD.items()),
                    unsafe_allow_html=True)

    st.markdown("#### 2 · Hechos generales (umbrales)")
    st.dataframe(
        pd.DataFrame([{"Concepto": USO[k][0], "Umbral": USO[k][1], "Se usa en": USO[k][2]} for k in UMBRALES]),
        hide_index=True, width="stretch")

    st.markdown("#### 3 · Reglas SI-ENTONCES")
    for rid, cond, concl in REGLAS:
        a, b, c = st.columns([1, 6, 2])
        a.markdown(f"**{rid}**")
        b.markdown(f"SI {cond}")
        c.markdown(pastilla(concl, COLOR_PRIORIDAD[concl]), unsafe_allow_html=True)
    navegacion("2 · Base de conocimiento")
