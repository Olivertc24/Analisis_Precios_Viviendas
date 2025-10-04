# Importar las librerías necesarias
import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Análisis de Precios de Viviendas",
    page_icon="🏠",
    layout="wide"
)

# --- CARGA DE DATOS ---
# Usamos el decorador @st.cache_data para que los datos se carguen solo una vez
@st.cache_data
def load_data(filepath):
    """Carga y preprocesa los datos de precios de viviendas."""
    try:
        df = pd.read_csv(filepath)
        # Convertir la columna 'date' a formato de fecha
        df['date'] = pd.to_datetime(df['date'])
        # Eliminar filas donde el precio es 0, ya que probablemente son datos erróneos
        df = df[df['price'] > 0]
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo en la ruta '{filepath}'. Asegúrate de que 'data_house_price.csv' esté en la misma carpeta que 'app.py'.")
        return None

# Cargar el dataframe
df = load_data("data_house_price.csv")

# Si el dataframe no se carga, detenemos la ejecución
if df is None:
    st.stop()


# --- TÍTULO PRINCIPAL ---
st.title("🏠 Dashboard de Análisis de Precios de Viviendas")
st.write("Explora los datos de precios de viviendas del condado de King, WA, EE. UU.")


# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("Filtros")

# Filtro por ciudad
# Obtenemos una lista de ciudades únicas para el selector
cities = sorted(df['city'].unique())
selected_city = st.sidebar.multiselect(
    "Selecciona la Ciudad",
    options=cities,
    default=cities[:5]  # Seleccionamos las primeras 5 ciudades por defecto
)

# Filtro por número de habitaciones
# Obtenemos los valores únicos de habitaciones y los ordenamos
bedrooms = sorted(df['bedrooms'].unique())
selected_bedrooms = st.sidebar.selectbox(
    "Selecciona el número de habitaciones",
    options=bedrooms,
    index=2 # Seleccionamos '3' habitaciones por defecto (asumiendo que está en el índice 2)
)

# Aplicar filtros al DataFrame
# Si no se selecciona ninguna ciudad, usamos todas.
if not selected_city:
    filtered_df = df[df['bedrooms'] == selected_bedrooms]
else:
    filtered_df = df[
        (df['city'].isin(selected_city)) &
        (df['bedrooms'] == selected_bedrooms)
    ]


# --- CUERPO PRINCIPAL DEL DASHBOARD ---

st.header(f"Mostrando viviendas de {selected_bedrooms} habitaciones en: {', '.join(selected_city) if selected_city else 'Todas las ciudades'}")

# --- MÉTRICAS CLAVE ---
col1, col2, col3 = st.columns(3)

with col1:
    avg_price = filtered_df['price'].mean() if not filtered_df.empty else 0
    st.metric(label="Precio Promedio", value=f"${avg_price:,.2f}")

with col2:
    avg_sqft = filtered_df['sqft_living'].mean() if not filtered_df.empty else 0
    st.metric(label="Superficie Promedio (sqft)", value=f"{avg_sqft:,.0f}")

with col3:
    num_houses = len(filtered_df)
    st.metric(label="Número de Viviendas", value=num_houses)

st.markdown("---")


# --- VISUALIZACIONES ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Distribución de Precios")
    if not filtered_df.empty:
        # Histograma de precios
        fig, ax = plt.subplots()
        ax.hist(filtered_df['price'], bins=50, color='#6495ED', edgecolor='black')
        ax.set_title("Frecuencia de Precios")
        ax.set_xlabel("Precio ($)")
        ax.set_ylabel("Frecuencia")
        st.pyplot(fig)
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")


with col2:
    st.subheader("Precio vs. Superficie (sqft_living)")
    if not filtered_df.empty:
        # Gráfico de dispersión
        fig, ax = plt.subplots()
        ax.scatter(filtered_df['sqft_living'], filtered_df['price'], alpha=0.5, color='#4682B4')
        ax.set_title("Relación Precio vs. Superficie")
        ax.set_xlabel("Superficie (sqft)")
        ax.set_ylabel("Precio ($)")
        st.pyplot(fig)
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")


# --- TABLA DE DATOS ---
st.subheader("Datos de Viviendas Filtrados")
if st.checkbox("Mostrar tabla de datos"):
    st.write(filtered_df)
