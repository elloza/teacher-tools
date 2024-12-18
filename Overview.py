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

    ### 📝 [Join Excel Files](JoinExcel)
    Esta herramienta permite unir dos archivos de Excel en función de una columna común. 
    Puedes seleccionar las columnas de unión de cada archivo y descargar el archivo combinado.

    ### 📝 [Only Last Answer](OnlyLastAnswer)
    Esta herramienta procesa un archivo de Excel para obtener solo la última respuesta de cada identificador único. 
    Puedes seleccionar la columna de identificación y la columna de tiempo para realizar el filtrado.

    ### 📝 [Lectora to Studium Excel Tool](StudiumExcelTool)
    Esta herramienta convierte los datos de la lectora en un archivo de Excel compatible con Studium (Moodle). 
    Necesitarás subir varios archivos, incluyendo los resultados de la lectora y un archivo de Excel de Studium, 
    y configurar los parámetros de corrección.
    """
  )