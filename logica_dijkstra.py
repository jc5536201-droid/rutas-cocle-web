"""
Lógica de negocio: grafo, Dijkstra, matrices y export a Excel.
Esta capa NO sabe nada de Streamlit — es la misma lógica
que ya validaste en la versión de consola de tu tesis.
"""

import heapq
from itertools import permutations
from io import BytesIO

import networkx as nx
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ═══════════════════════════════════════════════════════════════════════════
# 1. DATOS DEL SISTEMA TURÍSTICO
# ═══════════════════════════════════════════════════════════════════════════

ATRACTIVOS = {
    1:  {"nombre": "Playa Santa Clara",               "cod": "PSC", "tipo": "Playa",            "puntaje": 27, "distrito": "Antón"},
    2:  {"nombre": "Playa Farallón",                  "cod": "PFA", "tipo": "Playa",            "puntaje": 26, "distrito": "Antón"},
    3:  {"nombre": "Playa El Salado",                 "cod": "PES", "tipo": "Playa",            "puntaje": 21, "distrito": "Aguadulce"},
    4:  {"nombre": "Playa Blanca",                    "cod": "PBL", "tipo": "Playa",            "puntaje": 26, "distrito": "Antón"},
    5:  {"nombre": "Playa Juan Hombrón",              "cod": "PJH", "tipo": "Playa",            "puntaje": 20, "distrito": "Antón"},
    6:  {"nombre": "Mercado Artesanía Valle Antón",   "cod": "MAV", "tipo": "Cultural",         "puntaje": 26, "distrito": "Antón"},
    7:  {"nombre": "Serpentario Maravillas Tropicales","cod": "SMT", "tipo": "Naturaleza",       "puntaje": 24, "distrito": "Antón"},
    8:  {"nombre": "Museo Hermanos Arias Madrid",     "cod": "MHA", "tipo": "Cultural/Hist.",   "puntaje": 25, "distrito": "Penonomé"},
    9:  {"nombre": "P.N. Omar Torrijos",              "cod": "PNT", "tipo": "Parque Nacional",  "puntaje": 22, "distrito": "Penonomé"},
    10: {"nombre": "Sitio Arqueológico El Caño",      "cod": "SAC", "tipo": "Arqueológico",     "puntaje": 26, "distrito": "Natá"},
    11: {"nombre": "Museo Regional Stella Sierra",    "cod": "MSS", "tipo": "Cultural/Hist.",   "puntaje": 22, "distrito": "Aguadulce"},
    12: {"nombre": "Iglesia San Juan Bautista",       "cod": "ISJ", "tipo": "Histórico",        "puntaje": 24, "distrito": "Penonomé"},
    13: {"nombre": "El Chorro Las Yayas",             "cod": "CLY", "tipo": "Cascada",          "puntaje": 25, "distrito": "La Pintada"},
    14: {"nombre": "Balneario Las Mendozas",          "cod": "BLM", "tipo": "Balneario",        "puntaje": 21, "distrito": "Penonomé"},
    15: {"nombre": "Penonomé",                        "cod": "PEN", "tipo": "Hub/Ciudad",       "puntaje": 28, "distrito": "Penonomé"},
    16: {"nombre": "Aguadulce",                       "cod": "AGU", "tipo": "Hub/Ciudad",       "puntaje": 25, "distrito": "Aguadulce"},
    17: {"nombre": "Antón",                           "cod": "ANT", "tipo": "Hub/Ciudad",       "puntaje": 23, "distrito": "Antón"},
    18: {"nombre": "La Pintada",                      "cod": "LAP", "tipo": "Hub/Ciudad",       "puntaje": 22, "distrito": "La Pintada"},
    19: {"nombre": "Natá",                            "cod": "NAT", "tipo": "Hub/Ciudad",       "puntaje": 23, "distrito": "Natá"},
    20: {"nombre": "Parroquia Ntra. Sra. Candelaria", "cod": "PNC", "tipo": "Histórico",        "puntaje": 21, "distrito": "La Pintada"},
    21: {"nombre": "Cerro Gaital",                    "cod": "CGA", "tipo": "Montaña",          "puntaje": 27, "distrito": "Antón"},
}

# Distancias (km) y tiempos (min) medidos manualmente en Google Maps
ARISTAS_RAW = [
    (15, 17,  22.6,  25),  # ⭐ Penonomé → Antón (22.6 km)
    (15, 10,  29.8,  31),
    (15, 16,  50.2,  48),
    (15, 18,  18.4,  24),
    (15,  8,   4.4,   8),
    (15, 12,   4.6,   9),
    (15, 14,   4.6,   9),
    (15, 21,  42.9,  77),
    (17,  1,  23.1,  25),
    (17,  2,  21.4,  25),
    (17,  4,  19.8,  22),
    (17,  5,  18.0,  24),
    (17,  6,  37.6,  59),
    (17,  7,  39.8,  63),
    (17, 21,  40.5,  65),
    ( 1,  2,   6.8,  11),
    ( 2,  4,   8.4,  12),
    ( 4,  5,  24.0,  29),
    ( 1,  5,  27.3,  32),
    ( 6,  7,   2.2,   5),
    ( 6, 21,   2.9,   7),
    (19, 10,  28.7,  37),
    (19, 17,  66.0,  65),
    (19, 16,  19.4,  31),
    (16, 10,  26.8,  27),
    (16, 11,   2.8,   6),
    (16,  3,   2.6,   7),
    (18, 13,  34.2,  54),
    (18, 20,   0.1,   1),
    (18,  9,  41.3,  88),
    ( 9, 13,   7.1,  34),
    ( 9, 10,  44.7,  85),
]

# Aristas adicionales para completar conexiones
ARISTAS_ADICIONALES = [
    (7, 21, 2.5, 5),      # Valle de Antón
    (8, 12, 0.5, 2),      # Penonomé
    (8, 14, 1.0, 3),
    (12, 14, 0.8, 2),
    (13, 20, 0.3, 1),     # La Pintada
    (9, 20, 8.0, 15),
    (11, 3, 1.5, 4),      # Aguadulce
    (17, 18, 35.0, 40),   # Circuito Hubs
    (18, 19, 25.0, 30),
]

# Combinar todas las aristas
ARISTAS = ARISTAS_RAW + ARISTAS_ADICIONALES

# Configuración de días (7 días - rutas circulares)
DIAS_CONFIG = {
    1: {"destinos": [1, 2, 4, 5], "hub": 17, "zona": "Playas de Antón", "color": "#185FA5"},
    2: {"destinos": [6, 7, 21], "hub": 17, "zona": "Valle de Antón", "color": "#854F0B"},
    3: {"destinos": [8, 12, 14], "hub": 15, "zona": "Penonomé Histórico", "color": "#0F6E56"},
    4: {"destinos": [13, 20, 9], "hub": 18, "zona": "Circuito Montañoso", "color": "#534AB7"},
    5: {"destinos": [10, 19], "hub": 19, "zona": "El Caño y Natá", "color": "#993C1D"},
    6: {"destinos": [3, 11], "hub": 16, "zona": "Aguadulce", "color": "#0F6E56"},
    7: {"destinos": [17, 18, 19], "hub": 15, "zona": "Circuito Hubs", "color": "#5B4A00"},
}

COLORES_TIPO = {
    "Hub/Ciudad":      "#1D9E75",
    "Playa":           "#378ADD",
    "Cultural":        "#BA7517",
    "Cultural/Hist.":  "#BA7517",
    "Histórico":       "#BA7517",
    "Naturaleza":      "#7F77DD",
    "Parque Nacional": "#7F77DD",
    "Cascada":         "#7F77DD",
    "Balneario":       "#7F77DD",
    "Arqueológico":    "#D85A30",
    "Montaña":         "#7F77DD",
}

POSICIONES = {
    15: (0.50, 0.50), 17: (0.74, 0.42), 16: (0.22, 0.20), 18: (0.36, 0.74),
    19: (0.40, 0.26),  1: (0.94, 0.62),  2: (0.94, 0.50),  3: (0.10, 0.10),
     4: (0.92, 0.38),  5: (0.84, 0.26),  6: (0.82, 0.68),  7: (0.94, 0.74),
     8: (0.44, 0.44),  9: (0.18, 0.82), 10: (0.30, 0.30), 11: (0.10, 0.24),
    12: (0.58, 0.44), 13: (0.20, 0.90), 14: (0.50, 0.36), 20: (0.28, 0.84),
    21: (0.80, 0.82),
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. GRAFO Y DIJKSTRA
# ═══════════════════════════════════════════════════════════════════════════

def construir_grafo():
    """Construye el grafo con todos los atractivos y aristas."""
    G = nx.Graph()
    for nid, data in ATRACTIVOS.items():
        G.add_node(nid, **data)
    
    # Agregar todas las aristas
    for u, v, dist, tiempo in ARISTAS:
        costo = round(dist * 0.15, 2)
        G.add_edge(u, v, distancia=dist, tiempo=tiempo, costo=costo)
    
    # FORZAR arista directa 15-17 (por si acaso)
    if not G.has_edge(15, 17):
        G.add_edge(15, 17, distancia=22.6, tiempo=25, costo=3.39)
    
    return G


def dijkstra(G, origen, criterio):
    """Algoritmo de Dijkstra para encontrar las rutas más cortas."""
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
    """Reconstruye el camino más corto desde origen hasta destino."""
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = prev[actual]
    camino.reverse()
    return camino if camino and camino[0] == origen else []


def calcular_todas_matrices(G):
    """Calcula matrices de distancias mínimas para tiempo, distancia y costo."""
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
    """
    Encuentra la ruta circular óptima que comienza y termina en el hub.
    Si no se especifica hub, usa Penonomé (15) por defecto.
    """
    if hub is None:
        hub = 15  # Penonomé por defecto
    
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


# ═══════════════════════════════════════════════════════════════════════════
# 3. EXCEL EN MEMORIA
# ═══════════════════════════════════════════════════════════════════════════

def generar_excel_bytes(matrices, G):
    """Genera el Excel con matrices e inventario."""
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
