"""Imagen resumen del proyecto (SVG generado con la red y los resultados reales)."""
from motor.red import EN_DISPUTA, ORIGEN, POS, aristas

NAVY, NAVY2, BRASS, RUST, DENIM = "#0f1b2d", "#1c2e4a", "#d9a441", "#e2703e", "#6f9bd1"
FUENTE = "Helvetica, Arial, sans-serif"

TARJETAS = [
    ("1", "El mapa", "Cuánto tarda cada tramo", "104 min las 9 tiendas"),
    ("2", "El experto", "10 reglas de prioridad", "4 urgentes · 2 medias"),
    ("3", "El rival", "Teoría de juegos + buscador de rutas", "68 min · 2 paradas"),
    ("4", "Los grados", "Urgencia de 0 a 100 + unidades", "Unidades por tienda"),
]
FLUJO = ["Datos", "Reglas", "Rival", "Ruta", "Grados", "Carga"]


def _t(x, y, texto, tam=14, color="#ffffff", peso="400", ancla="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{FUENTE}" font-size="{tam}" fill="{color}" '
            f'font-weight="{peso}" text-anchor="{ancla}" {extra}>{texto}</text>')


def svg_resumen():
    esc, ox, oy = 0.98, 36, 96
    p = {n: (ox + (x - 50) * esc, oy + (y - 20) * esc) for n, (x, y) in POS.items()}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" width="1200" height="600">',
         f'<defs><linearGradient id="fondo" x1="0" y1="0" x2="1" y2="1">'
         f'<stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient></defs>',
         '<rect width="1200" height="600" rx="22" fill="url(#fondo)"/>',
         _t(44, 52, "ARTURO CALLE · LOGÍSTICA INTELIGENTE", 13, BRASS, "700", extra='letter-spacing="2"'),
         _t(44, 84, "De una ruta a una decisión completa", 30, "#ffffff", "700")]
    # zonas en disputa
    s.append(f'<ellipse cx="{p["C.C. El Tesoro"][0] + 80}" cy="{p["C.C. Oviedo"][1] - 10}" rx="190" ry="60" '
             f'transform="rotate(-18 {p["C.C. El Tesoro"][0] + 80} {p["C.C. Oviedo"][1] - 10})" fill="{BRASS}" '
             f'fill-opacity=".10" stroke="{BRASS}" stroke-dasharray="5 6" stroke-opacity=".7"/>')
    # red
    for a, b, w in aristas():
        (x1, y1), (x2, y2) = p[a], p[b]
        s.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{DENIM}" stroke-opacity=".35" stroke-width="2"/>')
    # ruta del equilibrio de Nash (Bodega → Oviedo → Unicentro → Bodega)
    ruta = [ORIGEN, "C.C. Oviedo", "Unicentro", ORIGEN]
    pts = " ".join(f"{p[n][0]:.0f},{p[n][1]:.0f}" for n in ruta)
    s.append(f'<polyline points="{pts}" fill="none" stroke="{BRASS}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
    # nodos
    for n, (x, y) in p.items():
        if n == ORIGEN:
            s.append(f'<rect x="{x - 14:.0f}" y="{y - 14:.0f}" width="28" height="28" rx="6" fill="#ffffff"/>')
            s.append(_t(f"{x:.0f}", f"{y + 5:.0f}", "B", 14, NAVY, "700", "middle"))
            continue
        visit = n in ruta
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{13 if visit else 9}" fill="{BRASS if visit else NAVY}" '
                 f'stroke="{BRASS if n in EN_DISPUTA else DENIM}" stroke-width="3"/>')
        if visit:
            s.append(_t(f"{x:.0f}", f"{y + 5:.0f}", str(ruta.index(n)), 13, NAVY, "700", "middle"))
    # etiquetas
    for n, dx, dy, anc in [("C.C. Oviedo", 22, 5, "start"), ("Unicentro", 22, 5, "start"), ("C.C. El Tesoro", 16, 5, "start"),
                           ("C.C. Premium Plaza", 16, 5, "start"), ("Puerta del Norte", 18, 5, "start"),
                           ("C.C. San Diego", 16, 5, "start"), ("C.C. Mayorca", -16, 5, "end"),
                           ("Sabaneta Plaza", 18, 5, "start"), ("Los Molinos Envigado", 40, 30, "middle"),
                           (ORIGEN, 0, 34, "middle")]:
        x, y = p[n]
        s.append(_t(f"{x + dx:.0f}", f"{y + dy:.0f}", n.replace("C.C. ", ""), 14, "#ffffff", "600", anc))
    # camión y rival
    xb, yb = p[ORIGEN]
    s.append(_t(f"{xb + 46:.0f}", f"{yb - 18:.0f}", "🚚", 28))
    xr, yr = p["Unicentro"]
    s.append(f'<rect x="{xr + 40:.0f}" y="{yr - 50:.0f}" width="232" height="30" rx="15" fill="{RUST}" fill-opacity=".18" stroke="{RUST}"/>')
    s.append(_t(f"{xr + 156:.0f}", f"{yr - 30:.0f}", "El rival llega en el minuto 45", 13, "#ffd9cc", "600", "middle"))
    s.append(_t(44, 584, "Ruta elegida · las zonas punteadas son donde llega el rival", 12, "#9fb0c8"))
    # tarjetas de sprints
    for i, (n, titulo, tec, metrica) in enumerate(TARJETAS):
        y = 118 + i * 100
        s.append(f'<rect x="660" y="{y}" width="500" height="86" rx="14" fill="#ffffff" fill-opacity=".07" stroke="#ffffff" stroke-opacity=".12"/>')
        s.append(f'<circle cx="700" cy="{y + 43}" r="20" fill="{BRASS}"/>')
        s.append(_t(700, y + 49, n, 18, NAVY, "700", "middle"))
        s.append(_t(736, y + 34, f"SPRINT {n}", 11, BRASS, "700", extra='letter-spacing="1.5"'))
        s.append(_t(736, y + 56, titulo, 19, "#ffffff", "700"))
        s.append(_t(736, y + 76, tec, 12, "#9fb0c8"))
        s.append(f'<rect x="{1148 - 7 * len(metrica) - 26}" y="{y + 28}" width="{7 * len(metrica) + 26}" height="30" rx="15" fill="{BRASS}" fill-opacity=".16" stroke="{BRASS}" stroke-opacity=".6"/>')
        s.append(_t(f"{1148 - (7 * len(metrica) + 26) / 2:.0f}", y + 48, metrica, 12.5, "#ffe4a8", "700", "middle"))
    # flujo
    x = 660
    for i, f in enumerate(FLUJO):
        w = 26 + 7.5 * len(f)
        s.append(f'<rect x="{x}" y="528" width="{w}" height="30" rx="15" fill="#ffffff" fill-opacity=".10"/>')
        s.append(_t(x + w / 2, 548, f, 12.5, "#ffffff", "600", "middle"))
        x += w
        if i < len(FLUJO) - 1:
            s.append(_t(x + 5, 548, "›", 18, BRASS, "700", "middle"))
            x += 10
    s.append("</svg>")
    return "".join(s)


if __name__ == "__main__":
    print(svg_resumen())
