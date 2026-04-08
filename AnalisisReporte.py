import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# =============================================================================
# CONFIGURACIÓN GENERAL
# =============================================================================
st.set_page_config(page_title="Analisis IMEI", layout="wide")

COLUMNAS_REQUERIDAS = [
    'Número Servicio Móvil',
    'IMEI',
    'Número Documento Legal del Abonado',
    'Fecha y Hora de Vinculación/Desvinculación',
    'Tipo'
]

# =============================================================================
# CARGA DE DATOS
# =============================================================================
@st.cache_data
def cargar_excel(archivo):
    """
    Carga archivo Excel con cache para mejorar rendimiento.

    Parameters:
        archivo (UploadedFile): archivo cargado desde Streamlit

    Returns:
        DataFrame: datos del Excel
    """
    return pd.read_excel(archivo)


# =============================================================================
# LIMPIEZA Y PREPARACIÓN
# =============================================================================
def limpiar_columnas(df):
    """
    Elimina espacios en nombres de columnas.

    Parameters:
        df (DataFrame)

    Returns:
        DataFrame limpio
    """
    df.columns = df.columns.str.strip()
    return df


def preparar_datos(df):
    """
    Prepara los datos para análisis:
    - Limpia columnas
    - Convierte fechas
    - Elimina registros inválidos

    Returns:
        DataFrame limpio y listo
    """
    df = limpiar_columnas(df)

    df['Fecha y Hora de Vinculación/Desvinculación'] = pd.to_datetime(
        df['Fecha y Hora de Vinculación/Desvinculación'],
        errors='coerce',
        dayfirst=True
    )

    # eliminar registros con fecha inválida
    df = df.dropna(subset=['Fecha y Hora de Vinculación/Desvinculación'])

    return df


# =============================================================================
# VALIDACIÓN
# =============================================================================
def validar_estructura(df):
    """
    Verifica que el archivo tenga la estructura correcta.

    Returns:
        bool
    """
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]

    if faltantes:
        st.error(f"❌ Faltan columnas: {faltantes}")
        return False

    return True


# =============================================================================
# ANÁLISIS
# =============================================================================
def imei_por_fecha(df):
    """
    Calcula cantidad de IMEI activados por fecha.

    Returns:
        DataFrame
    """
    df = df[df['Tipo'] == 'Vinculación']

    if df.empty:
        return pd.DataFrame(columns=['Fecha', 'IMEI Activados'])

    resultado = (
        df.groupby(df['Fecha y Hora de Vinculación/Desvinculación'].dt.date)['IMEI']
        .nunique()
        .reset_index(name='IMEI Activados')
    )

    resultado.columns = ['Fecha', 'IMEI Activados']
    return resultado


def detectar_sospechosos(df):
    """
    Detecta IMEI usados por múltiples números.

    Returns:
        DataFrame
    """
    sospechosos = (
        df.groupby('IMEI')['Número Servicio Móvil']
        .nunique()
        .reset_index(name='Cantidad Numeros')
    )

    return sospechosos[sospechosos['Cantidad Numeros'] > 1]


def detectar_clusters(df):
    """
    Detecta redes (componentes conectados).

    Returns:
        DataFrame
    """
    df = df[df['Tipo'] == 'Vinculación']

    G = nx.Graph()

    for _, r in df.iterrows():
        G.add_edge(str(r['Número Servicio Móvil']), str(r['IMEI']))

    clusters = list(nx.connected_components(G))

    resultado = [
        {
            "Cluster ID": i + 1,
            "Nodos": len(cluster),
            "Elementos": ", ".join(cluster)
        }
        for i, cluster in enumerate(clusters)
    ]

    return pd.DataFrame(resultado)


# =============================================================================
# VISUALIZACIÓN (GRAFO)
# =============================================================================
def grafo_relacional(df):
    """
    Genera grafo visual de relaciones:
    - Servicios (con DNI)
    - IMEI

    Uses:
        NetworkX + Matplotlib
    """
    df = df[df['Tipo'] == 'Vinculación']

    if df.empty:
        st.warning("No hay datos para graficar")
        return

    G = nx.Graph()

    for _, r in df.iterrows():
        servicio = str(r['Número Servicio Móvil'])
        imei = str(r['IMEI'])
        dni = str(r['Número Documento Legal del Abonado'])

        G.add_node(servicio, label=f"{servicio}\nDNI:{dni}", tipo="servicio")
        G.add_node(imei, label=f"IMEI\n{imei}", tipo="imei")
        G.add_edge(servicio, imei)

    # Layout del grafo
    pos = nx.spring_layout(G, k=1.2, iterations=50)

    plt.figure(figsize=(14, 12))

    servicios = [n for n, d in G.nodes(data=True) if d["tipo"] == "servicio"]
    imeis = [n for n, d in G.nodes(data=True) if d["tipo"] == "imei"]

    nx.draw_networkx_nodes(G, pos, nodelist=servicios, node_size=3000, node_color="#1f77b4")
    nx.draw_networkx_nodes(G, pos, nodelist=imeis, node_size=1800, node_color="#2ca02c")

    nx.draw_networkx_edges(G, pos, edge_color="#999999", width=2)

    labels = nx.get_node_attributes(G, 'label')

    nx.draw_networkx_labels(
        G,
        pos,
        labels=labels,
        font_size=10,
        font_weight="bold"
    )

    plt.title("Relación Servicio - IMEI (con DNI)", fontsize=20)
    plt.axis("off")

    st.pyplot(plt)
    plt.clf()


# =============================================================================
# INTERFAZ (UI)
# =============================================================================
st.title("📱 Sistema de Análisis IMEI")

archivo = st.file_uploader("📂 Subir archivo Excel", type=["xlsx"])

if archivo:
    try:
        df = cargar_excel(archivo)

        if validar_estructura(df):
            df = preparar_datos(df)

            st.success("✅ Archivo válido")

            df_v = df[df['Tipo'] == 'Vinculación']

            # ==========================
            # MÉTRICAS
            # ==========================
            col1, col2 = st.columns(2)

            col1.metric("📱 IMEI únicos", df_v['IMEI'].nunique())
            col2.metric(
                "📅 Fechas",
                df_v['Fecha y Hora de Vinculación/Desvinculación'].dt.date.nunique()
            )

            # ==========================
            # TABLA
            # ==========================
            tabla = imei_por_fecha(df)

            st.subheader("📊 IMEI activados por fecha")

            if not tabla.empty:
                tabla['Fecha'] = pd.to_datetime(tabla['Fecha']).dt.strftime('%d/%m/%Y')
                st.dataframe(tabla, use_container_width=True)

                fecha = st.selectbox("Seleccionar fecha", tabla['Fecha'])
                valor = tabla[tabla['Fecha'] == fecha]['IMEI Activados'].values[0]

                st.info(f"📌 IMEI activados el {fecha}: {valor}")

            # ==========================
            # ANÁLISIS AVANZADO
            # ==========================
            st.subheader("🚨 IMEI Sospechosos")
            st.dataframe(detectar_sospechosos(df))

            st.subheader("🧠 Clusters detectados")
            st.dataframe(detectar_clusters(df), use_container_width=True)

            # ==========================
            # GRAFO
            # ==========================
            st.subheader("🕸️ Grafo relacional")
            grafo_relacional(df)

    except Exception as e:
        st.error(f"❌ Error procesando archivo: {e}")