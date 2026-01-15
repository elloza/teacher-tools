# 🎓 Teacher Tools

> Conjunto de herramientas web para automatizar tareas comunes en la vida diaria de un profesor universitario.

## 🔒 Privacidad y Seguridad

**Todos tus datos permanecen en tu ordenador.** Esta aplicación está desarrollada con [stlite](https://github.com/whitphx/stlite), una versión de Streamlit que se ejecuta **100% en tu navegador** gracias a WebAssembly (Pyodide).

- ✅ No se envían datos a ningún servidor
- ✅ Todo el procesamiento ocurre localmente en tu máquina
- ✅ Tus archivos Excel, PDFs y ZIPs nunca salen de tu PC
- ✅ Código abierto y auditable en GitHub

**Excepción:** La herramienta *Studium Scraper* requiere conexión a Moodle y solo funciona en versión desktop debido a limitaciones CORS del navegador.

---

## 🎯 Propósito

Teacher Tools es una suite web diseñada para profesores de la Universidad de Salamanca (y otras instituciones) que utilizan **Moodle/Studium** y sistemas de actas oficiales. Automatiza tareas repetitivas relacionadas con:

- 📊 Procesamiento de calificaciones de exámenes tipo test (lectora óptica)
- 🔄 Cruce de notas entre Studium y actas oficiales
- 📈 Análisis de participación de estudiantes en Moodle
- ✅ Verificación de entregas de trabajos
- 🗂️ Manipulación avanzada de archivos Excel

---

## 🏗️ Arquitectura

### Stack Tecnológico

```
┌─────────────────────────────────────────┐
│         Navegador del Usuario           │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Frontend: stlite/Streamlit      │ │
│  │   (Python UI en WebAssembly)      │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Motor: Pyodide (Python WASM)    │ │
│  │   - pandas, fuzzywuzzy            │ │
│  │   - openpyxl, matplotlib          │ │
│  │   - BeautifulSoup, reportlab      │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Archivos del Usuario            │ │
│  │   (Excel, PDF, ZIP)               │ │
│  │   ⚠️ NUNCA SALEN DEL NAVEGADOR    │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
           │
           │ Solo archivos estáticos (.py, .html)
           ↓
┌─────────────────────────────────────────┐
│       GitHub Pages / CDN                │
│       (Hosting estático)                │
└─────────────────────────────────────────┘
```

### Características de la Arquitectura

- **Sin Backend:** No hay servidor Node.js, Flask, Django, etc.
- **Serverless:** Deploy simple en GitHub Pages o cualquier hosting estático
- **Client-Side Processing:** Toda la lógica se ejecuta en el navegador
- **WebAssembly:** Python compilado a WASM para rendimiento nativo
- **Dependencias Automáticas:** Se instalan en el navegador al cargar la aplicación

---

## 🛠️ Herramientas Disponibles

### 1️⃣ **Join Excel Files**
**Ubicación:** `pages/JoinExcel.py`

Combina dos archivos Excel realizando un LEFT JOIN basándose en columnas comunes.

**Características:**
- Renombrado de columnas de unión
- Estadísticas de coincidencias (total, encontrados, no encontrados)
- Exportación a Excel del resultado

**Caso de uso:** Fusionar listas de estudiantes de diferentes fuentes.

---

### 2️⃣ **Only Last Answer**
**Ubicación:** `pages/OnlyLastAnswer.py`

Filtra registros duplicados en Excel, manteniendo solo la última entrada por estudiante.

**Características:**
- Filtrado por columnas de ID y timestamp
- Exportación a CSV y Excel
- Útil para cuestionarios con múltiples intentos

**Caso de uso:** Obtener solo la última entrega de un cuestionario Moodle donde los estudiantes pudieron rehacer el examen.

---

### 3️⃣ **Lectora to Studium Excel Tool**
**Ubicación:** `pages/StudiumExcelTool.py` + `utils/StudiumExcelToolUtils.py`

Procesa archivos de **lectora óptica** (.DAT) y los cruza con datos de Studium (Moodle) para calcular notas automáticamente.

**Características:**
- Cálculo de notas con descuento configurable por respuesta incorrecta
- Fuzzy matching para identificar estudiantes (tolera errores en nombres)
- Rango personalizado de preguntas (ej: solo preguntas 5-20)
- Exportación con nota final calculada

**Caso de uso:** Procesar exámenes tipo test escaneados con lectora óptica y generar notas finales para Moodle.

---

### 4️⃣ **Studium Excel 2 Actas** ⭐
**Ubicación:** `pages/StudiumExcel2Actas.py`

Cruza notas de Studium (Moodle) con **actas oficiales de USAL** preservando el formato original del Excel.

**Características:**
- Matching inteligente por nombre y apellidos (fuzzywuzzy)
- Normalización de texto (acentos, mayúsculas/minúsculas)
- **Preserva formato del Excel** (colores, bordes, fórmulas) usando openpyxl
- Umbral de similitud configurable (default 70%)
- Redondeo de decimales configurable
- Exportación lista para enviar a secretaría

**Caso de uso:** Rellenar automáticamente las actas oficiales de USAL con las notas de Moodle sin perder el formato del documento.

---

### 5️⃣ **Studium Scraper** 🌐
**Ubicación:** `pages/StudiumScraper.py` + `utils/ScraperUtils.py`

Extrae datos de participación de estudiantes desde Moodle/Studium.

**Características:**
- Descarga lista de participantes del curso
- Extrae registros de actividad por estudiante
- Genera **gráficos de contribución** tipo GitHub
- Crea informes PDF individuales o masivos
- Requiere cookies de sesión de Moodle

**⚠️ Limitación:** Solo funciona en versión desktop por restricciones CORS del navegador.

**Caso de uso:** Generar informes de participación individuales para evaluar la actividad continua de los estudiantes en Moodle.

---

### 6️⃣ **Submission Verifier**
**Ubicación:** `pages/SubmissionVerifier.py`

Verifica entregas de trabajos de Moodle en formato ZIP masivo.

**Características:**
- Comprueba existencia de tipos de archivos específicos (PDF, DOCX, etc.)
- Fuzzy matching de nombres de estudiantes
- Extracción recursiva de ZIPs anidados
- Añade columna "Entregado" (0/1) al Excel de Studium
- Soporta hasta 5GB de archivos

**Caso de uso:** Verificar rápidamente qué estudiantes entregaron correctamente sus trabajos en el formato solicitado.

---

## 🚀 Uso

### Opción 1: Versión Web (Recomendado)
1. Accede a la aplicación desplegada en GitHub Pages *(URL pendiente)*
2. Selecciona la herramienta deseada en el menú lateral
3. Carga tus archivos Excel/ZIP/DAT
4. Configura los parámetros necesarios
5. Descarga el resultado procesado

### Opción 2: Ejecución Local (Desktop)
```bash
# Clonar el repositorio
git clone https://github.com/elloza/teacher-tools.git
cd teacher-tools

# Instalar dependencias
pip install streamlit pandas fuzzywuzzy openpyxl beautifulsoup4 matplotlib pypdf reportlab urllib3

# Ejecutar la aplicación
streamlit run Overview.py
```

**Nota:** Para usar el Studium Scraper, debes ejecutar la versión desktop debido a limitaciones CORS.

---

## 📦 Estructura del Proyecto

```
teacher-tools/
├── Overview.py                    # Página principal
├── index.html                     # Configuración stlite (web)
├── README.md                      # Este archivo
├── LICENSE                        # Licencia del proyecto
├── pages/                         # Herramientas (multi-página)
│   ├── JoinExcel.py
│   ├── OnlyLastAnswer.py
│   ├── StudiumExcelTool.py
│   ├── StudiumExcel2Actas.py
│   ├── StudiumScraper.py
│   └── SubmissionVerifier.py
├── utils/                         # Utilidades compartidas
│   ├── StudiumExcelToolUtils.py
│   └── ScraperUtils.py
├── img/                           # Recursos de imágenes
│   └── cookies.png
└── .streamlite/                   # Configuración de Streamlit
    └── config.toml
```

---

## 🔧 Dependencias

Todas las dependencias se instalan automáticamente en el navegador al cargar la aplicación web:

- **pandas:** Manipulación de datos tabulares
- **fuzzywuzzy:** Matching difuso de nombres
- **openpyxl:** Lectura/escritura Excel preservando formato
- **beautifulsoup4:** Scraping HTML de Moodle
- **matplotlib:** Generación de gráficos
- **pypdf:** Manipulación de archivos PDF
- **reportlab:** Generación de informes PDF
- **urllib3:** Peticiones HTTP

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-herramienta`)
3. Commit tus cambios (`git commit -m 'Añade nueva herramienta X'`)
4. Push a la rama (`git push origin feature/nueva-herramienta`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo [LICENSE](LICENSE).

---

## 🙏 Agradecimientos

- [stlite](https://github.com/whitphx/stlite) - Por hacer posible ejecutar Streamlit en el navegador
- [Pyodide](https://pyodide.org/) - Python en WebAssembly
- [Streamlit](https://streamlit.io/) - Framework de UI para Python

---

## 📧 Contacto

Para reportar bugs, solicitar features o hacer preguntas, abre un [issue en GitHub](https://github.com/elloza/teacher-tools/issues).

---

**Desarrollado con ❤️ para la comunidad docente de la Universidad de Salamanca**
