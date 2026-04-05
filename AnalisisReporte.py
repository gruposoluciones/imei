"""
Análisis de Reportes IMEI
============================
Script para analizar datos de activación/desactivación de IMEI en redes móviles.
Genera reportes estadísticos y visualizaciones de los datos.

ESTRUCTURA REQUERIDA DEL ARCHIVO:
  Las siguientes columnas son OBLIGATORIAS:
  - Número Servicio Móvil
  - IMEI
  - Número Documento Legal del Abonado
  - Fecha y Hora de Vinculación/Desvinculación
  - Tipo (valores: 'Vinculación' o 'Desvinculación')

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

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
# Configuración de matplotlib para mejor visualización
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Rutas y archivos
DIRECTORIO_SALIDA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DEFECTO = 'lista1.xlsx'

# Estructura requerida del archivo Excel
COLUMNAS_REQUERIDAS = {
    'Número Servicio Móvil': 'str',
    'IMEI': 'str',
    'Número Documento Legal del Abonado': 'str',
    'Fecha y Hora de Vinculación/Desvinculación': 'datetime',
    'Tipo': 'str'  # Debe contener: 'Vinculación' o 'Desvinculación'
}


# ============================================================================
# FUNCIONES DE CONFIGURACIÓN Y VALIDACIÓN
# ============================================================================
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


def validar_estructura_archivo(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Valida que el DataFrame cumpla con la estructura requerida.
    
    Verifica:
    - Presencia de todas las columnas obligatorias
    - Ausencia de valores nulos en columnas críticas
    - Validez de datos en campos específicos
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame a validar
        
    Returns:
    --------
    tuple[bool, str]
        (es_válido, mensaje_error)
        Si es_válido es True, mensaje_error será vacío
    """
    # Verificar columnas requeridas
    columnas_faltantes = set(COLUMNAS_REQUERIDAS.keys()) - set(df.columns)
    
    if columnas_faltantes:
        mensaje_error = f"❌ Columnas faltantes en el archivo:\n"
        mensaje_error += f"   Faltan: {', '.join(columnas_faltantes)}\n\n"
        mensaje_error += f"📋 Columnas requeridas:\n"
        for col in COLUMNAS_REQUERIDAS.keys():
            mensaje_error += f"   • {col}\n"
        return False, mensaje_error
    
    # Verificar valores nulos en columnas críticas
    columnas_criticas = list(COLUMNAS_REQUERIDAS.keys())
    valores_nulos = df[columnas_criticas].isnull().sum()
    
    if valores_nulos.any():
        mensaje_error = f"❌ Se encontraron valores nulos en columnas obligatorias:\n"
        for col, count in valores_nulos[valores_nulos > 0].items():
            mensaje_error += f"   • {col}: {count} valores nulos\n"
        return False, mensaje_error
    
    # Verificar valores válidos en columna 'Tipo'
    tipos_válidos = {'Vinculación', 'Desvinculación'}
    tipos_encontrados = set(df['Tipo'].unique())
    tipos_inválidos = tipos_encontrados - tipos_válidos
    
    if tipos_inválidos:
        mensaje_error = f"❌ Valores inválidos en columna 'Tipo':\n"
        mensaje_error += f"   Encontrados: {tipos_inválidos}\n"
        mensaje_error += f"   Válidos: {tipos_válidos}\n"
        return False, mensaje_error
    
    return True, ""


def listar_archivos_excel():
    """
    Lista los archivos Excel disponibles en el directorio.
    
    Returns:
    --------
    list
        Lista de nombres de archivos .xlsx encontrados
    """
    archivos_excel = [f for f in os.listdir(DIRECTORIO_SALIDA) if f.endswith('.xlsx')]
    return archivos_excel


# ============================================================================
# FUNCIONES DE CARGA Y PREPARACIÓN
# ============================================================================
def cargar_datos(ruta_archivo: str) -> pd.DataFrame:
    """
    Carga datos desde un archivo Excel y valida la estructura.
    
    Este función:
    1. Intenta abrir el archivo Excel
    2. Valida que contenga todas las columnas requeridas
    3. Verifica la integridad de los datos
    4. Rechaza archivos que no cumplan con la estructura
    
    Parameters:
    -----------
    ruta_archivo : str
        Ruta completa al archivo Excel
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con los datos cargados y validados
        None si hay error
    """
    # Paso 1: Verificar existencia del archivo
    if not os.path.exists(ruta_archivo):
        print(f"❌ Error: Archivo no encontrado en {ruta_archivo}\n")
        
        # Listar archivos Excel disponibles como sugerencia
        archivos_disponibles = listar_archivos_excel()
        if archivos_disponibles:
            print("📁 Archivos Excel disponibles en el directorio:")
            for archivo in archivos_disponibles:
                print(f"   • {archivo}")
        else:
            print("⚠️  No hay archivos Excel (.xlsx) en el directorio")
        print()
        return None
    
    # Paso 2: Intentar leer el archivo
    try:
        df = pd.read_excel(ruta_archivo)
        print(f"✓ Archivo leído correctamente: {ruta_archivo}")
        print(f"  Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas\n")
    except Exception as e:
        print(f"❌ Error al leer el archivo Excel: {str(e)}\n")
        return None
    
    # Paso 3: Validar estructura del archivo
    es_válido, mensaje_error = validar_estructura_archivo(df)
    
    if not es_válido:
        print(f"❌ VALIDACIÓN FALLIDA - Estructura de archivo incorrecta:\n")
        print(mensaje_error)
        print("⚠️  El archivo ha sido rechazado. Corrige la estructura e intenta nuevamente.\n")
        return None
    
    print("✓ Estructura del archivo validada correctamente\n")
    return df


def preparar_fechas(df: pd.DataFrame, columna_fecha: str = 'Fecha y Hora de Vinculación/Desvinculación') -> pd.DataFrame:
    """
    Convierte columna de fechas de tipo string a formato datetime.
    
    Utiliza formato de fecha DIA/MES/AÑO (europeo) y maneja errores de conversión.
    Las fechas que no puedan ser convertidas se marcan como NaT (Not a Time).
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame a modificar
    columna_fecha : str
        Nombre de la columna con fechas (default: 'Fecha y Hora de Vinculación/Desvinculación')
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con fechas convertidas al tipo datetime64
    """
    try:
        df[columna_fecha] = pd.to_datetime(df[columna_fecha], dayfirst=True, errors='coerce')
        # Verificar si hay fechas inválidas
        fechas_inválidas = df[columna_fecha].isnull().sum()
        if fechas_inválidas > 0:
            print(f"⚠️  {fechas_inválidas} fechas no pudieron ser convertidas (marcadas como NaT)")
    except Exception as e:
        print(f"⚠️  Error al convertir fechas: {str(e)}")
    
    return df


# ============================================================================
# ANÁLISIS ESTADÍSTICO
# ============================================================================
def analisis_imei_por_documento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Análisis estadístico: Cuenta cuántos IMEI tiene cada documento legal.
    
    Agrupa el DataFrame por 'Número Documento Legal del Abonado' y cuenta
    la cantidad de IMEI únicos asociados a cada documento.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con columnas:
        - Número Documento: ID del documento legal
        - Cantidad de IMEI: cantidad de IMEI vinculados
    """
    # Agrupar por documento y contar IMEI únicos
    conteo = df.groupby('Número Documento Legal del Abonado')['IMEI'].count().reset_index()
    conteo.columns = ['Número Documento', 'Cantidad de IMEI']
    
    # Ordenar por cantidad descendente para mejor legibilidad
    conteo = conteo.sort_values('Cantidad de IMEI', ascending=False).reset_index(drop=True)
    
    # Mostrar resultado formateado
    print("=" * 70)
    print("REPORTE ESTADÍSTICO: CANTIDAD DE IMEI POR DOCUMENTO")
    print("=" * 70)
    print(f"Total de documentos: {len(conteo)}")
    print(f"Total de IMEI: {conteo['Cantidad de IMEI'].sum()}")
    print(f"Promedio IMEI por documento: {conteo['Cantidad de IMEI'].mean():.2f}")
    print("-" * 70)
    print(conteo.to_string(index=False))
    print("\n")
    
    return conteo


def analisis_activaciones_por_fecha(df: pd.DataFrame) -> pd.DataFrame:
    """
    Análisis temporal: Agrupa y cuenta activaciones por fecha.
    
    Filtra solo los registros de tipo 'Vinculación' y agrupa por fecha,
    contando la cantidad de activaciones por cada día.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos (debe tener fechas convertidas a datetime)
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con columnas:
        - Fecha y Hora de Vinculación/Desvinculación: fecha del evento
        - Cantidad de Activaciones: cantidad de eventos ese día
    """
    # Filtrar solo registros de vinculación (activaciones)
    df_activaciones = df[df['Tipo'] == 'Vinculación'].copy()
    
    # Agrupar por fecha (extraer solo la fecha, sin hora)
    activaciones = df_activaciones.groupby(
        df_activaciones['Fecha y Hora de Vinculación/Desvinculación'].dt.date
    ).size().reset_index(name='Cantidad de Activaciones')
    
    # Mostrar resultado formateado
    print("=" * 70)
    print("PATRÓN TEMPORAL: ACTIVACIONES POR FECHA")
    print("=" * 70)
    print(f"Total de fechas: {len(activaciones)}")
    print(f"Total de activaciones: {activaciones['Cantidad de Activaciones'].sum()}")
    print(f"Promedio activaciones/día: {activaciones['Cantidad de Activaciones'].mean():.2f}")
    print("-" * 70)
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
    Visualización: Crea gráfico relacional (grafo) entre servicios móviles e IMEI.
    
    Genera un grafo donde:
    - NODOS: Números de servicio móvil (círculos) e IMEI (cuadrados)
    - CONEXIONES: Líneas que unen servicios con sus IMEI vinculados
    - ETIQUETAS: Fechas de activación en cada conexión
    
    Utiliza posicionamiento automático para optimizar visualización.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos (debe tener fechas ya convertidas)
    nombre_archivo : str
        Nombre del archivo de salida (default: 'grafico_relacional.png')
        
    Returns:
    --------
    None
        Guarda el gráfico en el directorio de salida
    """
    try:
        # PASO 1: Crear grafo vacío
        G = nx.Graph()
        
        # PASO 2: Agrupar IMEI por servicio móvil
        servicios_imei = df.groupby('Número Servicio Móvil')['IMEI'].apply(list).to_dict()
        
        # PASO 3: Agregar nodos y conexiones al grafo
        # Agregar un nodo por cada servicio y por cada IMEI
        for servicio, imei_list in servicios_imei.items():
            G.add_node(servicio, shape='circle')
            for imei in imei_list:
                G.add_node(imei, shape='box')
                G.add_edge(servicio, imei)  # Conectar servicio con IMEI
        
        # PASO 4: Preparar etiquetas de nodos (incluir documento en servicios)
        documento = df['Número Documento Legal del Abonado'].iloc[0]
        labels = {servicio: f"{servicio}\n{documento}" for servicio in servicios_imei.keys()}
        # Agregar etiquetas para IMEI
        labels.update({imei: str(imei) for imei_list in servicios_imei.values() for imei in imei_list})
        
        # PASO 5: Preparar etiquetas de edges (fechas de activación)
        edge_labels = _crear_etiquetas_edges(df)
        
        # PASO 6: Calcular posiciones de nodos para mejor visualización
        pos = _calcular_posiciones(servicios_imei)
        
        # PASO 7: Crear y configurar figura
        plt.figure(figsize=(14, 14))
        
        # PASO 8a: Dibujar nodos de servicios (círculos - en color magenta)
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=list(servicios_imei.keys()),
            node_shape='o',
            node_color='#A23B72',
            node_size=2500,
            alpha=0.9,
            label='Servicios Móviles'
        )
        
        # PASO 8b: Dibujar nodos de IMEI (cuadrados - en color naranja)
        imei_nodes = [n for sublist in servicios_imei.values() for n in sublist]
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=imei_nodes,
            node_shape='s',
            node_color='#F18F01',
            node_size=1500,
            alpha=0.9,
            label='IMEI Vinculados'
        )
        
        # PASO 9: Dibujar conexiones (edges)
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.6, edge_color='#888888')
        
        # PASO 10: Agregar etiquetas de nodos y edges
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
        
        # PASO 11: Configurar títulos y layout
        plt.title(
            'Relación entre Número de Servicio Móvil y IMEI Vinculados\n(con Fechas de Activación)',
            fontsize=14,
            fontweight='bold'
        )
        plt.axis('off')
        plt.legend(loc='upper left', fontsize=10)
        
        # PASO 12: Guardar archivo
        ruta_salida = os.path.join(DIRECTORIO_SALIDA, nombre_archivo)
        plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico relacional guardado: {nombre_archivo}")
        print(f"  Procesados {len(servicios_imei)} servicio(s) con {len(imei_nodes)} IMEI")
        plt.close()
        
    except Exception as e:
        print(f"❌ Error al generar gráfico relacional: {str(e)}")
        plt.close()


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def _crear_etiquetas_edges(df: pd.DataFrame) -> dict:
    """
    Función auxiliar: Crea etiquetas con fechas para los edges del grafo.
    
    Extrae la fecha de activación de cada conexión servicio-IMEI
    y la usa como etiqueta en el grafo relacional.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns:
    --------
    dict
        Diccionario con etiquetas de edges en formato {(nodo1, nodo2): 'fecha'}
    """
    edge_labels = {}
    
    # Procesar cada fila del DataFrame
    for _, row in df.iterrows():
        service = row['Número Servicio Móvil']
        imei = row['IMEI']
        fecha = row['Fecha y Hora de Vinculación/Desvinculación']
        
        # Convertir fecha a formato string legible
        if pd.notna(fecha):
            date_str = fecha.strftime('%d/%m/%Y')
        else:
            date_str = 'N/A'
        
        # Usar tupla ordenada como clave para identificar edge
        # Esto asegura que (service, imei) y (imei, service) usen la misma clave
        edge_key = tuple(sorted([service, imei]))
        edge_labels[edge_key] = date_str
    
    return edge_labels


def _calcular_posiciones(servicios_imei: dict) -> dict:
    """
    Función auxiliar: Calcula posiciones de nodos para el grafo relacional.
    
    Utiliza un algoritmo de posicionamiento radial donde:
    - Servicios se distribuyen en círculo exterior
    - IMEI de cada servicio se distribuyen alrededor de su servicio
    
    Parameters:
    -----------
    servicios_imei : dict
        Diccionario con servicios y sus IMEI {servicio: [imei1, imei2, ...]}
        
    Returns:
    --------
    dict
        Diccionario con posiciones (x, y) para cada nodo {nodo: (x, y)}
    """
    pos = {}
    servicios = list(servicios_imei.keys())
    n_servicios = len(servicios)
    
    # CASO 1: Un único servicio
    if n_servicios == 1:
        # Colocar servicio en el centro (0, 0)
        pos[servicios[0]] = (0, 0)
        
        # Distribuir IMEI en círculo alrededor del servicio
        imei_list = servicios_imei[servicios[0]]
        n_imei = len(imei_list)
        
        for i, imei in enumerate(imei_list):
            angle = 2 * np.pi * i / n_imei
            pos[imei] = (np.cos(angle), np.sin(angle))
    
    # CASO 2: Múltiples servicios
    else:
        # Distribuir servicios en círculo
        for i, servicio in enumerate(servicios):
            angle_s = 2 * np.pi * i / n_servicios
            pos[servicio] = (2 * np.cos(angle_s), 2 * np.sin(angle_s))
            
            # Distribuir IMEI del servicio alrededor del mismo
            imei_list = servicios_imei[servicio]
            n_imei = len(imei_list)
            
            for j, imei in enumerate(imei_list):
                angle_i = 2 * np.pi * j / n_imei
                # Posicionar IMEI relativo a su servicio
                pos[imei] = (pos[servicio][0] + np.cos(angle_i), pos[servicio][1] + np.sin(angle_i))
    
    return pos


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def main(archivo=None):
    """
    Función principal que coordina todo el análisis de IMEI.
    
    Flujo de ejecución:
    1. Obtiene ruta del archivo (argumento o por defecto)
    2. Carga datos con validación de estructura
    3. Prepara datos (conversión de fechas)
    4. Ejecuta análisis estadístico y temporal
    5. Genera visualizaciones
    
    Parameters:
    -----------
    archivo : str, optional
        Ruta al archivo Excel a procesar
    """
    # Encabezado de ejecución
    print("\n" + "=" * 70)
    print("ANÁLISIS DE REPORTES IMEI")
    print("=" * 70 + "\n")
    
    # PASO 1: Obtener ruta del archivo
    ruta_archivo = obtener_ruta_archivo(archivo)
    
    # PASO 2: Cargar datos (con validación de estructura)
    df = cargar_datos(ruta_archivo)
    if df is None:
        print("❌ El proceso ha sido cancelado debido a errores de validación.\n")
        return
    
    # PASO 3: Mostrar vista previa de datos
    print("VISTA PREVIA DE LOS DATOS:")
    print("-" * 70)
    print(df.head().to_string())
    print("\n")
    
    # PASO 4: Preparar datos (convertir fechas)
    df = preparar_fechas(df)
    
    # PASO 5: Realizar análisis estadístico
    print("=" * 70)
    print("EJECUTANDO ANÁLISIS...")
    print("=" * 70 + "\n")
    
    conteo_documentos = analisis_imei_por_documento(df)
    activaciones = analisis_activaciones_por_fecha(df)
    
    # PASO 6: Generar visualizaciones
    print("=" * 70)
    print("GENERANDO VISUALIZACIONES...")
    print("=" * 70 + "\n")
    
    try:
        grafico_serie_temporal(activaciones)
        grafico_relacional(df)
        print()
    except Exception as e:
        print(f"❌ Error al generar visualizaciones: {str(e)}\n")
    
    # Mensaje de finalización
    print("=" * 70)
    print("✓ ANÁLISIS COMPLETADO EXITOSAMENTE")
    print("=" * 70 + "\n")
    print("📁 Archivos generados:")
    print("   • grafico_tiempo.png (Patrón temporal de activaciones)")
    print("   • grafico_relacional.png (Relación servicio-IMEI)")
    print("\n")


if __name__ == "__main__":
    """
    Punto de entrada del script.
    
    Parsea argumentos de línea de comandos y ejecuta el análisis.
    """
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='Análisis de Reportes IMEI - Visualiza datos de activación de dispositivos móviles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ESTRUCTURA DEL ARCHIVO REQUERIDA:
  El archivo Excel debe contener las siguientes columnas OBLIGATORIAS:
  
  • Número Servicio Móvil     - Código del servicio móvil (texto)
  • IMEI                       - Número de identificación del dispositivo (texto)
  • Número Documento Legal del Abonado - DNI/Documento del propietario (texto)
  • Fecha y Hora de Vinculación/Desvinculación - Fecha del evento (formato: DD/MM/YYYY)
  • Tipo                       - Tipo de evento. Valores válidos: 'Vinculación' o 'Desvinculación'

EJEMPLOS DE USO:
  python3 AnalisisReporte.py                  # Usa lista1.xlsx por defecto
  python3 AnalisisReporte.py archivo.xlsx    # Especifica archivo relativo
  python3 AnalisisReporte.py /ruta/archivo.xlsx  # Especifica ruta absoluta
  python3 AnalisisReporte.py -h              # Muestra esta ayuda

SALIDA:
  El script genera dos archivos PNG en el mismo directorio:
  • grafico_tiempo.png - Gráfico temporal de activaciones
  • grafico_relacional.png - Gráfico de relaciones servicio-IMEI
        """
    )
    
    # Agregar argumentos
    parser.add_argument(
        'archivo',
        nargs='?',
        default=None,
        help='Archivo Excel a procesar (default: lista1.xlsx)'
    )
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar análisis
    main(args.archivo)
