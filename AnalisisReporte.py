#importamos las librerias para cargar datos de excel, csv o txt
import numpy as np 
# numpy es una libreria para el manejo de arreglos y operaciones matematicas
import pandas as pd
# pandas es una libreria para el manejo de datos en forma de tablas (dataframes)
import matplotlib.pyplot as plt
# matplotlib es una libreria para la visualizacion de datos
import seaborn as sns
# seaborn es una libreria para la visualizacion de datos estadisticos
import os
# os es una libreria para el manejo de archivos y directorios
import networkx as nx
# networkx es una libreria para grafos y redes

# Cargar el archivo de datos de excel
# ruta del archivo de excel
df = pd.read_excel('/Users/percybeltran/Proyectos/IMEI/lista1.xlsx')
# Mostrar las primeras filas del dataframe
print(df.head())

# Análisis estadístico: contar cuántos IMEI tiene cada número de documento
conteo_imei_por_documento = df.groupby('Número Documento Legal del Abonado')['IMEI'].count().reset_index()
conteo_imei_por_documento.columns = ['Número Documento', 'Cantidad de IMEI']
print("\nReporte estadístico: Cantidad de IMEI por Número de Documento Legal del Abonado")
print(conteo_imei_por_documento)

# Análisis de patrón temporal: contar activaciones por fecha
# Convertir la columna de fecha a datetime si no lo es
df['Fecha y Hora de Vinculación/Desvinculación'] = pd.to_datetime(df['Fecha y Hora de Vinculación/Desvinculación'], dayfirst=True, errors='coerce')
# Filtrar solo vinculaciones (activaciones)
df_activaciones = df[df['Tipo'] == 'Vinculación']
# Agrupar por fecha (día) y contar
activaciones_por_fecha = df_activaciones.groupby(df_activaciones['Fecha y Hora de Vinculación/Desvinculación'].dt.date).size().reset_index(name='Cantidad de Activaciones')
print("\nPatrón temporal: Cantidad de activaciones por fecha")
print(activaciones_por_fecha)

# Crear gráfico de tiempo (línea)
plt.figure(figsize=(12, 6))
plt.plot(activaciones_por_fecha['Fecha y Hora de Vinculación/Desvinculación'], activaciones_por_fecha['Cantidad de Activaciones'], marker='o')
plt.title('Patrón de Activaciones de IMEI por Fecha')
plt.xlabel('Fecha')
plt.ylabel('Cantidad de Activaciones')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('grafico_tiempo.png')  # Guardar el gráfico como imagen
plt.show()

# Crear gráfico relacional: número de servicio móvil en círculo, IMEI en rectángulos conectados
G = nx.Graph()
# Obtener servicios únicos y sus IMEI
servicios_imei = df.groupby('Número Servicio Móvil')['IMEI'].apply(list).to_dict()
# Agregar nodos y edges
for servicio, imei_list in servicios_imei.items():
    G.add_node(servicio, shape='circle')
    for imei in imei_list:
        G.add_node(imei, shape='box')
        G.add_edge(servicio, imei)
# Etiquetas de nodos: incluir número de documento en el servicio
documento = df['Número Documento Legal del Abonado'].iloc[0]  # Asumiendo mismo documento
labels = {servicio: f"{servicio}\n{documento}" for servicio in servicios_imei.keys()}
labels.update({imei: str(imei) for imei_list in servicios_imei.values() for imei in imei_list})
# Etiquetas de edges: fecha de activación
edge_labels = {}
for _, row in df.iterrows():
    service = row['Número Servicio Móvil']
    imei = row['IMEI']
    date = row['Fecha y Hora de Vinculación/Desvinculación'].strftime('%d/%m/%Y') if pd.notna(row['Fecha y Hora de Vinculación/Desvinculación']) else 'N/A'
    edge_labels[(service, imei)] = date
# Posiciones: servicios en el centro si uno, o distribuidos; IMEI alrededor
pos = {}
servicios = list(servicios_imei.keys())
n_servicios = len(servicios)
if n_servicios == 1:
    pos[servicios[0]] = (0, 0)
    imei_list = servicios_imei[servicios[0]]
    n_imei = len(imei_list)
    for i, imei in enumerate(imei_list):
        angle = 2 * np.pi * i / n_imei
        pos[imei] = (np.cos(angle), np.sin(angle))
else:
    # Si múltiples servicios, colocarlos en círculo y IMEI alrededor de cada uno
    for i, servicio in enumerate(servicios):
        angle_s = 2 * np.pi * i / n_servicios
        pos[servicio] = (2 * np.cos(angle_s), 2 * np.sin(angle_s))
        imei_list = servicios_imei[servicio]
        n_imei = len(imei_list)
        for j, imei in enumerate(imei_list):
            angle_i = 2 * np.pi * j / n_imei
            pos[imei] = (pos[servicio][0] + np.cos(angle_i), pos[servicio][1] + np.sin(angle_i))
# Dibujar el grafo
plt.figure(figsize=(14, 14))
nx.draw_networkx_nodes(G, pos, nodelist=servicios, node_shape='o', node_color='lightblue', node_size=2500)
nx.draw_networkx_nodes(G, pos, nodelist=[n for sublist in servicios_imei.values() for n in sublist], node_shape='s', node_color='lightgreen', node_size=1500)
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos, labels, font_size=8)
nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
plt.title('Relación entre Número de Servicio Móvil y IMEI Vinculados (con Fechas)')
plt.axis('off')
plt.savefig('grafico_relacional.png')  # Guardar el gráfico como imagen
plt.show()
