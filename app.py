# Importar las librerías necesarias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os  # <-- AÑADE ESTA LÍNEA

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Análisis de Precios de Viviendas",
    page_icon="🏠",
    layout="wide"
)

# --- CARGA DE DATOS (VERSIÓN CORREGIDA Y ROBUSTA) ---
@st.cache_data
def load_data(filepath):
    """Carga los datos desde una ruta absoluta."""
    try:
        df = pd.read_csv("/workspaces/Analisis_Precios_Viviendas/data_house_price.csv")
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['price'] > 1000]
        return df
    except FileNotFoundError:
        st.error(f"Error Crítico: No se encontró el archivo en la ruta '{filepath}'.")
        st.info("Asegúrate de que 'data_house_price.csv' está en la raíz de tu repositorio de GitHub.")
        return None

# --- CONSTRUIR LA RUTA ABSOLUTA AL ARCHIVO CSV ---
# Esta es la parte clave de la solución.
# Obtiene la ruta del directorio donde se encuentra el script 'app.py'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Une esa ruta con el nombre del archivo para crear una ruta completa
FILE_PATH = os.path.join(SCRIPT_DIR, "data_house_price.csv")

# Cargar el dataframe usando la ruta absoluta
df = load_data(FILE_PATH)

if df is None:
    st.stop()

# --- TÍTULO PRINCIPAL ---
st.title("🏠 Dashboard Interactivo de Precios de Viviendas")
st.write("Explora los datos de precios de viviendas del condado de King, WA, EE. UU. Usa los filtros de la barra lateral para segmentar los datos.")

# --- BARRA LATERAL (SIDEBAR) CON FILTROS ---
st.sidebar.header("Filtros de Búsqueda")

# Filtro por ciudad (multiselector)
cities = sorted(df['city'].unique())
selected_cities = st.sidebar.multiselect(
    "Selecciona una o varias ciudades:",
    options=cities,
    default=["Seattle", "Renton", "Bellevue"] # Ciudades por defecto
)

# Filtro por rango de precios (slider)
min_price, max_price = int(df['price'].min()), int(df['price'].max())
price_range = st.sidebar.slider(
    "Rango de precios ($):",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price/2) # Rango por defecto
)

# Aplicar filtros al DataFrame
if not selected_cities:
    filtered_df = df[
        (df['price'] >= price_range[0]) &
        (df['price'] <= price_range[1])
    ]
else:
    filtered_df = df[
        (df['city'].isin(selected_cities)) &
        (df['price'] >= price_range[0]) &
        (df['price'] <= price_range[1])
    ]

# --- CUERPO PRINCIPAL DEL DASHBOARD ---

st.header("Análisis de Viviendas Filtradas")

# --- MÉTRICAS CLAVE ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Número de Viviendas", value=f"{len(filtered_df):,}")
with col2:
    avg_price = filtered_df['price'].mean() if not filtered_df.empty else 0
    st.metric(label="Precio Promedio", value=f"${avg_price:,.0f}")
with col3:
    avg_sqft = filtered_df['sqft_living'].mean() if not filtered_df.empty else 0
    st.metric(label="Superficie Promedio", value=f"{avg_sqft:,.0f} sqft")

st.markdown("---")

# --- VISUALIZACIONES ---
st.subheader("Visualizaciones Interactivas")

if not filtered_df.empty:
    # Gráfico de dispersión: Precio vs. Superficie
    # Asegúrate de que esta línea esté exactamente así: fig, ax
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(filtered_df['sqft_living'], filtered_df['price'], alpha=0.5)
    
    # Todos estos métodos se llaman sobre 'ax'
    ax.set_title("Precio vs. Superficie Habitable (sqft)")
    ax.set_xlabel("Superficie (sqft)")
    ax.set_ylabel("Precio ($)")
    ax.grid(True)
    
    # Finalmente, se muestra la figura completa 'fig'
    st.pyplot(fig)
else:
    st.warning("No hay datos disponibles para los filtros seleccionados.")

# --- TABLA DE DATOS ---
if st.checkbox("Mostrar tabla de datos filtrados"):
    st.write(f"Mostrando {len(filtered_df)} registros")
    st.dataframe(filtered_df)
