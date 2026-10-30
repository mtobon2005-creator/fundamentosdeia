"""Elementos visuales compartidos: estilo, mapa, línea de tiempo y navegación."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from estado import PAGINAS, ir_a
from motor.red import EN_DISPUTA, ORIGEN, POS, TIEMPO_ATENCION, aristas, camino

NAVY, BRASS, RUST, DENIM = "#1c2e4a", "#b8892f", "#c0583f", "#4a78ad"
GRIS, LINEA, VERDE = "#7b8798", "#d5dae1", "#3f8f6b"
COLOR_PRIORIDAD = {"urgente": RUST, "media": BRASS, "baja": GRIS}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap');
.stApp, .stMarkdown, .stCaption, label, p {{ font-family: 'Inter', system-ui, sans-serif; }}
.block-container {{ padding-top: 4.5rem; max-width: 1240px; }}
[data-testid="stHeader"] {{ background: rgba(255,255,255,.0); }}
#MainMenu, footer {{ visibility: hidden; }}
h1, h2, h3 {{ font-family: 'Fraunces', Georgia, serif !important; color: {NAVY}; letter-spacing: -.01em; }}
h1 {{ font-weight: 700 !important; font-size: 2.3rem !important; }}
.eyebrow {{ font-size: .74rem; letter-spacing: .16em; text-transform: uppercase; color: {BRASS}; font-weight: 700; }}
.lead {{ font-size: 1.02rem; color: #5a6679; margin: .1rem 0 1rem 0; }}
.nota {{ font-size: .82rem; color: {GRIS}; }}
.pill {{ display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: .78rem; font-weight: 600;
         border: 1px solid; margin: 0 6px 6px 0; white-space: nowrap; }}
.paso {{ display: inline-block; padding: 6px 13px; border-radius: 999px; font-size: .86rem; font-weight: 600;
         background: #eef1f6; color: {NAVY}; margin: 2px 0; }}
.paso.ok {{ background: {NAVY}; color: #fff; }}
.paso.late {{ background: {RUST}; color: #fff; }}
.flecha {{ color: {BRASS}; font-weight: 700; margin: 0 6px; }}
/* tarjetas de métricas */
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: .4rem 0 1rem; }}
.kpi {{ background: linear-gradient(160deg, #ffffff, #f7f6f2); border: 1px solid #e6e2d8; border-radius: 14px;
        padding: 14px 16px; box-shadow: 0 1px 2px rgba(28,46,74,.05); }}
.kpi b {{ display: block; font-family: 'Fraunces', serif; font-size: 1.7rem; color: {NAVY}; line-height: 1.15; }}
.kpi span {{ font-size: .78rem; color: {GRIS}; text-transform: uppercase; letter-spacing: .06em; }}
.kpi.acento b {{ color: {BRASS}; }}
[data-testid="stMetric"] {{ background: linear-gradient(160deg, #ffffff, #f7f6f2); border: 1px solid #e6e2d8;
                            border-radius: 14px; padding: 12px 16px; }}
/* contenedores con borde = tarjetas que se elevan */
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 16px; transition: box-shadow .2s, transform .2s; }}
[data-testid="stVerticalBlockBorderWrapper"]:hover {{ box-shadow: 0 8px 24px rgba(28,46,74,.10); }}
.stButton > button {{ border-radius: 999px; font-weight: 600; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
/* perilla de los sliders: un pantalón */
[data-testid="stSlider"] div[data-rac]:has(> div > input[type="range"]),
[data-testid="stSlider"] [role="slider"] {{
  width: 26px !important; height: 33px !important; border-radius: 0 !important;
  background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 28 36'><path d='M5 2h18l3 32h-8l-4-18-4 18H2z' fill='%231c2e4a' stroke='%23b8892f' stroke-width='1.6' stroke-linejoin='round'/><path d='M5.6 6.2h16.8M14 6.2V16' stroke='%23d9a441' stroke-width='1.2' fill='none' stroke-dasharray='2 1.4'/><circle cx='14' cy='9' r='.9' fill='%23d9a441'/></svg>") center / contain no-repeat !important;
  background-color: transparent !important; box-shadow: none !important; border: none !important;
  transition: scale .15s;
}}
[data-testid="stSlider"] div[data-rac]:has(> div > input[type="range"]):hover,
[data-testid="stSlider"] div[data-rac]:has(> div > input[type="range"]):focus-within,
[data-testid="stSlider"] [role="slider"]:hover {{
  scale: 1.18; outline: none !important;
  filter: drop-shadow(0 2px 4px rgba(28,46,74,.35));
}}
[data-testid="stSlider"] div[role="group"] {{ margin-top: 22px; }}
/* barra lateral oscura */
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0f1b2d, #1c2e4a); border-right: none; }}
[data-testid="stSidebar"] * {{ color: #e8edf5 !important; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.15); }}
.sidebar-titulo {{ font-family: 'Fraunces', serif; font-weight: 700; font-size: 1.25rem; line-height: 1.15; color: #fff !important; }}
.sidebar-titulo span {{ color: {BRASS} !important; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{ padding: 6px 10px; border-radius: 10px; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background: rgba(255,255,255,.08); }}
/* portada */
.hero {{ background: linear-gradient(135deg, #0f1b2d, #1c2e4a); border-radius: 22px; padding: 30px 34px; margin-bottom: 14px; }}
.hero .eyebrow {{ color: {BRASS}; }}
.hero h1 {{ color: #fff !important; margin: .2rem 0 .3rem; }}
.hero p {{ color: #b6c3d8; margin: 0; font-size: 1.02rem; }}
table.matriz {{ border-collapse: separate; border-spacing: 8px; width: 100%; }}
table.matriz th, table.matriz td {{ border-radius: 14px; padding: 14px; text-align: center; background: #f7f6f2; }}
table.matriz th {{ color: {NAVY}; font-size: .85rem; }}
table.matriz td.nash {{ background: #fbf3df; box-shadow: inset 0 0 0 2px {BRASS}; }}
table.matriz .p {{ font-family: 'Fraunces', serif; font-size: 1.5rem; font-weight: 700; color: {NAVY}; }}
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


ETIQUETA = {
    "Concentrar|Expandirse": "Concentrar · rival se expande",
    "Concentrar|Mantener": "Concentrar · rival mantiene",
    "Distribuir|Expandirse": "Distribuir · rival se expande",
    "Distribuir|Mantener": "Distribuir · rival mantiene",
}
ICONOS = {
    "Inicio": ":material/home:", "1 · El mapa": ":material/route:",
    "2 · El experto": ":material/menu_book:", "3 · El plan del día": ":material/rule:",
    "4 · El rival": ":material/swords:", "5 · Grados de urgencia": ":material/tune:",
    "6 · La carga": ":material/local_shipping:",
}


def selector_escenario(clave):
    """Selector de los 4 escenarios del juego (guarda la elección en el estado)."""
    ss = st.session_state
    sel = st.segmented_control("Escenario", list(ETIQUETA), default=ss.escenario, key=clave,
                               format_func=lambda k: ETIQUETA[k] + ("  ·  Nash" if k == "Concentrar|Expandirse" else ""),
                               label_visibility="collapsed")
    if sel:
        ss.escenario = sel
    return ss.escenario


def kpis(items):
    """Fila de tarjetas: [(valor, etiqueta)] o [(valor, etiqueta, True)] para resaltar."""
    html = "".join(f'<div class="kpi{" acento" if len(i) > 2 and i[2] else ""}"><b>{i[0]}</b><span>{i[1]}</span></div>'
                   for i in items)
    st.markdown(f'<div class="kpis">{html}</div>', unsafe_allow_html=True)


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


def mapa(ruta=None, llegadas=None, tarde=(), subtitulos=None, zonas=True, altura=520, camion=None):
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
    if camion:
        fig.add_trace(go.Scatter(x=[p[0] for p in camion["recorrido"]], y=[p[1] for p in camion["recorrido"]],
                                 mode="lines", line=dict(color=NAVY, width=5), hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=[camion["x"]], y=[camion["y"] - 4], mode="text", text=["🚚"],
                                 textfont=dict(size=30), hoverinfo="skip"))
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


def subir_al_inicio():
    """Al cambiar de página, vuelve al principio (Streamlit conserva el scroll por defecto)."""
    ss = st.session_state
    if ss.get("_ultima_pagina") == ss.pagina:
        return
    ss["_ultima_pagina"] = ss.pagina
    html = f"""<script>/* {ss.pagina} */
        const subir = () => {{
          const d = window.parent.document;
          for (const sel of ['[data-testid="stMain"]', 'section.main', '[data-testid="stAppViewContainer"]']) {{
            const el = d.querySelector(sel);
            if (el) el.scrollTo({{ top: 0 }});
          }}
          window.parent.scrollTo({{ top: 0 }});
        }};
        subir(); setTimeout(subir, 80); setTimeout(subir, 400);
        </script>"""
    if hasattr(st, "iframe"):  # st.components.v1.html está en desuso en las versiones nuevas
        st.iframe(html, height=1)
    else:
        components.html(html, height=0)


def secciones(clave, nombres):
    """Selector de secciones que recuerda la elección aunque la página se recalcule (las pestañas se reiniciaban)."""
    ss = st.session_state
    sel = st.segmented_control("Sección", nombres, default=ss.get(clave, nombres[0]), key=f"w_{clave}",
                               label_visibility="collapsed")
    ss[clave] = sel or ss.get(clave, nombres[0])
    st.write("")
    return ss[clave]
