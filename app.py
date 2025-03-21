import streamlit as st
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from PIL import Image
import os
import datetime
import glob

# 📌 Configuración de la página en Streamlit
st.set_page_config(page_title="Gráfica de Fenton", layout="centered")

# 📌 Selector de género
genero = st.radio("Selecciona el sexo", ["Niño", "Niña"])

# 📌 Cargar la imagen y la hoja de Excel correspondientes
if genero == "Niño":
    image_path = "graficavaron.png"
    sheet_name = "Niño"  # Hoja con datos para niños
else:
    image_path = "graficanina.png"
    sheet_name = "Niña"  # Hoja con datos para niñas

# 📌 Cargar el archivo Excel con coordenadas específicas para cada género
file_path = "Coordenadas fenton pixeles.xlsx"
df = pd.read_excel(file_path, sheet_name=sheet_name)

# 📌 Extraer datos de referencia en píxeles específicos para el género seleccionado
edad_gestacional = df["Semanas"].values
x_coords = df["Edad gestacional eje X"].values
peso_real = df["KG"].values
peso_y_coords = df["Peso eje Y"].values
pc_real = df["CM"].values
pc_y_coords = df["PC eje Y"].values
talla_real = df["CM.1"].values
talla_y_coords = df["Talla eje Y"].values

# 📌 Función para interpolar coordenadas según el género seleccionado
def obtener_coordenadas(edad, valor, valores_reales, valores_y):
    """Interpola coordenadas en la imagen para un valor dado."""
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
edad = st.number_input("Edad gestacional (semanas)", min_value=20, max_value=50, value=40, step=1)
peso = st.number_input("Peso (kg)", min_value=0.5, max_value=8.0, value=3.5, step=0.1)
talla = st.number_input("Talla (cm)", min_value=15.0, max_value=60.0, value=51.0, step=0.1)
pc = st.number_input("Perímetro cefálico (cm)", min_value=0.0, max_value=55.0, value=35.0, step=0.1)

# 📌 Calcular coordenadas según los datos específicos del género seleccionado
peso_coord = obtener_coordenadas(edad, peso, peso_real, peso_y_coords)
talla_coord = obtener_coordenadas(edad, talla, talla_real, talla_y_coords)
pc_coord = obtener_coordenadas(edad, pc, pc_real, pc_y_coords)

# 📌 Cargar la imagen y mostrarla en la parte correcta
image = cv2.imread(image_path)
if image is not None:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
else:
    st.error(f"No se pudo cargar la imagen {image_path}. Verifica que el archivo esté en el repositorio.")

# 📌 Crear la figura para el ploteo
fig, ax = plt.subplots(figsize=(8, 10))
ax.imshow(image)

# 📌 Ajustar tamaño de los puntos
marker_size = 50  

# Ploteo de los puntos en la imagen seleccionada
if peso_coord:
    ax.scatter(*peso_coord, color='red', s=marker_size, label="Peso")
if talla_coord:
    ax.scatter(*talla_coord, color='blue', s=marker_size, label="Talla")
if pc_coord:
    ax.scatter(*pc_coord, color='green', s=marker_size, label="Perímetro Cefálico")

ax.axis('off')
ax.legend()
st.pyplot(fig)

# -----------------------------------------------------------------------------
# Sección para guardar el ploteo actual con timestamp
if st.button("Guardar ploteo actual"):
    # Directorio para guardar el historial de ploteos
    save_dir = "historial_plots"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Generar un nombre de archivo con timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"plot_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)
    
    # Guardar el gráfico actual
    fig.savefig(filepath)
    st.success(f"Ploteo guardado: {filepath}")

# -----------------------------------------------------------------------------
# Sección para visualizar el historial de ploteos (línea de tiempo)
st.header("Historial de Ploteos")

def obtener_plots(directorio="historial_plots"):
    """Obtiene y ordena los archivos de ploteo guardados en el directorio."""
    ruta_patron = os.path.join(directorio, "plot_*.png")
    imagenes = glob.glob(ruta_patron)
    imagenes.sort(key=lambda x: datetime.datetime.strptime(os.path.basename(x)[5:20], "%Y%m%d_%H%M%S"))
    return imagenes

plots_guardados = obtener_plots()

if plots_guardados:
    opciones = [os.path.basename(img) for img in plots_guardados]
    seleccion = st.selectbox("Selecciona un ploteo para visualizar", opciones)
    ruta_seleccionada = os.path.join("historial_plots", seleccion)
    st.image(ruta_seleccionada, caption=seleccion, use_column_width=True)
else:
    st.write("No hay ploteos guardados.")

# Sección para guardar el ploteo actual con expediente
st.header("Guardar Ploteo Actual")

# Campo para ingresar el número o nombre de expediente
expediente = st.text_input("Ingresa el número o nombre de expediente:")

if st.button("Guardar ploteo actual"):
    # Directorio para guardar el historial de ploteos
    save_dir = "historial_plots"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Generar un timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Verifica si se ha ingresado un expediente y lo incluye en el nombre del archivo
    if expediente.strip():
        filename = f"plot_{expediente}_{timestamp}.png"
    else:
        filename = f"plot_{timestamp}.png"
    
    filepath = os.path.join(save_dir, filename)
    
    # Guardar el gráfico actual
    fig.savefig(filepath)
    st.success(f"Ploteo guardado: {filepath}")
