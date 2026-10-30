import streamlit as st

from estado import ir_a
from paginas.resumen import svg_resumen


def render():
    st.markdown(
        '<div class="hero"><div class="eyebrow">Fundamentos de Inteligencia Artificial</div>'
        "<h1>Logística inteligente para Arturo Calle</h1>"
        "<p>Un camión, 90 minutos y 9 tiendas: ¿a cuáles vamos y cuánto llevamos?</p></div>",
        unsafe_allow_html=True,
    )
    st.image(svg_resumen(), width="stretch")

    sprints = [
        ("Sprint 1", "El mapa", "Medimos cuánto tarda llegar a cada tienda.", "1 · El mapa", ":material/route:"),
        ("Sprint 2", "El experto", "Reglas que dicen qué tienda necesita mercancía.", "3 · El plan del día", ":material/rule:"),
        ("Sprint 3", "El rival", "Qué hacer si un competidor llega a nuestras zonas.", "4 · El rival", ":material/swords:"),
        ("Sprint 4", "Los grados", "Urgencia de 0 a 100 y unidades por tienda.", "5 · Grados de urgencia", ":material/tune:"),
    ]
    for col, (s, titulo, texto, destino, icono) in zip(st.columns(4), sprints):
        with col.container(border=True):
            st.markdown(f'<div class="eyebrow">{s}</div>', unsafe_allow_html=True)
            st.markdown(f"**{titulo}**")
            st.caption(texto)
            st.button("Abrir", key=f"ver_{s}", on_click=ir_a, args=(destino,), icon=icono)
    st.button("Empezar el recorrido", type="primary", on_click=ir_a, args=("1 · El mapa",),
              icon=":material/arrow_forward:")
    st.caption("Mariana Tobón · Maria Clara Escobar")
