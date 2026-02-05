import streamlit as st
import pandas as pd

from utils.StudiumExcelToolUtils import combinar_datos, escribir_nuevo_excel_bytes, leer_archivo_excel, leer_archivo_txt, leer_y_procesar_fichero_DAT, reordenar_columnas

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

# Inicializar session_state para mantener los resultados
if 'resultado_procesado' not in st.session_state:
    st.session_state.resultado_procesado = False
    st.session_state.excel_bytes = None
    st.session_state.no_encontrados = None
    st.session_state.df_combinado = None
    st.session_state.archivo_salida_nombre = None
    st.session_state.text_lectora_solucion = None
    st.session_state.text_lectora_lectura = None
    st.session_state.df_studium_preview = None

# Boton procesar
if st.button("🚀 Procesar"):

    # Procesar ficheros
    # Comprobar si se han subido los ficheros
    if fichero_lectora_solucion is None or fichero_lectora_lectura is None or fichero_xlsx_studium is None or fichero_lectora_txt is None:
        st.write("⚠️ Por favor sube los ficheros necesarios para la herramienta")
    else:
        # Procesar ficheros
        # Previsualizar información .dat
        # Read text of the files in utf-8
        text_lectora_solucion = fichero_lectora_solucion.read().decode("utf-8")
        text_lectora_lectura = fichero_lectora_lectura.read().decode("utf-8")

        # Read excel file for preview
        df_studium = pd.read_excel(fichero_xlsx_studium)

        df_txt = leer_archivo_txt(fichero_lectora_txt, prefijo_columna)
        df_excel = leer_archivo_excel(fichero_xlsx_studium)
        df_dat = leer_y_procesar_fichero_DAT(fichero_lectora_lectura, fichero_lectora_solucion, num_preguntas, descuento, prefijo_columna, num_pregunta_inicio, num_pregunta_fin) # type: ignore
        df_combinado, no_encontrados = combinar_datos(df_txt, df_excel, df_dat, umbral, base_nota, prefijo_columna, num_preguntas)

        # Reordenar columnas para poner Original Lectora y Nota final al principio
        df_combinado = reordenar_columnas(df_combinado, prefijo_columna, base_nota)

        # Generar bytes del Excel en memoria
        excel_bytes = escribir_nuevo_excel_bytes(df_combinado)

        # Guardar en session_state
        st.session_state.resultado_procesado = True
        st.session_state.excel_bytes = excel_bytes
        st.session_state.no_encontrados = no_encontrados
        st.session_state.df_combinado = df_combinado
        st.session_state.archivo_salida_nombre = archivo_salida
        st.session_state.text_lectora_solucion = text_lectora_solucion
        st.session_state.text_lectora_lectura = text_lectora_lectura
        st.session_state.df_studium_preview = df_studium

# Mostrar resultados si ya se han procesado (persiste después de descargar)
if st.session_state.resultado_procesado:
    st.write("### 👀 Previsualización de los ficheros .DAT")
    st.text_area("📄 Fichero solucion.DAT", st.session_state.text_lectora_solucion, height=200)
    st.text_area("📄 Fichero lectura.DAT", st.session_state.text_lectora_lectura, height=200)

    st.write("### 👀 Previsualización del fichero .xlsx de Studium")
    st.dataframe(st.session_state.df_studium_preview, use_container_width=True)

    # Mostrar los alumnos no encontrados
    st.write("### 🚫 Alumnos no encontrados")
    if len(st.session_state.no_encontrados) > 0:
        st.write("⚠️ Los siguientes alumnos no han sido encontrados:")
        st.dataframe(st.session_state.no_encontrados)
    else:
        st.write("✅ Todos los alumnos han sido encontrados.")

    # Mostrar el fichero de salida para descargar con streamlit
    st.write("### 📥 Descargar fichero de salida")
    st.write("Descarga tu fichero de salida abajo:")
    st.download_button(
        '⬇️ Descargar fichero resultado',
        st.session_state.excel_bytes,
        file_name=st.session_state.archivo_salida_nombre,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
