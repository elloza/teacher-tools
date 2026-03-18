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
    st.session_state.num_registros_dat = None

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
        st.session_state.num_registros_dat = len(df_dat)

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

    # Sección de análisis estadístico de las notas
    st.write("### 📊 Análisis estadístico de las notas")

    col_nota_final = f'{prefijo_columna}_Nota final B({base_nota})'
    df_resultado = st.session_state.df_combinado

    if col_nota_final in df_resultado.columns:
        notas_validas = df_resultado[col_nota_final].dropna()
        # Presentados = registros en la lectora (.DAT)
        num_presentados = st.session_state.num_registros_dat
        # Total alumnos = registros en el Excel de Studium
        num_total = len(df_resultado)
        # No presentados = alumnos de Studium que no pasaron por la lectora
        num_no_presentados = num_total - num_presentados

        # Número de no presentados
        st.write("#### 🚷 No presentados")
        col_np1, col_np2, col_np3 = st.columns(3)
        col_np1.metric("Total alumnos (Studium)", num_total)
        col_np2.metric("Presentados (Lectora)", num_presentados)
        col_np3.metric("No presentados", num_no_presentados)

        if len(notas_validas) > 0:
            # Estadísticas descriptivas
            st.write("#### 📈 Estadísticas descriptivas")
            media = notas_validas.mean()
            mediana = notas_validas.median()
            desv_std = notas_validas.std()
            nota_min = notas_validas.min()
            nota_max = notas_validas.max()
            q1 = notas_validas.quantile(0.25)
            q3 = notas_validas.quantile(0.75)

            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.metric("Media", f"{media:.2f}")
            col_s2.metric("Mediana", f"{mediana:.2f}")
            col_s3.metric("Desv. estándar", f"{desv_std:.2f}")
            col_s4.metric("Moda", f"{notas_validas.mode().iloc[0]:.2f}" if not notas_validas.mode().empty else "N/A")

            col_s5, col_s6, col_s7, col_s8 = st.columns(4)
            col_s5.metric("Mínimo", f"{nota_min:.2f}")
            col_s6.metric("Máximo", f"{nota_max:.2f}")
            col_s7.metric("Q1 (25%)", f"{q1:.2f}")
            col_s8.metric("Q3 (75%)", f"{q3:.2f}")

            num_aprobados = int((notas_validas >= base_nota * 0.5).sum())
            num_suspensos = num_presentados - num_aprobados
            tasa_aprobados = (num_aprobados / num_presentados) * 100

            col_a1, col_a2, col_a3 = st.columns(3)
            col_a1.metric("Aprobados (>= 50%)", num_aprobados)
            col_a2.metric("Suspensos", num_suspensos)
            col_a3.metric("Tasa de aprobados", f"{tasa_aprobados:.1f}%")

            # Histograma
            st.write("#### 📊 Histograma de notas")
            fig_hist, ax_hist = plt.subplots(figsize=(10, 5))
            bins = np.arange(0, base_nota + 0.5, 0.5) if base_nota <= 10 else 20
            ax_hist.hist(notas_validas, bins=bins, edgecolor='black', alpha=0.7, color='#4CAF50')
            ax_hist.set_xlabel('Nota')
            ax_hist.set_ylabel('Número de alumnos')
            ax_hist.set_title('Distribución de notas')
            if base_nota <= 10:
                ax_hist.set_xticks(np.arange(0, base_nota + 1, 1))
            ax_hist.axvline(media, color='red', linestyle='--', linewidth=1.5, label=f'Media: {media:.2f}')
            ax_hist.axvline(mediana, color='blue', linestyle='--', linewidth=1.5, label=f'Mediana: {mediana:.2f}')
            ax_hist.legend()
            ax_hist.grid(axis='y', alpha=0.3)
            st.pyplot(fig_hist)

            # Box plot (Whisker plot)
            st.write("#### 📦 Diagrama de caja (Box & Whisker plot)")
            fig_box, ax_box = plt.subplots(figsize=(10, 4))
            bp = ax_box.boxplot(notas_validas, vert=False, patch_artist=True,
                                boxprops=dict(facecolor='#81D4FA', edgecolor='black'),
                                medianprops=dict(color='red', linewidth=2),
                                whiskerprops=dict(color='black'),
                                capprops=dict(color='black'),
                                flierprops=dict(marker='o', markerfacecolor='red', markersize=6))
            ax_box.set_xlabel('Nota')
            ax_box.set_title('Distribución de notas - Box Plot')
            if base_nota <= 10:
                ax_box.set_xticks(np.arange(0, base_nota + 1, 1))
            ax_box.grid(axis='x', alpha=0.3)
            st.pyplot(fig_box)
        else:
            st.warning("No hay notas disponibles para generar estadísticas.")
    else:
        st.warning(f"No se encontró la columna de notas '{col_nota_final}' en los resultados.")

    # Mostrar el fichero de salida para descargar con streamlit
    st.write("### 📥 Descargar fichero de salida")
    st.write("Descarga tu fichero de salida abajo:")
    st.download_button(
        '⬇️ Descargar fichero resultado',
        st.session_state.excel_bytes,
        file_name=st.session_state.archivo_salida_nombre,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
