# Para trabajar con postgresql
# -----------------------------------------------------------------------
import psycopg2

# Para trabajar gestionar los nulos
# -----------------------------------------------------------------------
import numpy as np


def establecer_conn(database_name, postgres_pass, usuario, host="localhost"):
    """
    Establece una conexión a una base de datos de PostgreSQL.

    Params:
        - database_name (str): El nombre de la base de datos a la que conectarse.
        - postgres_pass (str): La contraseña del usuario de PostgreSQL.
        - usuario (str): El nombre del usuario de PostgreSQL.
        - host (str, opcional): La dirección del servidor PostgreSQL. Por defecto es "localhost".

    Returns:
        psycopg2.extensions.connection: La conexión establecida a la base de datos PostgreSQL.

    """

    # Crear la conexión a la base de datos PostgreSQL
    conn = psycopg2.connect(
        host=host,
        user=usuario,
        password=postgres_pass,
        database=database_name
    )

    # Establecer la conexión en modo autocommit
    conn.autocommit = True # No hace necesario el uso del commit al final de cada sentencia de insert, delete, etc.
    
    return conn




def crear_db(database_name):
    """
    Crea una base de datos con el nombre proporcionado si no existe ya.

    Esta función se conecta a la base de datos por defecto de PostgreSQL, verifica si una base de datos 
    con el nombre proporcionado ya existe, y la crea si no existe. Si la base de datos ya existe, se notifica 
    al usuario. 

    El proceso incluye:
    1. Conectar a la base de datos por defecto de PostgreSQL.
    2. Crear un cursor para ejecutar comandos SQL.
    3. Ejecutar una consulta para verificar la existencia de la base de datos.
    4. Crear la base de datos si no existe.
    5. Cerrar el cursor y la conexión.

    Params:
        - database_name (str): El nombre de la base de datos a crear.

    Returns:
        No devuelve nada

    """
    
    # conexion a postgres
    conn = establecer_conn("postgres", "admin", "my_user") # Nos conectamos a la base de datos de postgres por defecto para poder crear la nueva base de datos
    
    # creamos un cursor con la conexion que acabamos de crear
    cur = conn.cursor()
    
    # hacemos una consulta a postgres para ver si existe una base de datos que se llame como el nombre que pasamos como argumento
    # pg_database es una tabla del sistema en Postgres con la info de todas las bbdd
    # WHERE datname es la clausula que devuelve solo donde coincida %s
    # database_name, es una TUPLA con el nombre que buscamos. El cursor lo sustituirá en %s.
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
    
    # Almacenamos en una variable el resultado del fetchone. Si existe tendrá una fila sino será None
    bbdd_existe = cur.fetchone()
    
    # Si bbdd_existe es None, creamos la base de datos
    if not bbdd_existe:
        cur.execute(f"CREATE DATABASE {database_name};")
        print(f"Base de datos {database_name} creada con éxito")
    else:
        print(f"La base de datos ya existe")
        
    # Cerramos el cursor y la conexion
    cur.close()
    conn.close()


def sacar_tablas_columnas(nombre_bbdd, contraseña, usuario):
    """
    Extrae los nombres de las tablas y sus columnas de una base de datos PostgreSQL.

    Esta función se conecta a una base de datos PostgreSQL utilizando las credenciales proporcionadas,
    y obtiene los nombres de todas las tablas junto con los nombres de sus columnas en el esquema público.
    Devuelve un diccionario donde las claves son los nombres de las tablas y los valores son listas de nombres de columnas.

    Params:
        - nombre_bbdd (str): El nombre de la base de datos a la que se va a conectar.
        - contraseña (str): La contraseña para la base de datos.
        - usuario (str): El nombre de usuario para la base de datos.

    Returns:
        dict: Un diccionario donde las claves son los nombres de las tablas y los valores son tuplas de nombres de columnas.
    """
    
    # creamos un diccionario para almacenar los nombres de las tablas y sus columnas
    diccionario_tablas = {}

    # creamos la conexión con la base de datos con la que queremos trabajar
    conn = establecer_conn(nombre_bbdd, contraseña, usuario) 
    
    # Creamos un cursor con la conexion que acabamos de crear
    cur = conn.cursor()

    # sacamos los nombres de las tablas que tenemos en la base de datos de centros hospitalarios
    cur.execute("""SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'""")
    
    # la query anterior, nos devuelve todas las tablas de la BBDD, nos devuelve una lista de tuplas, donde cada tupla corresponde con una tabla de la BBDD
    for tabla in cur.fetchall():

        # de cada tabla extraemos las columnas, con esta query estamos sacando la tabla con 0 resultados
        cur.execute(f"SELECT * FROM {tabla[0]} LIMIT 0")

        # sacamos las columnas de la tabla por la que estamos iterando. No incluimos la columna 'id'  ya que son autoincrementales (serial) y no hace falta incluirla en el insert
        colnames = [desc[0] for desc in cur.description if desc[0] != "id"]

        # alamcenamos en el diccionario, el nombre de la tabla y sus columnas
        if len(colnames) > 1:
            diccionario_tablas[tabla[0]] = tuple(colnames)
        else:
            diccionario_tablas[tabla[0]] = colnames[0]

    return diccionario_tablas

def crear_query_insercion(tablas_columnas):
    """
    Crea un diccionario de consultas SQL de inserción para varias tablas.

    Params:
        - tablas_columnas (dict): Un diccionario donde las claves son nombres de tablas y los valores son las columnas
                            correspondientes. Las columnas pueden ser una tupla de múltiples columnas o una sola columna.

    Returns:
        dict: Un diccionario donde las claves son nombres de tablas y los valores son las consultas SQL de inserción correspondientes.

    Ejemplo:
    >>> tablas_columnas = {
    ...     'tabla1': ('col1', 'col2', 'col3'),
    ...     'tabla2': 'col1'
    ... }
    >>> crear_query_insercion(tablas_columnas)
    {
        'tabla1': 'INSERT INTO tabla1  (col1, col2, col3) VALUES (%s, %s, %s)',
        'tabla2': 'INSERT INTO tabla2 (col1) VALUES (%s)'
    }
    """
    diccionario_insercion = {}
    for tabla, columnas in tablas_columnas.items():
        if type(columnas) == tuple:
            query = f"INSERT INTO {tabla}  {columnas} VALUES ({('%s,') * (len(columnas) - 1) + '%s'})".replace("'", "")
            diccionario_insercion[tabla] = query
        else:
            query = f"INSERT INTO {tabla} ({columnas}) VALUES ({('%s')})".replace("'", "")
            diccionario_insercion[tabla] = query
  
    return diccionario_insercion


def sacar_id(nombre_bbdd, contraseña, usuario, tabla, col_id, col_valor):
    """
    Extrae las claves primarias y los valores originales de una tabla en la base de datos.

    Params:
        - nombre_bbdd (str): El nombre de la base de datos a la cual conectarse.
        - contraseña (str): La contraseña para acceder a la base de datos.
        - usuario (str): El nombre de usuario para acceder a la base de datos.
        - tabla (str): El nombre de la tabla de la cual se extraerán los datos.
        - col_id (str): El nombre de la columna que contiene los IDs.
        - col_valor (str): El nombre de la columna que contiene los valores que serán las claves del diccionario.

    Returns:
        dict: Un diccionario donde las claves son los valores de la columna `col_valor` y los valores son los IDs de la columna `col_id`.
    """
    # creamos la conexión con la base de datos con la que queremos trabajar
    conn = establecer_conn(nombre_bbdd, contraseña, usuario) 

    # Creamos un cursor con la conexión que acabamos de crear
    cur = conn.cursor()

    # creamos la query para extraer las primary keys y sus respectivos valores
    query = f"select {col_valor}, {col_id} from {tabla} t"
    cur.execute(query)
    diccionario_tipos = dict(cur.fetchall())
    return diccionario_tipos


def crear_combinaciones_unicas(dataframe, columnas):
    """
    Crea una lista de combinaciones únicas de valores en las columnas especificadas de un DataFrame.

    Params:
        - dataframe (pandas.DataFrame): El DataFrame que contiene los datos.
        - columnas (list): Una lista de nombres de columnas para considerar en la creación de combinaciones únicas.

    Returns:
        list: Una lista de tuplas, donde cada tupla representa una combinación única de valores en las columnas especificadas.
    """
    try:
        combinaciones_unicas = {
            tuple(None if np.isnan(row[col]) else row[col] for col in columnas) # generamos una tupla para cada fila con los valores de las columnas especificadas.
            for _, row in dataframe.iterrows() # vamos a reemplazar los valores NaN con None para manejar los valores faltantes en SQL
        }

        # convertimos el set en lista
        return list(combinaciones_unicas)
    
    # en caso de que nos de error el código anterior, no gestiones los nulos y solo creamos una tupla para cada fila del DataFrame
    except:
        combinaciones_unicas = {
            tuple(row[col] for col in columnas) for _, row in dataframe.iterrows()
        }
        return list(combinaciones_unicas)


def insertar_datos(nombre_bbdd, contraseña, usuario, query_insercion, datos_insertar):
    """
    Inserta múltiples registros en una base de datos utilizando una consulta SQL proporcionada.

    Params:
        - nombre_bbdd (str): El nombre de la base de datos a la que se desea conectar.
        - contraseña (str): La contraseña del usuario de la base de datos.
        - usuario (str): El nombre de usuario de la base de datos.
        - query_insercion (str): La consulta SQL de inserción que se va a ejecutar. Debe contener placeholders para los valores a insertar.
        - datos_insertar (list of tuple): Una lista de tuplas, donde cada tupla contiene los valores que se deben insertar en la base de datos.

    Returns:
        No devuelve nada
    """
    # creamos la conexión con la base de datos con la que queremos trabajar
    conn = establecer_conn(nombre_bbdd, contraseña, usuario) 
    
    # Creamos un cursor con la conexion que acabamos de crear
    cur = conn.cursor()

    # utilizamos el método 'executemany' para insertar todos los datos de una vez
    cur.executemany(query_insercion, datos_insertar)

    print(f"Se han insertado {cur.rowcount} registros con éxito")

    # aplicamos los cambios en la base de datos
    conn.commit()

