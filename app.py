# Importar las librerías necesarias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Avanzado de Precios de Viviendas",
    page_icon="🏠",
    layout="wide"
)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data(filepath):
    """Carga los datos y realiza un pre-procesamiento básico."""
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        df['year_month'] = df['date'].dt.to_period('M')
        df = df[df['price'] > 1000] # Limpieza de datos
        # Aseguramos que las columnas categóricas tengan el tipo correcto
        df['condition'] = df['condition'].astype('category')
        df['waterfront'] = df['waterfront'].astype('category')
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo en la ruta '{filepath}'.")
        return None

# --- RUTA AL ARCHIVO ---
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.join(SCRIPT_DIR, "data_house_price.csv")
except NameError:
    FILE_PATH = "data_house_price.csv"

df = load_data(FILE_PATH)

if df is None:
    st.stop()

# --- TÍTULO PRINCIPAL ---
st.title("🏠 Dashboard Avanzado de Precios de Viviendas")
st.markdown("Un análisis interactivo del mercado inmobiliario en King County, WA.")

# --- BARRA LATERAL (SIDEBAR) CON FILTROS ---
with st.sidebar:
    st.header("Filtros de Búsqueda 🔎")

    # Filtro por ciudad
    cities = sorted(df['city'].unique())
    selected_cities = st.multiselect(
        "Selecciona Ciudades:",
        options=cities,
        default=["Seattle", "Bellevue", "Redmond", "Renton"]
    )

    # Filtro por rango de precios
    min_price, max_price = float(df['price'].min()), float(df['price'].max())
    price_range = st.slider(
        "Rango de Precios ($):",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price * 0.75),
        step=10000.0,
        format="$%f"
    )

    # Filtro por número de dormitorios
    min_beds, max_beds = int(df['bedrooms'].min()), int(df['bedrooms'].max())
    bedroom_range = st.slider(
        "Número de Dormitorios:",
        min_value=min_beds,
        max_value=max_beds,
        value=(min_beds, max_beds)
    )
    
    st.markdown("---")


# --- FILTRADO DE DATOS ---
query_parts = [
    f"@price_range[0] <= price <= @price_range[1]",
    f"@bedroom_range[0] <= bedrooms <= @bedroom_range[1]"
]
if selected_cities:
    query_parts.append("city in @selected_cities")

query_string = " & ".join(query_parts)
filtered_df = df.query(query_string)

# --- CUERPO PRINCIPAL CON PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visión General",
    "🌍 Análisis por Ubicación",
    "🔍 Análisis de Características",
    "📋 Explorador de Datos"
])

# --- PESTAÑA 1: VISIÓN GENERAL ---
with tab1:
    st.header("Resumen del Mercado Inmobiliario")

    # Métricas clave
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Viviendas Seleccionadas", value=f"{len(filtered_df):,}")
    with col2:
        avg_price = filtered_df['price'].mean() if not filtered_df.empty else 0
        st.metric(label="Precio Promedio", value=f"${avg_price:,.0f}")
    with col3:
        avg_sqft = filtered_df['sqft_living'].mean() if not filtered_df.empty else 0
        st.metric(label="Superficie Promedio (sqft)", value=f"{avg_sqft:,.0f}")
    
    st.markdown("---")

    if not filtered_df.empty:
        # Evolución del precio en el tiempo
        st.subheader("Evolución del Precio Promedio Mensual")
        price_over_time = filtered_df.groupby('year_month')['price'].mean().reset_index()
        price_over_time['year_month'] = price_over_time['year_month'].dt.to_timestamp()
        
        fig_time, ax_time = plt.subplots(figsize=(12, 6))
        ax_time.plot(price_over_time['year_month'], price_over_time['price'], marker='o', linestyle='-')
        ax_time.set_title("Tendencia del Precio Promedio")
        ax_time.set_xlabel("Fecha")
        ax_time.set_ylabel("Precio Promedio ($)")
        ax_time.grid(True)
        st.pyplot(fig_time)
        
    else:
        st.warning("No hay datos para los filtros seleccionados.")

# --- PESTAÑA 2: ANÁLISIS POR UBICACIÓN ---
with tab2:
    st.header("Análisis Geográfico por Ciudad")

    if not filtered_df.empty and selected_cities:
        # Gráfico de Violín: Distribución de precios por ciudad
        st.subheader("Distribución de Precios por Ciudad")
        fig_city_dist, ax_city_dist = plt.subplots(figsize=(12, 7))
        sns.violinplot(x='price', y='city', data=filtered_df, ax=ax_city_dist, orient='h', palette='viridis')
        ax_city_dist.set_title("Distribución de Precios en Ciudades Seleccionadas")
        ax_city_dist.set_xlabel("Precio ($)")
        ax_city_dist.set_ylabel("Ciudad")
        st.pyplot(fig_city_dist)
        st.markdown("Este gráfico de violín muestra la distribución de precios en cada ciudad. Las áreas más anchas indican una mayor concentración de viviendas a ese precio.")

        st.markdown("---")
        
        # Rankings de propiedades
        st.subheader("Rankings de Propiedades")
        col_rank1, col_rank2 = st.columns(2)
        with col_rank1:
            st.write("##### 💰 Top 5 Más Caras")
            st.dataframe(filtered_df.nlargest(5, 'price')[['city', 'price', 'bedrooms', 'sqft_living']])
        with col_rank2:
            st.write("##### 📉 Top 5 Más Económicas")
            st.dataframe(filtered_df.nsmallest(5, 'price')[['city', 'price', 'bedrooms', 'sqft_living']])

    else:
        st.warning("Selecciona al menos una ciudad para ver el análisis geográfico.")

# --- PESTAÑA 3: ANÁLISIS DE CARACTERÍSTICAS ---
with tab3:
    st.header("Impacto de las Características en el Precio")

    if not filtered_df.empty:
        col_feat1, col_feat2 = st.columns(2)
        
        with col_feat1:
            # Precio vs Condición de la vivienda
            st.subheader("Precio según la Condición de la Vivienda")
            fig_cond, ax_cond = plt.subplots()
            sns.boxplot(x='condition', y='price', data=filtered_df, ax=ax_cond, palette='pastel')
            ax_cond.set_title("Precio vs. Condición")
            ax_cond.set_xlabel("Condición (1=Mala, 5=Excelente)")
            ax_cond.set_ylabel("Precio ($)")
            st.pyplot(fig_cond)

        with col_feat2:
            # Precio vs Vista al Mar (Waterfront)
            st.subheader("Precio con y sin Vista al Mar")
            fig_water, ax_water = plt.subplots()
            sns.boxplot(x='waterfront', y='price', data=filtered_df, ax=ax_water, palette='coolwarm')
            ax_water.set_title("Comparativa de Precio: Vista al Mar")
            ax_water.set_xticklabels(['Sin Vista', 'Con Vista'])
            ax_water.set_xlabel("")
            ax_water.set_ylabel("Precio ($)")
            st.pyplot(fig_water)
        
        st.markdown("---")
        
        # Mapa de Calor de Correlaciones
        st.subheader("Correlación entre Variables Numéricas")
        corr_cols = ['price', 'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors', 'yr_built']
        corr_matrix = filtered_df[corr_cols].corr()
        fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="magma", ax=ax_corr)
        st.pyplot(fig_corr)
        st.markdown("El mapa de calor muestra qué tan fuerte es la relación entre diferentes características. Un valor cercano a 1 (o -1) indica una correlación fuerte positiva (o negativa). Como es de esperar, `sqft_living` tiene una alta correlación con el `price`.")

    else:
        st.warning("No hay datos disponibles para analizar con los filtros actuales.")

# --- PESTAÑA 4: EXPLORADOR DE DATOS ---
with tab4:
    st.header("Explorador de Datos Crudos")
    st.write(f"Mostrando {len(filtered_df):,} de {len(df):,} registros.")
    
    # Columnas a mostrar en el dataframe
    display_cols = ['city', 'price', 'bedrooms', 'bathrooms', 'sqft_living', 'condition', 'yr_built', 'date']
    st.dataframe(filtered_df[display_cols], use_container_width=True)

