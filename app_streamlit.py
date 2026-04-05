import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import os

st.title("Análisis de Reportes IMEI")

# Subir archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("Datos cargados:")
    st.dataframe(df.head())

    # Análisis estadístico
    conteo_imei_por_documento = df.groupby('Número Documento Legal del Abonado')['IMEI'].count().reset_index()
    conteo_imei_por_documento.columns = ['Número Documento', 'Cantidad de IMEI']
    st.subheader("Reporte estadístico: Cantidad de IMEI por Número de Documento")
    st.dataframe(conteo_imei_por_documento)

    # Patrón temporal
    df['Fecha y Hora de Vinculación/Desvinculación'] = pd.to_datetime(df['Fecha y Hora de Vinculación/Desvinculación'], dayfirst=True, errors='coerce')
    df_activaciones = df[df['Tipo'] == 'Vinculación']
    activaciones_por_fecha = df_activaciones.groupby(df_activaciones['Fecha y Hora de Vinculación/Desvinculación'].dt.date).size().reset_index(name='Cantidad de Activaciones')
    st.subheader("Patrón temporal: Cantidad de activaciones por fecha")
    st.dataframe(activaciones_por_fecha)

    # Gráfico de tiempo
    st.subheader("Gráfico de Patrón Temporal")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(activaciones_por_fecha['Fecha y Hora de Vinculación/Desvinculación'], activaciones_por_fecha['Cantidad de Activaciones'], marker='o')
    ax.set_title('Patrón de Activaciones de IMEI por Fecha')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Cantidad de Activaciones')
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig)

    # Gráfico relacional
    st.subheader("Gráfico Relacional: Servicio Móvil e IMEI")
    G = nx.Graph()
    servicios_imei = df.groupby('Número Servicio Móvil')['IMEI'].apply(list).to_dict()
    for servicio, imei_list in servicios_imei.items():
        G.add_node(servicio, shape='circle')
        for imei in imei_list:
            G.add_node(imei, shape='box')
            G.add_edge(servicio, imei)

    documento = df['Número Documento Legal del Abonado'].iloc[0]
    labels = {servicio: f"{servicio}\n{documento}" for servicio in servicios_imei.keys()}
    labels.update({imei: str(imei) for imei_list in servicios_imei.values() for imei in imei_list})

    edge_labels = {}
    for _, row in df.iterrows():
        service = row['Número Servicio Móvil']
        imei = row['IMEI']
        date = row['Fecha y Hora de Vinculación/Desvinculación'].strftime('%d/%m/%Y') if pd.notna(row['Fecha y Hora de Vinculación/Desvinculación']) else 'N/A'
        edge_labels[(service, imei)] = date

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
        for i, servicio in enumerate(servicios):
            angle_s = 2 * np.pi * i / n_servicios
            pos[servicio] = (2 * np.cos(angle_s), 2 * np.sin(angle_s))
            imei_list = servicios_imei[servicio]
            n_imei = len(imei_list)
            for j, imei in enumerate(imei_list):
                angle_i = 2 * np.pi * j / n_imei
                pos[imei] = (pos[servicio][0] + np.cos(angle_i), pos[servicio][1] + np.sin(angle_i))

    fig, ax = plt.subplots(figsize=(14, 14))
    nx.draw_networkx_nodes(G, pos, nodelist=servicios, node_shape='o', node_color='lightblue', node_size=2500, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=[n for sublist in servicios_imei.values() for n in sublist], node_shape='s', node_color='lightgreen', node_size=1500, ax=ax)
    nx.draw_networkx_edges(G, pos, ax=ax)
    nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, ax=ax)
    ax.set_title('Relación entre Número de Servicio Móvil y IMEI Vinculados (con Fechas)')
    ax.axis('off')
    st.pyplot(fig)

else:
    st.write("Por favor, sube un archivo Excel para comenzar el análisis.")