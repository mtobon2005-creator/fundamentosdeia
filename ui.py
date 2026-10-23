"""Elementos visuales compartidos: estilo, mapa, línea de tiempo y navegación."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from estado import PAGINAS, ir_a
from motor.red import EN_DISPUTA, ORIGEN, POS, TIEMPO_ATENCION, aristas, camino

NAVY, BRASS, RUST, DENIM = "#1c2e4a", "#b8892f", "#c0583f", "#4a78ad"
GRIS, LINEA, VERDE = "#7b8798", "#d5dae1", "#3f8f6b"
COLOR_PRIORIDAD = {"urgente": RUST, "media": BRASS, "baja": GRIS}

CSS = f"""
<style>
.block-container {{ padding-top: 2.4rem; max-width: 1080px; }}
#MainMenu, footer {{ visibility: hidden; }}
.eyebrow {{ font-size: .76rem; letter-spacing: .14em; text-transform: uppercase;
            color: {BRASS}; font-weight: 700; margin-bottom: .1rem; }}
h1 {{ color: {NAVY}; letter-spacing: -.01em; font-weight: 700 !important; }}
h2, h3 {{ color: {NAVY}; }}
.lead {{ font-size: 1.08rem; color: #4a5668; max-width: 64ch; margin: .2rem 0 1.2rem 0; }}
.nota {{ font-size: .85rem; color: {GRIS}; }}
.pill {{ display: inline-block; padding: 2px 11px; border-radius: 999px; font-size: .78rem;
         font-weight: 600; border: 1px solid; margin: 0 6px 6px 0; white-space: nowrap; }}
.paso {{ display: inline-block; padding: 5px 12px; border-radius: 6px; font-size: .88rem;
         font-weight: 600; background: #eef1f6; color: {NAVY}; margin: 2px 0; }}
.paso.ok {{ background: {NAVY}; color: #fff; }}
.paso.late {{ background: {RUST}; color: #fff; }}
.flecha {{ color: {BRASS}; font-weight: 700; margin: 0 6px; }}
[data-testid="stMetric"] {{ background: #f7f6f2; border: 1px solid #e6e2d8;
                            border-radius: 8px; padding: 12px 14px; }}
[data-testid="stSidebar"] {{ border-right: 1px solid #e6e2d8; }}
.sidebar-titulo {{ font-weight: 700; color: {NAVY}; font-size: 1.05rem; line-height: 1.2; }}
table.matriz {{ border-collapse: collapse; width: 100%; }}
table.matriz th, table.matriz td {{ border: 1px solid {LINEA}; padding: 12px 14px; text-align: center; }}
table.matriz th {{ background: #f7f6f2; color: {NAVY}; font-size: .85rem; }}
table.matriz td.nash {{ background: #fbf3df; box-shadow: inset 0 0 0 2px {BRASS}; }}
table.matriz .p {{ font-size: 1.35rem; font-weight: 700; color: {NAVY}; }}
table.matriz .t {{ font-size: .78rem; color: {GRIS}; }}
</style>
"""


def inyectar_css():
    st.markdown(CSS, unsafe_allow_html=True)


def corto(t):
    return t.replace("C.C. ", "")


def pastilla(texto, color):
    return f'<span class="pill" style="color:{color};border-color:{color}">{texto}</span>'


def pasos(ruta, llegadas=None, tarde=()):
    """Ruta como cadena de bloques: Bodega → tienda → … → Bodega."""
    bloques = []
    for i, n in enumerate(ruta):
        clase = "paso" if n == ORIGEN else ("paso late" if n in tarde else "paso ok")
        extra = f" · min {llegadas[n]}" if llegadas and n in llegadas else ""
        bloques.append(f'<span class="{clase}">{corto(n)}{extra}</span>')
    return '<span class="flecha">→</span>'.join(bloques)


def encabezado(sprint, titulo, bajada=None):
    st.markdown(f'<div class="eyebrow">{sprint}</div>', unsafe_allow_html=True)
    st.title(titulo)
    if bajada:
        st.markdown(f'<p class="lead">{bajada}</p>', unsafe_allow_html=True)


def nota(texto):
    st.markdown(f'<p class="nota">{texto}</p>', unsafe_allow_html=True)


def navegacion(actual):
    i = PAGINAS.index(actual)
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    if i > 0:
        c1.button(f"← {PAGINAS[i - 1]}", on_click=ir_a, args=(PAGINAS[i - 1],), key=f"prev_{i}")
    if i < len(PAGINAS) - 1:
        c3.button(f"{PAGINAS[i + 1]} →", on_click=ir_a, args=(PAGINAS[i + 1],),
                  type="primary", key=f"next_{i}")


def _elipse(cx, cy, rx, ry, grados, n=60):
    a = np.radians(grados)
    t = np.linspace(0, 2 * np.pi, n)
    x = cx + rx * np.cos(t) * np.cos(a) - ry * np.sin(t) * np.sin(a)
    y = cy + rx * np.cos(t) * np.sin(a) + ry * np.sin(t) * np.cos(a)
    return "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in zip(x, y)) + " Z"


def _base(fig, altura):
    fig.update_layout(
        height=altura, margin=dict(l=0, r=0, t=6, b=0), showlegend=False,
        plot_bgcolor="white", paper_bgcolor="white", font=dict(color=NAVY, size=12),
        xaxis=dict(visible=False, range=[-40, 610]),
        yaxis=dict(visible=False, range=[540, 20]),
    )


def mapa(ruta=None, llegadas=None, tarde=(), subtitulos=None, zonas=True, altura=520):
    """Mapa esquemático de la red. 'ruta' se dibuja sobre los caminos más cortos."""
    fig = go.Figure()
    if zonas:
        for cx, cy, rx, ry, g, nombre, lx, ly in [
            (225, 290, 205, 72, -18, "El Poblado (en disputa)", 40, 232),
            (282, 182, 118, 46, 14, "Centro (en disputa)", 485, 268),
        ]:
            fig.add_shape(type="path", path=_elipse(cx, cy, rx, ry, g), fillcolor="rgba(184,137,47,.08)",
                          line=dict(color=BRASS, width=1, dash="dot"), layer="below")
            fig.add_annotation(x=lx, y=ly, text=nombre, showarrow=False, font=dict(size=10, color=GRIS))
    for a, b, _ in aristas():
        fig.add_trace(go.Scatter(x=[POS[a][0], POS[b][0]], y=[POS[a][1], POS[b][1]], mode="lines",
                                 line=dict(color=LINEA, width=2), hoverinfo="skip"))
    if ruta and len(ruta) > 1:
        pts = []
        for i in range(len(ruta) - 1):
            c = camino(ruta[i], ruta[i + 1])
            pts += c if i == 0 else c[1:]
        fig.add_trace(go.Scatter(x=[POS[p][0] for p in pts], y=[POS[p][1] for p in pts], mode="lines",
                                 line=dict(color=BRASS, width=5), hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=[(POS[a][0] + POS[b][0]) / 2 + 9 for a, b, _ in aristas()],
        y=[(POS[a][1] + POS[b][1]) / 2 - 9 for a, b, _ in aristas()],
        mode="text", text=[f"{w}′" for _, _, w in aristas()],
        textfont=dict(size=10, color=GRIS), hoverinfo="skip"))
    orden = {t: i + 1 for i, t in enumerate(llegadas)} if llegadas else {}
    nombres = list(POS)
    fill, borde, simbolo, tam = [], [], [], []
    for n in nombres:
        if n == ORIGEN:
            fill.append(NAVY); borde.append(NAVY); simbolo.append("square"); tam.append(22)
        else:
            fill.append(RUST if n in tarde else BRASS if n in orden else "white")
            borde.append(BRASS if (zonas and n in EN_DISPUTA) else DENIM)
            simbolo.append("circle"); tam.append(22)
    fig.add_trace(go.Scatter(
        x=[POS[n][0] for n in nombres], y=[POS[n][1] for n in nombres], mode="markers+text",
        marker=dict(size=tam, color=fill, symbol=simbolo, opacity=1, line=dict(color=borde, width=3)),
        text=[str(orden.get(n, "")) for n in nombres], textfont=dict(color="white", size=12),
        textposition="middle center", hovertext=nombres, hoverinfo="text"))
    etiquetas = []
    for n in nombres:
        sub = f"<br><span style='font-size:10px;color:{GRIS}'>{subtitulos[n]}</span>" if subtitulos and n in subtitulos else ""
        etiquetas.append(f"<b>{corto(n)}</b>{sub}")
    # (dx, dy, posición del texto) por nodo; por defecto a la derecha o a la izquierda según el lado del mapa
    ajuste = {ORIGEN: (0, 26, "middle center"), "Los Molinos Envigado": (0, 26, "middle center"),
              "Sabaneta Plaza": (18, 0, "middle right")}
    dx, dy, pos = [], [], []
    for n in nombres:
        a_, b_, c_ = ajuste.get(n, (18, 0, "middle right") if POS[n][0] <= 350 else (-18, 0, "middle left"))
        dx.append(a_); dy.append(b_); pos.append(c_)
    fig.add_trace(go.Scatter(
        x=[POS[n][0] + d for n, d in zip(nombres, dx)], y=[POS[n][1] + d for n, d in zip(nombres, dy)],
        mode="text", text=etiquetas, textfont=dict(size=12, color=NAVY), hoverinfo="skip", textposition=pos))
    _base(fig, altura)
    return fig


def linea_tiempo(llegadas, total, tiempo, minuto_rival=None, tarde=()):
    """Barra de los minutos del día: viaje, atención y regreso."""
    fig = go.Figure()
    t, visto = 0, set()

    def barra(inicio, dur, color, nombre, texto="", opacidad=1.0):
        fig.add_trace(go.Bar(
            x=[dur], base=[inicio], y=[""], orientation="h", marker=dict(color=color, opacity=opacidad),
            name=nombre, showlegend=nombre not in visto, text=[texto], textposition="inside",
            insidetextanchor="middle", textfont=dict(color="white", size=11),
            hovertemplate=f"{nombre}: {dur} min<extra></extra>"))
        visto.add(nombre)

    for tienda, m in llegadas.items():
        barra(t, m - t, DENIM, "Viaje", opacidad=.45)
        barra(m, TIEMPO_ATENCION, RUST if tienda in tarde else BRASS, "Atención", corto(tienda))
        t = m + TIEMPO_ATENCION
    barra(t, total - t, DENIM, "Viaje", opacidad=.45)
    if minuto_rival is not None:
        fig.add_vline(x=minuto_rival, line_dash="dash", line_color=RUST,
                      annotation_text=f"llega el rival (min {minuto_rival})", annotation_font_color=RUST)
    fig.update_layout(
        barmode="overlay", height=130, margin=dict(l=0, r=0, t=26, b=0), plot_bgcolor="white",
        xaxis=dict(range=[0, tiempo], title="minutos", dtick=15, gridcolor=LINEA),
        yaxis=dict(visible=False), legend=dict(orientation="h", y=1.35, x=0), font=dict(color=NAVY))
    return fig


def grafico(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
