import plotly.graph_objects as go
import streamlit as st

from motor.red import DIST, ORIGEN, RED, TIENDAS, a_estrella_tsp, camino
from ui import NAVY, corto, encabezado, grafico, kpis, mapa, navegacion, pasos


@st.cache_data(show_spinner=False)
def _astar(cerrada):
    return a_estrella_tsp(DIST, ORIGEN, TIENDAS, cerrada)


def render():
    encabezado("Paso 1 · El mapa", "¿Cuánto tarda llegar a cada tienda?",
               "Una bodega, nueve tiendas y el tráfico del Valle de Aburrá. Los números del mapa son minutos.")
    vista = st.segmented_control("Vista", ["Camino más corto", "Recorrer las 9 tiendas"],
                                 default="Camino más corto", label_visibility="collapsed") or "Camino más corto"
    nodos = list(RED)
    if vista == "Camino más corto":
        c1, c2 = st.columns(2)
        a = c1.selectbox("Desde", nodos, index=0, format_func=corto)
        b = c2.selectbox("Hasta", nodos, index=nodos.index("Puerta del Norte"), format_func=corto)
        ruta_mapa = camino(a, b)
        tiempo = f"{DIST[a][b]} min"
        etiqueta = "es lo mínimo que tarda"
    else:
        cerrada = st.toggle("Volver a la bodega al final", value=True)
        ruta_mapa, costo = _astar(cerrada)
        tiempo = f"{costo} min"
        etiqueta = "solo de viaje"
    grafico(mapa(ruta=ruta_mapa, zonas=False, altura=600))
    kpis([(tiempo, etiqueta, True), (f"{_astar(True)[1] + 9 * 15} min", "recorrer las 9 con atención"), ("90 min", "tiene el camión")])
    st.markdown(pasos(ruta_mapa), unsafe_allow_html=True)
    st.info("No caben las 9 tiendas: hay que elegir a cuáles ir.", icon=":material/timer:")

    with st.expander("Ver todos los tiempos entre tiendas"):
        z = [[DIST[o][d] for d in nodos] for o in nodos]
        fig = go.Figure(go.Heatmap(z=z, x=[corto(n) for n in nodos], y=[corto(n) for n in nodos], text=z,
                                   texttemplate="%{text}", colorscale=[[0, "#ffffff"], [1, NAVY]], showscale=False))
        fig.update_layout(height=520, margin=dict(l=0, r=0, t=0, b=0), yaxis=dict(autorange="reversed"))
        grafico(fig)
    navegacion("1 · El mapa")
