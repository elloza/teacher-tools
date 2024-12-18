import pandas as pd
from fuzzywuzzy import process
import re
from io import StringIO

# Función para leer el archivo TXT de calificaciones
def leer_archivo_txt(uploaded_file, prefijo_columna="Test"):
    
    # Read lines
    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode('latin-1'))
    lineas = stringio.readlines()

    datos = []
    for linea in lineas:
        if linea.startswith('N'):
            break
        if len(linea.strip()) == 0:
            continue
        if len(linea.strip()) < 9:
            continue

        identificacion = linea[:9].strip()
        nota = linea[-7:].strip().replace(',', '.')
        datos.append([identificacion, nota])

    return pd.DataFrame(datos, columns=[f'{prefijo_columna}_Identificacion', f'{prefijo_columna}_Nota'])

# Función para leer el archivo Excel de Moodle
def leer_archivo_excel(ruta_archivo):
    return pd.read_excel(ruta_archivo)

# Función para comparar identificaciones
def comparar_identificaciones(identificacion, lista_ids, umbral):

    dictionary_ids = {}
    for id in lista_ids:
        new_identifier =  re.sub(r'\D', '', id).lower()
        dictionary_ids[new_identifier] = id

    match = process.extractOne(identificacion, list(dictionary_ids.keys()), score_cutoff=umbral)

    if match:
        return dictionary_ids[match[0]]
    else:
        return None

# Función para leer y procesar el fichero DAT
def leer_y_procesar_fichero_DAT(uploaded_file_lecturas,uploaded_file_soluciones, num_preguntas=10, descuento=0.33, prefijo_columna="Test"):
    datos = []

    soluciones_test = dict()

    stringio = StringIO(uploaded_file_soluciones.getvalue().decode('utf-8'))
    lineas_sol = stringio.readlines()

    for linea in lineas_sol:
        soluciones_test[int(linea[14:17])] = [int(linea[i]) for i in range(17, 17+num_preguntas)]

    stringio = StringIO(uploaded_file_lecturas.getvalue().decode('utf-8'))
    lineas_lecturas = stringio.readlines()
    
    for linea in lineas_lecturas:
        dni = linea[6:14]
        dni = dni.zfill(9)
        opcion = int(linea[14:17])
        respuestas = [int(linea[i]) for i in range(17, 17+num_preguntas)]
        respuestas_correctas = soluciones_test[opcion]
        # numero de respuestas sin marcar (valor 0)
        respuestas_no_contestadas = respuestas.count(0)
        # numero de respuestas correctas
        respuestas_correctas = sum([1 for i in range(num_preguntas) if respuestas[i] == respuestas_correctas[i]])
        # numero de respuestas incorrectas cuyo valor es distinto de 0 y de la respuesta correcta
        respuestas_incorrectas = sum([1 for i in range(num_preguntas) if respuestas[i] != 0 and respuestas[i] != soluciones_test[opcion][i]])
        # Nota numero de respuestas correctas - numero de respuestas incorrectas * descuento
        nota = respuestas_correctas - respuestas_incorrectas * descuento
        # Respuestas poniendo 0 a las no contestadas -descuento a las incorrectas y 1 a las correctas
        respuestas_valores = [0 if respuestas[i] == 0 else 1 if respuestas[i] == soluciones_test[opcion][i] else -descuento for i in range(num_preguntas)]

        # Juntar toda la información en una lista
        datos.append([dni, opcion, nota,respuestas_correctas,respuestas_incorrectas,respuestas_no_contestadas] + respuestas + respuestas_valores)

    columnas = [f'{prefijo_columna}_DNI', f'{prefijo_columna}_Opción', f'{prefijo_columna}_Nota',f'{prefijo_columna}_Respuestas correctas',f'{prefijo_columna}_Respuestas incorrectas',f'{prefijo_columna}_Respuestas no contestadas'] + [f'{prefijo_columna}_Pregunta {i}' for i in range(1, num_preguntas+1) ] + [f'{prefijo_columna}_Pregunta {i} valor' for i in range(1, num_preguntas+1) ]
    return pd.DataFrame(datos, columns=columnas)

# Función para combinar los datos
def combinar_datos(df_txt, df_excel, df_dat, umbral, base_nota, prefijo_columna, num_preguntas):
    df_excel[f'{prefijo_columna}_TEST_Original_Lectora'] = None

    # Normalizar el campo [f'{prefijo_columna}_Identificacion'] para que tenga 9 dígitos y una letra
    df_excel['Número de ID'] = df_excel['Número de ID'].apply(lambda x: x[:-1].zfill(9) + x[-1] if len(x) < 10 else x)
    
    # Df no encontrados
    no_encontrados = []

    df_txt[f'{prefijo_columna}_Nota'] = df_txt[f'{prefijo_columna}_Nota'].astype(float)


    for idx, row in df_txt.iterrows():
        identificacion = row[f'{prefijo_columna}_Identificacion']
        nota = row[f'{prefijo_columna}_Nota']
        id_similar = comparar_identificaciones(identificacion, df_excel['Número de ID'].tolist(), umbral)

        if id_similar:
            df_excel.loc[df_excel['Número de ID'] == id_similar, f'{prefijo_columna}_TEST_Original_Lectora'] = nota
            # Search in df_dat in DNI colum identificacion and substitute with id_similar
            df_dat.loc[df_dat[f'{prefijo_columna}_DNI'] == identificacion, f'{prefijo_columna}_DNI'] = id_similar
        else:
            # Añadir a no encontrados entrada para crear luego un dataframe
            row[f'{prefijo_columna}_Identificacion'] = identificacion
            row[f'{prefijo_columna}_Nota'] = nota

            no_encontrados.append(row)

    df_no_encontrados = pd.DataFrame(no_encontrados, columns=[f'{prefijo_columna}_Identificacion', f'{prefijo_columna}_Nota'])
    df_combinado = pd.merge(df_excel, df_dat, left_on='Número de ID', right_on=f'{prefijo_columna}_DNI', how='left')

    # Calcular nota final de tal manera que este en la base indicada por base_nota y teniendo el numero de preguntas
    # No tener en cuenta nans
    df_combinado[f'{prefijo_columna}_Nota'] = df_combinado[f'{prefijo_columna}_Nota'].astype(float)
    df_combinado[f'{prefijo_columna}_Nota final B({base_nota})'] = (df_combinado[f'{prefijo_columna}_Nota'] * (base_nota / num_preguntas)).round(3)

    return df_combinado, df_no_encontrados

# Función para escribir el nuevo archivo Excel
def escribir_nuevo_excel(df, ruta_archivo):
    df.to_excel(ruta_archivo, index=False)