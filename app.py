"""
Plataforma web — Optimización de Rutas Turísticas, Provincia de Coclé, Panamá
Algoritmo de Dijkstra | 21 Nodos | 3 Criterios | Streamlit
Universidad de Panamá – Facultad de Informática
"""

import os
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from logica_dijkstra import (
    ATRACTIVOS, DIAS_CONFIG, COLORES_TIPO, POSICIONES,
    construir_grafo, calcular_todas_matrices, ruta_optima_dia,
    generar_excel_bytes,
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Rutas Turísticas Coclé — Dijkstra",
    page_icon="🗺️",
    layout="wide",
)

CARPETA_IMAGENES = os.path.join(os.path.dirname(__file__), "imagenes")

# ═══════════════════════════════════════════════════════════════════════════
# ESTILO VISUAL (CSS propio sobre Streamlit)
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
h1, h2, h3, .hero-title { font-family: 'Poppins', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.hero {
    background: linear-gradient(120deg, #0F6E56 0%, #1D9E75 55%, #378ADD 130%);
    border-radius: 18px;
    padding: 42px 40px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 10px 30px rgba(15,110,86,0.25);
}
.hero-title { font-size: 2.1rem; font-weight: 800; margin: 0 0 8px 0; color: white; }
.hero-sub { font-size: 1.02rem; opacity: 0.92; max-width: 640px; line-height: 1.5; }
.hero-badges { margin-top: 18px; }
.hero-badge {
    display: inline-block; background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35); border-radius: 999px;
    padding: 5px 14px; margin-right: 8px; font-size: 0.82rem; font-weight: 600;
}

div[data-testid="stMetric"] {
    background: white; border-radius: 14px; padding: 14px 18px;
    border: 1px solid #E7ECEA; box-shadow: 0 2px 10px rgba(20,40,35,0.04);
}

.stButton>button, .stDownloadButton>button {
    border-radius: 10px; font-weight: 600; border: none;
    background: #1D9E75; color: white; padding: 8px 18px;
    transition: background 0.15s ease;
}
.stButton>button:hover, .stDownloadButton>button:hover { background: #0F6E56; color: white; }

section[data-testid="stSidebar"] {
    background: #F3F6F4;
    border-right: 1px solid #E4EAE7;
}

.chip {
    display: inline-block; padding: 3px 11px; border-radius: 999px;
    font-size: 0.78rem; font-weight: 600; margin-right: 6px;
    background: #EAF6F1; color: #0F6E56; border: 1px solid #CFEBDF;
}
</style>
""", unsafe_allow_html=True)


def imagen_de(cod: str):
    """Busca imagenes/<COD>.jpg|.jpeg|.png; devuelve la ruta si existe, si no None."""
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        ruta = os.path.join(CARPETA_IMAGENES, cod + ext)
        if os.path.isfile(ruta):
            return ruta
    return None


def mostrar_imagen(cod: str, nombre: str, ancho=None):
    ruta = imagen_de(cod)
    if ruta:
        st.image(ruta, caption=nombre, use_container_width=(ancho is None), width=ancho)
    else:
        st.markdown(
            f"""<div style="border:1px dashed #999;border-radius:8px;padding:18px;
            text-align:center;color:#888;background:#fafafa;">
            📷 Sin foto todavía<br><small>agrega <code>imagenes/{cod}.jpg</code></small>
            </div>""",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════
# CACHE: grafo y matrices se calculan una sola vez
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_resource
def cargar_datos():
    G = construir_grafo()
    matrices, caminos = calcular_todas_matrices(G)
    return G, matrices, caminos


G, matrices, caminos = cargar_datos()

UNIDAD = {"distancia": "km", "tiempo": "min", "costo": "USD"}
UNIDAD_SYM = {"distancia": "km", "tiempo": "min", "costo": "$"}
NOMBRE_CRIT = {"distancia": "Distancia mínima (km)", "tiempo": "Tiempo mínimo (min)", "costo": "Costo mínimo (USD)"}

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE DIBUJO
# ═══════════════════════════════════════════════════════════════════════════

def dibujar_grafo_completo(criterio):
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor("#F0F4F8")
    fig.patch.set_facecolor("#E8EDF2")

    for u, v, data in G.edges(data=True):
        x0, y0 = POSICIONES[u]; x1, y1 = POSICIONES[v]
        ax.plot([x0, x1], [y0, y1], color="#BBBBBB", linewidth=1.0, zorder=1, alpha=0.7)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        val = data[criterio]
        txt = f"${val:.2f}" if criterio == "costo" else f"{val}{UNIDAD_SYM[criterio]}"
        ax.text(mx, my, txt, fontsize=6.5, ha="center", va="center", color="#555555", zorder=2,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="#DDDDDD", alpha=0.85, linewidth=0.6))

    RADIO_HUB, RADIO_NORM = 0.032, 0.024
    for nid in G.nodes():
        x, y = POSICIONES[nid]
        tipo = G.nodes[nid]["tipo"]
        color = COLORES_TIPO.get(tipo, "#999999")
        radio = RADIO_HUB if tipo == "Hub/Ciudad" else RADIO_NORM
        ax.add_patch(plt.Circle((x + 0.004, y - 0.004), radio, color="#00000022", zorder=3))
        ax.add_patch(plt.Circle((x, y), radio, color=color, zorder=4, linewidth=2.0, ec="white"))
        ax.text(x, y + 0.006, G.nodes[nid]["cod"], ha="center", va="center", fontsize=8.5,
                fontweight="bold", color="white", zorder=5)
        nombre = G.nodes[nid]["nombre"]
        if x > 0.75: lx, ly, ha = x + 0.008, y + radio + 0.024, "left"
        elif x < 0.25: lx, ly, ha = x - 0.008, y + radio + 0.024, "right"
        elif y > 0.65: lx, ly, ha = x, y + radio + 0.024, "center"
        else: lx, ly, ha = x, y - radio - 0.024, "center"
        ax.text(lx, ly, nombre, ha=ha, va="center", fontsize=7.5, fontweight="600", color="#1A1A1A", zorder=6,
                bbox=dict(boxstyle="round,pad=0.28", facecolor="white", edgecolor=color, alpha=0.93, linewidth=0.8))

    leyenda = [
        mpatches.Patch(color="#1D9E75", label="Hub / Ciudad"),
        mpatches.Patch(color="#378ADD", label="Playa"),
        mpatches.Patch(color="#BA7517", label="Cultural / Histórico"),
        mpatches.Patch(color="#7F77DD", label="Naturaleza / Parque Nacional"),
        mpatches.Patch(color="#D85A30", label="Arqueológico"),
    ]
    ax.legend(handles=leyenda, loc="lower left", fontsize=9, framealpha=0.95, edgecolor="#AAAAAA", fancybox=True)
    ax.set_title(f"Grafo Turístico G=(V,E) — Coclé, Panamá\nCriterio: {NOMBRE_CRIT[criterio]} | 21 nodos · 32 aristas · Base: Penonomé",
                 fontsize=13, fontweight="bold", color="#1F4E79", pad=14)
    ax.set_xlim(-0.08, 1.12); ax.set_ylim(-0.06, 1.06)
    ax.axis("off")
    plt.tight_layout(pad=1.5)
    return fig


def dibujar_grafo_dia(dia, criterio, secuencia, costo_total):
    """Dibuja el grafo del día con la ruta óptima."""
    cfg = DIAS_CONFIG[dia]
    destinos = cfg["destinos"]
    hub = cfg["hub"]
    color_dia = cfg["color"]

    nodos_ruta = set(secuencia)
    aristas_ruta, segmentos_dir = [], []
    for i in range(len(secuencia) - 1):
        seg = caminos[criterio][secuencia[i]][secuencia[i + 1]]
        for j in range(len(seg) - 1):
            aristas_ruta.append(tuple(sorted([seg[j], seg[j + 1]])))
            segmentos_dir.append((seg[j], seg[j + 1]))
        nodos_ruta.update(seg)
    aristas_ruta = list(set(aristas_ruta))

    nodos_destino = set(destinos)
    nodos_transito = nodos_ruta - nodos_destino - {hub}
    pos_sub = {n: POSICIONES[n] for n in nodos_ruta}

    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_facecolor("#F0F4F8")
    fig.patch.set_facecolor("#E8EDF2")

    # Aristas no usadas
    for u, v in G.edges():
        if u in nodos_ruta and v in nodos_ruta and tuple(sorted([u, v])) not in aristas_ruta:
            x0, y0 = pos_sub[u]; x1, y1 = pos_sub[v]
            ax.plot([x0, x1], [y0, y1], color="#CCCCCC", linewidth=0.8, alpha=0.5, zorder=1)

    # Aristas de la ruta
    ya_etiquetado = set()
    for u, v in segmentos_dir:
        x0, y0 = pos_sub[u]; x1, y1 = pos_sub[v]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=color_dia, lw=2.6,
                                     connectionstyle="arc3,rad=0.08", mutation_scale=16), zorder=3)
        par = tuple(sorted([u, v]))
