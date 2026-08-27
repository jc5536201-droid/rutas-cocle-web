"""
TESIS: OPTIMIZACIÓN DE RUTAS TURÍSTICAS EN COCLÉ, PANAMÁ
Aplicación web con Streamlit
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# Importar la lógica de negocio
from logica_dijkstra import (
    ATRACTIVOS,
    DIAS_CONFIG,
    POSICIONES,
    construir_grafo,
    calcular_todas_matrices,
    ruta_circular_optima,
    diagnosticar_grafo,
    generar_excel_bytes
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE LA PÁGINA
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Rutas Turísticas Coclé",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏝️ Optimización de Rutas Turísticas - Coclé, Panamá")
st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("📋 Información")
    st.markdown("""
    **Sistema de optimización de rutas turísticas** utilizando el algoritmo de Dijkstra.
    
    **Características:**
    - 7 días de recorrido
    - Rutas circulares (sale y regresa al hotel)
    - Optimización por tiempo
    - Visualización interactiva
    """)
    
    st.markdown("---")
    
    # 🔍 DIAGNÓSTICO DEL GRAFO
    st.markdown("### 🔍 Diagnóstico del Grafo")
    if st.button("🔍 Verificar Grafo", type="primary"):
        with st.spinner("🔍 Diagnóstico en progreso..."):
            diag = diagnosticar_grafo()
            
            st.markdown("#### 📊 Resultados")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Nodos", diag["total_nodos"])
            with col2:
                st.metric("Aristas", diag["total_aristas"])
            
            # Verificar arista directa 15-17
            st.markdown("#### 🛣️ Arista 15 (Penonomé) → 17 (Antón)")
            
            if diag["arista_directa"]:
                st.success(f"✅ Arista directa existe")
                st.write(f"   📏 Distancia: {diag['distancia_directa']} km")
                st.write(f"   ⏱ Tiempo: {diag['tiempo_directo']} min")
            else:
                st.error("❌ ¡Arista directa NO existe!")
            
            # Comparar con Dijkstra
            st.markdown("#### 🔄 Comparación con Dijkstra")
            st.write(f"**Distancia Dijkstra:** {diag['dijkstra_distancia']} km")
            st.write(f"**Tiempo Dijkstra:** {diag['dijkstra_tiempo']} min")
            
            if diag["estado"] == "✅ CORRECTO":
                st.success("✅ Dijkstra está usando la ruta directa correcta")
            else:
                st.error(diag["estado"])
                
                # Mostrar rutas alternativas
                if diag["rutas_alternativas"]:
                    st.markdown("#### 🚧 Rutas Alternativas Encontradas")
                    for alt in diag["rutas_alternativas"][:3]:
                        ruta_str = " → ".join(str(n) for n in alt["ruta"])
                        st.write(f"• {ruta_str}")
                        st.write(f"  {alt['distancia']} km, {alt['tiempo']} min")
    
    st.markdown("---")
    st.markdown("**📊 Estadísticas:**")
    st.markdown(f"- **Atractivos:** {len(ATRACTIVOS)}")
    st.markdown(f"- **Días:** 7")
    
    st.markdown("---")
    st.markdown("**👨‍💻 Tesista:** [Tu nombre]")

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE VISUALIZACIÓN CON MATPLOTLIB
# ═══════════════════════════════════════════════════════════════════════════

def dibujar_mapa(ruta, color, titulo=""):
    """Dibuja el mapa de la ruta usando Matplotlib."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Dibujar aristas de la ruta
    for i in range(len(ruta)-1):
        x0, y0 = POSICIONES[ruta[i]]
        x1, y1 = POSICIONES[ruta[i+1]]
        
        # Color especial para la arista 15-17
        es_especial = (ruta[i] == 15 and ruta[i+1] == 17) or (ruta[i] == 17 and ruta[i+1] == 15)
        color_linea = '#FF0000' if es_especial else color
        width = 4 if es_especial else 2
        
        ax.plot([x0, x1], [y0, y1], color=color_linea, linewidth=width, alpha=0.8)
    
    # Dibujar nodos
    for nid in ruta:
        x, y = POSICIONES[nid]
        
        # Tamaño y color especial para 15 y 17
        es_especial = nid in [15, 17]
        size = 300 if es_especial else 200
        marker = 's' if es_especial else 'o'
        color_nodo = '#FF0000' if es_especial else color
        
        ax.scatter(x, y, s=size, c=color_nodo, marker=marker, 
                  edgecolors='white', linewidth=2, zorder=5)
        
        # Etiqueta
        ax.annotate(ATRACTIVOS[nid]['cod'], (x, y), 
                   xytext=(0, 10), textcoords='offset points',
                   ha='center', va='bottom', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect('equal')
    ax.axis('off')
    
    if titulo:
        ax.set_title(titulo, fontsize=14, fontweight='bold')
    
    return fig

# ═══════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Plan Semanal",
    "🗺️ Rutas por Día",
    "📊 Matrices Dijkstra",
    "📁 Exportar Datos"
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: PLAN SEMANAL
# ═══════════════════════════════════════════════════════════════════════════

with tab1:
    st.header("📅 Plan de Viaje Semanal")
    st.markdown("Rutas circulares optimizadas para 7 días")
    
    # Construir grafo y calcular matrices
    with st.spinner("⏳ Calculando rutas óptimas..."):
        G = construir_grafo()
        matrices, _ = calcular_todas_matrices(G)
        
        # Calcular todas las rutas
        resultados = {}
        for dia, config in DIAS_CONFIG.items():
            orden, costo, detalle = ruta_circular_optima(
                config["destinos"], 
                config["hub"], 
                matrices,
                "tiempo"
            )
            if orden:
                ruta = [config["hub"]] + orden + [config["hub"]]
                resultados[dia] = {
                    "ruta": ruta,
                    "tiempo": costo,
                    "destinos": len(config["destinos"]),
                    "detalle": detalle
                }
    
    # Mostrar resumen en columnas
    cols = st.columns(4)
    for i, (dia, data) in enumerate(resultados.items()):
        with cols[i % 4]:
            config = DIAS_CONFIG[dia]
            st.markdown(f"""
            <div style="
                background-color: {config['color']}22;
                padding: 15px;
                border-radius: 10px;
                border-left: 5px solid {config['color']};
                margin-bottom: 10px;
            ">
                <h4 style="margin: 0;">Día {dia}</h4>
                <p style="margin: 5px 0; font-size: 0.9em;">{config['zona']}</p>
                <p style="margin: 5px 0; font-size: 0.8em;">
                    ⏱ {data['tiempo']:.0f} min | 🏠 {ATRACTIVOS[config['hub']]['cod']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tabla detallada
    st.markdown("### 📋 Detalle de Rutas")
    
    df_data = []
    for dia, data in resultados.items():
        config = DIAS_CONFIG[dia]
        ruta_str = " → ".join([f"{n}({ATRACTIVOS[n]['cod']})" for n in data["ruta"]])
        
        # Calcular distancia total
        dist_total = 0
        for i in range(len(data["ruta"])-1):
            dist_total += matrices["distancia"][data["ruta"][i]][data["ruta"][i+1]]
        
        df_data.append({
            "Día": dia,
            "Zona": config["zona"],
            "Hotel": f"{config['hub']} ({ATRACTIVOS[config['hub']]['cod']})",
            "Atractivos": len(data["destinos"]),
            "Ruta": ruta_str,
            "Tiempo (min)": round(data["tiempo"], 1),
            "Distancia (km)": round(dist_total, 1)
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: RUTAS POR DÍA
# ═══════════════════════════════════════════════════════════════════════════

with tab2:
    st.header("🗺️ Visualización de Rutas por Día")
    
    # Selector de día
    dia_seleccionado = st.selectbox(
        "Selecciona un día:",
        options=list(DIAS_CONFIG.keys()),
        format_func=lambda x: f"Día {x} - {DIAS_CONFIG[x]['zona']}"
    )
    
    if dia_seleccionado:
        config = DIAS_CONFIG[dia_seleccionado]
        
        # Obtener ruta optimizada
        G = construir_grafo()
        matrices, _ = calcular_todas_matrices(G)
        orden, costo, detalle = ruta_circular_optima(
            config["destinos"], 
            config["hub"], 
            matrices,
            "tiempo"
        )
        
        if orden:
            ruta = [config["hub"]] + orden + [config["hub"]]
            
            # Mostrar información del día
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🏠 Hotel Base", f"{ATRACTIVOS[config['hub']]['nombre']}")
            with col2:
                st.metric("🎯 Atractivos", len(config["destinos"]))
            with col3:
                st.metric("⏱ Tiempo Total", f"{costo:.1f} min")
            
            # Mostrar ruta
            st.markdown("### 🚗 Ruta Circular Óptima")
            ruta_str = " → ".join([f"**{ATRACTIVOS[n]['nombre']}**" for n in ruta])
            st.markdown(f"{ruta_str}")
            
            # Tabla de tramos
            st.markdown("### 📋 Detalle de Tramos")
            tramos_data = []
            for i in range(len(ruta)-1):
                origen = ruta[i]
                destino = ruta[i+1]
                
                tramos_data.append({
                    "Tramo": f"{i+1}",
                    "Origen": f"{origen} ({ATRACTIVOS[origen]['cod']})",
                    "Destino": f"{destino} ({ATRACTIVOS[destino]['cod']})",
                    "Tiempo (min)": matrices["tiempo"][origen][destino],
                    "Distancia (km)": matrices["distancia"][origen][destino]
                })
            
            st.dataframe(pd.DataFrame(tramos_data), use_container_width=True, hide_index=True)
            
            # 🗺️ MAPA CON MATPLOTLIB
            st.markdown("### 🗺️ Mapa de la Ruta")
            
            titulo = f"Día {dia_seleccionado}: {config['zona']}"
            fig = dibujar_mapa(ruta, config['color'], titulo)
            st.pyplot(fig)
            
            st.info("""
            📖 **Leyenda del mapa:**
            - 🔴 **Línea roja:** Arista directa 15-17 (Penonomé → Antón)
            - ⬛ **Cuadrado rojo:** Nodos 15 (Penonomé) y 17 (Antón)
            - 🔵 **Círculo:** Otros atractivos
            """)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: MATRICES DIJKSTRA
# ═══════════════════════════════════════════════════════════════════════════

with tab3:
    st.header("📊 Matrices de Dijkstra")
    
    # Selector de criterio
    criterio = st.selectbox(
        "Selecciona el criterio:",
        options=["tiempo", "distancia", "costo"],
        format_func=lambda x: {
            "tiempo": "⏱ Tiempo (minutos)",
            "distancia": "📏 Distancia (km)",
            "costo": "💰 Costo (USD)"
        }[x]
    )
    
    G = construir_grafo()
    matrices, _ = calcular_todas_matrices(G)
    
    # Convertir matriz a DataFrame
    mat = matrices[criterio]
    nodos = sorted(G.nodes())
    
    df_mat = pd.DataFrame(index=nodos, columns=nodos)
    for i in nodos:
        for j in nodos:
            df_mat.loc[i, j] = mat[i][j] if mat[i][j] is not None else "∞"
    
    st.dataframe(
        df_mat,
        use_container_width=True,
        height=600
    )
    
    # Mostrar valores clave
    st.markdown("### 🔍 Valores Clave")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "15 → 17 (Penonomé → Antón)",
            f"{matrices['distancia'][15][17]} km",
            delta=f"{matrices['tiempo'][15][17]} min"
        )
    
    with col2:
        es_correcto = matrices['distancia'][15][17] == 22.6
        st.metric(
            "¿Usa ruta directa?",
            "✅" if es_correcto else "❌"
        )
    
    with col3:
        st.metric(
            "Costo 15 → 17",
            f"${matrices['costo'][15][17]:.2f}"
        )
    
    st.info("""
    **📖 Leyenda:**
    - Los valores representan la distancia mínima entre cada par de nodos
    - ∞ significa que no hay conexión posible
    - La diagonal principal siempre es 0 (distancia a sí mismo)
    - **15 → 17 DEBE SER 22.6 km** (ruta directa)
    """)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4: EXPORTAR DATOS
# ═══════════════════════════════════════════════════════════════════════════

with tab4:
    st.header("📁 Exportar Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Exportar a CSV")
        st.markdown("Descarga las rutas en formato CSV")
        
        # Preparar datos para CSV
        G = construir_grafo()
        matrices, _ = calcular_todas_matrices(G)
        
        csv_data = []
        for dia, config in DIAS_CONFIG.items():
            orden, costo, _ = ruta_circular_optima(
                config["destinos"], 
                config["hub"], 
                matrices,
                "tiempo"
            )
            if orden:
                ruta = [config["hub"]] + orden + [config["hub"]]
                ruta_str = " → ".join(str(n) for n in ruta)
                
                dist_total = 0
                for i in range(len(ruta)-1):
                    dist_total += matrices["distancia"][ruta[i]][ruta[i+1]]
                
                csv_data.append({
                    "Día": dia,
                    "Zona": config["zona"],
                    "Hub": config["hub"],
                    "Ruta": ruta_str,
                    "Tiempo (min)": round(costo, 1),
                    "Distancia (km)": round(dist_total, 1)
                })
        
        df_csv = pd.DataFrame(csv_data)
        
        csv = df_csv.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name="rutas_turisticas.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.markdown("### 📊 Exportar a Excel")
        st.markdown("Descarga todas las matrices y rutas en un archivo Excel")
        
        if st.button("📥 Generar Excel", type="primary", use_container_width=True):
            with st.spinner("⏳ Generando archivo Excel..."):
                try:
                    G = construir_grafo()
                    matrices, _ = calcular_todas_matrices(G)
                    
                    # Calcular resultados
                    resultados = {}
                    for dia, config in DIAS_CONFIG.items():
                        orden, costo, _ = ruta_circular_optima(
                            config["destinos"], 
                            config["hub"], 
                            matrices,
                            "tiempo"
                        )
                        if orden:
                            ruta = [config["hub"]] + orden + [config["hub"]]
                            resultados[dia] = {
                                "ruta": ruta,
                                "tiempo": costo,
                                "destinos": len(config["destinos"])
                            }
                    
                    # Generar Excel
                    excel_bytes = generar_excel_bytes(matrices, G, resultados)
                    
                    st.download_button(
                        label="📥 Descargar Excel",
                        data=excel_bytes,
                        file_name="rutas_turisticas_completas.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.success("✅ Excel generado exitosamente!")
                    
                except Exception as e:
                    st.error(f"❌ Error al generar Excel: {e}")
    
    st.markdown("---")
    st.caption("📋 Los datos incluyen: Día, Zona, Hub, Ruta optimizada, Tiempo y Distancia")

st.markdown("---")
st.caption("🏝️ Sistema de Optimización de Rutas Turísticas - Coclé, Panamá | Tesis de Grado")
