# Arturo Calle · Logística inteligente

Para observar el proyecto completo se puede revisar aquí https://fundamentosdeia-lyqrexugfztdad6nvoe4vh.streamlit.app/

Proyecto de **Fundamentos de Inteligencia Artificial** (Mariana Tobón y Maria Clara Escobar).
Una sola app de Streamlit que unifica los sprints del proyecto para agilizar el reparto de inventario
desde la Bodega Itagüí hacia 9 tiendas del Valle de Aburrá (90 min disponibles, 15 min de atención por tienda).

| Página | Sprint | Qué hace |
|---|---|---|
| 1 · El mapa | 1 | Red de tiempos, Dijkstra (camino más corto) y A* (recorrido completo) |
| 2 · El experto | 2 | Relaciones, umbrales y 10 reglas SI-ENTONCES del experto |
| 3 · El plan del día | 2 | Memoria de trabajo editable, razonamiento y plan del día |
| 4 · El rival | 3 | Teoría de juegos (Nash), escenario competitivo y algoritmo genético |
| 5 · Grados de urgencia | 4 | Prioridad difusa (Mamdani) que reemplaza urgente/media/baja |
| 6 · La carga | 4 | Capa difusa (Sugeno) que decide cuántas unidades enviar a cada tienda; exporta a Excel |

Con la prioridad clásica y la semilla 42, la app reproduce los resultados de los notebooks
(recorrido A* de 104 min, plan del día de 68 min, ruta Oviedo → Unicentro en el equilibrio de Nash).

## Estructura
```
app.py            # navegación y estilo
estado.py         # estado compartido entre páginas
servicio.py       # puente app ↔ motor (con caché) y exportación a Excel
ui.py             # mapa, línea de tiempo y componentes visuales
motor/            # lógica sin Streamlit: red, experto, juego, genético, difuso
paginas/          # una página por módulo
```

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en GitHub Pages
La app corre completa en el navegador con [stlite](https://github.com/whitphx/stlite) (Streamlit sobre Pyodide), sin servidor.
`index.html` carga los mismos archivos `.py` del repositorio.

1. En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions** (se guarda solo).
2. El flujo `.github/workflows/pages.yml` publica al hacer push; también se puede lanzar a mano en la pestaña **Actions**.
3. Abre `https://mtobon2005-creator.github.io/fundamentosdeia/` cuando termine el flujo (un par de minutos).

La primera carga descarga Python, pandas y plotly en el navegador y puede tardar hasta un minuto.

## Desplegar en Streamlit Community Cloud
1. Entra a https://share.streamlit.io con tu cuenta de GitHub.
2. **New app** → repositorio `mtobon2005-creator/fundamentosdeia`, rama `main`, archivo `app.py`.
3. **Deploy**.

## Imagen resumen y respaldo
- `assets/resumen_proyecto.svg` / `.png`: imagen que resume el proyecto (la misma de la portada de la app).
- La rama `respaldo-v1` guarda la versión de la app anterior al rediseño.
