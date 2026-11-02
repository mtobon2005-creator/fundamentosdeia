import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import servicio
from motor import genetico, juego, recorrido
from motor.red import EN_DISPUTA, ZONAS
from ui import (BRASS, DENIM, ETIQUETA, LINEA, NAVY, corto, encabezado, grafico, kpis, linea_tiempo, mapa,
                navegacion, nota, num, pasos, secciones, selector_escenario)

ZONA_DE = {t: z for z, ts in ZONAS.items() for t in ts}


def _otra_semilla():
    import random
    st.session_state.params["semilla"] = random.randint(1, 99999)


def _volver_notebook():
    st.session_state.params.update(genetico.PARAMS_NOTEBOOK)


def _tabla_pagos():
    filas = ""
    for a in juego.ESTRATEGIAS_AC:
        filas += f"<tr><th>{a}</th>"
        for r in juego.ESTRATEGIAS_RIVAL:
            pa, pr = juego.PAGOS[(a, r)]
            nash = (a, r) in juego.NASH
            marca = "<br><b style='color:#b8892f'>La mejor jugada</b>" if nash else ""
            filas += (f"<td class='{'nash' if nash else ''}'><span class='p'>{pa} · {pr}</span>"
                      f"<br><span class='t'>{juego.NOTAS[(a, r)]}</span>{marca}</td>")
        filas += "</tr>"
    return ("<table class='matriz'><tr><th>Arturo Calle \\ Rival</th><th>El rival se expande</th>"
            "<th>El rival se queda igual</th></tr>" + filas + "</table>")


def render():
    ss = st.session_state
    P = ss.params
    encabezado("Paso 4 · El rival", "Si un competidor llega, ¿qué hacemos?",
               "Elegimos una estrategia con teoría de juegos y un algoritmo busca la mejor ruta.")
    h = servicio.hechos_tupla(ss.hechos)
    selector_escenario("esc_comp")
    ss.modo_ruta = st.segmented_control(
        "Prioridad", ["Clásica", "Difusa"], default=ss.modo_ruta, key="modo_comp",
        help="Clásica: urgente / media / baja. Difusa: un grado de urgencia (paso 5).") or ss.modo_ruta
    ac, rv = ss.escenario.split("|")

    with st.expander("Ajustes del modelo", icon=":material/tune:"):
        a, b, c = st.columns(3)
        P["minuto"] = a.slider("Minuto en que llega el rival", 20, 90, int(P["minuto"]), 5)
        P["mult"] = b.slider("Peso de concentrar (×)", 1.0, 3.0, float(P["mult"]), 0.25)
        P["castigo"] = c.slider("Valor que se salva si llegamos tarde", 0.0, 1.0, float(P["castigo"]), 0.1)
        d, e, _ = st.columns([1, 1, 2])
        d.button("Probar otra semilla", on_click=_otra_semilla)
        e.button("Valores originales", on_click=_volver_notebook)
        nota(f"Semilla {P['semilla']}: número que fija el azar del buscador, para repetir resultados.")

    def res(ac_, rv_, modo=None):
        return servicio.resolver(h, ss.finde, ss.tiempo, modo or ss.modo_ruta, ac_, rv_,
                                 P["mult"], P["minuto"], P["castigo"], P["semilla"])

    r = res(ac, rv)
    clasica = servicio.clasica(h, ss.finde)
    sec = secciones("sec_comp", ["El juego", "Qué vale cada tienda", "La ruta", "¿Es la mejor?"])

    if sec == "El juego":
        st.markdown(_tabla_pagos(), unsafe_allow_html=True)
        nota("(Arturo Calle · rival): participación de mercado de 0 a 10. Son supuestos del modelo, no datos reales.")
        _, peor = juego.minimax_ac()
        c1, c2 = st.columns(2)
        c1.success("Al rival siempre le conviene **expandirse**. Sabiéndolo, a Arturo Calle le conviene **concentrar** "
                   "su inventario donde llega el rival.", icon=":material/check_circle:")
        c2.info(f"Peor caso: concentrar deja {peor['Concentrar']}, distribuir deja {peor['Distribuir']}. "
                "Concentrar protege más.", icon=":material/balance:")

    if sec == "Qué vale cada tienda":
        kpis([(f"× {num(P['mult'])}", "valor de tiendas en disputa si concentramos"),
              (f"min {P['minuto']}", "llega el rival"), (f"{int(P['castigo'] * 100)} %", "valor si llegamos tarde")])
        base = servicio.valores_base(h, ss.finde, ss.modo_ruta)
        orden = sorted(base, key=lambda t: -r["esc"]["valor_tienda"][t])
        fig = go.Figure(go.Bar(
            x=[corto(t) for t in orden], y=[r["esc"]["valor_tienda"][t] for t in orden],
            marker_color=[BRASS if t in EN_DISPUTA else DENIM for t in orden],
            text=[num(r["esc"]["valor_tienda"][t], 1) for t in orden], textposition="outside"))
        fig.update_layout(height=380, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white", showlegend=False,
                          title=dict(text="Valor de visitar cada tienda (dorado = zona en disputa)",
                                     font=dict(size=14, color=NAVY)),
                          yaxis=dict(gridcolor=LINEA, visible=False))
        grafico(fig)

    if sec == "La ruta":
        ok = abs(r["fitness"] - r["optimo"]) < 1e-9
        kpis([(len(r["llegadas"]), "tiendas visitadas"), (f"{r['total']} min", f"de {ss.tiempo} disponibles"),
              (num(r["fitness"], 1), "puntaje de la ruta"),
              ("Sí" if ok else "Casi", "¿es la mejor posible?", ok)])
        segs = recorrido.segmentos(r["ruta"])
        minuto = st.slider("Mueve el camión por el día (minutos)", 0, r["total"], 0,
                           key=f"hora_{ss.escenario}_{ss.modo_ruta}_{r['total']}")
        x, y, estado, pts = recorrido.posicion(segs, minuto)
        st.markdown(f"### {estado} · minuto {minuto}")
        sub = {t: f"{clasica[t][0]} · vale {num(r['esc']['valor_tienda'][t], 1)}" for t in r["esc"]["valor_tienda"]}
        grafico(mapa(ruta=r["ruta"], llegadas=r["llegadas"], tarde=r["tarde"], subtitulos=sub, altura=620,
                     camion={"x": x, "y": y, "recorrido": pts}))
        st.markdown(pasos(r["ruta"], r["llegadas"], r["tarde"]), unsafe_allow_html=True)
        if r["esc"]["hay_carrera"]:
            nota("En rojo: tienda a la que llegamos después que el rival.")
        grafico(linea_tiempo(r["llegadas"], r["total"], ss.tiempo,
                             P["minuto"] if r["esc"]["hay_carrera"] else None, r["tarde"]))

    if sec == "¿Es la mejor?":
        filas, aciertos = [], 0
        for a_ in juego.ESTRATEGIAS_AC:
            for r_ in juego.ESTRATEGIAS_RIVAL:
                x = res(a_, r_)
                coincide = abs(x["fitness"] - x["optimo"]) < 1e-9
                aciertos += coincide
                filas.append({
                    "Escenario": ETIQUETA[f"{a_}|{r_}"],
                    "Ruta": " → ".join(f"{corto(t)} ({m_})" for t, m_ in x["llegadas"].items()),
                    "Minutos": x["total"], "Puntaje": num(x["fitness"], 1), "Mejor posible": num(x["optimo"], 1),
                    "¿Coincide?": "Sí" if coincide else "No"})
        kpis([(f"{aciertos} de 4", "escenarios donde la ruta es la mejor posible", True)])
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
        nota("Comprobamos el buscador probando todas las rutas posibles una por una.")

        st.markdown("#### ¿Y si no cambiamos nada?")
        vieja = servicio.resolver(h, ss.finde, ss.tiempo, ss.modo_ruta, "Distribuir", "Mantener",
                                  P["mult"], P["minuto"], P["castigo"], P["semilla"])
        real = res("Distribuir", "Expandirse")
        f_vieja = genetico.calcular_fitness(list(vieja["llegadas"]), real["esc"], ss.tiempo)
        tarde_vieja = [t for t, m_ in vieja["llegadas"].items() if genetico.llega_tarde(real["esc"], t, m_)]
        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.markdown("**Seguir con la ruta de siempre**")
            st.markdown(f"## {num(f_vieja, 1)} puntos")
            st.markdown(pasos(vieja["ruta"], vieja["llegadas"], tarde_vieja), unsafe_allow_html=True)
        with c2.container(border=True):
            st.markdown("**Reorganizar la ruta**")
            st.markdown(f"## {num(real['fitness'], 1)} puntos")
            st.markdown(pasos(real["ruta"], real["llegadas"], real["tarde"]), unsafe_allow_html=True)

        with st.expander("Cómo aprendió el buscador (algoritmo genético)"):
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=r["prom"], mode="lines", name="Promedio", line=dict(color=DENIM)))
            fig.add_trace(go.Scatter(y=r["hist"], mode="lines", name="Mejor", line=dict(color=BRASS, width=3)))
            mejor = max(r["hist"])
            fig.add_hline(y=mejor, line_dash="dot", line_color=BRASS, annotation_text=f"Mejor: {num(mejor, 1)}",
                          annotation_position="top left", annotation_font_color=BRASS)
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="white",
                              xaxis=dict(title="generación", gridcolor=LINEA),
                              yaxis=dict(title="puntaje", gridcolor=LINEA, range=[min(r["prom"]) - 0.5, mejor * 1.08]),
                              legend=dict(orientation="h", y=-0.3))
            grafico(fig)
            st.markdown(f"Empieza con {r['pob']} rutas al azar y durante {r['gens']} generaciones elige las mejores, "
                        f"las mezcla y les cambia un detalle, como la evolución. Semilla: {P['semilla']}.")
    navegacion("4 · El rival")
