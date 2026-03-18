import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from utils.StudiumExcelToolUtils import combinar_datos, escribir_nuevo_excel_bytes, leer_archivo_excel, leer_archivo_txt, leer_y_procesar_fichero_DAT, reordenar_columnas

st.set_page_config(page_title="Lectora a Studium - Teacher Tools", page_icon="📚")

# Sidebar footer
current_year = datetime.now().year
st.sidebar.markdown(
    f"""
    <div style="position: fixed; bottom: 0; left: 0; width: var(--sidebar-width, 21rem); padding: 0.75rem 1rem; background-color: inherit; text-align: center; border-top: 1px solid rgba(128,128,128,0.2);">
        <p style="color: #666; font-size: 0.8rem; margin: 0;">
            Creado con ❤️ por
            <strong>Álvaro Lozano Murciego</strong>
            · {current_year}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Title of the page
st.title("📚 Lectora a Studium")

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
    st.session_state.prefijo_columna = None
    st.session_state.base_nota = None

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
        st.session_state.prefijo_columna = prefijo_columna
        st.session_state.base_nota = base_nota

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
        st.write("⚠️ Los siguientes alumnos no han sido encontrados. Se muestran sugerencias de alumnos con ID similar para facilitar la identificación:")
        st.dataframe(st.session_state.no_encontrados, use_container_width=True)
    else:
        st.write("✅ Todos los alumnos han sido encontrados.")

    # Sección de análisis estadístico
    st.write("### 📊 Análisis estadístico de resultados")

    pref = st.session_state.prefijo_columna
    bn = st.session_state.base_nota
    col_nota_final = f'{pref}_Nota final B({bn})'
    df_stats = st.session_state.df_combinado

    # Separar presentados y no presentados
    notas_presentados = df_stats[col_nota_final].dropna()
    num_total = len(df_stats)
    num_presentados = len(notas_presentados)
    num_no_presentados = num_total - num_presentados

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Total alumnos", num_total)
    col2.metric("Presentados", num_presentados)
    col3.metric("No presentados", num_no_presentados)

    if num_presentados > 0:
        # Estadísticas descriptivas
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Media", f"{notas_presentados.mean():.2f}")
        col_b.metric("Mediana", f"{notas_presentados.median():.2f}")
        col_c.metric("Desv. típica", f"{notas_presentados.std():.2f}")
        col_d.metric("Nota máxima", f"{notas_presentados.max():.2f}")

        col_e, col_f, col_g, col_h = st.columns(4)
        col_e.metric("Nota mínima", f"{notas_presentados.min():.2f}")
        col_f.metric("Q1 (25%)", f"{notas_presentados.quantile(0.25):.2f}")
        col_g.metric("Q3 (75%)", f"{notas_presentados.quantile(0.75):.2f}")
        aprobados = (notas_presentados >= bn * 0.5).sum()
        col_h.metric("% Aprobados", f"{aprobados / num_presentados * 100:.1f}%")

        # Histograma y Box plot lado a lado
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Histograma
        bins = np.arange(0, bn + 0.5, 0.5)
        ax1.hist(notas_presentados, bins=bins, edgecolor='black', alpha=0.7, color='#4CAF50')
        ax1.axvline(notas_presentados.mean(), color='red', linestyle='--', linewidth=1.5, label=f'Media: {notas_presentados.mean():.2f}')
        ax1.axvline(notas_presentados.median(), color='blue', linestyle='--', linewidth=1.5, label=f'Mediana: {notas_presentados.median():.2f}')
        ax1.axvline(bn * 0.5, color='orange', linestyle=':', linewidth=1.5, label=f'Aprobado: {bn * 0.5:.1f}')
        ax1.set_xlabel(f'Nota (base {bn})')
        ax1.set_ylabel('Frecuencia')
        ax1.set_title('Distribución de notas')
        ax1.legend(fontsize=8)
        ax1.set_xlim(0, bn)

        # Box plot (whisker plot)
        bp = ax2.boxplot(notas_presentados, vert=True, patch_artist=True,
                         boxprops=dict(facecolor='#81D4FA', edgecolor='black'),
                         medianprops=dict(color='red', linewidth=2),
                         whiskerprops=dict(color='black'),
                         capprops=dict(color='black'),
                         flierprops=dict(marker='o', markerfacecolor='red', markersize=6))
        ax2.axhline(bn * 0.5, color='orange', linestyle=':', linewidth=1.5, label=f'Aprobado: {bn * 0.5:.1f}')
        ax2.set_ylabel(f'Nota (base {bn})')
        ax2.set_title('Diagrama de caja (Whisker plot)')
        ax2.set_xticklabels(['Notas'])
        ax2.legend(fontsize=8)
        ax2.set_ylim(0, bn)

        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.write("No hay alumnos presentados para mostrar estadísticas.")

    # Mostrar el fichero de salida para descargar con streamlit
    st.write("### 📥 Descargar fichero de salida")
    st.write("Descarga tu fichero de salida abajo:")
    st.download_button(
        '⬇️ Descargar fichero resultado',
        st.session_state.excel_bytes,
        file_name=st.session_state.archivo_salida_nombre,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
