import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import servicio
from motor import difuso, experto
from motor.red import EN_DISPUTA
from ui import (BRASS, COLOR_PRIORIDAD, DENIM, GRIS, LINEA, NAVY, RUST, corto, encabezado, grafico, navegacion,
                nota, pasos, pastilla)

COLORES_SET = [DENIM, BRASS, RUST, GRIS]
ETIQUETA = {
    "Concentrar|Expandirse": "Concentrar / el rival se expande",
    "Concentrar|Mantener": "Concentrar / el rival mantiene",
    "Distribuir|Expandirse": "Distribuir / el rival se expande",
    "Distribuir|Mantener": "Distribuir / el rival mantiene",
}


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
    encabezado(
        "Sprint 4 · Prioridad difusa",
        "De “urgente / media / baja” a un grado de urgencia",
        "Con reglas clásicas, un inventario de 19 unidades es “crítico” y uno de 21 no lo es. La lógica difusa "
        "permite grados: cuánto cumple cada tienda cada condición, y de ahí un puntaje continuo de urgencia.",
    )
    h = servicio.hechos_tupla(ss.hechos)
    clasica = servicio.clasica(h, ss.finde)
    dif = servicio.difusa(h, ss.finde)

    t1, t2, t3 = st.tabs(["1 · Cómo funciona", "2 · Resultado por tienda", "3 · Impacto en la ruta"])

    with t1:
        st.markdown(
            "**1. Fuzzificación.** Cada dato se convierte en grados de pertenencia (0 a 1). Los conjuntos se centran en "
            "los umbrales de las reglas clásicas: justo en el umbral la pertenencia es 0,5.\n\n"
            "**2. Reglas.** Las mismas 10 reglas, pero con *Y = mínimo* y respetando su orden: una regla más urgente "
            "que se activa apaga en proporción a las menos urgentes.\n\n"
            "**3. Desfuzzificación.** Se combinan las salidas (*baja, media, alta*) y el centroide da un puntaje de 0 a 100."
        )
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
        nota(f"Para que el algoritmo genético use el puntaje, se convierte a la misma escala del experto (1 a 3): "
             f"valor = 1 + 2 × (puntaje − {difuso.S_MIN:.0f}) / ({difuso.S_MAX:.0f} − {difuso.S_MIN:.0f}). "
             "Baja pura = 1, alta pura = 3.")

    with t2:
        filas = [{"Tienda": t, "Clásica": clasica[t][0], "Puntaje (0-100)": round(dif[t]["score"], 1),
                  "Valor (1-3)": round(dif[t]["valor"], 2), "Difusa": dif[t]["prioridad"]}
                 for t in sorted(dif, key=lambda t: -dif[t]["score"])]
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch", column_config={
            "Puntaje (0-100)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")})
        difieren = [f["Tienda"] for f in filas if f["Clásica"] != f["Difusa"]]
        nota("La etiqueta difusa sale del valor: ≥ 2,5 urgente, ≥ 1,5 media, el resto baja. "
             + (f"Difieren de la clásica: {', '.join(corto(t) for t in difieren)}." if difieren
                else "En estos datos coinciden con la clásica, pero el puntaje distingue grados dentro de cada nivel."))

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
        nota(f"{corto(tienda)}: inventario {inv}, ventas {ventas}/sem., {dias} días sin reabastecer, quejas: {quejas}. "
             "La activación es el grado en que se cumple la regla; la fuerza final descuenta lo que apagan las reglas más urgentes.")

    with t3:
        P = ss.params
        claves = list(ETIQUETA)
        ss.escenario = st.selectbox("Escenario", claves, index=claves.index(ss.escenario), format_func=lambda k: ETIQUETA[k],
                                    key="esc_difusa")
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
        nota("Con valores graduados, dos tiendas de prioridad media-alta pueden pesar más que una urgente: "
             "el genético puede cambiar de ruta aunque el orden de urgencia no cambie.")
    navegacion("5 · Prioridad difusa")
