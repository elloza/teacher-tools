import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from pypdf import PdfWriter, PdfReader
import io
import tempfile
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import urllib3

http = urllib3.PoolManager()

def download_participant_logs(auth_token, course_id, user_id, moodle_session):
    log_url_template = "https://studium24.usal.es/report/log/index.php?sesskey={}&download=csv&id={}&user={}&modid=&chooselog=1&logreader=logstore_standard"
    log_url = log_url_template.format(auth_token, course_id, user_id)
    headers = {"Cookie": f"MoodleSession={moodle_session}"}
    response = http.request("GET", log_url, headers=headers)
    if response.status == 200:
        try:
            df = pd.read_csv(io.StringIO(response.data.decode('utf-8')))
            return df
        except Exception as e:
            return None
    else:
        return None

def generate_contribution_chart(activity_series):
    try:
        # Preparar fechas y contribuciones
        activity_series = activity_series.resample('D').sum().fillna(0)
        activity_df = activity_series.reset_index()
        activity_df.columns = ["Fecha", "Contribuciones"]

        # Crear columnas de día y semana consecutiva
        activity_df["Semana"] = ((activity_df["Fecha"] - activity_df["Fecha"].min()).dt.days // 7)
        activity_df["Día"] = activity_df["Fecha"].dt.weekday

        # Crear matriz de contribuciones
        semanas_totales = activity_df["Semana"].max() + 1
        matrix = np.zeros((7, semanas_totales))

        for _, row in activity_df.iterrows():
            matrix[row["Día"], row["Semana"]] += row["Contribuciones"]

        # Generar el gráfico
        fig, ax = plt.subplots(figsize=(14, 6))
        cmap = plt.cm.Greens
        norm = mcolors.Normalize(vmin=0, vmax=matrix.max())

        for day in range(7):
            for week in range(matrix.shape[1]):
                color = cmap(norm(matrix[day, week]))
                ax.add_patch(plt.Rectangle((week, day), 1, 1, color=color))
                # Añadir el valor en cada celda si es mayor a 0
                if matrix[day, week] > 0:
                    ax.text(week + 0.5, day + 0.5, int(matrix[day, week]), color="black", ha="center", va="center", fontsize=8)

        # Configuración de los ejes
        ax.set_xlim(0, matrix.shape[1])
        ax.set_ylim(-0.5, 6.5)
        ax.set_yticks(range(7))
        ax.set_yticklabels(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        ax.invert_yaxis()

        # Configurar las etiquetas del eje x con fechas de inicio de cada semana
        week_labels = [(activity_df["Fecha"].min() + pd.Timedelta(weeks=w)).strftime("%d-%b") for w in range(semanas_totales)]
        ax.set_xticks(np.arange(0.5, len(week_labels) + 0.5, 1))
        ax.set_xticklabels(week_labels, rotation=45, ha="right")

        # Barra de color
        plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, orientation="vertical", label="Contribuciones")

        ax.set_title("Contribuciones por Día y Semana")
        return fig
    except Exception as e:
        st.error(f"Error al generar el gráfico: {e}")
        return None

def generate_pdf_report(participant_name, img_path):
    # Crear un PDF temporal con la imagen usando reportlab
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        img_pdf_path = tmpfile.name
        c = canvas.Canvas(img_pdf_path, pagesize=A4)
        width, height = A4

        # Añadir texto al PDF como título centrado
        text_y_position = height - 40
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, text_y_position, f"Informe de Actividad para {participant_name}")

        # Añadir imagen al PDF ocupando todo el ancho hasta los márgenes
        image_y_position = text_y_position - 60  # Ajustar la posición de la imagen
        image_height = height - 100  # Ajustar la altura de la imagen
        c.drawImage(ImageReader(img_path), 0, image_y_position - image_height, width=width, height=image_height, preserveAspectRatio=True, mask='auto')

        c.showPage()
        c.save()

    # Leer el PDF temporal y combinarlo con el PDF principal usando pypdf
    pdf_writer = PdfWriter()
    with open(img_pdf_path, "rb") as img_pdf_file:
        img_pdf_reader = PdfReader(img_pdf_file)
        pdf_writer.add_page(img_pdf_reader.pages[0])

    # Guardar el PDF final en un objeto BytesIO
    output = io.BytesIO()
    pdf_writer.write(output)
    output.seek(0)
    os.unlink(img_pdf_path)  # Limpiar el archivo temporal
    return output
