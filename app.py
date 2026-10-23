"""Arturo Calle · Logística inteligente (Fundamentos de IA)."""
import streamlit as st

import estado
from paginas import carga, competencia, conocimiento, difusa, experto, inicio, red
from ui import inyectar_css

st.set_page_config(page_title="Arturo Calle · Logística inteligente", page_icon="📦", layout="wide")
estado.iniciar()
inyectar_css()

VISTAS = {
    "Inicio": inicio.render,
    "1 · Red logística": red.render,
    "2 · Base de conocimiento": conocimiento.render,
    "3 · Sistema experto": experto.render,
    "4 · Competencia y ruta": competencia.render,
    "5 · Prioridad difusa": difusa.render,
    "6 · Carga por tienda": carga.render,
}

with st.sidebar:
    st.markdown('<div class="sidebar-titulo">Arturo Calle<br>Logística inteligente</div>', unsafe_allow_html=True)
    st.caption("Fundamentos de IA · Valle de Aburrá")
    st.radio("Flujo", estado.PAGINAS, key="pagina", label_visibility="collapsed")
    st.divider()
    ss = st.session_state
    st.caption(f"Datos del día: {ss.tiempo} min · fin de semana {'sí' if ss.finde else 'no'}")
    st.caption("Mariana Tobón · Maria Clara Escobar")

VISTAS[st.session_state["pagina"]]()
