import streamlit as st
import pandas as pd
from github import Github
import datetime
import json

st.set_page_config(page_title="Repository Analyzer", page_icon="🔍")

st.title("🔍 Repository Analyzer")
st.markdown("""
¡Bienvenido a la herramienta **Repository Analyzer**! 🎉

### ¿Qué hace esta herramienta?
Esta aplicación te permite analizar los repositorios de GitHub de tus alumnos. Puedes subir un archivo de Excel con las URLs de los repositorios y obtener información sobre los commits realizados.

### ¿Qué necesitas hacer?
1. **Sube tu archivo de Excel** usando el botón de carga de archivos. 📂
2. **Selecciona la columna con las URLs de los repositorios**. 🌐
3. **Introduce tu token de GitHub** para autenticarte. 🔑

### ¿Qué obtienes?
- Una tabla con el número de commits y los datos de cada commit (fecha y líneas cambiadas) para cada repositorio. 📋
""")

# Función para obtener los datos del repositorio
def get_repo_data(repo_url, github_token):
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_url.replace("https://github.com/", ""))
        commits = repo.get_commits()
        
        commit_data = []
        for commit in commits:
            commit_date = commit.commit.author.date
            lines_changed = commit.stats.total
            commit_data.append((commit_date, lines_changed))
        
        num_commits = len(commits)
        if num_commits > 0:
            first_commit_date = commits[-1].commit.author.date
            last_commit_date = commits[0].commit.author.date
            months = (last_commit_date.year - first_commit_date.year) * 12 + last_commit_date.month - first_commit_date.month + 1
            avg_commits_per_month = num_commits / months
        else:
            avg_commits_per_month = 0
        
        return num_commits, avg_commits_per_month, commit_data
    except Exception:
        return None, None, None

# Cargar el archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Archivo cargado con éxito")
    
    # Seleccionar la columna con las URLs de los repositorios
    column = st.selectbox("Selecciona la columna con las URLs de los repositorios", df.columns)
    
    # Autenticación en GitHub
    github_token = st.text_input("Introduce tu token de GitHub", type="password")
    
    if github_token and column:
        if st.button("Iniciar análisis"):
            # Inicializar la barra de progreso
            progress_bar = st.progress(0)
            total_rows = len(df)
            
            # Procesar cada URL en la columna seleccionada
            results = []
            for index, row in df.iterrows():
                repo_url = row[column]
                if pd.notna(repo_url):
                    num_commits, avg_commits_per_month, commit_data = get_repo_data(repo_url, github_token)
                    if num_commits is not None:
                        df.at[index, "Número de commits"] = num_commits
                        df.at[index, "Promedio de commits por mes"] = avg_commits_per_month
                        df.at[index, "Datos de commits"] = json.dumps([{"fecha": str(date), "lineas_cambiadas": lines} for date, lines in commit_data])
                
                # Actualizar la barra de progreso
                progress_bar.progress((index + 1) / total_rows)
            
            # Mostrar los resultados
            st.write(df)
            
            # Permitir la descarga del archivo Excel resultante
            output_file = "resultados_analisis.xlsx"
            df.to_excel(output_file, index=False)
            with open(output_file, "rb") as file:
                btn = st.download_button(
                    label="Descargar resultados",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
