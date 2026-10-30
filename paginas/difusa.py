import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import servicio
from motor import difuso, experto
from motor.red import EN_DISPUTA
from ui import (BRASS, COLOR_PRIORIDAD, DENIM, ETIQUETA, GRIS, LINEA, NAVY, RUST, corto, encabezado, grafico, kpis,
                navegacion, nota, pasos, pastilla, selector_escenario)

COLORES_SET = [DENIM, BRASS, RUST, GRIS]
def _funciones_pertenencia(finde, marca=None):
    conjuntos = difuso.conjuntos_entrada(finde)
    fig = make_subplots(rows=2, cols=2, subplot_titles=list(conjuntos), vertical_spacing=0.2)
    for k, (var, sets) in enumerate(conjuntos.items()):
        x = np.linspace(0, difuso.RANGOS[var], 400)
        for j, (nombre, p) in enumerate(sets.items()):
            fig.add_trace(go.Scatter(x=x, y=difuso.trap(x, *p), mode="lines", name=nombre,
                                     line=dict(color=COLORES_SET[j % 4], width=2.5), showlegend=False,
                                     hovertemplate=f"{nombre}: %{{y:.2f}}<extra></extra>"),
                          row=k // 2 + 1, col=k % 2 + 1)
            xm = x[np.argmax(difuso.trap(x, *p))] + j * 0.09 * difuso.RANGOS[var]
            fig.add_annotation(x=xm, y=1.08, text=nombre, showarrow=False, font=dict(size=10, color=COLORES_SET[j % 4]),
                               row=k // 2 + 1, col=k % 2 + 1)
        if marca is not None:
            fig.add_vline(x=marca[var], line_dash="dash", line_color=NAVY, row=k // 2 + 1, col=k % 2 + 1)
    fig.update_yaxes(range=[0, 1.2], gridcolor=LINEA, tickvals=[0, .5, 1])
    fig.update_xaxes(gridcolor=LINEA)
    fig.update_layout(height=430, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white", font=dict(color=NAVY))
    return fig


def render():
    ss = st.session_state
    encabezado("Paso 5 · Grados, no etiquetas", "¿Qué tan urgente es cada tienda?",
               "En vez de “urgente o no”, medimos la urgencia de 0 a 100. Esto es lógica difusa.")
    h = servicio.hechos_tupla(ss.hechos)
    clasica = servicio.clasica(h, ss.finde)
    dif = servicio.difusa(h, ss.finde)

    t0, t2, t3, t1 = st.tabs(["Pruébalo", "Por tienda", "Efecto en la ruta", "Cómo funciona"])

    with t0:
        st.caption("Mueve los datos de una tienda y mira cómo cambia su urgencia.")
        c1, c2 = st.columns([2, 3])
        with c1:
            inv = st.slider("Unidades en la tienda", 0, 150, 15)
            ventas = st.slider("Ventas por semana", 0, 120, 55)
            dias = st.slider("Días sin recibir mercancía", 0, 45, 12)
            quejas = st.slider("Quejas de clientes", 0, 8, 1)
        r = difuso.evaluar(inv, ventas, dias, quejas, ss.finde)
        clasico, regla = experto.regla_prioridad(inv, ventas, dias, quejas, ss.finde)
        with c2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=r["score"], number=dict(suffix=" / 100", font=dict(color=NAVY)),
                gauge=dict(axis=dict(range=[0, 100]), bar=dict(color=NAVY),
                           steps=[dict(range=[0, 35], color="#e7eaf0"), dict(range=[35, 65], color="#f3e3b8"),
                                  dict(range=[65, 100], color="#f0c4b6")])))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=10, b=0))
            grafico(fig)
            a, b = st.columns(2)
            a.markdown("**Con etiquetas**<br>" + pastilla(f"{clasico} · {regla}", COLOR_PRIORIDAD[clasico]), unsafe_allow_html=True)
            b.markdown("**Con grados**<br>" + pastilla(f"{r['prioridad']} · {r['score']:.0f} pts", COLOR_PRIORIDAD[r["prioridad"]]),
                       unsafe_allow_html=True)
            fig = go.Figure(go.Bar(x=r["fuerza"][::-1], y=[x[0] for x in difuso.REGLAS_DIFUSAS][::-1], orientation="h",
                                   marker_color=[{"alta": RUST, "media": BRASS, "baja": GRIS}[x[2]] for x in difuso.REGLAS_DIFUSAS][::-1]))
            fig.update_layout(height=260, margin=dict(l=0, r=0, t=26, b=0), plot_bgcolor="white",
                              title=dict(text="Qué reglas pesan más", font=dict(size=13, color=NAVY)),
                              xaxis=dict(range=[0, 1], gridcolor=LINEA))
            grafico(fig)

    with t1:
        st.markdown("**1 · Medir en grados** (de 0 a 1)  →  **2 · Aplicar las reglas**  →  **3 · Resumir en un puntaje** (0 a 100)")
        grafico(_funciones_pertenencia(ss.finde))
        c1, c2 = st.columns([3, 2])
        with c1:
            st.dataframe(pd.DataFrame([{"Regla": rid, "SI": txt, "ENTONCES urgencia": s}
                                       for rid, txt, s in difuso.REGLAS_DIFUSAS]), hide_index=True, width="stretch")
        with c2:
            fig = go.Figure()
            for (nombre, curva), col in zip(difuso.CURVAS.items(), [GRIS, BRASS, RUST]):
                fig.add_trace(go.Scatter(x=difuso.U, y=curva, mode="lines", name=nombre, line=dict(color=col, width=2.5)))
            fig.update_layout(height=250, margin=dict(l=0, r=0, t=26, b=0), plot_bgcolor="white",
                              title=dict(text="Urgencia (salida)", font=dict(size=14, color=NAVY)),
                              xaxis=dict(gridcolor=LINEA), yaxis=dict(gridcolor=LINEA, tickvals=[0, .5, 1]),
                              legend=dict(orientation="h", y=-0.25))
            grafico(fig)
        nota(f"Valor para el genético = 1 + 2 × (puntaje − {difuso.S_MIN:.0f}) / ({difuso.S_MAX:.0f} − {difuso.S_MIN:.0f}): baja pura 1, alta pura 3.")

    with t2:
        filas = [{"Tienda": t, "Clásica": clasica[t][0], "Puntaje (0-100)": round(dif[t]["score"], 1),
                  "Valor (1-3)": round(dif[t]["valor"], 2), "Difusa": dif[t]["prioridad"]}
                 for t in sorted(dif, key=lambda t: -dif[t]["score"])]
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch", column_config={
            "Puntaje (0-100)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")})
        difieren = [f["Tienda"] for f in filas if f["Clásica"] != f["Difusa"]]
        difieren = [f["Tienda"] for f in filas if f["Clásica"] != f["Difusa"]]
        if difieren:
            nota(f"Difieren de la clásica: {', '.join(corto(t) for t in difieren)}.")

        tienda = st.selectbox("Inspeccionar una tienda", list(dif), format_func=corto)
        r = dif[tienda]
        inv, ventas, dias, quejas = servicio._a_dict(h)[tienda]
        a, b = st.columns([3, 2])
        with a:
            fig = go.Figure()
            for nombre, curva in difuso.CURVAS.items():
                fig.add_trace(go.Scatter(x=difuso.U, y=curva, mode="lines", line=dict(color=LINEA, width=1), showlegend=False))
            fig.add_trace(go.Scatter(x=difuso.U, y=r["agregada"], fill="tozeroy", mode="lines", name="Salida combinada",
                                     line=dict(color=BRASS, width=2), fillcolor="rgba(184,137,47,.3)"))
            fig.add_vline(x=r["score"], line_color=NAVY, annotation_text=f"centroide {r['score']:.1f}")
            fig.update_layout(height=260, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white", showlegend=False,
                              title=dict(text=f"Desfuzzificación · {corto(tienda)}", font=dict(size=14, color=NAVY)),
                              xaxis=dict(title="urgencia", gridcolor=LINEA), yaxis=dict(gridcolor=LINEA, range=[0, 1.05]))
            grafico(fig)
        with b:
            st.dataframe(pd.DataFrame({
                "Regla": [x[0] for x in difuso.REGLAS_DIFUSAS],
                "Activación": [round(x, 2) for x in r["activaciones"]],
                "Fuerza final": [round(x, 2) for x in r["fuerza"]]}),
                hide_index=True, width="stretch", height=250)
        nota(f"{corto(tienda)}: inventario {inv}, ventas {ventas}/sem., {dias} días, quejas {quejas}.")

    with t3:
        P = ss.params
        selector_escenario("esc_difusa")
        ac, rv = ss.escenario.split("|")

        def res(modo):
            return servicio.resolver(h, ss.finde, ss.tiempo, modo, ac, rv, P["mult"], P["minuto"], P["castigo"], P["semilla"])

        c1, c2 = st.columns(2)
        for col, modo in ((c1, "Clásica"), (c2, "Difusa")):
            x = res(modo)
            with col.container(border=True):
                st.markdown(f"**Prioridad {modo.lower()}**")
                st.markdown(pasos(x["ruta"], x["llegadas"], x["tarde"]), unsafe_allow_html=True)
                m = st.columns(3)
                m[0].metric("Paradas", len(x["llegadas"]))
                m[1].metric("Tiempo", f"{x['total']} min")
                m[2].metric("Fitness", f"{x['fitness']:.2f}")
        v = servicio.valores_base(h, ss.finde, "Difusa")
        v0 = servicio.valores_base(h, ss.finde, "Clásica")
        fig = go.Figure()
        orden = sorted(v, key=lambda t: -v[t])
        fig.add_trace(go.Bar(x=[corto(t) for t in orden], y=[v0[t] for t in orden], name="Clásica", marker_color=LINEA))
        fig.add_trace(go.Bar(x=[corto(t) for t in orden], y=[v[t] for t in orden], name="Difusa", marker_color=BRASS))
        fig.update_layout(barmode="group", height=280, margin=dict(l=0, r=0, t=26, b=0), plot_bgcolor="white",
                          title=dict(text="Valor de cada tienda para el algoritmo genético", font=dict(size=14, color=NAVY)),
                          yaxis=dict(gridcolor=LINEA, range=[0, 3.2]), legend=dict(orientation="h", y=-0.25))
        grafico(fig)
        nota("Con valores graduados, dos tiendas medias pueden pesar más que una urgente: la ruta puede cambiar.")
    navegacion("5 · Grados de urgencia")
