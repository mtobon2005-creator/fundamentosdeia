import plotly.graph_objects as go
import streamlit as st

from motor.red import DIST, ORIGEN, RED, TIENDAS, a_estrella_tsp, camino
from ui import NAVY, encabezado, grafico, mapa, navegacion, nota, pasos


@st.cache_data(show_spinner=False)
def _astar(cerrada):
    return a_estrella_tsp(DIST, ORIGEN, TIENDAS, cerrada)


def render():
    encabezado("Sprint 1 · Red logística", "Una bodega, nueve tiendas",
               "Los tramos son minutos en hora pico, no kilómetros.")
    vista = st.segmented_control("Vista", ["Camino más corto", "Recorrido completo (A*)"],
                                 default="Camino más corto", label_visibility="collapsed") or "Camino más corto"
    izq, der = st.columns([3, 2])
    nodos = list(RED)
    if vista.startswith("Camino"):
        with der:
            a = st.selectbox("Desde", nodos, index=0)
            b = st.selectbox("Hasta", nodos, index=nodos.index("Puerta del Norte"))
            ruta = camino(a, b)
            st.metric("Tiempo mínimo (Dijkstra)", f"{DIST[a][b]} min")
            st.markdown(pasos(ruta), unsafe_allow_html=True)
        ruta_mapa = ruta
    else:
        cerrada = der.toggle("Volver a la bodega al final", value=True)
        ruta_mapa, costo = _astar(cerrada)
        with der:
            st.metric("Tiempo de viaje", f"{costo} min", help="Solo viaje, sin los 15 min de atención por tienda.")
            st.markdown(pasos(ruta_mapa), unsafe_allow_html=True)
    with izq:
        grafico(mapa(ruta=ruta_mapa, zonas=False))

    cerrada_costo = _astar(True)[1]
    st.info(f"Las 9 tiendas toman **{cerrada_costo + 9 * 15} min** con la atención; el camión tiene **90**. "
            "Hay que elegir a cuáles ir.", icon=":material/timer:")

    with st.expander("Tiempos mínimos entre todos los pares (matriz de Dijkstra)"):
        z = [[DIST[o][d] for d in nodos] for o in nodos]
        fig = go.Figure(go.Heatmap(z=z, x=nodos, y=nodos, text=z, texttemplate="%{text}",
                                   colorscale=[[0, "#ffffff"], [1, NAVY]], showscale=False))
        fig.update_layout(height=520, margin=dict(l=0, r=0, t=0, b=0), yaxis=dict(autorange="reversed"))
        grafico(fig)
    navegacion("1 · Red logística")
