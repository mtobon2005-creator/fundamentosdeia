"""Arturo Calle · Logística inteligente (Fundamentos de IA)."""
import streamlit as st

import estado
from paginas import carga, competencia, conocimiento, difusa, experto, inicio, red
from ui import ICONOS, inyectar_css, subir_al_inicio

st.set_page_config(page_title="Arturo Calle · Logística inteligente", page_icon="📦", layout="wide")
estado.iniciar()
inyectar_css()

VISTAS = {
    "Inicio": inicio.render,
    "1 · El mapa": red.render,
    "2 · El experto": conocimiento.render,
    "3 · El plan del día": experto.render,
    "4 · El rival": competencia.render,
    "5 · Grados de urgencia": difusa.render,
    "6 · La carga": carga.render,
}

with st.sidebar:
    st.markdown('<div class="sidebar-titulo">Arturo Calle<br><span>Logística inteligente</span></div>', unsafe_allow_html=True)
    st.caption("Fundamentos de IA · Valle de Aburrá")
    st.radio("Flujo", estado.PAGINAS, key="pagina", label_visibility="collapsed",
             format_func=lambda p: f"{ICONOS[p]} {p}")
    st.divider()
    ss = st.session_state
    st.caption(f"Datos del día: {ss.tiempo} min · fin de semana {'sí' if ss.finde else 'no'}")
    st.caption("Mariana Tobón · Maria Clara Escobar")

subir_al_inicio()
VISTAS[st.session_state["pagina"]]()
