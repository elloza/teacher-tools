import streamlit as st
import pandas as pd
from fuzzywuzzy import process
import re
from datetime import datetime

def run():
    st.set_page_config(
        page_title="Teacher Tools",
        page_icon="🎓",
        layout="wide"
    )

    # Sidebar con título
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: #1E88E5; margin: 0;">🎓 Teacher Tools</h1>
            <p style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">Herramientas para docentes</p>
        </div>
        <hr style="margin: 0.5rem 0 1rem 0;">
        """, unsafe_allow_html=True)

    st.write("# Bienvenido a Teacher Tools! 🎓")

    # Footer en el sidebar (al final)
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


if __name__ == "__main__":
    run()
    st.markdown(
        """
    Este sitio web está desarrollado con [stlite](https://stlite.net/) (una versión de Streamlit que se ejecuta enteramente en tu navegador) 🖥️
    por lo que puedes estar tranquilo de que tus datos no saldrán de tu pc y todo el procesamiento se hace en tu máquina. 🔒

    Además, si no te fías, aquí tienes el [repositorio de GitHub](https://github.com/elloza/teacher-tools) por si quieres revisar el código fuente y dejar una estrella de paso. ⭐

    ## Descripción de las herramientas disponibles:

    ### 📊 Unir Excels
    Esta herramienta permite unir dos archivos de Excel en función de una columna común.
    Puedes seleccionar las columnas de unión de cada archivo y descargar el archivo combinado.

    ### ⏱️ Última Respuesta
    Esta herramienta procesa un archivo de Excel para obtener solo la última respuesta de cada identificador único.
    Puedes seleccionar la columna de identificación y la columna de tiempo para realizar el filtrado.

    ### 📚 Lectora a Studium
    Esta herramienta convierte los datos de la lectora en un archivo de Excel compatible con Studium (Moodle).
    Necesitarás subir varios archivos, incluyendo los resultados de la lectora y un archivo de Excel de Studium,
    y configurar los parámetros de corrección.

    ### ✅ Verificar Entregas
    Esta herramienta permite inspeccionar un fichero zip de entregas de Moodle junto con un listado de alumnos
    para comprobar si en sus entregas se incluye algún fichero con alguna de las extensiones especificadas.
    Se añade una columna con un 1 si se ha encontrado algún fichero y 0 en caso contrario.

    ### 📈 Scraper Studium
    Esta herramienta permite extraer la lista de participantes de un curso de Moodle en Studium y generar
    un informe como un timeline de GitHub a partir de sus registros de actividad.
    Necesitarás introducir las cookies de sesión de Moodle y el ID del curso.

    ### 📋 Studium a Actas
    Esta herramienta permite cruzar datos entre dos archivos Excel: uno de Studium (Moodle) con las notas
    y otro de la aplicación de actas de la USAL.
    El cruce se realiza automáticamente por nombres y apellidos usando matching inteligente.

    """
    )
