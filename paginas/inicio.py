import streamlit as st

from estado import ir_a
from paginas.resumen import svg_resumen
from ui import kpis


def render():
    st.markdown(
        '<div class="hero"><div class="eyebrow">Fundamentos de Inteligencia Artificial</div>'
        "<h1>Logística inteligente para Arturo Calle</h1>"
        "<p>Un camión, 90 minutos, 9 tiendas y un rival que puede expandirse: ¿a dónde ir y cuánto llevar?</p></div>",
        unsafe_allow_html=True,
    )
    st.image(svg_resumen(), width="stretch")
    kpis([("9", "tiendas"), ("90 min", "para repartir"), ("104 min", "recorrerlas todas", True), ("68 min", "ruta elegida")])

    sprints = [
        ("Sprint 1", "Red logística", "Dijkstra y A*", "1 · Red logística", ":material/route:"),
        ("Sprint 2", "Sistema experto", "10 reglas de prioridad", "3 · Sistema experto", ":material/rule:"),
        ("Sprint 3", "Competencia", "Nash + genético", "4 · Competencia y ruta", ":material/swords:"),
        ("Sprint 4", "Lógica difusa", "Prioridad y carga", "5 · Prioridad difusa", ":material/tune:"),
    ]
    for col, (s, titulo, texto, destino, icono) in zip(st.columns(4), sprints):
        with col.container(border=True):
            st.markdown(f'<div class="eyebrow">{s}</div>', unsafe_allow_html=True)
            st.markdown(f"**{titulo}**")
            st.caption(texto)
            st.button("Abrir", key=f"ver_{s}", on_click=ir_a, args=(destino,), icon=icono)
    st.caption("Mariana Tobón · Maria Clara Escobar")
    st.button("Empezar el recorrido", type="primary", on_click=ir_a, args=("1 · Red logística",), icon=":material/arrow_forward:")
