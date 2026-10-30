import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import servicio
from motor import difuso
from motor.red import EN_DISPUTA
from ui import (BRASS, DENIM, LINEA, NAVY, RUST, corto, encabezado, grafico, kpis, mapa, navegacion, nota, pasos,
                selector_escenario)

def render():
    ss = st.session_state
    C, P = ss.carga, ss.params
    encabezado("Sprint 4 · Carga por tienda", "¿Cuántas unidades lleva el camión a cada tienda?",
               "La ruta dice a dónde ir; el sistema difuso dice cuánto dejar en cada parada.")
    h = servicio.hechos_tupla(ss.hechos)
    hechos = servicio._a_dict(h)

    selector_escenario("esc_carga")
    b, c = st.columns(2)
    C["capacidad"] = int(b.slider("Capacidad del camión (u.)", 20, 400, int(C["capacidad"]), 10))
    C["objetivo"] = int(c.slider("Inventario objetivo por tienda", 20, 200, int(C["objetivo"]), 10,
                                 help="Nivel al que se quiere dejar cada tienda (100 = umbral de sobrante del experto)."))
    ac, rv = ss.escenario.split("|")

    r = servicio.resolver(h, ss.finde, ss.tiempo, "Difusa", ac, rv, P["mult"], P["minuto"], P["castigo"], P["semilla"])
    valores = servicio.valores_base(h, ss.finde, "Difusa")
    filas = servicio.plan_de_carga(r["llegadas"], valores, hechos, C["capacidad"], C["objetivo"], ac == "Concentrar", P["mult"])

    st.markdown("**Ruta del día con prioridad difusa**")
    st.markdown(pasos(r["ruta"], r["llegadas"], r["tarde"]), unsafe_allow_html=True)

    solicitado = sum(f["Solicitud"] for f in filas)
    enviado = sum(f["Envío"] for f in filas)
    alcanza = solicitado <= C["capacidad"] + 0.5
    kpis([(len(filas), "tiendas en ruta"), (f"{solicitado:.0f}", "unidades solicitadas"),
          (f"{enviado} / {C['capacidad']}", "unidades enviadas", True), ("Alcanza" if alcanza else "No alcanza", "capacidad")])
    if not alcanza:
        st.warning("No alcanza para todo: se reparte en proporción a lo que cada tienda necesita"
                   + (f"; las tiendas en disputa pesan × {P['mult']:g}." if ac == "Concentrar" else "."),
                   icon=":material/local_shipping:")
    df = pd.DataFrame(filas).drop(columns="_reglas")
    st.dataframe(df, hide_index=True, width="stretch", column_config={
        "% a enviar": st.column_config.ProgressColumn("% del faltante", min_value=0, max_value=100, format="%.0f%%"),
        "Envío": st.column_config.NumberColumn("Envío (u.)")})

    if filas:
        fig = go.Figure()
        nombres = [corto(f["Tienda"]) for f in filas]
        fig.add_trace(go.Bar(x=nombres, y=[f["Inventario"] for f in filas], name="Inventario actual", marker_color=DENIM))
        fig.add_trace(go.Bar(x=nombres, y=[f["Envío"] for f in filas], name="Envío", marker_color=BRASS))
        fig.add_trace(go.Scatter(x=nombres, y=[C["objetivo"]] * len(filas), mode="lines", name="Objetivo",
                                 line=dict(color=RUST, dash="dash")))
        fig.update_layout(barmode="stack", height=300, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="white",
                          yaxis=dict(gridcolor=LINEA, title="unidades"), legend=dict(orientation="h", y=-0.2))
        grafico(fig)

        with st.expander("Cómo decidió el sistema difuso"):
            st.markdown("Entradas: **urgencia** y **déficit** (% que falta para el objetivo). "
                        "Salida: **% del faltante a enviar** (25 · 60 · 100 %), promedio ponderado tipo Sugeno.")
            matriz = pd.DataFrame(
                [[difuso.MATRIZ_CARGA[(u, d)] for d in difuso.DEFICIT] for u in difuso.URGENCIA],
                index=[f"urgencia {u}" for u in difuso.URGENCIA], columns=[f"déficit {d}" for d in difuso.DEFICIT])
            st.dataframe(matriz, width="stretch")
            tienda = st.selectbox("Reglas activas en", [f["Tienda"] for f in filas], format_func=corto)
            reglas = next(f["_reglas"] for f in filas if f["Tienda"] == tienda)
            st.dataframe(pd.DataFrame([{"Urgencia": u, "Déficit": d, "Envío": s, "Fuerza": round(w, 2)}
                                       for u, d, s, w in reglas if w > 0]), hide_index=True, width="stretch")

    prior = pd.DataFrame([{
        "Tienda": t, "Prioridad clásica": servicio.clasica(h, ss.finde)[t][0],
        "Puntaje difuso": round(d["score"], 1), "Valor difuso": round(d["valor"], 2)}
        for t, d in servicio.difusa(h, ss.finde).items()])
    ruta = pd.DataFrame([{"Parada": i + 1, "Tienda": t, "Minuto de llegada": m_,
                          "Llega tarde": "Sí" if t in r["tarde"] else "No"} for i, (t, m_) in enumerate(r["llegadas"].items())])
    st.download_button(
        "Descargar plan en Excel", icon=":material/download:", data=servicio.exportar_excel({"Prioridad": prior, "Ruta": ruta, "Carga": df}),
        file_name="plan_arturo_calle.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    navegacion("6 · Carga por tienda")
