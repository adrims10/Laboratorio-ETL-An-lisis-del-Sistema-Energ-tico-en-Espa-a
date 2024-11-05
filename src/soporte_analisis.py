# Para trabajar con postgresql
# -----------------------------------------------------------------------
import psycopg2

# Para trabajar con DataFrames
# -----------------------------------------------------------------------
import pandas as pd

def realizar_query(database_name, postgres_pass, usuario, query, host="localhost"):
    """
    Ejecuta una consulta en una base de datos PostgreSQL y devuelve los resultados en un DataFrame de pandas.

    Params:
        - database_name (str): El nombre de la base de datos a la cual se va a conectar.
        - postgres_pass (str): La contraseña del usuario de la base de datos PostgreSQL.
        - usuario (str): El nombre de usuario para la conexión a la base de datos.
        - query (str): La consulta SQL a ejecutar en la base de datos.
        - host (str, optional): El host donde se encuentra la base de datos. Por defecto es "localhost".

    Returns:
        pandas.DataFrame: Un DataFrame que contiene los resultados de la consulta SQL. 
                          Las columnas del DataFrame corresponden a las columnas devueltas por la consulta.
    """
    # crear la conexión a la base de datos PostgreSQL
    conn = psycopg2.connect(
        host=host,
        user=usuario,
        password=postgres_pass,
        database=database_name
    )

    # establecer la conexión en modo autocommit
    conn.autocommit = True 
    
    cursor = conn.cursor()

    # ejecutar la consulta
    cursor.execute(query)
    datos = cursor.fetchall()

    # obtener los nombres de las columnas
    cols = list(map(lambda x: x[0], cursor.description))

    # crear un DataFrame de pandas con los datos
    df = pd.DataFrame(datos, columns=cols)

    # devolvemos el DataFrame de la query
    return df
