import streamlit as st

import pandas as pd
from io import BytesIO

st.set_page_config(page_title = "Only last answer", page_icon = "📝")

# Descripción en markdown de la página
st.markdown("""
# 📝 Only Last Answer

¡Bienvenido a la herramienta **Only Last Answer**! 🎉

### ¿Qué hace esta herramienta?
Esta aplicación te permite subir un archivo de Excel 📊 y procesarlo para obtener solo la última respuesta de cada identificador único. 

### ¿Qué necesitas hacer?
1. **Sube tu archivo de Excel** usando el botón de carga de archivos. 📂
2. **Selecciona la columna de identificación** (por ejemplo, ID de usuario). 🆔
3. **Selecciona la columna de tiempo** (por ejemplo, fecha y hora de la respuesta). ⏰

### ¿Qué obtienes?
- Una tabla con solo la última respuesta de cada identificador único. 📋
- La opción de descargar esta tabla en formato CSV o Excel. 📥

¡Esperamos que disfrutes usando esta herramienta! 😊
""")

uploaded_file = st.file_uploader("Sube tu archivo de Excel", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    columns = df.columns.tolist()
    id_column = st.selectbox("Selecciona la columna de identificación", columns)
    time_column = st.selectbox("Selecciona la columna de tiempo", columns)
    if id_column and time_column:
        if id_column in df.columns and time_column in df.columns:

            df[time_column] = pd.to_datetime(df[time_column])
            df_sorted = df.sort_values(by=time_column, ascending=False)
            df_last_answers = df_sorted.drop_duplicates(subset=id_column, keep='first')
            
            # Mostrar solo los repetidos en la previsualización
            df_duplicates = df[df.duplicated(subset=id_column, keep=False)]
            st.dataframe(df_duplicates)

            num_duplicates = df.duplicated(subset=id_column).sum()
            st.write(f"Número total de repetidos: {num_duplicates}")

            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df_to_csv(df_last_answers)
            st.download_button("Descargar CSV", data=csv, file_name="last_answers.csv", mime="text/csv")

            @st.cache_data
            def convert_df_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Hoja1')
                return output.getvalue()

            excel = convert_df_to_excel(df_last_answers)
            st.download_button("Descargar Excel", data=excel, file_name="last_answers.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error("Las columnas especificadas no existen en el archivo.")
