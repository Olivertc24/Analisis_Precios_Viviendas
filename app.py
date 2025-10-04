import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar los datos
df = pd.read_csv('data_house_price.csv')

# Configuración de la página
st.set_page_config(layout="wide", page_title="Análisis de Precios de Viviendas")

# Tema "La noche estrellada" usando CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #001f3f;
            color: #ffffff;
        }
        .st-emotion-cache-16txtl3 {
            color: #F0E68C;
        }
        h1, h2, h3 {
            color: #FFD700;
        }
        .stPlotlyChart {
            border-radius: 10px;
            padding: 10px;
            background-color: #003366;
        }
    </style>
""", unsafe_allow_html=True)

st.title('Dashboard de Análisis de Precios de Viviendas en Washington')
st.write('Este dashboard presenta un análisis de los precios de las viviendas en el estado de Washington.')

# --- Fila 1 ---
col1, col2 = st.columns(2)

with col1:
    st.header("Distribución de Precios de Viviendas")
    fig, ax = plt.subplots()
    sns.histplot(df['price'], bins=50, kde=True, color='gold', ax=ax)
    ax.set_facecolor('#001f3f')
    fig.set_facecolor('#001f3f')
    ax.tick_params(colors='white', which='both')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    plt.xlabel('Precio')
    plt.ylabel('Frecuencia')
    st.pyplot(fig)

with col2:
    st.header("Precio vs. Superficie habitable (sqft_living)")
    fig, ax = plt.subplots()
    sns.scatterplot(x='sqft_living', y='price', data=df, color='cyan', ax=ax, alpha=0.5)
    ax.set_facecolor('#001f3f')
    fig.set_facecolor('#001f3f')
    ax.tick_params(colors='white', which='both')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    plt.xlabel('Superficie habitable (pies cuadrados)')
    plt.ylabel('Precio')
    st.pyplot(fig)

# --- Fila 2 ---
col3, col4 = st.columns(2)

with col3:
    st.header("Precio por Condición de la Vivienda")
    fig, ax = plt.subplots()
    sns.boxplot(x='condition', y='price', data=df, palette='viridis', ax=ax)
    ax.set_facecolor('#001f3f')
    fig.set_facecolor('#001f3f')
    ax.tick_params(colors='white', which='both')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    plt.xlabel('Condición')
    plt.ylabel('Precio')
    st.pyplot(fig)

with col4:
    st.header("Top 10 Ciudades por Precio Promedio")
    top_cities = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_cities.values, y=top_cities.index, palette='plasma', ax=ax)
    ax.set_facecolor('#001f3f')
    fig.set_facecolor('#001f3f')
    ax.tick_params(colors='white', which='both')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    plt.xlabel('Precio Promedio')
    plt.ylabel('Ciudad')
    st.pyplot(fig)
