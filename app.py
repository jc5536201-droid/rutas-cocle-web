"""
PLATAFORMA WEB - OPTIMIZACIÓN DE RUTAS TURÍSTICAS
Provincia de Coclé, Panamá
28 Atractivos | 7 Itinerarios | Algoritmo de Dijkstra
"""

import os
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import pandas as pd

from logica_dijkstra import (
    ATRACTIVOS, DIAS_CONFIG, COLORES_TIPO, POSICIONES,
    construir_grafo, calcular_todas_matrices, ruta_optima_dia,
    generar_excel_bytes, diagnosticar_grafo
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Rutas Turísticas Coclé — 28 Atractivos",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CARPETA_IMAGENES = os.path.join(os.path.dirname(__file__), "imagenes")

# ═══════════════════════════════════════════════════════════════════════════
# ESTILO CSS
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
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


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

def imagen_de(cod: str):
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
            📷 Sin foto<br><small><code>imagenes/{cod}.jpg</code></small>
            </div>""",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════
# CARGAR DATOS (CACHE)
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
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_facecolor("#F0F4F8")
    fig.patch.set_facecolor("#E8EDF2")

    for u, v, data in G.edges(data=True):
        x0, y0 = POSICIONES[u]; x1, y1 = POSICIONES[v]
        ax.plot([x0, x1], [y0, y1], color="#BBBBBB", linewidth=1.0, zorder=1, alpha=0.6)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        val = data[criterio]
        txt = f"${val:.2f}" if criterio == "costo" else f"{val}{UNIDAD_SYM[criterio]}"
        ax.text(mx, my, txt, fontsize=6, ha="center", va="center", color="#555555", zorder=2,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="#DDDDDD", alpha=0.85, linewidth=0.5))

    RADIO_HUB, RADIO_NORM = 0.035, 0.025
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
        if x > 0.78:
            lx, ly, ha = x + 0.008, y + radio + 0.024, "left"
        elif x < 0.22:
            lx, ly, ha = x - 0.008, y + radio + 0.024, "right"
        elif y > 0.68:
            lx, ly, ha = x, y + radio + 0.024, "center"
        else:
            lx, ly, ha = x, y - radio - 0.024, "center"
        ax.text(lx, ly, nombre, ha=ha, va="center", fontsize=7, fontweight="600", color="#1A1A1A", zorder=6,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=color, alpha=0.93, linewidth=0.8))

    leyenda = [
        mpatches.Patch(color="#1D9E75", label="Hub / Ciudad"),
        mpatches.Patch(color="#378ADD", label="Playa"),
        mpatches.Patch(color="#BA7517", label="Cultural / Histórico"),
        mpatches.Patch(color="#7F77DD", label="Naturaleza / Parque / Montaña"),
        mpatches.Patch(color="#D85A30", label="Arqueológico"),
        mpatches.Patch(color="#FF6B35", label="Mirador"),
    ]
    ax.legend(handles=leyenda, loc="lower left", fontsize=9, framealpha=0.95, edgecolor="#AAAAAA", fancybox=True)
    ax.set_title(f"Grafo Turístico G=(V,E) — Coclé, Panamá\n28 Nodos · {G.number_of_edges()} Aristas | Criterio: {NOMBRE_CRIT[criterio]}",
                 fontsize=13, fontweight="bold", color="#1F4E79", pad=14)
    ax.set_xlim(-0.08, 1.12); ax.set_ylim(-0.06, 1.06)
    ax.axis("off")
    plt.tight_layout(pad=1.5)
    return fig


def dibujar_grafo_dia(dia, criterio, secuencia, costo_total):
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

    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_facecolor("#F0F4F8")
    fig.patch.set_facecolor("#E8EDF2")

    for u, v in G.edges():
        if u in nodos_ruta and v in nodos_ruta and tuple(sorted([u, v])) not in aristas_ruta:
            x0, y0 = pos_sub[u]; x1, y1 = pos_sub[v]
            ax.plot([x0, x1], [y0, y1], color="#CCCCCC", linewidth=0.6, alpha=0.3, zorder=1, linestyle="dotted")

    ya_etiquetado = set()
    for u, v in segmentos_dir:
        x0, y0 = pos_sub[u]; x1, y1 = pos_sub[v]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=color_dia, lw=2.8,
                                     connectionstyle="arc3,rad=0.05", mutation_scale=18), zorder=3)
        par = tuple(sorted([u, v]))
        if par not in ya_etiquetado and G.has_edge(u, v):
            val = G[u][v][criterio]
            txt = f"${val:.2f}" if criterio == "costo" else f"{val}{UNIDAD_SYM[criterio]}"
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            ax.text(mx, my, txt, ha="center", va="center", fontsize=8, fontweight="bold", color=color_dia, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color_dia, alpha=0.95, linewidth=1.0))
            ya_etiquetado.add(par)

    RADIO_BASE, RADIO_DEST, RADIO_TRANS = 0.050, 0.040, 0.025
    for nid in nodos_ruta:
        x, y = pos_sub[nid]
        if nid == hub:
            cn, radio, ec, lw = "#1D9E75", RADIO_BASE, "white", 3.5
        elif nid in nodos_destino:
            cn, radio, ec, lw = COLORES_TIPO.get(G.nodes[nid]["tipo"], "#378ADD"), RADIO_DEST, color_dia, 3.0
        else:
            cn, radio, ec, lw = "#AAAAAA", RADIO_TRANS, "#888888", 1.5

        ax.add_patch(plt.Circle((x, y), radio, color=cn, ec=ec, linewidth=lw, zorder=4))
        cod = G.nodes[nid]["cod"] + ("*" if nid in nodos_transito else "")
        fs_cod = 11 if nid == hub else (10 if nid in nodos_destino else 8)
        ax.text(x, y + 0.008, cod, ha="center", va="center", fontsize=fs_cod, fontweight="bold", color="white", zorder=5)

        nombre = G.nodes[nid]["nombre"]
        if x > 0.78:
            lx, ly, ha = x - 0.015, y + radio + 0.035, "right"
        elif x < 0.22:
            lx, ly, ha = x + 0.015, y + radio + 0.035, "left"
        elif y > 0.78:
            lx, ly, ha = x, y - radio - 0.035, "center"
        else:
            lx, ly, ha = x, y + radio + 0.035, "center"
        peso_f = "bold" if (nid in nodos_destino or nid == hub) else "normal"
        borde_l = color_dia if (nid in nodos_destino or nid == hub) else "#BBBBBB"
        ax.text(lx, ly, nombre, ha=ha, va="center", fontsize=9, fontweight=peso_f, color="#1A1A1A", zorder=6,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=borde_l, alpha=0.97, linewidth=1.2))

    for i, nodo in enumerate(secuencia):
        if nodo != hub:
            x, y = pos_sub[nodo]
            ax.text(x + RADIO_DEST + 0.015, y + RADIO_DEST + 0.015, str(i), fontsize=11, fontweight="bold",
                    color=color_dia, zorder=7,
                    bbox=dict(boxstyle="circle,pad=0.18", facecolor="white", edgecolor=color_dia, linewidth=1.5, alpha=0.98))

    ruta_str = " → ".join(G.nodes[n]["cod"] for n in secuencia)
    if len(ruta_str) > 70:
        cods = [G.nodes[n]["cod"] for n in secuencia]
        partes = []
        for i in range(0, len(cods), 7):
            partes.append(" → ".join(cods[i:i+7]))
        ruta_str = "\n".join(partes)

    ax.text(0.01, 0.01, f"Ruta óptima ({criterio}):\n{ruta_str}\nTotal: {costo_total:.1f} {UNIDAD[criterio]}",
            transform=ax.transAxes, fontsize=9, color="#1A1A1A", va="bottom",
            bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor=color_dia, alpha=0.95, linewidth=1.5))

    leyenda = [
        mpatches.Patch(color="#1D9E75", label=f"Hub: {ATRACTIVOS[hub]['nombre']}"),
        mpatches.Patch(color=color_dia, label="Ruta óptima Dijkstra"),
        mpatches.Patch(color="#AAAAAA", label="Nodo de tránsito (*)"),
        mpatches.Patch(color="#CCCCCC", label="Conexiones no usadas"),
    ]
    ax.legend(handles=leyenda, loc="lower right", fontsize=9, framealpha=0.95, edgecolor="#AAAAAA", fancybox=True)

    ax.set_title(f"DÍA {dia} — {cfg['zona']}\n{NOMBRE_CRIT[criterio]} · {len(destinos)} destinos + hub",
                 fontsize=13, fontweight="bold", color=color_dia, pad=15)
    ax.set_xlim(-0.10, 1.12); ax.set_ylim(-0.08, 1.08)
    ax.axis("off")
    plt.tight_layout(pad=2.0)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

st.sidebar.title("🗺️ Rutas Coclé")
st.sidebar.caption("28 Atractivos · Algoritmo de Dijkstra")

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
        <div class="hero-title">🗺️ Rutas Turísticas Óptimas — Coclé, Panamá</div>
        <div class="hero-sub">Plataforma con <b>28 atractivos</b> y <b>44 conexiones</b> viales, optimizadas con el algoritmo de <b>Dijkstra</b>.<br>
        7 itinerarios diarios de 6-8 horas para que el turista salga desde su hotel y regrese por la tarde.</div>
        <div class="hero-badges">
            <span class="hero-badge">📍 28 nodos</span>
            <span class="hero-badge">🔗 44 aristas</span>
            <span class="hero-badge">📅 7 días</span>
            <span class="hero-badge">🏨 5 hubs</span>
            <span class="hero-badge">🎓 Universidad de Panamá</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏛️ Atractivos", G.number_of_nodes())
    col2.metric("🛣️ Conexiones", G.number_of_edges())
    col3.metric("📅 Itinerarios", len(DIAS_CONFIG))
    col4.metric("🏨 Hubs", len([d for d in ATRACTIVOS.values() if d["tipo"] == "Hub/Ciudad"]))

    st.subheader("✨ Atractivos destacados")
    destacados = [15, 21, 10, 13, 28, 26, 24]
    cols = st.columns(len(destacados))
    for col, nid in zip(cols, destacados):
        with col:
            mostrar_imagen(ATRACTIVOS[nid]["cod"], ATRACTIVOS[nid]["nombre"])

    if not os.path.isdir(CARPETA_IMAGENES) or not os.listdir(CARPETA_IMAGENES):
        st.info("💡 Coloca imágenes en la carpeta `imagenes/` con el código del atractivo")

# ═══════════════════════════════════════════════════════════════════════════
# INVENTARIO
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "📋 Inventario":
    st.title("📋 Inventario de Atractivos Turísticos")
    st.write(f"**Total: {len(ATRACTIVOS)} atractivos** | **{len([d for d in ATRACTIVOS.values() if d['tipo'] == 'Hub/Ciudad'])} hubs**")

    filtro_tipo = st.multiselect("Filtrar por tipo:", sorted({d["tipo"] for d in ATRACTIVOS.values()}))

    for nid, data in sorted(ATRACTIVOS.items()):
        if filtro_tipo and data["tipo"] not in filtro_tipo:
            continue
        color = COLORES_TIPO.get(data["tipo"], "#999999")
        with st.container(border=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                mostrar_imagen(data["cod"], data["nombre"], ancho=180)
            with col2:
                st.markdown(f"**{data['nombre']}** `{data['cod']}` (ID: {nid})")
                st.markdown(f"<span class='chip' style='background:{color}22;color:{color};border-color:{color}55;'>{data['tipo']}</span> <span class='chip'>📍 {data['distrito']}</span>", unsafe_allow_html=True)
                st.write(f"⭐ Puntaje: **{data['puntaje']}** | 🔗 Conexiones: **{G.degree(nid)}**")

# ═══════════════════════════════════════════════════════════════════════════
# GRAFO COMPLETO
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "🕸️ Grafo completo":
    st.title("Grafo Turístico Completo")
    st.write(f"**28 nodos** · **{G.number_of_edges()} aristas** · 3 criterios de optimización")
    criterio = st.radio("Criterio:", ["distancia", "tiempo", "costo"], horizontal=True)
    fig = dibujar_grafo_completo(criterio)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════
# RUTA POR DÍA
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "📅 Ruta por día":
    st.title("📅 Ruta Óptima por Día")

    dia = st.selectbox(
        "Selecciona el día:",
        list(DIAS_CONFIG.keys()),
        format_func=lambda d: f"Día {d} — {DIAS_CONFIG[d]['zona']}",
    )
    criterio = st.radio("Criterio de optimización:", ["distancia", "tiempo", "costo"], horizontal=True)

    cfg = DIAS_CONFIG[dia]
    hub = cfg["hub"]
    destinos = cfg["destinos"]
    orden, costo_total = ruta_optima_dia(destinos, matrices, hub=hub, criterio=criterio)

    if orden is None:
        st.error("No se pudo calcular la ruta para este día.")
    else:
        secuencia = [hub] + orden + [hub]

        # Info del día
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏨 Hotel Base", f"{hub} ({ATRACTIVOS[hub]['cod']})")
        col2.metric("🎯 Atractivos", len(destinos))
        col3.metric("🚗 Tiempo traslado", f"{costo_total:.1f} min")
        col4.metric("📏 Distancia total", f"{sum(matrices['distancia'][secuencia[i]][secuencia[i+1]] for i in range(len(secuencia)-1)):.1f} km")

        st.markdown("### 🚗 Ruta Óptima")
        ruta_str = " → ".join([f"**{ATRACTIVOS[n]['cod']}**" for n in secuencia])
        st.markdown(f"{ruta_str}")

        # Tabla de tramos
        st.markdown("### 📋 Detalle de Tramos")
        tramos = []
        for i in range(len(secuencia)-1):
            origen, destino = secuencia[i], secuencia[i+1]
            tramos.append({
                "Tramo": i+1,
                "Origen": f"{origen} ({ATRACTIVOS[origen]['cod']})",
                "Destino": f"{destino} ({ATRACTIVOS[destino]['cod']})",
                "Tiempo (min)": matrices["tiempo"][origen][destino],
                "Distancia (km)": matrices["distancia"][origen][destino],
                "Costo ($)": matrices["costo"][origen][destino],
            })
        st.dataframe(pd.DataFrame(tramos), use_container_width=True, hide_index=True)

        # Mapa
        st.markdown("### 🗺️ Mapa de la Ruta")
        fig = dibujar_grafo_dia(dia, criterio, secuencia, costo_total)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # Itinerario hora a hora
        st.markdown("### 🕐 Itinerario Hora a Hora")

        hora_actual = 8.0
        if dia == 7:
            hora_actual = 7.0
            st.info("⏰ **Día 7**: Salida recomendada a las 7:00 AM (día más largo)")

        st.markdown(f"**{int(hora_actual):02d}:{int((hora_actual%1)*60):02d}** - 🏁 Salida del hotel (**{ATRACTIVOS[hub]['nombre']}**)")

        for i in range(len(secuencia)-1):
            origen, destino = secuencia[i], secuencia[i+1]
            tiempo_viaje = matrices["tiempo"][origen][destino]
            distancia_viaje = matrices["distancia"][origen][destino]
            hora_actual += tiempo_viaje / 60

            hh, mm = int(hora_actual), int((hora_actual % 1) * 60)
            st.markdown(f"**{hh:02d}:{mm:02d}** - 🚗 Llegada a **{ATRACTIVOS[destino]['nombre']}** ({tiempo_viaje:.0f} min, {distancia_viaje:.1f} km)")

            if i < len(secuencia)-2:
                tiempo_visita = 90
                hora_actual += tiempo_visita / 60
                hh, mm = int(hora_actual), int((hora_actual % 1) * 60)
                st.markdown(f"**{hh:02d}:{mm:02d}** - 🏛️ Fin de visita en **{ATRACTIVOS[destino]['nombre']}** ({tiempo_visita:.0f} min)")

                if i == 1 or i == 3:
                    hora_actual += 45 / 60
                    hh, mm = int(hora_actual), int((hora_actual % 1) * 60)
                    st.markdown(f"**{hh:02d}:{mm:02d}** - 🍽️ Almuerzo (45 min)")

        hh, mm = int(hora_actual), int((hora_actual % 1) * 60)
        st.markdown(f"**{hh:02d}:{mm:02d}** - 🏁 Regreso al hotel (**{ATRACTIVOS[hub]['nombre']}**) ✅")

        # Resumen
        st.markdown("### 📊 Resumen del Día")
        tiempo_visitas = len(destinos) * 90
        tiempo_almuerzo = 45 if len(destinos) >= 3 else 0
        total_minutos = costo_total + tiempo_visitas + tiempo_almuerzo

        col1, col2, col3 = st.columns(3)
        col1.metric("🚗 Traslado", f"{costo_total:.0f} min ({costo_total/60:.2f} h)")
        col2.metric("🏛️ Visitas", f"{tiempo_visitas:.0f} min ({len(destinos)*1.5:.1f} h)")
        col3.metric("⏱️ Total día", f"{total_minutos:.0f} min ({total_minutos/60:.2f} h)")

        # Galería
        st.markdown("### 🖼️ Galería de destinos del día")
        cols = st.columns(len(destinos))
        for col, nid in zip(cols, destinos):
            with col:
                mostrar_imagen(ATRACTIVOS[nid]["cod"], ATRACTIVOS[nid]["nombre"])

# ═══════════════════════════════════════════════════════════════════════════
# CAMINO MÍNIMO
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "🔗 Camino mínimo":
    st.title("🔗 Camino Mínimo entre Dos Nodos")

    opciones = {f"{d['cod']} — {d['nombre']}": nid for nid, d in sorted(ATRACTIVOS.items())}
    col1, col2 = st.columns(2)
    origen_label = col1.selectbox("Origen:", list(opciones.keys()), index=list(opciones.values()).index(15))
    destino_label = col2.selectbox("Destino:", list(opciones.keys()), index=0)
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

# ═══════════════════════════════════════════════════════════════════════════
# MATRICES
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "📊 Matrices":
    st.title("📊 Matrices de Caminos Mínimos")

    criterio = st.radio("Matriz:", ["distancia", "tiempo", "costo"], horizontal=True)
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

    st.dataframe(tabla, use_container_width=True, height=600, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# EXPORTAR EXCEL
# ═══════════════════════════════════════════════════════════════════════════

elif seccion == "⬇️ Exportar Excel":
    st.title("⬇️ Exportar Matrices a Excel")

    st.write("""
    Descarga el archivo Excel con:
    - 📊 Matrices de tiempo, distancia y costo (28×28)
    - 📋 Inventario de atractivos
    - 📅 7 itinerarios optimizados
    """)

    excel_bytes = generar_excel_bytes(matrices, G)

    st.download_button(
        label="⬇️ Descargar Matrices_Dijkstra_Cocle.xlsx",
        data=excel_bytes,
        file_name="Matrices_Dijkstra_Cocle_28Nodos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary"
    )

    st.success(f"✅ Archivo generado con {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas")
