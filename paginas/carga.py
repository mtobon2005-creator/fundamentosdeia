import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import servicio
from motor import difuso
from ui import (BRASS, DENIM, LINEA, RUST, corto, encabezado, grafico, kpis, navegacion, nota, num, pasos,
                selector_escenario)


def render():
    ss = st.session_state
    C, P = ss.carga, ss.params
    encabezado("Paso 6 · La carga", "¿Cuántas unidades llevamos a cada tienda?",
               "La ruta dice a dónde ir; aquí decidimos cuánto dejar en cada parada.")
    h = servicio.hechos_tupla(ss.hechos)
    hechos = servicio._a_dict(h)

    selector_escenario("esc_carga")
    ss.modo_ruta = st.segmented_control(
        "Prioridad de la ruta", ["Clásica", "Difusa"], default=ss.modo_ruta, key="modo_carga",
        help="La ruta sigue el mismo selector del paso 4. El reparto de unidades siempre usa la urgencia difusa.") or ss.modo_ruta
    b, c = st.columns(2)
    C["capacidad"] = int(b.slider("Unidades que caben en el camión", 20, 400, int(C["capacidad"]), 10))
    C["objetivo"] = int(c.slider("Inventario ideal por tienda", 20, 200, int(C["objetivo"]), 10,
                                 help="Hasta qué nivel queremos llenar cada tienda."))
    ac, rv = ss.escenario.split("|")

    r = servicio.resolver(h, ss.finde, ss.tiempo, ss.modo_ruta, ac, rv, P["mult"], P["minuto"], P["castigo"], P["semilla"])
    valores = servicio.valores_base(h, ss.finde, "Difusa")
    filas = servicio.plan_de_carga(r["llegadas"], valores, hechos, C["capacidad"], C["objetivo"],
                                   ac == "Concentrar", P["mult"])
    solicitado = sum(f["_sol"] for f in filas)
    faltante = sum(f["Faltante"] for f in filas)
    enviado = sum(f["Envío"] for f in filas)
    alcanza = solicitado <= C["capacidad"] + 0.5

    kpis([(len(filas), "tiendas en la ruta"), (f"{solicitado:.0f}", "unidades que piden"),
          (f"{enviado} / {C['capacidad']}", "unidades que llevamos", True),
          ("Alcanza" if alcanza else "No alcanza", "el camión")])
    if round(solicitado) != faltante:
        nota(f"A las tiendas les faltan {faltante} unidades para llegar al ideal, pero piden {solicitado:.0f}: "
             "cada una pide solo una parte (25, 60 o 100 %) de lo que le falta, según qué tan urgente es.")
    if filas:
        nombres = [corto(f["Tienda"]) for f in filas]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=nombres, y=[f["Inventario"] for f in filas], name="Ya tiene", marker_color=DENIM,
                             text=[f["Inventario"] for f in filas], textposition="inside"))
        fig.add_trace(go.Bar(x=nombres, y=[f["Envío"] for f in filas], name="Le llevamos", marker_color=BRASS,
                             text=[f"+{f['Envío']}" for f in filas], textposition="inside"))
        fig.add_trace(go.Scatter(x=nombres, y=[C["objetivo"]] * len(filas), mode="lines+markers", name="Ideal",
                                 line=dict(color=RUST, dash="dash")))
        fig.update_layout(barmode="stack", height=480, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="white",
                          yaxis=dict(gridcolor=LINEA, title="unidades"), legend=dict(orientation="h", y=-0.12),
                          font=dict(size=14))
        grafico(fig)
    st.markdown(f"**Ruta con prioridad {ss.modo_ruta.lower()}**")
    st.markdown(pasos(r["ruta"], r["llegadas"], r["tarde"]), unsafe_allow_html=True)
    if not alcanza:
        st.warning("No alcanza para todo: repartimos en proporción a lo que cada tienda necesita"
                   + (f" y las tiendas en disputa pesan × {num(P['mult'])}." if ac == "Concentrar" else "."),
                   icon=":material/local_shipping:")

    df = pd.DataFrame(filas).drop(columns=["_reglas", "_sol"])
    prior = pd.DataFrame([{
        "Tienda": t, "Prioridad clásica": servicio.clasica(h, ss.finde)[t][0],
        "Puntaje difuso": num(d["score"], 1), "Valor difuso": num(d["valor"], 2)}
        for t, d in servicio.difusa(h, ss.finde).items()])
    ruta = pd.DataFrame([{"Parada": i + 1, "Tienda": t, "Minuto de llegada": m_,
                          "Llega tarde": "Sí" if t in r["tarde"] else "No"} for i, (t, m_) in enumerate(r["llegadas"].items())])
    st.download_button("Descargar el plan en Excel", icon=":material/download:",
                       data=servicio.exportar_excel({"Prioridad": prior, "Ruta": ruta, "Carga": df}),
                       file_name="plan_arturo_calle.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with st.expander("Ver el detalle por tienda"):
        st.dataframe(df.assign(Tienda=df["Tienda"].map(corto)), hide_index=True, width="stretch", column_config={
            "% a enviar": st.column_config.ProgressColumn("% de lo que falta", min_value=0, max_value=100, format="%.0f%%")})
    if filas:
        with st.expander("¿Cómo decide cuánto llevar?"):
            st.markdown("Combina dos cosas: **qué tan urgente** es la tienda y **cuánto le falta** para el nivel ideal. "
                        "Con eso decide llevar el 25 %, el 60 % o el 100 % de lo que le falta.")
            matriz = pd.DataFrame(
                [[difuso.MATRIZ_CARGA[(u, d)] for d in difuso.DEFICIT] for u in difuso.URGENCIA],
                index=[f"urgencia {u}" for u in difuso.URGENCIA], columns=[f"le falta {d}" for d in difuso.DEFICIT])
            st.dataframe(matriz, width="stretch")
    navegacion("6 · La carga")
