"""
Análisis de Reportes IMEI
============================
Script para analizar datos de activación/desactivación de IMEI en redes móviles.
Genera reportes estadísticos y visualizaciones de los datos.

Uso:
    python3 AnalisisReporte.py                    # Usa lista1.xlsx por defecto
    python3 AnalisisReporte.py archivo.xlsx       # Especifica archivo
    python3 AnalisisReporte.py -h                 # Muestra ayuda

Autor: Percy Beltrán
Fecha: 2026-04-05
"""

# ============================================================================
# IMPORTACIONES
# ============================================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import os
import sys
import argparse

# Configuración de matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ============================================================================
# CONFIGURACIÓN
# ============================================================================
DIRECTORIO_SALIDA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DEFECTO = 'lista1.xlsx'


def obtener_ruta_archivo(archivo_arg=None):
    """
    Obtiene la ruta del archivo a procesar.
    
    Parameters:
    -----------
    archivo_arg : str, optional
        Ruta del archivo proporcionada como argumento
        
    Returns:
    --------
    str
        Ruta absoluta del archivo
    """
    # Usar argumento si se proporciona, si no usar por defecto
    nombre_archivo = archivo_arg or ARCHIVO_DEFECTO
    
    # Si es ruta relativa, convertir a absoluta en el directorio del script
    if not os.path.isabs(nombre_archivo):
        ruta_archivo = os.path.join(DIRECTORIO_SALIDA, nombre_archivo)
    else:
        ruta_archivo = nombre_archivo
    
    return ruta_archivo


def listar_archivos_excel():
    """
    Lista los archivos Excel disponibles en el directorio."""
    archivos_excel = [f for f in os.listdir(DIRECTORIO_SALIDA) if f.endswith('.xlsx')]
    return archivos_excel


# ============================================================================
# FUNCIONES DE CARGA Y PREPARACIÓN
# ============================================================================
def cargar_datos(ruta_archivo: str) -> pd.DataFrame:
    """
    Carga datos desde un archivo Excel.
    
    Parameters:
    -----------
    ruta_archivo : str
        Ruta completa al archivo Excel
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con los datos cargados
    """
    try:
        df = pd.read_excel(ruta_archivo)
        print(f"✓ Datos cargados correctamente desde: {ruta_archivo}")
        print(f"  Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas\n")
        return df
    except FileNotFoundError:
        print(f"✗ Error: Archivo no encontrado en {ruta_archivo}\n")
        
        # Listar archivos Excel disponibles
        archivos_disponibles = listar_archivos_excel()
        if archivos_disponibles:
            print("📁 Archivos Excel disponibles en el directorio:")
            for archivo in archivos_disponibles:
                print(f"   • {archivo}")
        else:
            print("⚠️  No hay archivos Excel (.xlsx) en el directorio")
        print()
        return None
    except Exception as e:
        print(f"✗ Error al leer el archivo: {str(e)}\n")
        return None


def preparar_fechas(df: pd.DataFrame, columna_fecha: str = 'Fecha y Hora de Vinculación/Desvinculación') -> pd.DataFrame:
    """
    Convierte columna de fechas a formato datetime.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame a modificar
    columna_fecha : str
        Nombre de la columna con fechas
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con fechas convertidas
    """
    df[columna_fecha] = pd.to_datetime(df[columna_fecha], dayfirst=True, errors='coerce')
    return df


# ============================================================================
# ANÁLISIS ESTADÍSTICO
# ============================================================================
def analisis_imei_por_documento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cuenta cuántos IMEI tiene cada número de documento legal.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con conteo de IMEI por documento
    """
    conteo = df.groupby('Número Documento Legal del Abonado')['IMEI'].count().reset_index()
    conteo.columns = ['Número Documento', 'Cantidad de IMEI']
    
    print("=" * 70)
    print("REPORTE ESTADÍSTICO: CANTIDAD DE IMEI POR DOCUMENTO")
    print("=" * 70)
    print(conteo.to_string(index=False))
    print("\n")
    
    return conteo


def analisis_activaciones_por_fecha(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa activaciones por fecha.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con conteo de activaciones por fecha
    """
    # Filtrar solo registros de vinculación
    df_activaciones = df[df['Tipo'] == 'Vinculación'].copy()
    
    # Agrupar por fecha
    activaciones = df_activaciones.groupby(
        df_activaciones['Fecha y Hora de Vinculación/Desvinculación'].dt.date
    ).size().reset_index(name='Cantidad de Activaciones')
    
    print("=" * 70)
    print("PATRÓN TEMPORAL: ACTIVACIONES POR FECHA")
    print("=" * 70)
    print(activaciones.to_string(index=False))
    print("\n")
    
    return activaciones


# ============================================================================
# VISUALIZACIONES
# ============================================================================
def grafico_serie_temporal(activaciones: pd.DataFrame, nombre_archivo: str = 'grafico_tiempo.png') -> None:
    """
    Crea gráfico de línea con patrón temporal de activaciones.
    
    Parameters:
    -----------
    activaciones : pd.DataFrame
        DataFrame con activaciones por fecha
    nombre_archivo : str
        Nombre del archivo de salida
    """
    plt.figure(figsize=(12, 6))
    plt.plot(
        activaciones['Fecha y Hora de Vinculación/Desvinculación'],
        activaciones['Cantidad de Activaciones'],
        marker='o',
        linewidth=2,
        markersize=8,
        color='#2E86AB'
    )
    
    plt.title('Patrón de Activaciones de IMEI por Fecha', fontsize=14, fontweight='bold')
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Cantidad de Activaciones', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    ruta_salida = f"{DIRECTORIO_SALIDA}/{nombre_archivo}"
    plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico temporal guardado: {nombre_archivo}")
    plt.close()


def grafico_relacional(df: pd.DataFrame, nombre_archivo: str = 'grafico_relacional.png') -> None:
    """
    Crea gráfico relacional entre servicios móviles e IMEI.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
    nombre_archivo : str
        Nombre del archivo de salida
    """
    # Crear grafo
    G = nx.Graph()
    
    # Agrupar IMEI por servicio móvil
    servicios_imei = df.groupby('Número Servicio Móvil')['IMEI'].apply(list).to_dict()
    
    # Agregar nodos y conexiones
    for servicio, imei_list in servicios_imei.items():
        G.add_node(servicio, shape='circle')
        for imei in imei_list:
            G.add_node(imei, shape='box')
            G.add_edge(servicio, imei)
    
    # Preparar etiquetas de nodos
    documento = df['Número Documento Legal del Abonado'].iloc[0]
    labels = {servicio: f"{servicio}\n{documento}" for servicio in servicios_imei.keys()}
    labels.update({imei: str(imei) for imei_list in servicios_imei.values() for imei in imei_list})
    
    # Preparar etiquetas de edges (fechas de activación)
    edge_labels = _crear_etiquetas_edges(df)
    
    # Calcular posiciones
    pos = _calcular_posiciones(servicios_imei)
    
    # Dibujar grafo
    plt.figure(figsize=(14, 14))
    
    # Nodos de servicios (círculos azules)
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=list(servicios_imei.keys()),
        node_shape='o',
        node_color='#A23B72',
        node_size=2500,
        alpha=0.9
    )
    
    # Nodos de IMEI (cuadrados verdes)
    imei_nodes = [n for sublist in servicios_imei.values() for n in sublist]
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=imei_nodes,
        node_shape='s',
        node_color='#F18F01',
        node_size=1500,
        alpha=0.9
    )
    
    # Edges (conexiones)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.6, edge_color='#888888')
    
    # Etiquetas
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
    
    plt.title('Relación entre Número de Servicio Móvil y IMEI Vinculados\n(con Fechas de Activación)',
              fontsize=14, fontweight='bold')
    plt.axis('off')
    
    ruta_salida = f"{DIRECTORIO_SALIDA}/{nombre_archivo}"
    plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico relacional guardado: {nombre_archivo}")
    plt.close()


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def _crear_etiquetas_edges(df: pd.DataFrame) -> dict:
    """
    Crea etiquetas con fechas para los edges del grafo.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    dict
        Diccionario con etiquetas de edges
    """
    edge_labels = {}
    for _, row in df.iterrows():
        service = row['Número Servicio Móvil']
        imei = row['IMEI']
        fecha = row['Fecha y Hora de Vinculación/Desvinculación']
        
        # Formatear fecha
        if pd.notna(fecha):
            date_str = fecha.strftime('%d/%m/%Y')
        else:
            date_str = 'N/A'
        
        # Usar tupla ordenada como clave
        edge_key = tuple(sorted([service, imei]))
        edge_labels[edge_key] = date_str
    
    return edge_labels


def _calcular_posiciones(servicios_imei: dict) -> dict:
    """
    Calcula posiciones de nodos para el grafo.
    
    Parameters:
    -----------
    servicios_imei : dict
        Diccionario con servicios y sus IMEI
        
    Returns:
    --------
    dict
        Diccionario con posiciones (x, y) para cada nodo
    """
    pos = {}
    servicios = list(servicios_imei.keys())
    n_servicios = len(servicios)
    
    if n_servicios == 1:
        # Si hay un solo servicio, colocarlo en el centro
        pos[servicios[0]] = (0, 0)
        imei_list = servicios_imei[servicios[0]]
        n_imei = len(imei_list)
        
        for i, imei in enumerate(imei_list):
            angle = 2 * np.pi * i / n_imei
            pos[imei] = (np.cos(angle), np.sin(angle))
    else:
        # Si hay múltiples servicios, distribuirlos en círculo
        for i, servicio in enumerate(servicios):
            angle_s = 2 * np.pi * i / n_servicios
            pos[servicio] = (2 * np.cos(angle_s), 2 * np.sin(angle_s))
            
            imei_list = servicios_imei[servicio]
            n_imei = len(imei_list)
            
            for j, imei in enumerate(imei_list):
                angle_i = 2 * np.pi * j / n_imei
                pos[imei] = (pos[servicio][0] + np.cos(angle_i), pos[servicio][1] + np.sin(angle_i))
    
    return pos


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def main(archivo=None):
    """
    Función principal que coordina todo el análisis.
    
    Parameters:
    -----------
    archivo : str, optional
        Ruta al archivo Excel a procesar
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS DE REPORTES IMEI")
    print("=" * 70 + "\n")
    
    # Obtener ruta del archivo
    ruta_archivo = obtener_ruta_archivo(archivo)
    
    # Cargar datos
    df = cargar_datos(ruta_archivo)
    if df is None:
        return
    
    # Mostrar vista previa
    print("VISTA PREVIA DE LOS DATOS:")
    print("-" * 70)
    print(df.head().to_string())
    print("\n")
    
    # Preparar datos
    df = preparar_fechas(df)
    
    # Realizar análisis
    conteo_documentos = analisis_imei_por_documento(df)
    activaciones = analisis_activaciones_por_fecha(df)
    
    # Generar visualizaciones
    print("=" * 70)
    print("GENERANDO VISUALIZACIONES...")
    print("=" * 70 + "\n")
    
    grafico_serie_temporal(activaciones)
    grafico_relacional(df)
    
    print("=" * 70)
    print("✓ ANÁLISIS COMPLETADO")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description='Análisis de Reportes IMEI - Visualiza datos de activación de dispositivos móviles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 AnalisisReporte.py                  # Usa lista1.xlsx por defecto
  python3 AnalisisReporte.py archivo.xlsx    # Especifica archivo relativo
  python3 AnalisisReporte.py /ruta/archivo.xlsx  # Especifica ruta absoluta
        """
    )
    
    parser.add_argument(
        'archivo',
        nargs='?',
        default=None,
        help='Archivo Excel a procesar (default: lista1.xlsx)'
    )
    
    args = parser.parse_args()
    main(args.archivo)
