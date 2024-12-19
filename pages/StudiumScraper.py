import os
from pypdf import PdfReader, PdfWriter
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import io
import tempfile
from utils.ScraperUtils import generate_contribution_chart, generate_pdf_report, download_participant_logs
import zipfile
import urllib3

http = urllib3.PoolManager()

# Título de la aplicación
st.title("Scraper de Participantes y Registros - Studium Moodle")

# URLs y plantillas
base_url = "https://studium24.usal.es/user/index.php?page=0&perpage=5000&contextid=0&id={}&newcourse"
log_url_template = "https://studium24.usal.es/report/log/index.php?sesskey={}&download=csv&id={}&user={}&modid=&chooselog=1&logreader=logstore_standard"

# Inicialización de variables en sesión
if "participants_df" not in st.session_state:
    st.session_state.participants_df = None

if "logs_df" not in st.session_state:
    st.session_state.logs_df = None

# Paso 1: Datos del usuario
st.header("Introduce los datos necesarios:")
moodle_session = st.text_input("Cookie MoodleSession", type="password")
auth_token = st.text_input("MDL_SSP_SessID", type="password")
course_id = st.text_input("ID del curso", placeholder="Ejemplo: 2400874")

# Mostrar imagen de ejemplo de cookies
st.image("img/cookies.png", caption="Ejemplo de cookies")

# Explicación de las variables necesarias
st.markdown("""
**Cookie MoodleSession**: Esta cookie se utiliza para mantener la sesión del usuario en Moodle. Debes copiar el valor de esta cookie desde tu navegador cuando estés autenticado en Moodle.

**MDL_SSP_SessID**: Este es un token de autenticación adicional que puede ser necesario para acceder a ciertos recursos en Moodle. Debes copiar el valor de esta cookie desde tu navegador cuando estés autenticado en Moodle.

**ID del curso**: Este es el identificador único del curso en Moodle. Puedes encontrar este ID en la URL del curso cuando estás navegando en Moodle. Por ejemplo, en la URL `https://studium24.usal.es/course/view.php?id=2400874`, el ID del curso es `2400874`.
""")

# Botón para extraer participantes
if st.button("Extraer Participantes"):
    if moodle_session and auth_token and course_id:
        headers = {"Cookie": f"MoodleSession={moodle_session}"}
        response = http.request("GET", base_url.format(course_id), headers=headers)

        if response.status == 200:
            soup = BeautifulSoup(response.data, "html.parser")
            tbody = soup.find("table", class_="generaltable").find("tbody")
            rows = tbody.find_all("tr")

            data = []
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 6:
                    user_input = cells[0].find("input")
                    user_id = user_input['id'].replace("user", "") if user_input else None
                    name_label = cells[0].find("label")
                    name = name_label.text.replace("Seleccionar '", "").replace("'", "") if name_label else None
                    if user_id and name:
                        data.append({"ID Usuario": user_id, "Nombre": name})

            if data:
                st.session_state.participants_df = pd.DataFrame(data)
                st.success("Participantes extraídos correctamente.")
            else:
                st.warning("No se encontraron participantes.")
        else:
            st.error(f"Error: {response.status}")
    else:
        st.error("Completa todos los campos.")

# Mostrar participantes
if st.session_state.participants_df is not None:
    st.dataframe(st.session_state.participants_df)

    # Selección de participante
    st.subheader("Selecciona un participante:")
    selected_name = st.selectbox("Nombre del participante", st.session_state.participants_df["Nombre"])
    user_id = st.session_state.participants_df.loc[
        st.session_state.participants_df["Nombre"] == selected_name, "ID Usuario"
    ].values[0]

    # Botón para descargar registros
    if st.button("Cargar registros"):
        st.session_state.logs_df = download_participant_logs(auth_token, course_id, user_id, moodle_session)
        if st.session_state.logs_df is not None:
            st.success(f"Registros cargados para {selected_name}")
        else:
            st.error("No se pudieron descargar los registros.")

# Gráfico de contribuciones
if st.session_state.logs_df is not None:
    st.subheader("Actividad del Alumno")
    st.write(st.session_state.logs_df.head())  # Mostrar primeras filas de registros

    # Mostrar el número de registros
    st.write(f"Número de registros: {len(st.session_state.logs_df)}")

    # Verificar si existe una columna de fecha
    date_column = st.selectbox("Selecciona la columna de fecha", st.session_state.logs_df.columns)
    st.session_state.logs_df[date_column] = pd.to_datetime(st.session_state.logs_df[date_column], format="%d/%m/%y, %H:%M:%S")

    # Seleccionar rango de fechas
    min_date = st.session_state.logs_df[date_column].min()
    max_date = st.session_state.logs_df[date_column].max()
    start_date = st.date_input("Fecha de inicio", min_date)
    end_date = st.date_input("Fecha de fin", max_date)

    if st.button("Generar gráfica"):
        # Filtrar registros por rango de fechas
        filtered_logs_df = st.session_state.logs_df[
            (st.session_state.logs_df[date_column] >= pd.to_datetime(start_date)) &
            (st.session_state.logs_df[date_column] <= pd.to_datetime(end_date))
        ]

        # Generar contribuciones diarias
        daily_activity = filtered_logs_df.set_index(date_column).resample('D').size()

        # Mostrar el gráfico
        fig = generate_contribution_chart(daily_activity)
        if fig:
            st.pyplot(fig)

    # Botón para descargar registros como XLSX
    if st.button("Descargar registros como XLSX"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state.logs_df.to_excel(writer, index=False, sheet_name='Registros')
            writer.save()
        output.seek(0)
        st.download_button(
            label="Descargar XLSX",
            data=output,
            file_name=f"registros_{selected_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Botón para generar PDF con informe
    if st.button("Generar Informe PDF"):
        # Filtrar registros por rango de fechas
        filtered_logs_df = st.session_state.logs_df[
            (st.session_state.logs_df[date_column] >= pd.to_datetime(start_date)) &
            (st.session_state.logs_df[date_column] <= pd.to_datetime(end_date))
        ]

        # Generar contribuciones diarias
        daily_activity = filtered_logs_df.set_index(date_column).resample('D').size()

        # Generar la figura
        fig = generate_contribution_chart(daily_activity)

        # Save the figure to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name)
            pdf_output = generate_pdf_report(selected_name, tmpfile.name)
            st.download_button(
                label="Descargar Informe PDF",
                data=pdf_output,
                file_name=f"informe_{selected_name}.pdf",
                mime="application/pdf"
            )
        os.remove(tmpfile.name)  # Clean up the temporary file

    # Botón para generar informes para todos los participantes
    if st.button("Generar informe para todos los participantes"):
        total_participants = len(st.session_state.participants_df)
        progress_bar = st.progress(0)
        pdf_files = []
        
        for idx, participant in enumerate(st.session_state.participants_df.iterrows()):
            user_id = participant[1]["ID Usuario"]
            name = participant[1]["Nombre"]
            logs_df = download_participant_logs(auth_token, course_id, user_id, moodle_session)
            if logs_df is not None:
                logs_df[date_column] = pd.to_datetime(logs_df[date_column], format="%d/%m/%y, %H:%M:%S")
                daily_activity = logs_df.set_index(date_column).resample('D').size()
                fig = generate_contribution_chart(daily_activity)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    fig.savefig(tmpfile.name)
                    pdf_output = generate_pdf_report(name, tmpfile.name)
                    pdf_files.append(pdf_output)
                    plt.close(fig)  # Close the figure to avoid memory issues
            
            # Update progress bar
            progress = (idx + 1) / total_participants
            progress_bar.progress(progress)
        
        # Combine all PDFs into one
        pdf_writer = PdfWriter()
        for pdf_output in pdf_files:
            pdf_reader = PdfReader(pdf_output)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        
        # Save the combined PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf_output_path = tmpfile.name
            with open(pdf_output_path, "wb") as output_file:
                pdf_writer.write(output_file)
            with open(pdf_output_path, "rb") as output_file:
                st.download_button(
                    label="Descargar Informe PDF",
                    data=output_file,
                    file_name="informe_todos_los_participantes.pdf",
                    mime="application/pdf"
                )
