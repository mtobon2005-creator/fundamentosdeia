import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import servicio
from motor import experto, genetico, juego
from motor.red import EN_DISPUTA, ZONAS
from motor import recorrido
from ui import (BRASS, DENIM, ETIQUETA, LINEA, NAVY, corto, encabezado, grafico, kpis, linea_tiempo, mapa,
                navegacion, nota, pasos, selector_escenario)

ZONA_DE = {t: z for z, ts in ZONAS.items() for t in ts}


def _otra_semilla():
    import random
    st.session_state.params["semilla"] = random.randint(1, 99999)


def _volver_notebook():
    st.session_state.params.update(genetico.PARAMS_NOTEBOOK)


def _tabla_pagos(seleccion):
    filas = ""
    for a in juego.ESTRATEGIAS_AC:
        filas += f"<tr><th>{a}</th>"
        for r in juego.ESTRATEGIAS_RIVAL:
            pa, pr = juego.PAGOS[(a, r)]
            nash = " nash" if (a, r) in juego.NASH else ""
            marca = "<br><b style='color:#b8892f'>Equilibrio de Nash</b>" if nash else ""
            filas += (f"<td class='{nash.strip()}'><span class='p'>{pa} · {pr}</span>"
                      f"<br><span class='t'>{juego.NOTAS[(a, r)]}</span>{marca}</td>")
        filas += "</tr>"
    return ("<table class='matriz'><tr><th>AC \\ Rival</th><th>Se expande</th><th>Mantiene</th></tr>"
            + filas + "</table>")


def render():
    ss = st.session_state
    P = ss.params
    encabezado("Sprint 3 · Competencia y ruta", "Si el rival se expande, ¿qué hacemos?",
               "El juego elige la estrategia; el algoritmo genético arma la ruta.")
    h = servicio.hechos_tupla(ss.hechos)
    selector_escenario("esc_comp")
    ss.modo_ruta = st.segmented_control("Prioridad usada", ["Clásica", "Difusa"], default=ss.modo_ruta,
                                        key="modo_comp", help="Clásica: urgente 3 · media 2 · baja 1 (notebook). "
                                        "Difusa: valor continuo de 1 a 3.") or ss.modo_ruta
    ac, rv = ss.escenario.split("|")

    with st.expander("Parámetros del modelo"):
        a, b, c = st.columns(3)
        P["minuto"] = a.slider("Llegada del rival (min)", 20, 90, int(P["minuto"]), 5)
        P["mult"] = b.slider("Efecto de concentrar (×)", 1.0, 3.0, float(P["mult"]), 0.25)
        P["castigo"] = c.slider("Valor rescatado si llega tarde", 0.0, 1.0, float(P["castigo"]), 0.1)
        d, e, _ = st.columns([1, 1, 2])
        d.button("Otra semilla", on_click=_otra_semilla)
        e.button("Valores del notebook", on_click=_volver_notebook)
        nota(f"Semilla {P['semilla']}" + (" (igual al notebook)." if P["semilla"] == 42 else "."))

    def res(ac_, rv_, modo=None):
        return servicio.resolver(h, ss.finde, ss.tiempo, modo or ss.modo_ruta, ac_, rv_,
                                 P["mult"], P["minuto"], P["castigo"], P["semilla"])

    r = res(ac, rv)
    clasica = servicio.clasica(h, ss.finde)
    t_juego, t_esc, t_ruta, t_val = st.tabs(["1 · Juego", "2 · Escenario", "3 · Ruta óptima", "4 · Validación"])

    with t_juego:
        st.markdown(_tabla_pagos(ss.escenario), unsafe_allow_html=True)
        nota("(pago de Arturo Calle · pago del rival), de 0 a 10. Son supuestos del modelo, no datos reales.")
        _, peor = juego.minimax_ac()
        c1, c2 = st.columns(2)
        c1.success("**Expandirse es dominante** para el rival (5 > 4 y 8 > 6). Sabiéndolo, a AC le conviene "
                   "**concentrar** (6 > 3).", icon=":material/check_circle:")
        c2.info(f"**Minimax** lo confirma: peor caso de concentrar {peor['Concentrar']}, de distribuir {peor['Distribuir']}.",
                icon=":material/balance:")

    with t_esc:
        kpis([(f"× {P['mult']:g}", "valor de tiendas en disputa si concentras"),
              (f"min {P['minuto']}", "llega el rival"), (f"{int(P['castigo'] * 100)} %", "valor si llegas tarde")])
        base = servicio.valores_base(h, ss.finde, ss.modo_ruta)
        filas = [{"Tienda": t, "Zona": ZONA_DE[t] + (" · en disputa" if t in EN_DISPUTA else ""),
                  "Prioridad": clasica[t][0], "Valor base": round(base[t], 2),
                  "Valor en el escenario": round(r["esc"]["valor_tienda"][t], 2)} for t in base]
        st.dataframe(pd.DataFrame(filas).sort_values("Valor en el escenario", ascending=False),
                     hide_index=True, width="stretch")

    with t_ruta:
        ok = abs(r["fitness"] - r["optimo"]) < 1e-9
        kpis([(len(r["llegadas"]), "paradas"), (f"{r['total']} min", f"de {ss.tiempo} disponibles"),
              (f"{r['fitness']:.2f}", "fitness"), ("Óptima" if ok else f"Óptimo {r['optimo']:.2f}", "vs. búsqueda exhaustiva", ok)])
        st.markdown(pasos(r["ruta"], r["llegadas"], r["tarde"]), unsafe_allow_html=True)
        segs = recorrido.segmentos(r["ruta"])
        minuto = st.slider("Mueve el camión por el día (min)", 0, r["total"], 0, key=f"hora_{ss.escenario}_{ss.modo_ruta}_{r['total']}")
        x, y, estado, recorrido_pts = recorrido.posicion(segs, minuto)
        izq, der = st.columns([3, 2])
        with izq:
            sub = {t: f"{clasica[t][0]} · vale {r['esc']['valor_tienda'][t]:.2f}" for t in r["esc"]["valor_tienda"]}
            grafico(mapa(ruta=r["ruta"], llegadas=r["llegadas"], tarde=r["tarde"], subtitulos=sub,
                         camion={"x": x, "y": y, "recorrido": recorrido_pts}))
        with der:
            st.markdown(f"### {estado}")
            st.caption(f"Minuto {minuto} de {r['total']}")
            for t, m_ in r["llegadas"].items():
                if t not in EN_DISPUTA:
                    et = "fuera de disputa"
                elif not r["esc"]["hay_carrera"]:
                    et = "en disputa, sin carrera"
                else:
                    et = "llega **después** del rival" if t in r["tarde"] else "llega **antes** del rival"
                st.markdown(f"**min {m_} · {corto(t)}**  \n{clasica[t][0]} · {et}")
        grafico(linea_tiempo(r["llegadas"], r["total"], ss.tiempo,
                             P["minuto"] if r["esc"]["hay_carrera"] else None, r["tarde"]))
        with st.expander("Cómo funciona el algoritmo genético"):
            st.markdown(
                "- **Cromosoma:** orden de visita de las 9 tiendas; entra solo si alcanza el tiempo.\n"
                "- **Fitness:** valor entregado − 0,01 × minutos.\n"
                "- **Config.:** población 30 · 60 generaciones · ruleta · cruce por orden · mutación 20 % · elitismo 2.\n"
                "- **Control:** búsqueda exhaustiva de todas las rutas factibles.")

    with t_val:
        filas, aciertos = [], 0
        for a_ in juego.ESTRATEGIAS_AC:
            for r_ in juego.ESTRATEGIAS_RIVAL:
                x = res(a_, r_)
                coincide = abs(x["fitness"] - x["optimo"]) < 1e-9
                aciertos += coincide
                filas.append({
                    "Escenario": ETIQUETA[f"{a_}|{r_}"] + (" · Nash" if (a_, r_) in juego.NASH else ""),
                    "Ruta (minuto de llegada)": " → ".join(f"{corto(t)} ({m_})" for t, m_ in x["llegadas"].items()),
                    "Tiempo": x["total"], "Fitness AG": round(x["fitness"], 2),
                    "Óptimo": round(x["optimo"], 2), "¿Coincide?": "Sí" if coincide else "No"})
        kpis([(f"{aciertos} de 4", "escenarios donde el genético llega al óptimo", True), (P["semilla"], "semilla")])
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")

        fig = go.Figure()
        fig.add_trace(go.Scatter(y=r["prom"], mode="lines", name="Promedio de la población", line=dict(color=DENIM)))
        fig.add_trace(go.Scatter(y=r["hist"], mode="lines", name="Mejor individuo", line=dict(color=BRASS, width=3)))
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white",
                          title=dict(text=f"Convergencia · {ETIQUETA[ss.escenario]}", font=dict(size=14, color=NAVY)),
                          xaxis=dict(title="generación", gridcolor=LINEA), yaxis=dict(title="fitness", gridcolor=LINEA),
                          legend=dict(orientation="h", y=-0.3))
        grafico(fig)

        st.markdown("##### ¿Y si Arturo Calle no reacciona?")
        vieja = servicio.resolver(h, ss.finde, ss.tiempo, ss.modo_ruta, "Distribuir", "Mantener",
                                  P["mult"], P["minuto"], P["castigo"], P["semilla"])
        real = res("Distribuir", "Expandirse")
        esc_real = real["esc"]
        f_vieja = genetico.calcular_fitness(list(vieja["llegadas"]), esc_real, ss.tiempo)
        tarde_vieja = [t for t, m_ in vieja["llegadas"].items() if genetico.llega_tarde(esc_real, t, m_)]
        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.markdown("**Ruta de siempre** (sin competencia)")
            st.metric("Fitness con el rival expandiéndose", f"{f_vieja:.2f}")
            st.markdown(pasos(vieja["ruta"], vieja["llegadas"], tarde_vieja), unsafe_allow_html=True)
        with c2.container(border=True):
            st.markdown("**Reordenando la ruta**")
            st.metric("Fitness", f"{real['fitness']:.2f}", f"{real['fitness'] - f_vieja:+.2f}")
            st.markdown(pasos(real["ruta"], real["llegadas"], real["tarde"]), unsafe_allow_html=True)
        nota("Ambas rutas se miden con el rival expandiéndose y AC distribuyendo.")
    navegacion("4 · Competencia y ruta")
