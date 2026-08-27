"""
LÓGICA DE NEGOCIO - OPTIMIZACIÓN DE RUTAS TURÍSTICAS
Provincia de Coclé, Panamá
28 Atractivos Turísticos | Algoritmo de Dijkstra
"""

import heapq
from itertools import permutations
from io import BytesIO
import networkx as nx
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ═══════════════════════════════════════════════════════════════════════════
# 1. ATRACTIVOS TURÍSTICOS (28 NODOS)
# ═══════════════════════════════════════════════════════════════════════════

ATRACTIVOS = {
    # === PLAYAS (Costa Pacífica) ===
    1: {"nombre": "Playa Santa Clara", "cod": "PSC", "tipo": "Playa", "puntaje": 27, "distrito": "Antón"},
    2: {"nombre": "Playa Farallón", "cod": "PFA", "tipo": "Playa", "puntaje": 26, "distrito": "Antón"},
    3: {"nombre": "Playa El Salado", "cod": "PES", "tipo": "Playa", "puntaje": 21, "distrito": "Aguadulce"},
    4: {"nombre": "Playa Blanca", "cod": "PBL", "tipo": "Playa", "puntaje": 26, "distrito": "Antón"},
    5: {"nombre": "Playa Juan Hombrón", "cod": "PJH", "tipo": "Playa", "puntaje": 20, "distrito": "Antón"},
    26: {"nombre": "Playa La Hueca", "cod": "PLH", "tipo": "Playa", "puntaje": 22, "distrito": "Antón"},
    
    # === CULTURA E HISTORIA ===
    6: {"nombre": "Mercado Artesanía Valle Antón", "cod": "MAV", "tipo": "Cultural", "puntaje": 26, "distrito": "Antón"},
    8: {"nombre": "Museo Hermanos Arias Madrid", "cod": "MHA", "tipo": "Cultural/Hist.", "puntaje": 25, "distrito": "Penonomé"},
    11: {"nombre": "Museo Regional Stella Sierra", "cod": "MSS", "tipo": "Cultural/Hist.", "puntaje": 22, "distrito": "Aguadulce"},
    25: {"nombre": "Museo de la Sal", "cod": "MSA", "tipo": "Cultural", "puntaje": 21, "distrito": "Aguadulce"},
    12: {"nombre": "Iglesia San Juan Bautista", "cod": "ISJ", "tipo": "Histórico", "puntaje": 24, "distrito": "Penonomé"},
    20: {"nombre": "Parroquia Ntra. Sra. Candelaria", "cod": "PNC", "tipo": "Histórico", "puntaje": 21, "distrito": "La Pintada"},
    
    # === NATURALEZA Y PARQUES ===
    7: {"nombre": "Serpentario Maravillas Tropicales", "cod": "SMT", "tipo": "Naturaleza", "puntaje": 24, "distrito": "Antón"},
    9: {"nombre": "P.N. Omar Torrijos", "cod": "PNT", "tipo": "Parque Nacional", "puntaje": 22, "distrito": "Penonomé"},
    10: {"nombre": "Sitio Arqueológico El Caño", "cod": "SAC", "tipo": "Arqueológico", "puntaje": 26, "distrito": "Natá"},
    13: {"nombre": "El Chorro Las Yayas", "cod": "CLY", "tipo": "Cascada", "puntaje": 25, "distrito": "La Pintada"},
    14: {"nombre": "Balneario Las Mendozas", "cod": "BLM", "tipo": "Balneario", "puntaje": 21, "distrito": "Penonomé"},
    21: {"nombre": "Cerro Gaital", "cod": "CGA", "tipo": "Montaña", "puntaje": 27, "distrito": "Antón"},
    22: {"nombre": "Manglares de Aguadulce", "cod": "MAG", "tipo": "Naturaleza", "puntaje": 23, "distrito": "Aguadulce"},
    23: {"nombre": "Cerro El Valle", "cod": "CEV", "tipo": "Montaña", "puntaje": 24, "distrito": "Antón"},
    24: {"nombre": "Balneario El Copé", "cod": "BEC", "tipo": "Balneario", "puntaje": 22, "distrito": "La Pintada"},
    27: {"nombre": "Cerro La Cruz", "cod": "CLC", "tipo": "Montaña", "puntaje": 23, "distrito": "Penonomé"},
    28: {"nombre": "Mirador de Natá", "cod": "MIN", "tipo": "Mirador", "puntaje": 22, "distrito": "Natá"},
    
    # === CIUDADES / HUBS ===
    15: {"nombre": "Penonomé", "cod": "PEN", "tipo": "Hub/Ciudad", "puntaje": 28, "distrito": "Penonomé"},
    16: {"nombre": "Aguadulce", "cod": "AGU", "tipo": "Hub/Ciudad", "puntaje": 25, "distrito": "Aguadulce"},
    17: {"nombre": "Antón", "cod": "ANT", "tipo": "Hub/Ciudad", "puntaje": 23, "distrito": "Antón"},
    18: {"nombre": "La Pintada", "cod": "LAP", "tipo": "Hub/Ciudad", "puntaje": 22, "distrito": "La Pintada"},
    19: {"nombre": "Natá", "cod": "NAT", "tipo": "Hub/Ciudad", "puntaje": 23, "distrito": "Natá"},
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. ARISTAS - CONEXIONES VIALES (40 ARISTAS)
# ═══════════════════════════════════════════════════════════════════════════

ARISTAS = [
    # === CONEXIONES PRINCIPALES (Panamericana y rutas principales) ===
    (15, 17, 35.0, 35),   # Penonomé ↔ Antón
    (15, 16, 52.2, 48),   # Penonomé ↔ Aguadulce
    (15, 18, 26.0, 30),   # Penonomé ↔ La Pintada
    (15, 19, 67.0, 67),   # Penonomé ↔ Natá
    (15, 8, 2.5, 5),      # Penonomé ↔ Museo Hnos. Arias
    (15, 12, 2.0, 4),     # Penonomé ↔ Iglesia San Juan
    (15, 14, 3.0, 6),     # Penonomé ↔ Balneario Mendozas
    (15, 21, 42.6, 40),   # Penonomé ↔ Cerro Gaital
    (15, 10, 78.0, 55),   # Penonomé ↔ El Caño
    (19, 10, 8.0, 12),    # Natá ↔ El Caño
    (19, 16, 28.0, 32),   # Natá ↔ Aguadulce
    (19, 17, 32.0, 35),   # Natá ↔ Antón
    (16, 10, 26.8, 27),   # Aguadulce ↔ El Caño
    (16, 11, 5.0, 8),     # Aguadulce ↔ Museo Stella Sierra
    (16, 3, 8.5, 12),     # Aguadulce ↔ Playa El Salado
    (18, 9, 35.0, 50),    # La Pintada ↔ Omar Torrijos
    (18, 13, 14.0, 20),   # La Pintada ↔ El Chorro Las Yayas
    (18, 20, 0.5, 2),     # La Pintada ↔ Parroquia Candelaria
    (17, 1, 18.0, 20),    # Antón ↔ Playa Santa Clara
    (17, 2, 20.5, 22),    # Antón ↔ Playa Farallón
    (17, 4, 22.0, 24),    # Antón ↔ Playa Blanca
    (17, 5, 14.5, 16),    # Antón ↔ Playa Juan Hombrón
    (17, 6, 22.0, 25),    # Antón ↔ Mercado Artesanía
    (17, 7, 22.5, 26),    # Antón ↔ Serpentario
    (17, 21, 10.0, 15),   # Antón ↔ Cerro Gaital
    (1, 2, 6.8, 11),      # P. Santa Clara ↔ P. Farallón
    (2, 4, 2.5, 5),       # P. Farallón ↔ P. Blanca
    (4, 5, 9.5, 12),      # P. Blanca ↔ P. Juan Hombrón
    (1, 5, 17.0, 20),     # P. Santa Clara ↔ P. Juan Hombrón
    (6, 7, 0.5, 2),       # Mercado ↔ Serpentario
    (6, 21, 38.0, 45),    # Mercado ↔ Cerro Gaital
    (9, 13, 12.0, 18),    # Omar Torrijos ↔ El Chorro
    (9, 10, 39.7, 65),    # Omar Torrijos ↔ El Caño
    
    # === NUEVAS ARISTAS (Nodos 22-28) ===
    # Aguadulce y alrededores
    (16, 22, 3.5, 5),     # Aguadulce ↔ Manglares
    (16, 25, 2.0, 4),     # Aguadulce ↔ Museo de la Sal
    (22, 25, 1.5, 3),     # Manglares ↔ Museo de la Sal
    
    # Antón y alrededores
    (17, 23, 8.0, 12),    # Antón ↔ Cerro El Valle
    (17, 26, 15.0, 18),   # Antón ↔ Playa La Hueca
    (23, 26, 12.0, 15),   # Cerro El Valle ↔ Playa La Hueca
    
    # La Pintada y alrededores
    (18, 24, 12.0, 18),   # La Pintada ↔ Balneario El Copé
    (24, 9, 18.0, 25),    # El Copé ↔ Omar Torrijos
    
    # Penonomé y alrededores
    (15, 27, 3.0, 6),     # Penonomé ↔ Cerro La Cruz
    
    # Natá y alrededores
    (19, 28, 2.5, 5),     # Natá ↔ Mirador de Natá
    (28, 10, 6.0, 10),    # Mirador ↔ El Caño
]

# ═══════════════════════════════════════════════════════════════════════════
# 3. CONFIGURACIÓN DE DÍAS (RUTAS CIRCULARES MEJORADAS)
# ═══════════════════════════════════════════════════════════════════════════

DIAS_CONFIG = {
    1: {
        "destinos": [1, 2, 4, 5],   # 4 playas
        "hub": 17,                  # Antón
        "zona": "Ruta Costera Norte – Playas de Antón",
        "color": "#185FA5",
        "descripcion": "Recorrido por las 4 playas principales del distrito de Antón"
    },
    2: {
        "destinos": [6, 7, 23, 21], # Mercado, Serpentario, Cerro El Valle, Cerro Gaital
        "hub": 17,                  # Antón
        "zona": "Valle de Antón y Montañas",
        "color": "#854F0B",
        "descripcion": "Circuito cultural y de montaña en el Valle de Antón"
    },
    3: {
        "destinos": [8, 12, 27, 14], # Museo, Iglesia, Cerro La Cruz, Balneario
        "hub": 15,                   # Penonomé
        "zona": "Penonomé Cultural y Natural",
        "color": "#0F6E56",
        "descripcion": "Historia, cultura y naturaleza en la ciudad de Penonomé"
    },
    4: {
        "destinos": [13, 24, 9, 20], # El Chorro, El Copé, Omar Torrijos, Candelaria
        "hub": 18,                   # La Pintada
        "zona": "Circuito Montañoso – Cascadas y Parque",
        "color": "#534AB7",
        "descripcion": "Aventura en cascadas, balneario y parque nacional"
    },
    5: {
        "destinos": [3, 25, 22, 11, 16], # Playa, Museo Sal, Manglares, Stella, Aguadulce
        "hub": 16,                       # Aguadulce
        "zona": "Aguadulce – Costa Sur y Cultura",
        "color": "#993C1D",
        "descripcion": "Playas, manglares, museos y ciudad de Aguadulce"
    },
    6: {
        "destinos": [28, 10, 19],    # Mirador, El Caño, Natá
        "hub": 19,                   # Natá
        "zona": "Zona Arqueológica – El Caño y Natá",
        "color": "#0F6E56",
        "descripcion": "Sitio arqueológico, mirador y ciudad histórica de Natá"
    },
    7: {
        "destinos": [26, 5, 17, 19, 28], # Playa Hueca, Juan Hombrón, Antón, Natá, Mirador
        "hub": 15,                       # Penonomé
        "zona": "Circuito Integrador – Costa, Hubs y Miradores",
        "color": "#5B4A00",
        "descripcion": "Recorrido por la costa, ciudades históricas y miradores"
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# 4. COLORES Y POSICIONES
# ═══════════════════════════════════════════════════════════════════════════

COLORES_TIPO = {
    "Hub/Ciudad": "#1D9E75",
    "Playa": "#378ADD",
    "Cultural": "#BA7517",
    "Cultural/Hist.": "#BA7517",
    "Histórico": "#BA7517",
    "Naturaleza": "#7F77DD",
    "Parque Nacional": "#7F77DD",
    "Cascada": "#7F77DD",
    "Balneario": "#7F77DD",
    "Arqueológico": "#D85A30",
    "Montaña": "#7F77DD",
    "Mirador": "#FF6B35",
}

POSICIONES = {
    15: (0.50, 0.50), 17: (0.74, 0.42), 16: (0.22, 0.20), 18: (0.36, 0.74),
    19: (0.40, 0.26), 1: (0.94, 0.62), 2: (0.94, 0.50), 3: (0.10, 0.10),
    4: (0.92, 0.38), 5: (0.84, 0.26), 6: (0.82, 0.68), 7: (0.94, 0.74),
    8: (0.44, 0.44), 9: (0.18, 0.82), 10: (0.30, 0.30), 11: (0.10, 0.24),
    12: (0.58, 0.44), 13: (0.20, 0.90), 14: (0.50, 0.36), 20: (0.28, 0.84),
    21: (0.80, 0.82), 22: (0.15, 0.15), 23: (0.88, 0.78), 24: (0.28, 0.78),
    25: (0.18, 0.18), 26: (0.90, 0.20), 27: (0.56, 0.56), 28: (0.34, 0.28),
}

# ═══════════════════════════════════════════════════════════════════════════
# 5. ALGORITMO DE DIJKSTRA
# ═══════════════════════════════════════════════════════════════════════════

def construir_grafo():
    G = nx.Graph()
    for nid, data in ATRACTIVOS.items():
        G.add_node(nid, **data)
    for u, v, dist, tiempo in ARISTAS:
        costo = round(dist * 0.15, 2)
        G.add_edge(u, v, distancia=dist, tiempo=tiempo, costo=costo)
    return G


def dijkstra(G, origen, criterio):
    INF = float('inf')
    dist = {n: INF for n in G.nodes()}
    prev = {n: None for n in G.nodes()}
    dist[origen] = 0
    heap = [(0, origen)]
    visitados = set()

    while heap:
        d_u, u = heapq.heappop(heap)
        if u in visitados:
            continue
        visitados.add(u)
        for v in G.neighbors(u):
            peso = G[u][v][criterio]
            alt = dist[u] + peso
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))
    return dist, prev


def reconstruir_camino(prev, origen, destino):
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = prev[actual]
    camino.reverse()
    return camino if camino and camino[0] == origen else []


def calcular_todas_matrices(G):
    nodos = sorted(G.nodes())
    matrices, caminos = {}, {}
    for criterio in ["distancia", "tiempo", "costo"]:
        mat, cam = {}, {}
        for origen in nodos:
            dist_min, prev = dijkstra(G, origen, criterio)
            mat[origen] = {d: round(dist_min[d], 2) if dist_min[d] != float('inf') else None
                          for d in nodos}
            cam[origen] = {d: reconstruir_camino(prev, origen, d) for d in nodos}
        matrices[criterio] = mat
        caminos[criterio] = cam
    return matrices, caminos


def ruta_optima_dia(destinos, matrices, hub=None, criterio="tiempo"):
    if hub is None:
        hub = 15
    mat = matrices[criterio]
    mejor_costo = float('inf')
    mejor_orden = None

    for perm in permutations(destinos):
        secuencia = [hub] + list(perm) + [hub]
        total, valida = 0, True
        for i in range(len(secuencia) - 1):
            c = mat[secuencia[i]][secuencia[i + 1]]
            if c is None or c == float('inf'):
                valida = False
                break
            total += c
        if valida and total < mejor_costo:
            mejor_costo = total
            mejor_orden = list(perm)

    return mejor_orden, mejor_costo


def diagnosticar_grafo():
    G = construir_grafo()
    matrices, _ = calcular_todas_matrices(G)
    resultados = {
        "total_nodos": G.number_of_nodes(),
        "total_aristas": G.number_of_edges(),
        "arista_15_17": G.has_edge(15, 17),
        "distancia_15_17": matrices["distancia"][15][17],
        "tiempo_15_17": matrices["tiempo"][15][17],
    }
    return resultados


# ═══════════════════════════════════════════════════════════════════════════
# 6. EXPORTACIÓN A EXCEL
# ═══════════════════════════════════════════════════════════════════════════

def generar_excel_bytes(matrices, G):
    wb = Workbook()
    wb.remove(wb.active)

    AZUL, VERDE, NARAN, GRIS, BLANC = "1F4E79", "1D9E75", "C55A11", "F2F2F2", "FFFFFF"

    def celda(ws, fila, col, valor, bold=False, bg=None, color="000000", alinear="center", size=10):
        c = ws.cell(row=fila, column=col, value=valor)
        c.font = Font(name="Arial", bold=bold, color=color, size=size)
        if bg:
            c.fill = PatternFill("solid", fgColor=bg)
        c.alignment = Alignment(horizontal=alinear, vertical="center", wrap_text=True)
        lado = Side(style="thin", color="AAAAAA")
        c.border = Border(left=lado, right=lado, top=lado, bottom=lado)
        return c

    config = [
        ("Matriz_Tiempo", "tiempo", "MATRIZ DIJKSTRA – TIEMPO MÍNIMO (minutos)", AZUL),
        ("Matriz_Distancia", "distancia", "MATRIZ DIJKSTRA – DISTANCIA MÍNIMA (km)", VERDE),
        ("Matriz_Costo", "costo", "MATRIZ DIJKSTRA – COSTO MÍNIMO (USD)", NARAN),
    ]

    nodos = sorted(G.nodes())
    for sheet, criterio, titulo, color in config:
        ws = wb.create_sheet(sheet)
        ws.sheet_view.showGridLines = False
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(nodos)+1)
        c = ws.cell(row=1, column=1, value=titulo)
        c.font = Font(name="Arial", bold=True, color=BLANC, size=12)
        c.fill = PatternFill("solid", fgColor=color)
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 28

        celda(ws, 2, 1, "O \\ D", bold=True, bg=GRIS, size=8)
        for j, n in enumerate(nodos, 2):
            celda(ws, 2, j, f"{n}\n{ATRACTIVOS[n]['cod']}", bold=True, bg=GRIS, size=7)
            ws.column_dimensions[get_column_letter(j)].width = 9
        ws.column_dimensions["A"].width = 12
        ws.row_dimensions[2].height = 28

        mat = matrices[criterio]
        for i, origen in enumerate(nodos, 3):
            celda(ws, i, 1, f"{origen} {ATRACTIVOS[origen]['cod']}", bold=True, bg=GRIS, size=8)
            ws.row_dimensions[i].height = 18
            for j, destino in enumerate(nodos, 2):
                if origen == destino:
                    celda(ws, i, j, 0, bg="D9D9D9", size=8)
                else:
                    val = mat[origen][destino]
                    if val is None:
                        celda(ws, i, j, "∞", bg="FFE2CC", size=8)
                    else:
                        fmt = f"${val:.2f}" if criterio == "costo" else round(val, 1)
                        bg = GRIS if i % 2 == 0 else BLANC
                        celda(ws, i, j, fmt, bg=bg, size=8)
        ws.freeze_panes = "B3"

    # Inventario
    ws_inv = wb.create_sheet("Inventario_Atractivos")
    ws_inv.sheet_view.showGridLines = False
    ws_inv.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)
    c = ws_inv.cell(row=1, column=1, value="INVENTARIO DE ATRACTIVOS TURÍSTICOS – COCLÉ, PANAMÁ")
    c.font = Font(name="Arial", bold=True, color=BLANC, size=12)
    c.fill = PatternFill("solid", fgColor=AZUL)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws_inv.row_dimensions[1].height = 26

    hdrs = ["ID", "Código", "Nombre", "Tipo", "Distrito", "Puntaje", "Grado", "Tipo Hub"]
    for j, h in enumerate(hdrs, 1):
        celda(ws_inv, 2, j, h, bold=True, bg="BDD7EE", size=10)

    for i, (nid, data) in enumerate(ATRACTIVOS.items(), 3):
        bg = GRIS if i % 2 == 0 else BLANC
        grado = G.degree(nid)
        es_hub = "✔" if data["tipo"] == "Hub/Ciudad" else ""
        for j, val in enumerate([nid, data["cod"], data["nombre"], data["tipo"],
                                  data["distrito"], data["puntaje"], grado, es_hub], 1):
            al = "left" if j == 3 else "center"
            celda(ws_inv, i, j, val, bg=bg, alinear=al, size=10)

    anchos = [5, 7, 38, 20, 14, 9, 8, 9]
    for j, w in enumerate(anchos, 1):
        ws_inv.column_dimensions[get_column_letter(j)].width = w

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
