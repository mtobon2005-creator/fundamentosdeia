import pandas as pd
import streamlit as st

from motor.experto import REGLAS, UMBRALES
from motor.red import RED
from paginas.conocimiento_uso import USO
from ui import COLOR_PRIORIDAD, encabezado, navegacion, pastilla

ARQUITECTURA = """
digraph G {
  rankdir=LR; bgcolor="transparent"; nodesep=0.5; ranksep=0.7;
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=15, margin="0.3,0.18", color="#1c2e4a", fillcolor="#eef1f6", fontcolor="#1c2e4a"];
  edge [color="#b8892f", penwidth=2];
  bc [label="Lo que se sabe siempre\\n(mapa, límites, 10 reglas)"];
  mt [label="Lo que pasa hoy\\n(inventario de cada tienda)"];
  r  [label="Razonar\\n¿quién es urgente?", fillcolor="#fbf3df"];
  s  [label="Decidir\\nla ruta del día", fillcolor="#fbf3df"];
  bc -> r; mt -> r; r -> s;
}
"""


def render():
    encabezado("Paso 2 · El experto", "¿Cómo decide quién necesita mercancía?",
               "Como un buen gerente: reglas claras aplicadas a los datos de hoy.")
    st.graphviz_chart(ARQUITECTURA, width="stretch")

    st.markdown("#### Las 10 reglas")
    cols = st.columns(2)
    for i, (rid, cond, concl) in enumerate(REGLAS):
        with cols[i // 5]:
            st.markdown(f"**{rid}** · SI {cond}<br>{pastilla(concl, COLOR_PRIORIDAD[concl])}", unsafe_allow_html=True)

    with st.expander("Ver los límites del negocio"):
        st.dataframe(pd.DataFrame([{"Concepto": USO[k][0], "Límite": USO[k][1], "Regla": USO[k][2]} for k in UMBRALES]),
                     hide_index=True, width="stretch")
    with st.expander("Ver los tramos del mapa"):
        filas = [{"Desde": a, "Hasta": b, "Minutos": w} for a, vs in RED.items() for b, w in vs if a < b]
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
    navegacion("2 · El experto")
