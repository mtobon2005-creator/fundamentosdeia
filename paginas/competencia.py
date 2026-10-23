import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import servicio
from motor import experto, genetico, juego
from motor.red import EN_DISPUTA, ZONAS
from ui import (BRASS, COLOR_PRIORIDAD, DENIM, GRIS, LINEA, NAVY, RUST, corto, encabezado, grafico,
                linea_tiempo, mapa, navegacion, nota, pasos)

ETIQUETA = {
    "Concentrar|Expandirse": "Concentrar / el rival se expande",
    "Concentrar|Mantener": "Concentrar / el rival mantiene",
    "Distribuir|Expandirse": "Distribuir / el rival se expande",
    "Distribuir|Mantener": "Distribuir / el rival mantiene",
}
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
    encabezado(
        "Sprint 3 · Competencia y ruta",
        "Qué hacer si el rival se expande",
        "Si un competidor entra a El Poblado y el Centro (justo donde están varias tiendas), ¿conviene concentrar "
        "el inventario ahí o repartirlo en todas? El juego decide la estrategia y el algoritmo genético arma la ruta.",
    )
    h = servicio.hechos_tupla(ss.hechos)

    c1, c2 = st.columns([3, 2])
    with c1:
        claves = list(ETIQUETA)
        ss.escenario = st.selectbox("Escenario", claves, index=claves.index(ss.escenario),
                                    format_func=lambda k: ETIQUETA[k] + ("  ·  Nash" if tuple(k.split("|")) in juego.NASH else ""))
    with c2:
        ss.modo_ruta = st.radio("Prioridad usada", ["Clásica", "Difusa"], index=["Clásica", "Difusa"].index(ss.modo_ruta),
                                horizontal=True, help="Clásica = urgente 3 / media 2 / baja 1, como en el notebook. "
                                "Difusa = valor continuo de 1 a 3 (página 5).")
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
        st.markdown("Cada casilla muestra **(pago de Arturo Calle · pago del rival)**: participación de mercado "
                    "esperada, de 0 a 10. *Son supuestos del modelo, no datos reales.*")
        st.markdown(_tabla_pagos(ss.escenario), unsafe_allow_html=True)
        st.markdown("")
        st.markdown(
            "- Si AC concentra, al rival le conviene **expandirse** (5 > 4). Si AC distribuye, también (8 > 6): "
            "expandirse es **dominante** para el rival.\n"
            "- Sabiendo eso, a AC le conviene **concentrar** (6 > 3).\n"
            "- (Distribuir, Mantener) daría (7, 6), mejor para ambos, pero no es estable: el rival tiene incentivo a expandirse."
        )
        _, peor = juego.minimax_ac()
        st.success(f"**Equilibrio de Nash: (Concentrar, Expandirse).** Minimax lo confirma: peor caso de concentrar "
                   f"{peor['Concentrar']}, de distribuir {peor['Distribuir']}.")

    with t_esc:
        st.markdown(
            "El juego no da una ruta: **cambia cuánto vale cada tienda**.\n"
            "- **Concentrar:** las tiendas en disputa (El Poblado y Centro) valen × el efecto elegido, porque reciben más inventario.\n"
            "- **Expandirse:** hay carrera. Si el camión llega a una tienda en disputa *después* del minuto "
            f"{P['minuto']}, solo se rescata el {int(P['castigo'] * 100)} % del valor.\n"
            "- **Mantener:** no hay carrera; el minuto de llegada no castiga."
        )
        base = servicio.valores_base(h, ss.finde, ss.modo_ruta)
        filas = [{"Tienda": t, "Zona": ZONA_DE[t] + (" · en disputa" if t in EN_DISPUTA else ""),
                  "Prioridad": clasica[t][0], "Valor base": round(base[t], 2),
                  "Valor en el escenario": round(r["esc"]["valor_tienda"][t], 2)} for t in base]
        st.dataframe(pd.DataFrame(filas).sort_values("Valor en el escenario", ascending=False),
                     hide_index=True, width="stretch")

    with t_ruta:
        m = st.columns(4)
        m[0].metric("Paradas", len(r["llegadas"]))
        m[1].metric(f"Tiempo (de {ss.tiempo} min)", f"{r['total']} min")
        m[2].metric("Fitness", f"{r['fitness']:.2f}")
        ok = abs(r["fitness"] - r["optimo"]) < 1e-9
        m[3].metric("Vs. exhaustiva", "Coincide" if ok else f"Óptimo {r['optimo']:.2f}")
        st.markdown(pasos(r["ruta"], r["llegadas"], r["tarde"]), unsafe_allow_html=True)
        izq, der = st.columns([3, 2])
        with izq:
            sub = {t: f"{clasica[t][0]} · vale {r['esc']['valor_tienda'][t]:.2f}" for t in r["esc"]["valor_tienda"]}
            grafico(mapa(ruta=r["ruta"], llegadas=r["llegadas"], tarde=r["tarde"], subtitulos=sub))
        with der:
            for t, minuto in r["llegadas"].items():
                if t not in EN_DISPUTA:
                    estado = "fuera de disputa"
                elif not r["esc"]["hay_carrera"]:
                    estado = "en disputa, sin carrera"
                else:
                    estado = "llega **después** del rival" if t in r["tarde"] else "llega **antes** del rival"
                st.markdown(f"**min {minuto} · {t}**  \n{clasica[t][0]} · {estado}")
        grafico(linea_tiempo(r["llegadas"], r["total"], ss.tiempo,
                             P["minuto"] if r["esc"]["hay_carrera"] else None, r["tarde"]))
        with st.expander("Cómo funciona el algoritmo genético"):
            st.markdown(
                "- **Cromosoma:** el orden en que se intenta visitar las 9 tiendas. Una tienda entra solo si alcanza el tiempo para ir, atenderla y volver.\n"
                "- **Fitness:** valor entregado − 0,01 × minutos usados. El castigo por tiempo solo desempata rutas con el mismo valor.\n"
                "- **Configuración:** población 30 · 60 generaciones · selección por ruleta · cruce por orden · mutación por intercambio (20 %) · elitismo 2.\n"
                "- **Control:** búsqueda exhaustiva de todas las rutas factibles, para comprobar si el genético llegó al óptimo."
            )

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
        st.markdown(f"**El genético coincide con el óptimo exhaustivo en {aciertos} de 4 escenarios** (semilla {P['semilla']}).")
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
        nota("En ambos casos el rival se expande y Arturo Calle distribuye, así que los fitness se miden con las mismas reglas. "
             "Los fitness de escenarios distintos no se comparan entre sí: esa comparación la hace la matriz de pagos.")
    navegacion("4 · Competencia y ruta")
