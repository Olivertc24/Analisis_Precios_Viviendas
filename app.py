import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ----------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------
# Usamos 'wide' para que el contenido ocupe todo el ancho de la pantalla
st.set_page_config(page_title="Dashboard de Precios de Viviendas",
                   page_icon="🏠",
                   layout="wide")

# ----------------------------------
# FUNCIONES AUXILIARES
# ----------------------------------

# Función para cargar y cachear los datos para mejorar el rendimiento
@st.cache_data
def cargar_datos(filepath):
    """Carga los datos desde un archivo CSV."""
    try:
        df = pd.read_csv(filepath)
        # Convertir 'Fecha' a formato de fecha para un mejor manejo
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        # Asegurarnos que las columnas numéricas no tengan valores nulos que den problemas
        for col in ['Precio', 'Habitaciones', 'Baños', 'Metros_Cuadrados']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['Precio', 'Metros_Cuadrados', 'Fecha'], inplace=True)
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo en la ruta '{filepath}'. Asegúrate de que el archivo .csv esté en el mismo directorio que app.py")
        return None

# Función para obtener la imagen de fondo en formato base64
# Esto es necesario para que Streamlit pueda mostrar una imagen de fondo local
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    """Aplica una imagen PNG como fondo de la página."""
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
    background-image: url("data:image/png;base64,{bin_str}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: scroll;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# ----------------------------------
# CARGA DE DATOS Y ESTILO
# ----------------------------------

# Reemplaza 'nombre_del_archivo.csv' con el nombre de tu archivo de datos
DATA_PATH = 'precios_viviendas.csv'

# Cargar los datos
datos = cargar_datos(DATA_PATH)

# Aplicar el fondo (si el archivo de imagen existe)
try:
    set_png_as_page_bg(BACKGROUND_IMAGE_PATH)
except FileNotFoundError:
    st.warning("No se encontró la imagen de fondo 'background.png'. Se usará un fondo de color sólido.")

# Paleta de colores inspirada en "La Noche Estrellada"
STARRY_NIGHT_COLORS = ['#0B3D91', '#F0E68C', '#FFD700', '#1E90FF', '#4682B4']

# ----------------------------------
# CUERPO PRINCIPAL DEL DASHBOARD
# ----------------------------------

if datos is not None:
    # Título principal con un toque de estilo
    st.title("🏠 Dashboard Interactivo de Precios de Viviendas")
    st.markdown("### Explora las tendencias del mercado inmobiliario con la magia de Van Gogh")
    st.markdown("---")

    # ----------------------------------
    # BARRA LATERAL CON FILTROS
    # ----------------------------------
    with st.sidebar:
        st.header("🎨 Filtros de Visualización")

        # Filtro por ciudad (multiselección)
        ciudades_disponibles = sorted(datos['Ciudad'].unique())
        ciudades_seleccionadas = st.multiselect(
            "Selecciona la(s) Ciudad(es):",
            options=ciudades_disponibles,
            default=ciudades_disponibles[:3] # Seleccionamos las primeras 3 por defecto
        )

        # Filtro por rango de precios (slider)
        precio_min = float(datos['Precio'].min())
        precio_max = float(datos['Precio'].max())
        precios_seleccionados = st.slider(
            "Rango de Precios ($):",
            min_value=precio_min,
            max_value=precio_max,
            value=(precio_min, precio_max)
        )

        # Filtro por número de habitaciones
        habitaciones_disponibles = sorted(datos['Habitaciones'].unique())
        habitaciones_seleccionadas = st.multiselect(
            "Número de Habitaciones:",
            options=habitaciones_disponibles,
            default=habitaciones_disponibles
        )

    # Filtrar el DataFrame principal según la selección del usuario
    datos_filtrados = datos[
        (datos['Ciudad'].isin(ciudades_seleccionadas)) &
        (datos['Precio'].between(precios_seleccionados[0], precios_seleccionados[1])) &
        (datos['Habitaciones'].isin(habitaciones_seleccionadas))
    ]

    # Mostrar advertencia si no hay datos con los filtros aplicados
    if datos_filtrados.empty:
        st.warning("No se encontraron viviendas que cumplan con los criterios de búsqueda. Por favor, ajusta los filtros.")
    else:
        # ----------------------------------
        # MÉTRICAS PRINCIPALES (KPIs)
        # ----------------------------------
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="**Precio Promedio**",
                      value=f"${datos_filtrados['Precio'].mean():,.2f}")
        with col2:
            st.metric(label="**Total de Viviendas**",
                      value=f"{len(datos_filtrados):,}")
        with col3:
            st.metric(label="**M² Promedio**",
                      value=f"{datos_filtrados['Metros_Cuadrados'].mean():.2f} m²")

        st.markdown("---")

        # ----------------------------------
        # VISUALIZACIONES
        # ----------------------------------
        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            st.subheader("Precio a lo largo del Tiempo")
            fig_linea_tiempo = px.line(
                datos_filtrados.sort_values('Fecha'),
                x='Fecha',
                y='Precio',
                color='Ciudad',
                title="Evolución del Precio Promedio por Ciudad",
                labels={'Precio': 'Precio ($)', 'Fecha': 'Año'},
                color_discrete_sequence=STARRY_NIGHT_COLORS
            )
            # Personalización del estilo del gráfico
            fig_linea_tiempo.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0.5)',
                font_color='white'
            )
            st.plotly_chart(fig_linea_tiempo, use_container_width=True)

        with col_graf2:
            st.subheader("Distribución de Precios por Ciudad")
            fig_boxplot = px.box(
                datos_filtrados,
                x='Ciudad',
                y='Precio',
                color='Ciudad',
                title="Rango de Precios en Ciudades Seleccionadas",
                labels={'Precio': 'Precio ($)', 'Ciudad': 'Ciudad'},
                color_discrete_sequence=STARRY_NIGHT_COLORS
            )
            fig_boxplot.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0.5)',
                font_color='white'
            )
            st.plotly_chart(fig_boxplot, use_container_width=True)

        st.subheader("Relación entre Precio y Metros Cuadrados")
        fig_dispersion = px.scatter(
            datos_filtrados,
            x='Metros_Cuadrados',
            y='Precio',
            color='Ciudad',
            size='Precio',
            hover_data=['Habitaciones', 'Baños'],
            title="Precio vs. Superficie (m²)",
            labels={'Metros_Cuadrados': 'Metros Cuadrados', 'Precio': 'Precio ($)'},
            color_discrete_sequence=STARRY_NIGHT_COLORS
        )
        fig_dispersion.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0.5)',
            font_color='white'
        )
        st.plotly_chart(fig_dispersion, use_container_width=True)

        # Mostrar tabla de datos filtrados
        with st.expander("Ver datos filtrados"):
            st.dataframe(datos_filtrados)

else:
    st.warning("No hay datos disponibles para los filtros seleccionados.")

# --- TABLA DE DATOS ---
st.markdown("---")
if st.checkbox("Mostrar tabla de datos filtrados"):
    st.write(f"Mostrando {len(filtered_df)} registros")
    st.dataframe(filtered_df)

