"""
Aplicación Web Streamlit - Análisis de Reportes IMEI
=====================================================
Interfaz web interactiva para análisis de activación/desactivación de IMEI.
Permite carga de archivos Excel y visualización de reportes estadísticos y gráficos.

Uso: streamlit run app_streamlit.py
Autor: Percy Beltrán
Fecha: 2026-04-05
"""

# ============================================================================
# IMPORTACIONES
# ============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

# Configurar página
st.set_page_config(
    page_title="Análisis IMEI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de estilos
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def preparar_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte columna de fechas a formato datetime.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame a procesar
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con fechas convertidas
    """
    df['Fecha y Hora de Vinculación/Desvinculación'] = pd.to_datetime(
        df['Fecha y Hora de Vinculación/Desvinculación'],
        dayfirst=True,
        errors='coerce'
    )
    return df


def obtener_estadisticas_documento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula cantidad de IMEI por número de documento.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    pd.DataFrame
        Estadísticas de IMEI por documento
    """
    estadisticas = df.groupby('Número Documento Legal del Abonado')['IMEI'].count().reset_index()
    estadisticas.columns = ['Número Documento', 'Cantidad de IMEI']
    return estadisticas


def obtener_activaciones_por_fecha(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa y cuenta activaciones por fecha.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    pd.DataFrame
        Activaciones por fecha
    """
    df_activaciones = df[df['Tipo'] == 'Vinculación'].copy()
    activaciones = df_activaciones.groupby(
        df_activaciones['Fecha y Hora de Vinculación/Desvinculación'].dt.date
    ).size().reset_index(name='Cantidad de Activaciones')
    return activaciones


def crear_grafico_temporal(activaciones: pd.DataFrame):
    """
    Crea gráfico de línea con serie temporal.
    
    Parameters:
    -----------
    activaciones : pd.DataFrame
        DataFrame con activaciones por fecha
        
    Returns:
    --------
    matplotlib.figure.Figure
        Figura del gráfico
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        activaciones['Fecha y Hora de Vinculación/Desvinculación'],
        activaciones['Cantidad de Activaciones'],
        marker='o',
        linewidth=2,
        markersize=8,
        color='#2E86AB'
    )
    ax.set_title('Patrón de Activaciones de IMEI por Fecha', fontsize=14, fontweight='bold')
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Cantidad de Activaciones', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def crear_etiquetas_edges(df: pd.DataFrame) -> dict:
    """
    Crea etiquetas con fechas para los edges del grafo.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    dict
        Etiquetas para edges
    """
    edge_labels = {}
    for _, row in df.iterrows():
        service = row['Número Servicio Móvil']
        imei = row['IMEI']
        fecha = row['Fecha y Hora de Vinculación/Desvinculación']
        
        if pd.notna(fecha):
            date_str = fecha.strftime('%d/%m/%Y')
        else:
            date_str = 'N/A'
        
        edge_key = tuple(sorted([service, imei]))
        edge_labels[edge_key] = date_str
    
    return edge_labels


def calcular_posiciones_grafo(servicios_imei: dict) -> dict:
    """
    Calcula posiciones para nodos del grafo relacional.
    
    Parameters:
    -----------
    servicios_imei : dict
        Diccionario con servicios y sus IMEI
        
    Returns:
    --------
    dict
        Posiciones (x, y) para cada nodo
    """
    pos = {}
    servicios = list(servicios_imei.keys())
    n_servicios = len(servicios)
    
    if n_servicios == 1:
        # Un solo servicio al centro
        pos[servicios[0]] = (0, 0)
        imei_list = servicios_imei[servicios[0]]
        n_imei = len(imei_list)
        
        for i, imei in enumerate(imei_list):
            angle = 2 * np.pi * i / n_imei
            pos[imei] = (np.cos(angle), np.sin(angle))
    else:
        # Múltiples servicios distribuidos en círculo
        for i, servicio in enumerate(servicios):
            angle_s = 2 * np.pi * i / n_servicios
            pos[servicio] = (2 * np.cos(angle_s), 2 * np.sin(angle_s))
            
            imei_list = servicios_imei[servicio]
            n_imei = len(imei_list)
            
            for j, imei in enumerate(imei_list):
                angle_i = 2 * np.pi * j / n_imei
                pos[imei] = (pos[servicio][0] + np.cos(angle_i), pos[servicio][1] + np.sin(angle_i))
    
    return pos


def crear_grafico_relacional(df: pd.DataFrame):
    """
    Crea gráfico relacional entre servicios e IMEI.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    matplotlib.figure.Figure
        Figura del gráfico relacional
    """
    # Crear grafo
    G = nx.Graph()
    servicios_imei = df.groupby('Número Servicio Móvil')['IMEI'].apply(list).to_dict()
    
    # Agregar nodos
    for servicio, imei_list in servicios_imei.items():
        G.add_node(servicio, shape='circle')
        for imei in imei_list:
            G.add_node(imei, shape='box')
            G.add_edge(servicio, imei)
    
    # Preparar etiquetas y edges
    documento = df['Número Documento Legal del Abonado'].iloc[0]
    labels = {servicio: f"{servicio}\n{documento}" for servicio in servicios_imei.keys()}
    labels.update({imei: str(imei) for imei_list in servicios_imei.values() for imei in imei_list})
    
    edge_labels = crear_etiquetas_edges(df)
    pos = calcular_posiciones_grafo(servicios_imei)
    
    # Dibujar grafo
    fig, ax = plt.subplots(figsize=(14, 14))
    
    # Nodos de servicios (círculos)
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=list(servicios_imei.keys()),
        node_shape='o',
        node_color='#A23B72',
        node_size=2500,
        alpha=0.9,
        ax=ax
    )
    
    # Nodos de IMEI (cuadrados)
    imei_nodes = [n for sublist in servicios_imei.values() for n in sublist]
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=imei_nodes,
        node_shape='s',
        node_color='#F18F01',
        node_size=1500,
        alpha=0.9,
        ax=ax
    )
    
    # Conexiones y etiquetas
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.6, edge_color='#888888', ax=ax)
    nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, ax=ax)
    
    ax.set_title(
        'Relación entre Número de Servicio Móvil y IMEI Vinculados\n(con Fechas de Activación)',
        fontsize=14,
        fontweight='bold'
    )
    ax.axis('off')
    
    return fig


# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================
def main():
    """Función principal que ejecuta la aplicación Streamlit."""
    
    # Título y descripción
    st.title("📊 Análisis de Reportes IMEI")
    st.markdown("""
    Aplicación interactiva para análisis de datos de activación/desactivación de IMEI.
    Carga un archivo Excel y obtén reportes estadísticos y visualizaciones.
    """)
    
    # Barra lateral con información
    with st.sidebar:
        st.header("ℹ️ Información")
        st.markdown("""
        ### Características:
        - 📈 Análisis estadístico de IMEI por documento
        - 📅 Patrón temporal de activaciones
        - 🕸️ Gráfico relacional servicio-IMEI
        
        ### Requisitos:
        - Archivo Excel (.xlsx)
        - Columnas: Número Servicio Móvil, IMEI, Fecha, etc.
        """)
    
    # Widget para cargar archivo
    uploaded_file = st.file_uploader(
        "📁 Sube tu archivo Excel",
        type=["xlsx"],
        help="Selecciona un archivo Excel con datos de IMEI"
    )
    
    if uploaded_file is not None:
        try:
            # Cargar y preparar datos
            df = pd.read_excel(uploaded_file)
            df = preparar_fechas(df)
            
            # Mostrar datos cargados
            with st.expander("👁️ Vista Previa de Datos"):
                st.dataframe(df.head(), use_container_width=True)
                st.info(f"Total de registros: {len(df)} | Columnas: {len(df.columns)}")
            
            # Tabulación de resultados
            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "📈 Temporal", "🕸️ Grafo Relacional"])
            
            # Tab 1: Estadísticas
            with tab1:
                st.subheader("Cantidad de IMEI por Número de Documento")
                estadisticas = obtener_estadisticas_documento(df)
                st.dataframe(estadisticas, use_container_width=True)
                
                # Métrica destacada
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Documentos", estadisticas['Número Documento'].nunique())
                with col2:
                    st.metric("Total de IMEI", estadisticas['Cantidad de IMEI'].sum())
                with col3:
                    st.metric("Promedio por Doc.", f"{estadisticas['Cantidad de IMEI'].mean():.1f}")
            
            # Tab 2: Análisis temporal
            with tab2:
                st.subheader("Patrón Temporal de Activaciones")
                activaciones = obtener_activaciones_por_fecha(df)
                
                # Mostrar tabla
                st.dataframe(activaciones, use_container_width=True)
                
                # Mostrar gráfico
                fig = crear_grafico_temporal(activaciones)
                st.pyplot(fig)
            
            # Tab 3: Grafo relacional
            with tab3:
                st.subheader("Grafo Relacional: Servicios e IMEI")
                fig = crear_grafico_relacional(df)
                st.pyplot(fig)
        
        except Exception as e:
            st.error(f"⚠️ Error procesando archivo: {str(e)}")
            st.info("Verifica que el archivo tenga las columnas esperadas.")
    
    else:
        # Mensaje cuando no hay archivo
        st.info("👆 Por favor, sube un archivo Excel para comenzar el análisis.")
        st.markdown("""
        ### Formato esperado:
        El archivo debe contener las siguientes columnas:
        - `Número Servicio Móvil`
        - `IMEI`
        - `Número Documento Legal del Abonado`
        - `Fecha y Hora de Vinculación/Desvinculación`
        - `Tipo` (Vinculación/Desvinculación)
        """)


if __name__ == "__main__":
    main()