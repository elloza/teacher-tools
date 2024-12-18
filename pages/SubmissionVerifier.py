import streamlit as st
import pandas as pd
import zipfile
import os
from pathlib import Path
from fuzzywuzzy import process

def check_submissions(excel_file, zip_file, file_types, name_column, last_name_column, delivery_column='Entregado'):
    # Create tmp directory if it doesn't exist
    tmp_dir = Path('tmp')
    tmp_dir.mkdir(exist_ok=True)
    
    submissions_dir = tmp_dir / 'submissions'
    submissions_dir.mkdir(exist_ok=True)
    
    # Load the Excel file
    df = pd.read_excel(excel_file)
    
    # Create a column "Entregado" initialized to 0
    df[delivery_column] = 0
    
    # Extract the zip file into tmp/submissions
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(submissions_dir)

    # Assure that there is no further compressed files in each student directory
    for root, dirs, files in os.walk(submissions_dir):
        for file in files:
            if file.endswith('.zip'):
                with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref:
                    zip_ref.extractall(root)
                os.remove(os.path.join(root, file))

    
    # Generate a single column with the full name
    df['Nombre Completo'] = df[name_column] + ' ' + df[last_name_column]
    
    # Check each submission directory for extract students names and get the index from the dataframe
    # only directories a first level deep

    for student_dir in submissions_dir.iterdir():
        if student_dir.is_dir():
            student_name = student_dir.name
            student_name = student_name.split('_')[0]
            
            # Check if the student name is in the dataframe
            match = process.extractOne(student_name, df['Nombre Completo'])
            if match[1] > 90:
                
                # Comprobar si hay archivos del tipo correcto de forma recursiva en este directorio
                for root, dirs, files in os.walk(student_dir):
                    for file in files:
                        if file.split('.')[-1] in file_types:
                            df.loc[match[2], delivery_column] = 1
                            break
                    else:
                        continue
                    break

    
    # Clean up the extracted files
    for root, dirs, files in os.walk(submissions_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    
    # Remove the submissions directory
    submissions_dir.rmdir()
    
    return df

st.title('🎯 ¡Verificador de Entregas!')

# Widgets de carga
excel_file = st.file_uploader("📚 Sube el Excel con la Lista de Estudiantes", type=["xlsx"])

# Una vez se haya subido ofrecer selectores para la columna nombre y la columna de apellidos de streamlite
# para que el usuario pueda seleccionar las columnas de nombre y apellidos

if excel_file:

    # las opciones vienen de las columnas del excel
    df = pd.read_excel(excel_file)
    columns = df.columns

    # Seleccionar la columna de nombre
    name_column = st.selectbox('👤 Selecciona la columna de Nombre', options=columns)

    # Seleccionar la columna de apellidos
    last_name_column = st.selectbox('👤 Selecciona la columna de Apellidos', options=columns)


zip_file = st.file_uploader("📦 Sube el ZIP con las Entregas", type=["zip"])
file_types = st.text_input("✨ ¿Qué tipos de archivo buscamos? (separados por coma)", "pdf,docx")

# After file_types input and before verification button
delivery_column = st.text_input("📝 ¿Cómo quieres llamar a la columna de entrega?", "Entregado")

if st.button('🔍 ¡A Verificar!'):
    if excel_file and zip_file:
        file_types_list = [ft.strip() for ft in file_types.split(',')]
        # Pass delivery_column name to check_submissions function
        result_df = check_submissions(excel_file, zip_file, file_types_list, name_column, last_name_column, delivery_column)
        st.write("🎉 ¡Aquí están los resultados!")
        st.write(result_df)
        
        # Botón de descarga
        st.download_button(
            label="⬇️ Descarga los Resultados",
            data=result_df.to_csv(index=False).encode('utf-8'),
            file_name='resultados_entregas.csv',
            mime='text/csv'
        )
    else:
        st.error("🚨 ¡Ups! Necesito tanto el Excel como el ZIP para poder ayudarte")