from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Evita bloqueos de ventana al exportar PNG en local
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import geopandas as gpd
from shapely.geometry import box
import folium


# ==============================================================================
# 1. CONFIGURACIÓN DE RUTAS DEL PROYECTO
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_CSV = BASE_DIR / "datos" / "Doc02_dataset_metricas_proyecto_software.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 2. CARGA, AUDITORÍA Y LIMPIEZA DE DATOS
# ==============================================================================
def cargar_y_auditar_datos(ruta: Path) -> pd.DataFrame:
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en: {ruta}\n"
            "Por favor copia 'Doc02_dataset_metricas_proyecto_software.csv' dentro de la carpeta 'datos/'."
        )

    try:
        df = pd.read_csv(ruta, sep=None, engine="python", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(ruta, sep=None, engine="python", encoding="latin-1")

    df.columns = [col.strip() for col in df.columns]

    print("=" * 65)
    print("AUDITORÍA INICIAL DEL DATASET - EA3 GEOVISUALIZACIÓN")
    print("=" * 65)
    print(f"Dimensiones: {df.shape[0]} registros x {df.shape[1]} columnas")
    print(f"Valores nulos totales: {df.isna().sum().sum()}")
    print(f"Registros duplicados: {df.duplicated().sum()}")
    print("\nTipos de datos:")
    print(df.dtypes)
    print("\nResumen estadístico:")
    print(df.describe().round(2))
    print("=" * 65)

    return df


# ==============================================================================
# 3. VISUALIZACIÓN 1: MATPLOTLIB (ESTÁTICA BASE - ESFUERZO POR EQUIPO)
# ==============================================================================
def generar_matplotlib(df: pd.DataFrame) -> None:
    resumen_horas = (
        df.groupby("Equipo")[["Horas_Desarrollo", "Horas_Pruebas"]]
        .sum()
        .sort_values(by="Horas_Desarrollo", ascending=False)
    )

    ax = resumen_horas.plot(
        kind="bar",
        figsize=(10, 6),
        color=["#1f4e78", "#5b9bd5"],
        edgecolor="black",
        width=0.75,
    )
    ax.set_title(
        "Esfuerzo Acumulado: Horas de Desarrollo vs. Pruebas por Equipo",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    ax.set_xlabel("Equipo de Desarrollo", fontsize=11)
    ax.set_ylabel("Total de Horas", fontsize=11)
    ax.legend(["Horas de Desarrollo", "Horas de Pruebas"], frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=0)

    for contenedor in ax.containers:
        ax.bar_label(contenedor, fmt="%d", padding=3, fontsize=9)

    plt.tight_layout()
    salida = OUTPUT_DIR / "01_matplotlib_horas_equipo.png"
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[OK] Matplotlib exportado -> {salida.name}")


# ==============================================================================
# 4. VISUALIZACIÓN 2: SEABORN (ESTADÍSTICA - CORRELACIÓN DE MÉTRICAS)
# ==============================================================================
def generar_seaborn(df: pd.DataFrame) -> None:
    columnas_numericas = [
        "Sprint",
        "Horas_Desarrollo",
        "Horas_Pruebas",
        "Errores_Detectados",
        "Retraso_Entrega (días)",
        "Costo_Excedente ($)",
    ]
    corr = df[columnas_numericas].corr()

    plt.figure(figsize=(9, 7))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        linewidths=0.8,
        vmin=-1,
        vmax=1,
        cbar_kws={"label": "Coeficiente de Correlación de Pearson"},
    )
    plt.title(
        "Matriz de Correlación entre Métricas de Ingeniería y Sobrecostos",
        fontsize=12,
        fontweight="bold",
        pad=14,
    )
    plt.xticks(rotation=25, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    salida = OUTPUT_DIR / "02_seaborn_correlacion_metricas.png"
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[OK] Seaborn exportado    -> {salida.name}")


# ==============================================================================
# 5. VISUALIZACIÓN 3: PLOTLY (INTERACTIVA - EVOLUCIÓN TEMPORAL POR SPRINT)
# ==============================================================================
def generar_plotly(df: pd.DataFrame) -> None:
    df_ordenado = df.sort_values(by=["Sprint", "Equipo"])

    fig = px.line(
        df_ordenado,
        x="Sprint",
        y="Costo_Excedente ($)",
        color="Equipo",
        markers=True,
        hover_data=[
            "Horas_Desarrollo",
            "Horas_Pruebas",
            "Errores_Detectados",
            "Retraso_Entrega (días)",
        ],
        title="Evolución Interactiva del Costo Excedente ($) por Sprint y Equipo",
        labels={
            "Sprint": "Número de Sprint",
            "Costo_Excedente ($)": "Costo Excedente ($ USD)",
            "Equipo": "Equipo",
        },
        template="plotly_white",
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
    fig.update_xaxes(dtick=1)

    salida = OUTPUT_DIR / "03_plotly_evolucion_sprints.html"
    fig.write_html(salida)
    print(f"[OK] Plotly exportado     -> {salida.name}")


# ==============================================================================
# 6. GEORREFERENCIACIÓN DE NODOS OPERATIVOS PARA GEOPANDAS Y FOLIUM
# ==============================================================================
def construir_resumen_geoespacial(df: pd.DataFrame) -> gpd.GeoDataFrame:
    resumen = (
        df.groupby("Equipo", as_index=False)
        .agg(
            Sprints_Ejecutados=("Sprint", "count"),
            Horas_Desarrollo=("Horas_Desarrollo", "sum"),
            Horas_Pruebas=("Horas_Pruebas", "sum"),
            Errores_Detectados=("Errores_Detectados", "sum"),
            Retraso_Promedio=("Retraso_Entrega (días)", "mean"),
            Costo_Excedente=("Costo_Excedente ($)", "sum"),
        )
        .sort_values(by="Equipo")
        .reset_index(drop=True)
    )

    # Nodos regionales de operación en Colombia asociados a cada equipo
    nodos_colombia = [
        {"Ciudad": "Medellín (Antioquia)", "lat": 6.2442, "lon": -75.5812},
        {"Ciudad": "Bogotá D.C.", "lat": 4.7110, "lon": -74.0721},
        {"Ciudad": "Cali (Valle del Cauca)", "lat": 3.4516, "lon": -76.5320},
        {"Ciudad": "Barranquilla (Atlántico)", "lat": 10.9685, "lon": -74.7813},
        {"Ciudad": "Bucaramanga (Santander)", "lat": 7.1193, "lon": -73.1227},
    ]

    geometrias = []
    ciudades = []
    latitudes = []
    longitudes = []

    for idx in range(len(resumen)):
        nodo = nodos_colombia[idx % len(nodos_colombia)]
        lat, lon = nodo["lat"], nodo["lon"]
        # Polígono zonal (cuadrante operativo alrededor de cada nodo regional)
        poligono_zonal = box(lon - 0.85, lat - 0.65, lon + 0.85, lat + 0.65)
        geometrias.append(poligono_zonal)
        ciudades.append(nodo["Ciudad"])
        latitudes.append(lat)
        longitudes.append(lon)

    resumen["Nodo_Operativo"] = ciudades
    resumen["Latitud"] = latitudes
    resumen["Longitud"] = longitudes

    gdf = gpd.GeoDataFrame(resumen, geometry=geometrias, crs="EPSG:4326")
    return gdf


# ==============================================================================
# 7. VISUALIZACIÓN 4: GEOPANDAS (MAPA COROPLÉTICO ZONAL)
# ==============================================================================
def generar_geopandas(gdf: gpd.GeoDataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))

    gdf.plot(
        column="Costo_Excedente",
        cmap="OrRd",
        linewidth=1.5,
        edgecolor="#222222",
        legend=True,
        legend_kwds={
            "label": "Costo Excedente Acumulado ($ USD)",
            "orientation": "vertical",
            "shrink": 0.75,
        },
        ax=ax,
    )

    for _, fila in gdf.iterrows():
        centroide = fila.geometry.centroid
        etiqueta = (
            f"{fila['Equipo']}\n"
            f"{fila['Nodo_Operativo']}\n"
            f"${fila['Costo_Excedente']:,.0f} | Err: {fila['Errores_Detectados']}"
        )
        ax.annotate(
            etiqueta,
            xy=(centroide.x, centroide.y),
            ha="center",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.88),
        )

    ax.set_title(
        "Mapa Coroplético Zonal (GeoPandas - EPSG:4326)\n"
        "Distribución Geográfica de Sobrecostos y Errores por Nodo Operativo",
        fontsize=12,
        fontweight="bold",
        pad=14,
    )
    ax.set_xlabel("Longitud (°)")
    ax.set_ylabel("Latitud (°)")
    ax.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()

    salida = OUTPUT_DIR / "04_geopandas_mapa_zonal.png"
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[OK] GeoPandas exportado  -> {salida.name}")


# ==============================================================================
# 8. VISUALIZACIÓN 5: FOLIUM (MAPA INTERACTIVO WEB)
# ==============================================================================
def generar_folium(gdf: gpd.GeoDataFrame) -> None:
    mapa = folium.Map(
        location=[6.2442, -75.5812],
        zoom_start=6,
        tiles="CartoDB positron",
    )

    max_costo = gdf["Costo_Excedente"].max()

    for _, fila in gdf.iterrows():
        radio = 14 + (fila["Costo_Excedente"] / max_costo) * 20
        color = "#d73027" if fila["Costo_Excedente"] == max_costo else "#fc8d59"

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 230px;">
            <h4 style="margin:0 0 6px 0; color:#1f4e78;">{fila['Equipo']}</h4>
            <b>Nodo:</b> {fila['Nodo_Operativo']}<br>
            <b>Costo Excedente:</b> ${fila['Costo_Excedente']:,.0f} USD<br>
            <b>Errores Detectados:</b> {fila['Errores_Detectados']}<br>
            <b>Retraso Promedio:</b> {fila['Retraso_Promedio']:.1f} días/sprint<br>
            <b>Horas Dev / QA:</b> {fila['Horas_Desarrollo']}h / {fila['Horas_Pruebas']}h
        </div>
        """

        folium.CircleMarker(
            location=[fila["Latitud"], fila["Longitud"]],
            radius=radio,
            color="#7f0000",
            weight=1.5,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{fila['Equipo']} ({fila['Nodo_Operativo']}): ${fila['Costo_Excedente']:,.0f}",
        ).add_to(mapa)

    salida = OUTPUT_DIR / "05_folium_mapa_interactivo.html"
    mapa.save(str(salida))
    print(f"[OK] Folium exportado     -> {salida.name}")


# ==============================================================================
# FLUJO PRINCIPAL
# ==============================================================================
def main() -> None:
    df = cargar_y_auditar_datos(RUTA_CSV)
    generar_matplotlib(df)
    generar_seaborn(df)
    generar_plotly(df)

    gdf_equipos = construir_resumen_geoespacial(df)
    generar_geopandas(gdf_equipos)
    generar_folium(gdf_equipos)

    print("\nPipeline finalizado con éxito. Revisa la carpeta 'output/'.")


if __name__ == "__main__":
    main()