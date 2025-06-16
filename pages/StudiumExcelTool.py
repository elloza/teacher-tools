import streamlit as st
import pandas as pd

from utils.StudiumExcelToolUtils import combinar_datos, escribir_nuevo_excel, leer_archivo_excel, leer_archivo_txt, leer_y_procesar_fichero_DAT

st.set_page_config(page_title = "Lectora StudiumExcel", page_icon = "📝")

# Title of the page
st.title("📝 Lectora to Studium Excel Tool")

# Description of the page
st.markdown('''
    ¡Bienvenido a la herramienta mágica que convierte datos de la lectora en un Excel de Studium! ✨📊
    
    Para comenzar, necesitarás subir los siguientes archivos:
    - 📄 **Fichero de la lectora solucion.DAT** (plantillas de solución para cada tipo de cuestionario)
    - 📄 **Fichero de la lectora lectura.DAT** (resultados leídos de la máquina)
    - 📄 **Fichero txt de la lectora (lalfnot.txt)** (calificaciones para verificación)
    - 📄 **Fichero de Studium exportado a Excel .xlsx** (¡ojo, no Open Office!)

    Una vez subidos estos archivos, configura los parámetros de la herramienta que aparecen más abajo y pulsa el botón "Procesar". 🛠️
    Después, tu fichero Excel estará listo para descargar. 📥
    Además, si algún alumno no se encuentra, te lo mostraremos en pantalla. 👀
''')

# Sección subida de ficheros
st.write("## 📂 Subida de ficheros")
st.write("Sube los ficheros necesarios para la herramienta:")

fichero_lectora_solucion = st.file_uploader("📄 Fichero solucion.DAT", accept_multiple_files=False)
fichero_lectora_lectura = st.file_uploader("📄 Fichero lectura.DAT", accept_multiple_files=False)
fichero_lectora_txt = st.file_uploader("📄 Fichero txt de la lectora (lalfnot.txt)", accept_multiple_files=False)
fichero_xlsx_studium = st.file_uploader("📄 Fichero Excel .xlsx de Studium", accept_multiple_files=False)

# Sección parámetros de corrección
st.write("## ⚙️ Parámetros de corrección")
st.write("Configura los parámetros de la herramienta:")

# num_preguntas, descuento, archivo_salida, umbral, base_nota, prefijo_columna

# Num pregunta
num_preguntas = st.number_input("🔢 Número de preguntas", min_value=1, max_value=120, value=10, step=1)

# Num pregunta de inicio
num_pregunta_inicio = st.number_input("🔢 Número de pregunta de inicio", min_value=1, max_value=120, value=1, step=1)

# Num pregunta de fin
num_pregunta_fin = st.number_input("🔢 Número de pregunta de fin", min_value=1, max_value=120, value=10, step=1)

# Descuento (valor real entre 0 y 1)
descuento = st.number_input("📉 Descuento por pregunta fallada", min_value=0.0, max_value=1.0, value=0.33)

# Umbral para matching de nombres (valor real entre 0 y 100)
umbral = st.number_input("🔍 Umbral para matching de nombres (Cambiar si se quiere intentar obtener más valores pero puede fallar)", min_value=0, max_value=100, value=100, step=1)

# Prefijo que se le añadirá a las columnas
prefijo_columna = st.text_input("🔠 Prefijo de las columnas", value="Test")

# Base en la que se quiere la columna Nota
base_nota = st.number_input("📏 Base en la que se quiere la columna Nota", min_value=0, max_value=10, value=10)

# Nombre del archivo de salida
archivo_salida = st.text_input("💾 Nombre del archivo de salida", value="Salida.xlsx")

# Boton procesar
if st.button("🚀 Procesar"):

    # Procesar ficheros
    # Comprobar si se han subido los ficheros
    if fichero_lectora_solucion is None or fichero_lectora_lectura is None or fichero_xlsx_studium is None or fichero_lectora_txt is None:
        st.write("⚠️ Por favor sube los ficheros necesarios para la herramienta")
    else:
        # Procesar ficheros
        # Previsualizar información .dat
        st.write("### 👀 Previsualización de los ficheros .DAT")
        # Read text of the files in utf-8
        text_lectora_solucion = fichero_lectora_solucion.read().decode("utf-8")
        text_lectora_lectura = fichero_lectora_lectura.read().decode("utf-8")
        # Display the text on text area
        st.text_area("📄 Fichero solucion.DAT", text_lectora_solucion, height=200)
        st.text_area("📄 Fichero lectura.DAT", text_lectora_lectura, height=200)

        # Previsualizar información .xlsx en un dataframe
        st.write("### 👀 Previsualización del fichero .xlsx de Studium")
        # Read excel file
        df_studium = pd.read_excel(fichero_xlsx_studium)
        # Display dataframe on streamlit
        st.dataframe(df_studium, use_container_width=True)

        df_txt = leer_archivo_txt(fichero_lectora_txt, prefijo_columna)
        df_excel = leer_archivo_excel(fichero_xlsx_studium)
        df_dat = leer_y_procesar_fichero_DAT(fichero_lectora_lectura, fichero_lectora_solucion, num_preguntas, descuento, prefijo_columna, num_pregunta_inicio, num_pregunta_fin) # type: ignore
        df_combinado, no_encontrados = combinar_datos(df_txt, df_excel, df_dat, umbral, base_nota, prefijo_columna, num_preguntas)
        
        escribir_nuevo_excel(df_combinado, archivo_salida)

        # Mostrar los alumnos no encontrados
        st.write("### 🚫 Alumnos no encontrados")
        if len(no_encontrados) > 0:
            st.write("⚠️ Los siguientes alumnos no han sido encontrados:")
            st.dataframe(no_encontrados)
        else:
            st.write("✅ Todos los alumnos han sido encontrados.")

        # Mostrar el fichero de salida para descargar con streamlit
        st.write("### 📥 Descargar fichero de salida")
        st.write("Descarga tu fichero de salida abajo:")
        with open(archivo_salida, 'rb') as f:
            st.download_button('⬇️ Descargar fichero resultado', f, file_name=archivo_salida)  # Defaults to 'application/octet-stream'
