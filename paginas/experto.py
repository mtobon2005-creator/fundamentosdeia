import pandas as pd
import streamlit as st

import servicio
from estado import COLUMNAS, hechos_notebook
from motor import experto
from motor.red import ORIGEN
from ui import COLOR_PRIORIDAD, encabezado, grafico, mapa, navegacion, nota, pasos, pastilla

TEXTO_REGLA = {rid: cond for rid, cond, _ in experto.REGLAS}


def render():
    ss = st.session_state
    encabezado(
        "Sprint 2 · Sistema experto",
        "Quién necesita mercancía hoy",
        "Edita los datos del día y el motor aplica las 10 reglas a cada tienda. Estos datos alimentan "
        "todas las páginas siguientes.",
    )

    st.markdown("#### Memoria de trabajo: datos de hoy")
    c1, c2, c3 = st.columns([2, 2, 1])
    ss.finde = c1.toggle("Se acerca el fin de semana", value=ss.finde)
    ss.tiempo = int(c2.number_input("Tiempo disponible hoy (min)", 30, 300, int(ss.tiempo), step=5))
    if c3.button("Restablecer"):
        ss.hechos = hechos_notebook()
        ss.pop("editor_hechos", None)
        st.rerun()
    editado = st.data_editor(
        ss.hechos, key="editor_hechos", num_rows="fixed", width="stretch",
        column_config={c: st.column_config.NumberColumn(min_value=0, max_value=500, step=1) for c in COLUMNAS},
    )
    ss.hechos = editado.fillna(0)
    h = servicio.hechos_tupla(ss.hechos)
    clasica = servicio.clasica(h, ss.finde)

    st.markdown("#### 3.1 Razonamiento: prioridad de cada tienda")
    filas = [
        {"Tienda": t, "Prioridad": p, "Regla": r, "Por qué": TEXTO_REGLA[r]}
        for t, (p, r) in sorted(clasica.items(), key=lambda x: experto.ORDEN_PRIORIDAD[x[1][0]])
    ]
    cuenta = {p: sum(1 for f in filas if f["Prioridad"] == p) for p in experto.ORDEN_PRIORIDAD}
    st.markdown(" ".join(pastilla(f"{n} {p}", COLOR_PRIORIDAD[p]) for p, n in cuenta.items()), unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")

    st.markdown("#### 3.2 Solución: plan del día")
    plan = experto.plan_del_dia({t: p for t, (p, _) in clasica.items()}, ss.tiempo)
    st.markdown(pasos(plan["ruta"], plan["llegadas"]), unsafe_allow_html=True)
    m = st.columns(3)
    m[0].metric("Tiendas visitadas", len(plan["llegadas"]))
    m[1].metric(f"Tiempo total (de {ss.tiempo} min)", f"{plan['total']} min")
    m[2].metric("Pendientes", len(plan["pendientes"]))
    izq, der = st.columns([3, 2])
    with izq:
        grafico(mapa(ruta=plan["ruta"], llegadas=plan["llegadas"], zonas=False,
                     subtitulos={t: p for t, (p, _) in clasica.items()}))
    with der:
        if plan["pendientes"]:
            st.markdown("**Quedan para el próximo reparto**")
            st.markdown("\n".join(f"- {t} ({clasica[t][0]})" for t in plan["pendientes"]))
        nota("Se ordenan de más a menos urgente y se agregan mientras alcance el tiempo para ir, atender (15 min) "
             "y volver a la bodega. Una tienda que ya no cabe queda pendiente, aunque la siguiente sí quepa.")
    navegacion("3 · Sistema experto")
