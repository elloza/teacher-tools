import streamlit as st
import pandas as pd
from fuzzywuzzy import process
import re
 
def run():
    st.set_page_config(
        page_title="Loza tools",
        page_icon="📝",
    )

    st.write("# Bienvenido a loza tools! 👋")
    st.sidebar.success("Selecciona una de las herramientas.")
    st.markdown(
        """
    """
    )


if __name__ == "__main__":
  run()
  st.markdown(
    """
    Este sitio web está desarrollado con [stlite](https://stlite.net/) (una versión de streamlite que se ejecuta enteramente en tu navegador) 🖥️
    por lo que puedes estar tranquilo de que tus datos no saldrán de tu pc y todo el procesamiento se hace en tu máquina. 🔒

    Además, si no te fías, aquí tienes el [repositorio de GitHub](https://github.com/elloza/teacher-tools) por si quieres revisar el código fuente y dejar una estrella de paso. ⭐

    ## Descripción de las herramientas disponibles:

    ### 📝 Join Excel Files
    Esta herramienta permite unir dos archivos de Excel en función de una columna común. 📊 
    Puedes seleccionar las columnas de unión de cada archivo y descargar el archivo combinado. 📂

    ### 📝 Only Last Answer
    Esta herramienta procesa un archivo de Excel para obtener solo la última respuesta de cada identificador único. ⏳ 
    Puedes seleccionar la columna de identificación y la columna de tiempo para realizar el filtrado. 🕒

    ### 📝 Lectora to Studium Excel Tool
    Esta herramienta convierte los datos de la lectora en un archivo de Excel compatible con Studium (Moodle). 📚 
    Necesitarás subir varios archivos, incluyendo los resultados de la lectora y un archivo de Excel de Studium, 
    y configurar los parámetros de corrección. ⚙️

    ### 📝 Submission Verifier
    Esta herramienta permite inspeccionar un fichero zip de entregas de Moodle junto con un listado de alumnos de Moodle
    para comprobar si en sus entregas se incluye algún fichero con alguna de las extensiones especificadas. 📁 Se añade una columna
    con un 1 si se ha encontrado algún fichero de alguno de los tipos introducidos y 0 en caso contrario. ✅❌

    ### 📝 Studium Scraper
    Esta herramienta permite extraer la lista de participantes de un curso de Moodle en Studium y generar un informe como un timeline
    de github a partir de sus registros de actividad. 📊

    Necesitarás iniciar sesión con tu cuenta e introducir las cookies de sesión de Moodle y el ID del curso para extraer los participantes y sus registros. 🍪

    """
  )