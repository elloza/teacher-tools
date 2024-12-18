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
    ## Descripción de las herramientas disponibles:

    ### 📝 Join Excel Files
    Esta herramienta permite unir dos archivos de Excel en función de una columna común. 
    Puedes seleccionar las columnas de unión de cada archivo y descargar el archivo combinado.

    ### 📝 Only Last Answer
    Esta herramienta procesa un archivo de Excel para obtener solo la última respuesta de cada identificador único. 
    Puedes seleccionar la columna de identificación y la columna de tiempo para realizar el filtrado.

    ### 📝 Lectora to Studium Excel Tool
    Esta herramienta convierte los datos de la lectora en un archivo de Excel compatible con Studium (Moodle). 
    Necesitarás subir varios archivos, incluyendo los resultados de la lectora y un archivo de Excel de Studium, 
    y configurar los parámetros de corrección.

    ### 📝 Submission Verifier
    Esta herramienta permite inspeccionar un fichero zip de entregas de Moodle junto con un listado de alumnos de Moodle
    para comprobar si en sus entregas se incluye algun fichero con alguna de las extensiones especificadas. Se añade una columna
    con un 1 si se ha encontrado algún fichero de alguno de los tipos introducidos y 0 en caso contrario.

    """
  )