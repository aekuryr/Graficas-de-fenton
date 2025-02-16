# Graficas de fenton

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from PIL import Image

# 📌 Configuración de la página en Streamlit
st.set_page_config(page_title="Gráfica de Fenton - Niños", layout="centered")

# 📌 Cargar la imagen precargada en el entorno
image_path = "graficavaron.png"  # Ruta de la imagen guardada en el entorno
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 📌 Cargar el archivo Excel con coordenadas precargadas
file_path = "coordenadas_fenton.xlsx"  # Ruta del archivo en el entorno
df = pd.read_excel(file_path, sheet_name="Hoja 1")

# 📌 Extraer datos de referencia en píxeles
edad_gestacional = df["Semanas"].values
x_coords = df["Edad gestacional eje X"].values
peso_real = df["KG"].values
peso_y_coords = df["Peso eje Y"].values
pc_real = df["CM"].values
pc_y_coords = df["PC eje Y"].values
talla_real = df["CM.1"].values
talla_y_coords = df["Talla eje Y"].values

# 📌 Función para interpolar coordenadas
def obtener_coordenadas(edad, valor, valores_reales, valores_y):
    """ Interpola coordenadas en la imagen para un valor dado. """
    if valor < min(valores_reales) or valor > max(valores_reales):
        return None
    
    f_interp = interp1d(valores_reales, valores_y, kind='linear', fill_value="extrapolate")
    y_interp = f_interp(valor)
    
    f_x_interp = interp1d(edad_gestacional, x_coords, kind='linear', fill_value="extrapolate")
    x_interp = f_x_interp(edad)
    
    return int(x_interp), int(y_interp)

# 📌 Interfaz en Streamlit
st.title("Gráfica de Fenton - Crecimiento Neonatal")

# 📌 Entrada de datos por el usuario
edad = st.number_input("Edad gestacional (semanas)", min_value=22, max_value=48, value=40, step=1)
peso = st.number_input("Peso (kg)", min_value=0.5, max_value=8.0, value=3.5, step=0.1)
talla = st.number_input("Talla (cm)", min_value=30.0, max_value=60.0, value=51.0, step=0.1)
pc = st.number_input("Perímetro cefálico (cm)", min_value=20.0, max_value=55.0, value=35.0, step=0.1)

# 📌 Calcular coordenadas
peso_coord = obtener_coordenadas(edad, peso, peso_real, peso_y_coords)
talla_coord = obtener_coordenadas(edad, talla, talla_real, talla_y_coords)
pc_coord = obtener_coordenadas(edad, pc, pc_real, pc_y_coords)

# 📌 Mostrar la imagen con los puntos ploteados
fig, ax = plt.subplots(figsize=(8, 10))
ax.imshow(image)

# Ajustar tamaño de los puntos
marker_size = 50  

# Ploteo de los puntos
if peso_coord:
    ax.scatter(*peso_coord, color='red', s=marker_size)
if talla_coord:
    ax.scatter(*talla_coord, color='blue', s=marker_size)
if pc_coord:
    ax.scatter(*pc_coord, color='green', s=marker_size)

ax.axis('off')
st.pyplot(fig)
