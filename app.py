# Importar las librerías necesarias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Análisis de Precios de Viviendas",
    page_icon="🏠",
    layout="wide"
)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data(filepath):
    """Carga y preprocesa los datos de precios de viviendas."""
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        # Limpiamos datos erróneos (precios en 0 o muy bajos)
        df = df[df['price'] > 1000]
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo '{filepath}'. Asegúrate de que está en la misma carpeta.")
        return None

# Cargar el dataframe
df = load_data("data_house_price.csv")

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
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(filtered_df['sqft_living'], filtered_df['price'], alpha=0.5)
    ax.set_title("Precio vs. Superficie Habitable (sqft)")
    ax.set_xlabel("Superficie (sqft)")
    ax.set_ylabel("Precio ($)")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.warning("No hay datos disponibles para los filtros seleccionados.")

# --- TABLA DE DATOS ---
if st.checkbox("Mostrar tabla de datos filtrados"):
    st.write(f"Mostrando {len(filtered_df)} registros")
    st.dataframe(filtered_df)
