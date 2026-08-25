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

/* Oculta el menú y el footer por defecto de Streamlit para look más limpio */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ---- Hero de portada ---- */
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

/* ---- Tarjetas métricas ---- */
div[data-testid="stMetric"] {
    background: white; border-radius: 14px; padding: 14px 18px;
    border: 1px solid #E7ECEA; box-shadow: 0 2px 10px rgba(20,40,35,0.04);
}

/* ---- Tarjetas genéricas (contenedores con borde) ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border: 1px solid #E7ECEA !important;
    box-shadow: 0 2px 10px rgba(20,40,35,0.05);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 22px rgba(20,40,35,0.10);
    transform: translateY(-2px);
}

/* ---- Botones ---- */
.stButton>button, .stDownloadButton>button {
    border-radius: 10px; font-weight: 600; border: none;
    background: #1D9E75; color: white; padding: 8px 18px;
    transition: background 0.15s ease;
}
.stButton>button:hover, .stDownloadButton>button:hover { background: #0F6E56; color: white; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: #F3F6F4;
    border-right: 1px solid #E4EAE7;
}
section[data-testid="stSidebar"] .stRadio > label { font-weight: 600; }

/* ---- Chips de tipo/distrito ---- */
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
# FUNCIONES DE DIBUJO (idénticas al original, pero devuelven fig para st.pyplot)
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


def dibujar_grafo_dia(dia, criterio):
    cfg = DIAS_CONFIG[dia]
    destinos = cfg["destinos"]
    BASE = 15
    color_dia = cfg["color"]

    orden, costo_total = ruta_optima_dia(destinos, matrices, criterio)
    if orden is None:
        return None, None, None

    secuencia = [BASE] + orden + [BASE]
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
    nodos_transito = nodos_ruta - nodos_destino - {BASE}
    pos_sub = {n: POSICIONES[n] for n in nodos_ruta}

    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_facecolor("#F0F4F8")
    fig.patch.set_facecolor("#E8EDF2")

    for u, v in G.edges():
        if u in nodos_ruta and v in nodos_ruta and tuple(sorted([u, v])) not in aristas_ruta:
            x0, y0 = pos_sub[u]; x1, y1 = pos_sub[v]
            ax.plot([x0, x1], [y0, y1], color="#CCCCCC", linewidth=0.8, alpha=0.5, zorder=1)

    ya_etiquetado = set()
    for u, v in segmentos_dir:
        x0, y0 = pos_sub[u]; x1, y1 = pos_sub[v]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=color_dia, lw=2.6,
                                     connectionstyle="arc3,rad=0.08", mutation_scale=16), zorder=3)
        par = tuple(sorted([u, v]))
        if par not in ya_etiquetado and G.has_edge(u, v):
            val = G[u][v][criterio]
            txt = f"${val:.2f}" if criterio == "costo" else f"{val}{UNIDAD_SYM[criterio]}"
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            ax.text(mx, my, txt, ha="center", va="center", fontsize=7.5, fontweight="bold", color=color_dia, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.26", facecolor="white", edgecolor=color_dia, alpha=0.93, linewidth=0.8))
            ya_etiquetado.add(par)

    RADIO_BASE, RADIO_DEST, RADIO_TRANS = 0.046, 0.036, 0.022
    for nid in nodos_ruta:
        x, y = pos_sub[nid]
        if nid == BASE:
            cn, radio, ec, lw = "#1D9E75", RADIO_BASE, "white", 3.0
        elif nid in nodos_destino:
            cn, radio, ec, lw = COLORES_TIPO.get(G.nodes[nid]["tipo"], "#378ADD"), RADIO_DEST, color_dia, 2.5
        else:
            cn, radio, ec, lw = "#AAAAAA", RADIO_TRANS, "#888888", 1.5

        ax.add_patch(plt.Circle((x, y), radio, color=cn, ec=ec, linewidth=lw, zorder=4))
        cod = G.nodes[nid]["cod"] + ("*" if nid in nodos_transito else "")
        fs_cod = 10 if nid == BASE else (9 if nid in nodos_destino else 7)
        ax.text(x, y + 0.006, cod, ha="center", va="center", fontsize=fs_cod, fontweight="bold", color="white", zorder=5)

        nombre = G.nodes[nid]["nombre"]
        if x > 0.72: lx, ly, ha = x + 0.010, y + radio + 0.032, "left"
        elif x < 0.28: lx, ly, ha = x - 0.010, y + radio + 0.032, "right"
        elif y > 0.65: lx, ly, ha = x, y + radio + 0.032, "center"
        else: lx, ly, ha = x, y - radio - 0.032, "center"
        peso_f = "bold" if (nid in nodos_destino or nid == BASE) else "normal"
        borde_l = color_dia if (nid in nodos_destino or nid == BASE) else "#BBBBBB"
        ax.text(lx, ly, nombre, ha=ha, va="center", fontsize=8, fontweight=peso_f, color="#1A1A1A", zorder=6,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=borde_l, alpha=0.95, linewidth=1.0))

    for i, nodo in enumerate(secuencia):
        if nodo != BASE:
            x, y = pos_sub[nodo]
            ax.text(x + RADIO_DEST + 0.012, y + RADIO_DEST + 0.012, str(i), fontsize=10, fontweight="bold",
                    color=color_dia, zorder=7,
                    bbox=dict(boxstyle="circle,pad=0.15", facecolor="white", edgecolor=color_dia, linewidth=1.2, alpha=0.96))

    ruta_str = " → ".join(G.nodes[n]["cod"] for n in secuencia)
    ax.text(0.01, 0.01, f"Ruta óptima ({criterio}):\n{ruta_str}\nTotal: {costo_total:.1f} {UNIDAD[criterio]}",
            transform=ax.transAxes, fontsize=8.5, color="#1A1A1A", va="bottom",
            bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor=color_dia, alpha=0.95, linewidth=1.2))

    leyenda = [
        mpatches.Patch(color="#1D9E75", label="Base: Penonomé"),
        mpatches.Patch(color=color_dia, label="Ruta óptima Dijkstra"),
        mpatches.Patch(color="#AAAAAA", label="Nodo de tránsito (*)"),
    ]
    ax.legend(handles=leyenda, loc="lower right", fontsize=9, framealpha=0.95, edgecolor="#AAAAAA", fancybox=True)
    ax.set_title(f"DÍA {dia} — {cfg['zona']}\n{NOMBRE_CRIT[criterio]} · {len(destinos)} destinos + base",
                 fontsize=12, fontweight="bold", color=color_dia, pad=12)
    ax.set_xlim(-0.08, 1.08); ax.set_ylim(-0.08, 1.08)
    ax.axis("off")
    plt.tight_layout(pad=1.5)
    return fig, secuencia, costo_total


def dibujar_camino_minimo(origen, destino, criterio):
    camino = caminos[criterio][origen][destino]
    if not camino:
        return None
    nodos_cam = set(camino)
    subG = G.subgraph(nodos_cam)
    pos_sub = {n: POSICIONES[n] for n in nodos_cam}
    aristas_cam = [(camino[i], camino[i + 1]) for i in range(len(camino) - 1)]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#F0F2F5")

    nx.draw_networkx_edges(subG, pos_sub, ax=ax, edge_color="#CCCCCC", width=1.0)
    nx.draw_networkx_edges(G, pos_sub, edgelist=aristas_cam, ax=ax, edge_color="#E63946", width=3.2, alpha=0.9)

    cols = [COLORES_TIPO.get(G.nodes[n]["tipo"], "#999") for n in subG.nodes()]
    nx.draw_networkx_nodes(subG, pos_sub, ax=ax, node_color=cols, node_size=1300, alpha=0.92)
    nx.draw_networkx_labels(subG, pos_sub, labels={n: G.nodes[n]["cod"] for n in subG.nodes()},
                             ax=ax, font_size=9, font_weight="bold", font_color="white")
    pos_nom = {n: (x, y - 0.05) for n, (x, y) in pos_sub.items()}
    nx.draw_networkx_labels(subG, pos_nom, labels={n: G.nodes[n]["nombre"][:15] for n in subG.nodes()},
                             ax=ax, font_size=7, font_color="#333")

    edge_labels = {}
    for u, v in aristas_cam:
        val = G[u][v][criterio]
        edge_labels[(u, v)] = f"${val:.2f}" if criterio == "costo" else f"{val}{UNIDAD_SYM[criterio]}"
    nx.draw_networkx_edge_labels(G, pos_sub, edge_labels=edge_labels, ax=ax, font_size=8, font_color="#E63946",
                                  bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#E63946", alpha=0.85))

    valor = matrices[criterio][origen][destino]
    camino_str = " → ".join(G.nodes[n]["cod"] for n in camino)
    ax.set_title(f"Camino Mínimo: {G.nodes[origen]['cod']} → {G.nodes[destino]['cod']}\n"
                 f"Criterio: {criterio} | Valor: {valor:.2f} {UNIDAD[criterio]}\nRuta: {camino_str}",
                 fontsize=11, fontweight="bold", color="#1F4E79", pad=10)
    ax.axis("off")
    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# BARRA LATERAL — NAVEGACIÓN
# ═══════════════════════════════════════════════════════════════════════════

st.sidebar.title("🗺️ Rutas Coclé")
st.sidebar.caption("Algoritmo de Dijkstra · Universidad de Panamá")
seccion = st.sidebar.radio(
    "Ir a:",
    ["🏠 Inicio", "📋 Inventario", "🕸️ Grafo completo", "📅 Ruta por día",
     "🔗 Camino mínimo", "📊 Matrices", "⬇️ Exportar Excel"],
)

# ═══════════════════════════════════════════════════════════════════════════
# INICIO
# ═══════════════════════════════════════════════════════════════════════════

if seccion == "🏠 Inicio":
    st.markdown("""
    <div class="hero">
        <div class="hero-title">🗺️ Rutas Turísticas Óptimas — Provincia de Coclé, Panamá</div>
        <div class="hero-sub">Plataforma construida sobre el algoritmo de <b>Dijkstra</b>, aplicado a un
        grafo de 21 atractivos turísticos y 32 conexiones, con tres criterios de optimización:
        distancia, tiempo y costo.</div>
        <div class="hero-badges">
            <span class="hero-badge">📍 21 nodos</span>
            <span class="hero-badge">🔗 32 aristas</span>
            <span class="hero-badge">📅 7 itinerarios</span>
            <span class="hero-badge">🎓 Universidad de Panamá</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Nodos (atractivos)", G.number_of_nodes())
    c2.metric("Aristas (conexiones)", G.number_of_edges())
    c3.metric("Itinerarios diseñados", len(DIAS_CONFIG))

    st.subheader("✨ Vista previa de algunos atractivos")
    destacados = [15, 21, 10, 13]  # Penonomé, Cerro Gaital, El Caño, El Chorro Las Yayas
    cols = st.columns(len(destacados))
    for col, nid in zip(cols, destacados):
        with col:
            mostrar_imagen(ATRACTIVOS[nid]["cod"], ATRACTIVOS[nid]["nombre"])

    if not os.path.isdir(CARPETA_IMAGENES) or not os.listdir(CARPETA_IMAGENES):
        st.info("💡 Aún no hay fotos cargadas. Coloca tus imágenes en la carpeta `imagenes/`, "
                "nombradas con el código del atractivo — por ejemplo `imagenes/PSC.jpg` para "
                "Playa Santa Clara, `imagenes/CGA.jpg` para Cerro Gaital, etc. (ver códigos en Inventario).")

# ═══════════════════════════════════════════════════════════════════════════
# INVENTARIO
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "📋 Inventario":
    st.markdown('<div class="hero-title" style="color:#0F6E56;">📋 Inventario de Atractivos Turísticos</div>', unsafe_allow_html=True)
    st.write("")
    filtro_tipo = st.multiselect("Filtrar por tipo:", sorted({d["tipo"] for d in ATRACTIVOS.values()}))
    for nid, data in sorted(ATRACTIVOS.items()):
        if filtro_tipo and data["tipo"] not in filtro_tipo:
            continue
        color = COLORES_TIPO.get(data["tipo"], "#999999")
        with st.container(border=True):
            c_img, c_info = st.columns([1, 3])
            with c_img:
                mostrar_imagen(data["cod"], data["nombre"], ancho=180)
            with c_info:
                st.markdown(
                    f"""<span style="font-size:1.1rem;font-weight:700;color:#1A2E29;">{data['nombre']}</span>
                    &nbsp;<code>{data['cod']}</code>""",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""<span class="chip" style="background:{color}22;color:{color};border-color:{color}55;">{data['tipo']}</span>
                    <span class="chip">📍 {data['distrito']}</span>""",
                    unsafe_allow_html=True,
                )
                st.write("")
                cc1, cc2 = st.columns(2)
                cc1.write(f"⭐ Puntaje: **{data['puntaje']}**")
                cc2.write(f"🔗 Conexiones: **{G.degree(nid)}**")

# ═══════════════════════════════════════════════════════════════════════════
# GRAFO COMPLETO
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "🕸️ Grafo completo":
    st.title("Grafo Turístico Completo")
    criterio = st.radio("Criterio a visualizar:", ["distancia", "tiempo", "costo"], horizontal=True)
    fig = dibujar_grafo_completo(criterio)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════
# RUTA POR DÍA
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "📅 Ruta por día":
    st.markdown('<div class="hero-title" style="color:#0F6E56;">📅 Ruta Óptima por Día</div>', unsafe_allow_html=True)
    st.write("")
    dia = st.selectbox(
        "Elige el día:",
        list(DIAS_CONFIG.keys()),
        format_func=lambda d: f"Día {d} — {DIAS_CONFIG[d]['zona']}",
    )
    criterio = st.radio("Criterio de optimización:", ["distancia", "tiempo", "costo"], horizontal=True)

    fig, secuencia, costo_total = dibujar_grafo_dia(dia, criterio)
    if fig is None:
        st.error("No se pudo calcular la ruta para este día.")
    else:
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        ruta_str = " → ".join(G.nodes[n]["cod"] for n in secuencia)
        color_dia = DIAS_CONFIG[dia]["color"]
        st.markdown(
            f"""<div style="background:{color_dia}14;border:1px solid {color_dia}55;border-radius:12px;
            padding:14px 18px;margin:6px 0 18px 0;">
            <b style="color:{color_dia};">Ruta óptima:</b> {ruta_str}
            &nbsp;&nbsp;|&nbsp;&nbsp; <b style="color:{color_dia};">Total:</b> {costo_total:.1f} {UNIDAD[criterio]}
            </div>""",
            unsafe_allow_html=True,
        )

        st.subheader("📋 Detalle del tramo")
        filas = []
        tot_d = tot_t = tot_c = 0
        for i in range(len(secuencia) - 1):
            u, v = secuencia[i], secuencia[i + 1]
            d = matrices["distancia"][u][v] or 0
            t = matrices["tiempo"][u][v] or 0
            c = matrices["costo"][u][v] or 0
            tot_d += d; tot_t += t; tot_c += c
            filas.append({
                "Tramo": f"{G.nodes[u]['cod']} → {G.nodes[v]['cod']}",
                "Distancia (km)": round(d, 1), "Tiempo (min)": round(t, 1), "Costo ($)": round(c, 2),
            })
        st.dataframe(filas, use_container_width=True, hide_index=True)

        st.subheader("Galería de destinos del día")
        destinos_dia = DIAS_CONFIG[dia]["destinos"]
        cols = st.columns(len(destinos_dia))
        for col, nid in zip(cols, destinos_dia):
            with col:
                mostrar_imagen(ATRACTIVOS[nid]["cod"], ATRACTIVOS[nid]["nombre"])

# ═══════════════════════════════════════════════════════════════════════════
# CAMINO MÍNIMO
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "🔗 Camino mínimo":
    st.title("Camino Mínimo entre Dos Nodos")
    opciones = {f"{d['cod']} — {d['nombre']}": nid for nid, d in sorted(ATRACTIVOS.items())}
    c1, c2 = st.columns(2)
    origen_label = c1.selectbox("Origen:", list(opciones.keys()), index=list(opciones.values()).index(15))
    destino_label = c2.selectbox("Destino:", list(opciones.keys()), index=0)
    criterio = st.radio("Criterio:", ["distancia", "tiempo", "costo"], horizontal=True)

    origen, destino = opciones[origen_label], opciones[destino_label]
    if origen == destino:
        st.warning("Elige dos atractivos distintos.")
    else:
        camino = caminos[criterio][origen][destino]
        if not camino:
            st.error("No existe camino entre esos dos nodos.")
        else:
            valor = matrices[criterio][origen][destino]
            ruta_str = " → ".join(G.nodes[n]["cod"] for n in camino)
            st.success(f"**Ruta:** {ruta_str}  —  **Valor total:** {valor:.2f} {UNIDAD[criterio]}")

            fig = dibujar_camino_minimo(origen, destino, criterio)
            if fig:
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

            filas = []
            for i in range(len(camino) - 1):
                a, b = camino[i], camino[i + 1]
                filas.append({
                    "Paso": i + 1, "De": G.nodes[a]["cod"], "A": G.nodes[b]["cod"],
                    "Distancia (km)": G[a][b]["distancia"], "Tiempo (min)": G[a][b]["tiempo"],
                    "Costo ($)": G[a][b]["costo"],
                })
            st.dataframe(filas, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# MATRICES
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "📊 Matrices":
    st.title("Matrices de Caminos Mínimos (21×21)")
    criterio = st.radio("Matriz a mostrar:", ["distancia", "tiempo", "costo"], horizontal=True)
    nodos = sorted(G.nodes())
    mat = matrices[criterio]
    tabla = []
    for origen in nodos:
        fila = {"": ATRACTIVOS[origen]["cod"]}
        for destino in nodos:
            if origen == destino:
                fila[ATRACTIVOS[destino]["cod"]] = 0
            else:
                val = mat[origen][destino]
                fila[ATRACTIVOS[destino]["cod"]] = "∞" if val is None else round(val, 1)
        tabla.append(fila)
    st.dataframe(tabla, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# EXPORTAR EXCEL
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "⬇️ Exportar Excel":
    st.title("Exportar Matrices a Excel")
    st.write("Genera el mismo libro de Excel de la versión de consola (3 matrices + inventario), "
             "listo para descargar directamente desde el navegador.")
    excel_bytes = generar_excel_bytes(matrices, G)
    st.download_button(
        label="⬇️ Descargar Matrices_Dijkstra_Cocle.xlsx",
        data=excel_bytes,
        file_name="Matrices_Dijkstra_Cocle.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
