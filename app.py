%%writefile app.py
import streamlit as st
import pandas as pd
import numpy as np
from vega_datasets import data

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Vuelos",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Título y Descripción ---
st.title("✈️ Dashboard Interactivo de Vuelos en EE. UU.")
st.markdown("""
Bienvenido a este dashboard interactivo para el análisis de vuelos.
Utiliza los filtros en la barra lateral para explorar los datos por aerolínea y distancia.
""")

# --- Carga de Datos Optimizada ---
@st.cache_data # Decorador para cachear los datos y mejorar el rendimiento
def load_data():
    """Carga y pre-procesa el dataset de vuelos."""
    df = data.flights_2k()  # Dataset con 2,000 registros de vuelos
    df['delay'] = df['delay'].fillna(0).astype(int)
    df['distance'] = df['distance'].astype(int)
    df['date'] = pd.to_datetime(df['date'])
    return df

flights_df = load_data()

# --- Barra Lateral de Filtros (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Filtros de Visualización")

    # Filtro multi-selección para aerolíneas (usando el aeropuerto de origen)
    unique_origins = sorted(flights_df['origin'].unique())
    selected_carrier = st.multiselect(
        "✈️ Selecciona Aerolíneas (por origen):",
        options=unique_origins,
        default=unique_origins
    )

    # Filtro de rango para la distancia
    min_dist, max_dist = int(flights_df['distance'].min()), int(flights_df['distance'].max())
    selected_distance = st.slider(
        "📍 Filtra por Distancia del Vuelo (millas):",
        min_value=min_dist,
        max_value=max_dist,
        value=(min_dist, max_dist)
    )

# Aplicar filtros al DataFrame principal
filtered_df = flights_df[
    (flights_df['origin'].isin(selected_carrier)) &
    (flights_df['distance'].between(selected_distance[0], selected_distance[1]))
]

# --- Cuerpo Principal del Dashboard ---

# 1. Métricas Clave en Columnas
st.header("📊 Métricas Generales")
col1, col2, col3 = st.columns(3)

total_flights = filtered_df.shape[0]
avg_delay = int(filtered_df['delay'].mean())
total_distance = int(filtered_df['distance'].sum())

col1.metric("Vuelos Totales Filtrados", f"{total_flights:,}")
col2.metric("Retraso Promedio", f"{avg_delay} min")
col3.metric("Distancia Total Recorrida", f"{total_distance:,} millas")

st.markdown("---")

# 2. Visualizaciones
st.header("📈 Visualizaciones Interactivas")

# Gráfico de Barras: Vuelos por Aeropuerto de Origen
st.subheader("Número de Vuelos por Aeropuerto de Origen")
flights_by_origin = filtered_df['origin'].value_counts()
st.bar_chart(flights_by_origin)

# Gráfico de Línea: Retraso Promedio a lo largo del tiempo
st.subheader("Evolución del Retraso Promedio")
delay_by_date = filtered_df.groupby(filtered_df['date'].dt.date)['delay'].mean()
st.line_chart(delay_by_date)

# 3. Vista de Datos Crudos (Opcional)
with st.expander("Ver Datos Crudos Filtrados"):
    st.dataframe(filtered_df)
