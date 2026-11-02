import pandas as pd
import streamlit as st

import servicio
from estado import COLUMNAS, hechos_notebook
from motor import experto
from ui import COLOR_PRIORIDAD, corto, encabezado, grafico, kpis, mapa, navegacion, nota, pasos, pastilla

TEXTO_REGLA = {rid: cond for rid, cond, _ in experto.REGLAS}


def render():
    ss = st.session_state
    encabezado("Paso 3 · El experto en acción", "¿A qué tiendas vamos hoy?",
               "El experto revisa cada tienda y arma el plan del día.")
    resultado = st.container()  # se llena abajo, después de leer los datos editados

    with st.expander("Cambiar los datos de hoy", icon=":material/edit:"):
        c1, c2, c3 = st.columns([2, 2, 1])
        ss.finde = c1.toggle("Se acerca el fin de semana", value=ss.finde)
        ss.tiempo = int(c2.number_input("Minutos disponibles", 30, 300, int(ss.tiempo), step=5))
        if c3.button("Restablecer"):
            ss.hechos = hechos_notebook()
            ss.pop("editor_hechos", None)
            st.rerun()
        editado = st.data_editor(
            ss.hechos, key="editor_hechos", num_rows="fixed", width="stretch",
            column_config={c: st.column_config.NumberColumn(min_value=0, max_value=500, step=1) for c in COLUMNAS})
        ss.hechos = editado.fillna(0)

    h = servicio.hechos_tupla(ss.hechos)
    clasica = servicio.clasica(h, ss.finde)
    plan = experto.plan_del_dia({t: p for t, (p, _) in clasica.items()}, ss.tiempo)
    cuenta = {p: sum(1 for v in clasica.values() if v[0] == p) for p in experto.ORDEN_PRIORIDAD}

    with resultado:
        kpis([(f"{cuenta['urgente']}", "tiendas urgentes", True), (len(plan["llegadas"]), "tiendas hoy"),
              (f"{plan['total']} de {ss.tiempo} min", "tiempo usado"), (len(plan["pendientes"]), "quedan para después")])
        grafico(mapa(ruta=plan["ruta"], llegadas=plan["llegadas"], zonas=False, altura=600,
                     subtitulos={t: p for t, (p, _) in clasica.items()}))
        st.markdown(pasos(plan["ruta"], plan["llegadas"]), unsafe_allow_html=True)

    with st.expander("¿Por qué cada tienda tiene esa prioridad?"):
        st.markdown(" ".join(pastilla(f"{n} {p}", COLOR_PRIORIDAD[p]) for p, n in cuenta.items()), unsafe_allow_html=True)
        filas = [{"Tienda": corto(t), "Prioridad": p, "Regla": r, "Porque": TEXTO_REGLA[r]}
                 for t, (p, r) in sorted(clasica.items(), key=lambda x: experto.ORDEN_PRIORIDAD[x[1][0]])]
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
        if plan["pendientes"]:
            nota("Quedan para el próximo reparto: " + ", ".join(corto(t) for t in plan["pendientes"]) + ".")
    navegacion("3 · El plan del día")
