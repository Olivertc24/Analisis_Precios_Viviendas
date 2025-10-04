# Importar las librerías necesarias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # Importamos seaborn para el mapa de calor
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Análisis de Precios de Viviendas",
    page_icon="🏠",
    layout="wide"
)

# --- CARGA DE DATOS (VERSIÓN CORREGIDA Y ROBUSTA) ---
@st.cache_data
def load_data(filepath):
    """Carga los datos desde una ruta y los pre-procesa."""
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        # Creamos una columna 'year_month' para análisis de series temporales
        df['year_month'] = df['date'].dt.to_period('M')
        # Limpiamos datos erróneos (precios en 0 o muy bajos)
        df = df[df['price'] > 1000]
        return df
    except FileNotFoundError:
        st.error(f"Error Crítico: No se encontró el archivo en la ruta '{filepath}'.")
        st.info("Asegúrate de que 'data_house_price.csv' se ha añadido y subido a tu repositorio.")
        return None

# --- CONSTRUIR LA RUTA AL ARCHIVO CSV ---
# Esta lógica ayuda a que la app funcione tanto localmente como en servidores como Render o Streamlit Cloud.
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.join(SCRIPT_DIR, "data_house_price.csv")
except NameError:
    FILE_PATH = "data_house_price.csv"

# Cargar el dataframe
df = load_data(FILE_PATH)

# Si el dataframe no se carga, detenemos la ejecución de la app
if df is None:
    st.stop()

# --- TÍTULO PRINCIPAL ---
st.title("🏠 Dashboard Interactivo de Precios de Viviendas")
st.write("Explora los datos de precios de viviendas del condado de King, WA, EE. UU. Usa los filtros de la barra lateral para segmentar los datos.")

# --- BARRA LATERAL (SIDEBAR) CON FILTROS ---
st.sidebar.header("Filtros de Búsqueda 🔎")

# Filtro por ciudad (multiselector)
cities = sorted(df['city'].unique())
selected_cities = st.sidebar.multiselect(
    "Selecciona una o varias ciudades:",
    options=cities,
    default=["Seattle", "Renton", "Bellevue"]
)

# Filtro por rango de precios (slider)
min_price, max_price = float(df['price'].min()), float(df['price'].max())
price_range = st.sidebar.slider(
    "Rango de precios ($):",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price / 2),
    step=1000.0,
    format="$%f"
)

# Filtro por número de dormitorios (slider)
min_beds, max_beds = int(df['bedrooms'].min()), int(df['bedrooms'].max())
bedroom_range = st.sidebar.slider(
    "Número de dormitorios:",
    min_value=min_beds,
    max_value=max_beds,
    value=(min_beds, max_beds) # Por defecto, todo el rango
)


# Aplicar filtros al DataFrame
query_parts = [
    f"@price_range[0] <= price <= @price_range[1]",
    f"@bedroom_range[0] <= bedrooms <= @bedroom_range[1]"
]
if selected_cities:
    query_parts.append("city in @selected_cities")

query_string = " & ".join(query_parts)
filtered_df = df.query(query_string)


# --- CUERPO PRINCIPAL DEL DASHBOARD ---

st.header("Análisis de Viviendas Filtradas 📊")

# --- MÉTRICAS CLAVE ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Número de Viviendas", value=f"{len(filtered_df):,}")
with col2:
    avg_price = filtered_df['price'].mean() if not filtered_df.empty else 0
    st.metric(label="Precio Promedio", value=f"${avg_price:,.0f}")
with col3:
    avg_sqft = filtered_df['sqft_living'].mean() if not filtered_df.empty else 0
    st.metric(label="Superficie Promedio (sqft)", value=f"{avg_sqft:,.0f}")

st.markdown("---")

# --- VISUALIZACIONES ---
st.subheader("Visualizaciones Interactivas")

if not filtered_df.empty:
    # --- Dividimos el espacio en dos columnas para organizar los gráficos ---
    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        # GRÁFICO 1: Distribución de Precios (Histograma)
        st.write("#### Distribución de Precios")
        fig1, ax1 = plt.subplots()
        sns.histplot(filtered_df['price'], kde=True, ax=ax1, bins=50)
        ax1.set_xlabel("Precio ($)")
        ax1.set_ylabel("Frecuencia")
        ax1.set_title("Histograma de Precios de Viviendas")
        st.pyplot(fig1)

        # GRÁFICO 3: Evolución del Precio en el Tiempo (Gráfico de Líneas)
        st.write("#### Evolución del Precio Promedio")
        # Convertimos 'year_month' a timestamp para poder graficarlo correctamente
        price_over_time = filtered_df.groupby('year_month')['price'].mean().reset_index()
        price_over_time['year_month'] = price_over_time['year_month'].dt.to_timestamp()

        fig3, ax3 = plt.subplots()
        ax3.plot(price_over_time['year_month'], price_over_time['price'])
        ax3.set_xlabel("Fecha (Mes)")
        ax3.set_ylabel("Precio Promedio ($)")
        ax3.set_title("Precio Promedio a lo Largo del Tiempo")
        plt.xticks(rotation=45)
        st.pyplot(fig3)


    with viz_col2:
        # GRÁFICO 2: Precio por Número de Dormitorios (Gráfico de Barras)
        st.write("#### Precio Promedio por Nro. de Dormitorios")
        avg_price_by_beds = filtered_df.groupby('bedrooms')['price'].mean().sort_index()
        fig2, ax2 = plt.subplots()
        avg_price_by_beds.plot(kind='bar', ax=ax2)
        ax2.set_xlabel("Número de Dormitorios")
        ax2.set_ylabel("Precio Promedio ($)")
        ax2.set_title("Precio Promedio vs. Dormitorios")
        plt.xticks(rotation=0)
        st.pyplot(fig2)

        # GRÁFICO 4: Mapa de Calor de Correlaciones
        st.write("#### Correlación entre Características")
        corr_cols = ['price', 'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors', 'condition']
        corr_matrix = filtered_df[corr_cols].corr()
        fig4, ax4 = plt.subplots()
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax4)
        ax4.set_title("Mapa de Calor de Correlaciones")
        st.pyplot(fig4)

    # Gráfico de dispersión original (ahora ocupa todo el ancho)
    st.write("#### Relación entre Precio y Superficie")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(filtered_df['sqft_living'], filtered_df['price'], alpha=0.5)
    ax.set_title("Precio vs. Superficie Habitable (sqft)")
    ax.set_xlabel("Superficie (sqft)")
    ax.set_ylabel("Precio ($)")
    ax.grid(True)
    st.pyplot(fig)

else:
    st.warning("No hay datos disponibles para los filtros seleccionados. Por favor, amplía tus criterios de búsqueda.")

# --- TABLA DE DATOS ---
st.markdown("---")
if st.checkbox("Mostrar tabla de datos filtrados"):
    st.write(f"Mostrando {len(filtered_df)} registros")
    # Mostramos una versión más limpia de la tabla para el usuario
    display_cols = ['city', 'price', 'bedrooms', 'bathrooms', 'sqft_living', 'yr_built', 'condition']
    st.dataframe(filtered_df[display_cols])

