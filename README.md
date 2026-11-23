# EA3 — Análisis Estadístico y Geovisualización de Métricas de Software

Proyecto modular en Python desarrollado para la **Evidencia de Aprendizaje 3 (EA3)** en el programa de **Ingeniería en Hardware y Datos** de la **IU Digital de Antioquia**. 

El pipeline audita el desempeño operativo y financiero de equipos de desarrollo de software a lo largo de múltiples sprints, integrando visualizaciones estadísticas estáticas, series temporales interactivas y cartografía geoespacial proyectada sobre nodos regionales en Colombia (`EPSG:4326`).

---

## Estructura del Proyecto

```text
EA3 GEOLOCALIZACION/
├── datos/
│   └── Doc02_dataset_metricas_proyecto_software.csv   # Dataset fuente (50 registros, 7 variables)
├── output/
│   ├── 01_matplotlib_horas_equipo.png                 # Barras agrupadas de esfuerzo (Dev vs. QA)
│   ├── 02_seaborn_correlacion_metricas.png            # Matriz de correlación de Pearson
│   ├── 03_plotly_evolucion_sprints.html               # Serie temporal interactiva por sprint
│   ├── 04_geopandas_mapa_zonal.png                    # Mapa coroplético zonal (EPSG:4326)
│   └── 05_folium_mapa_interactivo.html                # Mapa web interactivo con fichas técnicas
├── src/
│   └── geovisualizacion.py                            # Script principal modularizado
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Stack Tecnológico y Justificación de Librerías

| Librería | Rol en el Pipeline | Justificación Técnica |
| :--- | :--- | :--- |
| **Pandas** | Auditoría y agregación | Limpieza, validación de integridad (50 filas × 7 columnas, 0 nulos) y agrupación por equipo/sprint. |
| **Matplotlib** | Gráfico estático (`300 DPI`) | Control preciso de ejes, etiquetas numéricas y formato de alta resolución para informes técnicos. |
| **Seaborn** | Análisis multivariable | Cálculo y visualización limpia de coeficientes de correlación de Pearson mediante mapas de calor. |
| **Plotly** | Serie temporal interactiva | Exploración longitudinal por sprint con *hover tooltips* enriquecidos y filtrado dinámico en HTML. |
| **GeoPandas** | Cartografía vectorial zonal | Construcción de `GeoDataFrame` con geometrías poligonales (`Shapely`) y mapas coropléticos en `EPSG:4326`. |
| **Folium** | Geovisualización web | Renderizado interactivo sobre Leaflet (`CartoDB positron`) con marcadores proporcionales y *popups* ejecutivos. |

---

## Instalación y Ejecución Local (Windows PowerShell)

1. **Clonar o abrir la carpeta del proyecto** en Visual Studio Code (`EA3 GEOLOCALIZACION`).
2. **Crear y activar el entorno virtual**:
   ```powershell
   python -m venv venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```
3. **Instalar las dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Ejecutar el pipeline completo**:
   ```powershell
   python src\geovisualizacion.py
   ```
5. **Visualizar los entregables interactivos (`.html`)** en el navegador:
   ```powershell
   ii output\03_plotly_evolucion_sprints.html, output\05_folium_mapa_interactivo.html
   ```

---

## Principales Hallazgos Analíticos

* **Integridad del dataset:** Se procesaron **50 registros** distribuidos en **5 equipos** sin valores nulos ni duplicados.
* **Sobrecosto acumulado total:** **$60,681 USD**, con un promedio de **$12,136.20 USD** por equipo:
  * **Equipo B (Nodo Bogotá D.C.):** **$15,663 USD** (concentra el **25.81%** del sobrecosto total).
  * **Equipo C (Nodo Cali):** **$12,967 USD**.
  * **Equipo A (Nodo Medellín):** **$11,297 USD**.
  * **Equipo E (Nodo Bucaramanga):** **$10,618 USD**.
  * **Equipo D (Nodo Barranquilla):** **$10,136 USD**.
* **Brecha operativa:** El **Equipo B** presenta un sobrecosto **$5,527 USD superior (+54.53%)** frente al **Equipo D**, evidenciando la necesidad de intervenir la relación entre defectos detectados y retrasos de entrega en sus sprints críticos.

---

## Autor

* **Oscar Javier García García** — [@nickend12](https://github.com/nickend12)  
  Ingeniería en Hardware y Datos — **IU Digital de Antioquia**