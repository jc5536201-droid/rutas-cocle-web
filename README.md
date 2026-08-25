# Rutas Turísticas Coclé — Plataforma Web (Streamlit)

## 1. Cómo agregar tus fotos

Coloca las imágenes dentro de la carpeta `imagenes/`, **nombradas con el código
del atractivo** (lo ves en la sección Inventario). Ejemplos:

```
imagenes/PSC.jpg   → Playa Santa Clara
imagenes/CGA.jpg   → Cerro Gaital
imagenes/SAC.png   → Sitio Arqueológico El Caño
imagenes/PEN.jpg   → Penonomé
```

Acepta `.jpg`, `.jpeg`, `.png` y `.webp`. Si un atractivo no tiene imagen,
la app muestra automáticamente un recuadro de "Sin foto todavía" — no se
rompe nada, puedes ir agregando fotos poco a poco.

No hace falta que tengas las 21; agrega primero las de los destinos que
más uses en tu sustentación.

## 2. Probar en tu computadora

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre solo en el navegador (normalmente `http://localhost:8501`).

## 3. Publicar gratis (para compartir el link con tu jurado)

1. Sube esta carpeta a un repositorio de GitHub (incluye `imagenes/` con tus fotos).
2. Entra a https://share.streamlit.io con tu cuenta de GitHub.
3. Selecciona el repo y el archivo `app.py`.
4. En un par de minutos tienes una URL pública tipo
   `https://tu-usuario-rutas-cocle.streamlit.app`.

## 4. Estructura del proyecto

```
rutas_cocle_web/
├── app.py                 ← interfaz web (Streamlit)
├── logica_dijkstra.py     ← grafo, Dijkstra, matrices, Excel (tu lógica original)
├── requirements.txt
├── imagenes/               ← tus fotos, una por atractivo (CODIGO.jpg)
└── README.md
```

La lógica de `logica_dijkstra.py` es exactamente la que ya usaste y validaste
en la versión de consola — no se modificó ningún cálculo, solo se separó
para poder importarla desde la web.
