# Para gestionar ficheros
# -----------------------------------------------------------------------
import os
import glob

# Para trabajar con access
# -----------------------------------------------------------------------
import subprocess


# Para trabajar con DataFrames
# -----------------------------------------------------------------------
import pandas as pd


# Para trabajar con regex
# -----------------------------------------------------------------------
import re


def sacar_nombres_tablas_access(ruta):
    """
    Obtiene una lista de nombres de tablas desde una base de datos de Microsoft Access (.mdb).

    Esta función usa el comando de línea de comandos `mdb-tables` para listar los nombres de tablas en un archivo .mdb especificado. El comando se ejecuta y su salida se procesa para extraer los nombres de las tablas.

    Params:
        - ruta (str): La ruta completa al archivo de base de datos de Access (.mdb) desde el cual se desea obtener los nombres de las tablas.

    Returns:
        Una lista de nombres de tablas presentes en la base de datos de Access. Las entradas vacías se excluyen de la lista.
    """

    # Ejecuta el comando 'mdb-tables' con el archivo .mdb especificado
    result = subprocess.run([ 
                            'mdb-tables', # nos permite listar las tablas en una base de datos de Access.
                             '-1', # es una opción que hace que mdb-tables devuelva una lista de tablas. 
                             ruta # es la ruta del archivo .mdb (del archivo de access)
                             ], 
                            capture_output=True, # nos muestra tanto los mensajes de error como como los mensajes normales
                            text=True # hace que la salida capturada se devuelva como una cadena de texto en lugar de bytes
                            )
    # Divide la salida del comando en líneas individuales
    tablas = result.stdout.split('\n')
    
    # Devuelve una lista de nombres de tablas, excluyendo cualquiera que esté vacía
    return [tabla for tabla in tablas if tabla]


def convertir_access_txt(tablas, ruta, ruta_destino):
    """
    Convierte tablas específicas de una base de datos Access a archivos de texto.

    Params:
        - tablas (list): Una lista de nombres de tablas a convertir.
        - ruta (str): La ruta de la base de datos Access (.mdb).
        - ruta_destino (str): La ruta de la carpeta donde se guardarán los archivos de texto.

    Returns:
        No devuelve nada
    """

    # iteramos por cada una de las tablas que tenemos en los archivos de access
    for table in tablas:

        # si el nombre de la tabla empieza por "C". Esto lo hacemos porque en algunas de los ficheros de access hay tablas adicionales que no nos aportan valor, y todas las que tenemos empiezan por "C"
        if table.startswith("C"):

            # definimos la ruta donde vamos a querer guardar las tablas de access en formato txt.
            csv_output = os.path.join(ruta_destino, f'{table}.txt')

            # guardamos el archivo de la tabla a la que estamos accediendo
            with open(csv_output, 'w') as f:
                subprocess.run(['mdb-export', # exportamos los datos de la tabla específica desde un archivo access.
                                ruta, # especificamos la ruta donde queremos guardarla
                                table], # especificamos la tabla que queremos exportar
                                stdout=f) # especificamos que queremos guardar los datos en un archivo externo
            print(f'Datos exportados a {csv_output}')


def crear_df_ingresos(ruta_origen, ruta_destino, anio, tipos_hospitalizacion=["hospital", "hospdom", "hospdia"], mapeo={'700': 'particulares', '701': 'aseguradoras', '701_1': 'aseguradoras_enfermedad', '701_2': 'aseguradoreas_trafico', '702': 'mutuas'}):
    """
    Crea un DataFrame con los datos de ingresos de distintos tipos de hospitalización y mapea las columnas a nombres más comprensibles.

    Params:
        - ruta_origen (str): Ruta del archivo CSV que contiene los datos de ingresos.
        - ruta_destino (str): Ruta del archivo donde se guardará el DataFrame resultante en formato CSV.
        - tipos_hospitalizacion (list, opcional): Lista de tipos de hospitalización a considerar. Por defecto, incluye "Hospital", "HospDom", "hospDia".
        - mapeo (dict, opcional): Diccionario para renombrar las columnas de ingresos. Por defecto, mapea algunas columnas específicas a nombres más comprensibles.
  
    Returns:
        pd.DataFrame: DataFrame con los datos de ingresos filtrados, con las columnas renombradas y tipos de hospitalización añadidos.

    """

    # Leer el archivo CSV con los datos de ingresos
    df = pd.read_csv(ruta_origen, encoding='latin-1', sep=";")

    # cambiamos el nombre de las columnas para ponerlas todas en minúsculas, para evitar problemas en el futuro
    df.columns = [col.lower() for col in df.columns]

    # hay algunos ficheros cuya separación en las columnas no es por ';' y además que no tienen encoding, en ese caso
    # si abrimos el fichero con la línea anterior, solo nos devuelve una columna, por lo que aprovechamos esa condición 
    if df.shape[1] == 1: 
        df = pd.read_csv(ruta_origen)
        df.columns = [col.lower() for col in df.columns]

    # Crear un DataFrame vacío para almacenar los datos filtrados
    df_ingresos_tipos = pd.DataFrame()


    # Filtrar y agregar los datos por cada tipo de hospitalización
    for tipo in tipos_hospitalizacion:

        # filtramos, quedándonos solo con las columnas del tipo de hospitalización al que estamos accediendo
        df_tipo = df.filter(like=tipo)
        
        # Seleccionar las columnas que tienen los códigos de ingresos seleccionados
        df_tipo = df_tipo.filter(regex="7(00|01|02)")

        df_tipo.columns = ["_".join(re.findall("\d+", i)) for i in df_tipo.columns]

        # Añadir las columnas de año y código del centro
        df_tipo[["año", "ncodi"]] = df[["año", "ncodi"]]

        # Añadir una columna con el tipo de hospitalización
        df_tipo["tipo_hospitalizacion"] = tipo


        # Agregar al DataFrame que hemos creado vacío
        df_ingresos_tipos = pd.concat([df_tipo, df_ingresos_tipos], axis=0)

    # Renombrar las columnas según el mapeo proporcionado
    df_ingresos_tipos.rename(columns=mapeo, inplace=True)

    # la columna de 'ncodi' en algunos ficheros está en formato de string, por lo que a esos ficheros les vamos a quitar las ',' y convertirlo a float
    try:
        # Convertir el código del centro a float, reemplazando las comas por puntos
        df_ingresos_tipos["ncodi"] = df_ingresos_tipos["ncodi"].str.replace(",", ".").astype(float)

    # en caso de que este en formato número, no hacemos nada
    except:
        pass

    # guardamos los datos en la carpeta especificada
    df_ingresos_tipos.to_csv(f"{ruta_destino}/datos_ingresos_{anio}.csv", index=False)


    return df_ingresos_tipos

def crear_df_gastos(ruta_origen, ruta_destino, anio):
    """
    Crea un DataFrame a partir de un archivo CSV con los datos de ingresos, renombrando las columnas para eliminar números y caracteres no alfabéticos.

    Params:
        - ruta_origen (str): Ruta del archivo CSV que contiene los datos de ingresos.
        - ruta_destino (str): Ruta del archivo donde se guardará el DataFrame resultante en formato CSV.


    Returns:
        pd.DataFrame: DataFrame con los datos de ingresos con columnas renombradas y el código del centro convertido a tipo float.

    """

    # Leer el archivo CSV con los datos de ingresos
    df = pd.read_csv(ruta_origen, encoding='latin-1', sep=";")

    # cambiamos el nombre de las columnas para ponerlas todas en minúsculas, para evitar problemas en el futuro
    df.columns = [col.lower() for col in df.columns]

    # hay algunos ficheros cuya separación en las columnas no es por ';' y además que no tienen encoding, en ese caso
    # si abrimos el fichero con la línea anterior, solo nos devuelve una columna, por lo que aprovechamos esa condición 
    if df.shape[1] == 1: 
        df = pd.read_csv(ruta_origen)
        df.columns = [col.lower() for col in df.columns]


    # cambiamos el nombre de las columnas para ponerlas todas en minúsculas, para evitar problemas en el futuro
    df.columns = [col.lower() for col in df.columns]

    # Definir el patrón para eliminar números y caracteres no alfabéticos de los nombres de las columnas
    patron = "\D+"

    # Renombrar las columnas aplicando el patrón definido
    df.columns = [re.findall(patron, col.replace("_", ""))[0] for col in df.columns]

    # la columna de 'ncodi' en algunos ficheros está en formato de string, por lo que a esos ficheros les vamos a quitar las ',' y convertirlo a float
    try:
        # Convertir el código del centro a float, reemplazando las comas por puntos
        df["ncodi"] = df["ncodi"].str.replace(",", ".").astype(float)

    # en caso de que este en formato número, no hacemos nada
    except:
        pass


    # guardamos los datos en la carpeta especificada
    df.to_csv(f"{ruta_destino}/datos_gastos_{anio}.csv", index=False)

    return df


def leer_todos_archivos(patron, ruta_origen, nombre_fichero):
    """
    Lee todos los archivos que coinciden con un patrón en una ruta específica, los concatena en un DataFrame y 
    guarda el DataFrame resultante en un archivo CSV.

    Params:
        - patron (str): El patrón de búsqueda para los nombres de archivo. Puede incluir comodines, por ejemplo, '*.csv'.
        - ruta_origen (str): La ruta del directorio donde se buscarán los archivos.
        - nombre_fichero (str):  El nombre del archivo CSV resultante (sin la extensión .csv).

    Returns:

        pandas.DataFrame: Un DataFrame que contiene la concatenación de todos los archivos leídos.
    """
    
    # usamos glob para buscar todos los archivos que coinciden con el patrón
    archivos = glob.glob(f"{ruta_origen}/{patron}")
    # definimos un DataFrame para concatenar los csv que vamos abriendo
    df_concatenado = pd.DataFrame()

    # iteramos por la lista de archivos que hemos buscado previamente
    for archivo in archivos:
        # leemos el archivo con Pandas
        df = pd.read_csv(archivo)  

        # lo concatenamos con el DataFrame que hemos definido previamente
        df_concatenado = pd.concat([df_concatenado, df], axis = 0, ignore_index=True)

    # Guardar el DataFrame concatenado en un archivo CSV
    df_concatenado.to_csv(f"{ruta_origen}/{nombre_fichero}.csv", index=False)

    return df_concatenado


def unir_datos(dataframe_gastos, dataframe_ingresos, ruta_destino):
    """
    Une dos DataFrames de gastos e ingresos hospitalarios en función de las columnas 'año' y 'NCODI', 
    y guarda el resultado en un archivo CSV.

    Params:
        - dataframe_gastos (pd.DataFrame): DataFrame que contiene los datos de gastos hospitalarios.
        - dataframe_ingresos (pd.DataFrame): DataFrame que contiene los datos de ingresos hospitalarios.
        - ruta_destino (str): Ruta del archivo donde se guardará el DataFrame resultante en formato CSV.

    Returns:
        No devuelve nada
    """

    # unimos los dos conjuntos de datos 
    df = pd.merge(dataframe_gastos, dataframe_ingresos, on=['año', 'ncodi'], suffixes=('_gasto', '_ingreso'))
    
    # guardamos los datos en la carpeta especificada
    df.to_csv(f"{ruta_destino}/todos_datos.csv", index=False)

