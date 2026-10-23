import streamlit as st

from estado import ir_a
from ui import encabezado, nota


def render():
    encabezado(
        "Fundamentos de Inteligencia Artificial",
        "Logística inteligente para Arturo Calle",
        "Cómo agilizar el reparto de inventario desde la Bodega Itagüí hacia 9 tiendas del Valle de Aburrá, "
        "con un camión, 90 minutos y un competidor que puede expandirse.",
    )
    c = st.columns(4)
    c[0].metric("Tiendas", "9")
    c[1].metric("Tiempo disponible", "90 min")
    c[2].metric("Atención por tienda", "15 min")
    c[3].metric("Recorrer las 9 (A*)", "104 min")
    nota("Las 9 tiendas no caben en el día: hay que decidir cuáles visitar, en qué orden y cuánto llevar a cada una.")

    st.subheader("Cuatro sprints, un solo flujo")
    sprints = [
        ("Sprint 1", "Red logística", "Mapa de tiempos entre tiendas. Dijkstra calcula el camino más corto y A* "
         "resuelve el recorrido completo.", "1 · Red logística"),
        ("Sprint 2", "Sistema experto", "Base de conocimiento de 10 reglas SI-ENTONCES que clasifica cada tienda "
         "como urgente, media o baja.", "2 · Base de conocimiento"),
        ("Sprint 3", "Competencia y ruta", "Teoría de juegos (Nash) frente al rival y un algoritmo genético que "
         "arma la ruta del día.", "4 · Competencia y ruta"),
        ("Sprint 4", "Lógica difusa", "Prioridad difusa en lugar de urgente/media/baja, y una capa que decide "
         "cuántas unidades enviar a cada tienda.", "5 · Prioridad difusa"),
    ]
    cols = st.columns(4)
    for col, (s, titulo, texto, destino) in zip(cols, sprints):
        with col.container(border=True):
            st.markdown(f'<div class="eyebrow">{s}</div>', unsafe_allow_html=True)
            st.markdown(f"**{titulo}**")
            st.caption(texto)
            st.button("Ver", key=f"ver_{s}", on_click=ir_a, args=(destino,))

    st.subheader("Cómo se conecta")
    st.markdown(
        "**Red** → **Conocimiento del experto** → **Prioridad por tienda** → **Juego contra el rival** → "
        "**Ruta del día** → **Prioridad difusa** → **Unidades por tienda**"
    )
    st.markdown(
        "- Los datos del día (inventario, ventas, días sin reabastecer, quejas) se editan una sola vez en "
        "*Sistema experto* y alimentan todo lo demás.\n"
        "- Cada página usa el resultado de la anterior; puedes recorrerlas con los botones de abajo."
    )
    nota("Integrantes: Mariana Tobón y Maria Clara Escobar · Los pagos del juego son supuestos del modelo, no datos reales.")
    st.divider()
    st.button("Empezar: 1 · Red logística →", type="primary", on_click=ir_a, args=("1 · Red logística",))
