# SPara trabajar con selenium
# -----------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Para controlar el tiempo en las acciones de selenium
# -----------------------------------------------------------------------
import time


# Para gestionar con regex
# -----------------------------------------------------------------------
import re


# Para gestionar las carpetas y la descompresión de archivos zip
# -----------------------------------------------------------------------
import os
import zipfile
import shutil


def sacar_anios(opciones_chrome, url):
    """
    Extrae la cantidad de años disponibles en un desplegable específico de una página web.

    Params:
        - opciones_chrome (webdriver.ChromeOptions): Las opciones y preferencias de configuración para el navegador Chrome.
        - url (str): La URL de la página web que se va a abrir con el navegador.

    Returns:
        int: La cantidad de años disponibles en el desplegable de la página web.
    """
    
    # iniciamos el driver con las preferencias deseadas
    driver = webdriver.Chrome(options=opciones_chrome)

    # abrimos el driver con la url especificada en el parámetro
    driver.get(url)

    # seleccionamos la opción 'Estadística de Centros Sanitarios de Atención Especializada' del desplegable de tipo de dato
    # este código va a esperar hasta 10 segundos hasta que el elemento sea clicable
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#tipoMicrodatos > option:nth-child(7)"))
    ).click()

    # buscamos todos los elementos de la opción años para sacar su longitud y saber el número de años que tenemos (calculando su longitud)
    cantidad_años = len(driver.find_elements(By.CSS_SELECTOR, "#anioMicrodatos > option"))
  
    # cerramos el driver
    #driver.quit()

    # devolvemos la cantidad de años
    return cantidad_años

def descargar_datos_anio(indice_año, opciones_chrome, url, download_wait_time=60):
    """
    Descarga datos para un año específico desde una página web utilizando Selenium con Chrome.

    Esta función navega a una página web, selecciona opciones específicas para descargar
    datos de centros sanitarios, y espera a que la descarga se complete dentro de un tiempo 
    máximo de espera.

    Params:
        - indice_año (int): El índice del año en el desplegable de la página web. La cuenta empieza en 0.
        - opciones_chrome (webdriver.ChromeOptions): Opciones de configuración para el navegador Chrome.
        - url (str): La URL de la página web desde la cual se descargan los datos.
        - download_wait_time (int, optional): El tiempo máximo de espera en segundos para completar la descarga. 
                                              Por defecto es 60 segundos.

    Raises:
        - Exception: Si hay algún problema durante la descarga de los datos, se imprime el error.

    Returns: 
        No devuelve nada
    """
    try:
        # Iniciar el driver con las preferencias deseadas
        driver = webdriver.Chrome(options=opciones_chrome)

        # Abrir la URL especificada
        driver.get(url)

        # Seleccionar la opción específica del desplegable
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#tipoMicrodatos > option:nth-child(7)"))
        ).click()

        # Seleccionar el año especificado por el índice
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"#anioMicrodatos > option:nth-child({indice_año + 2})"))
        ).click()

        # Hacer clic en el botón de consultar
        driver.find_element(By.CSS_SELECTOR, "#fl1 > div.text-center > input").click()
        time.sleep(3)

        # Esperar hasta que el elemento "Descarga Completa" esté presente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[text()='Descarga Completa']"))
        )

        # Hacer clic en el enlace de descarga
        driver.find_element(By.XPATH, "//h4[text()='Descarga Completa']/following-sibling::ul/li/a").click()

        # Controlar el tiempo de descarga del archivo
        descarga_completa = False
        start_time = time.time()
        
        # Esperar hasta que la descarga esté completa o el tiempo de espera se exceda
        while not descarga_completa and (time.time() - start_time) < download_wait_time:
            time.sleep(1)
            for file_name in os.listdir("/Users/ana.garcia/Documents/Contenido/DataScience/ETL/DatosDescargados"):
                if file_name.endswith(".crdownload"):
                    descarga_completa = False
                    break
                descarga_completa = True

    # en caso de que no puedas descargar los datos, lanza un error e indica que año es el que está dando error
    except Exception as e:
        print(f"Error procesando el año con índice {indice_año}: {e}")

    # pase lo que pase cierra el driver
    finally:
        driver.quit()


def cambiar_nombre_archivos(ruta):
    """
    Cambia el nombre de los archivos ZIP en una carpeta específica, usando el año presente en sus nombres.

    Params:
        ruta (str): La ruta de la carpeta que contiene los archivos ZIP.

    Raises:
        FileNotFoundError: Si no se encuentra el archivo especificado.
        AttributeError: Si no se encuentra un año en el nombre del archivo.

    Example:
        cambiar_nombre_archivos("/ruta/a/tu/carpeta")
    """
    
    # Listamos los archivos que tenemos en la ruta, los archivos descargados
    archivos = os.listdir(ruta)

    # Iteramos por la lista de archivos en la carpeta de archivos descargados
    for archivo in archivos:

        # Definimos el patrón para sacar los años de los nombres de los archivos ZIP
        patron = r"\d+"

        # Sacamos el año
        anio = re.search(patron, archivo)
        
        if anio:
            anio = anio.group()
            # Cambiamos el nombre del archivo
            os.rename(f"{ruta}/{archivo}", f"{ruta}/{anio}.zip")
        else:
            raise AttributeError(f"No se encontró un año en el nombre del archivo: {archivo}")



def descomprimir_zip(zip_folder, extract_folder):
    """
    Descomprime todos los archivos ZIP en una carpeta especificada y extrae su contenido 
    en carpetas correspondientes dentro de un directorio de destino.

    Params:
        zip_folder (str): La ruta de la carpeta que contiene los archivos ZIP.
        extract_folder (str): La ruta de la carpeta de destino donde se extraerán los archivos.

    Raises:
        OSError: Si hay un error al crear directorios de destino o al manipular archivos.

    Returns:
        No devuelve nada
    """

    # comprobamos si existe la carpeta de destino de los archivos descomprimidos
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    # recorremos todos los archivos en la carpeta zip_folder
    for item in os.listdir(zip_folder):

        # si el archivo termina en 'zip'
        if item.endswith('.zip'):

            # definimos la ruta completa del archivo zip
            zip_path = os.path.join(zip_folder, item)

            # Nombre del directorio de extracción (sin extensión .zip)
            extract_dir = os.path.join(extract_folder, os.path.splitext(item)[0])

            # nos aseguramos de que la carpeta de extracción específica exista
            if not os.path.exists(extract_dir):
                os.makedirs(extract_dir)

            # extraemos el contenido del archivo zip en la carpeta correspondiente
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f'Archivo {item} extraído en {extract_dir}')



def buscar_archivos_y_carpetas(ruta):
    """
    Busca si dentro de una carpeta hay otras carpetas o archivos de tipo .txt o .mdb.

    Params:
        ruta (str): La ruta de la carpeta a inspeccionar.

    Returns:
        str: 'carpetas' si se encuentran carpetas, 'archivos' si se encuentran archivos .txt o .mdb.
              Si no se encuentra nada, no devuelve nada.
    """

    # recorremos todos los elementos en la carpeta especificada
    for item in os.listdir(ruta):

        # creamos la ruta completa del elemento
        ruta_item = os.path.join(ruta, item)

        # si el elemento es una carpeta
        if os.path.isdir(ruta_item):
            return "carpetas"
        
        # si el elemento es un archivo
        elif os.path.isfile(ruta_item):

            # que sea de tipo '.txt' o '.mdb'
            if item.endswith('.txt') or item.endswith('.mdb'):
                return "archivos"



def mover_archivos_a_principal(ruta_principal):
    """
    Mueve todos los archivos de las subcarpetas a la carpeta principal.

    Params:
        ruta_principal (str): La ruta de la carpeta principal.

    Returns:
        No devuelve nada
    """
    # recorremos todos los elementos en la carpeta principal
    for root, _, ficheros in os.walk(ruta_principal):

        # si no hay subcarpetas, no hacemos nada
        if root == ruta_principal:
            continue
        else:
            # en caso de que sí haya subcarpetas 
            for fichero in ficheros:

                # construimos la ruta completa del archivo
                ruta_fichero = os.path.join(root, fichero)

                # movemos el archivo a la carpeta principal
                shutil.move(ruta_fichero, ruta_principal)
