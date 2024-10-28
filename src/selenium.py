from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
# Selenium para establecer la configuración del driver
# -----------------------------------------------------------------------
from selenium import webdriver

# Para generar una barra de proceso en los bucles for
# -----------------------------------------------------------------------
from tqdm import tqdm

# Para trabajar con ficheros
# -----------------------------------------------------------------------
import os

import re

import zipfile
import shutil



def acceder_datos_multiple(url):
    chrome_options = webdriver.ChromeOptions()
    

    prefs = {
        "download.default_directory": "C:\\Users\\HP\\Boot\\Proyecto extraccion-carpeta-des\\datos",
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    chrome_options.add_experimental_option("prefs", prefs)


    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    sleep(5)
    
 
    driver.find_element('css selector', '#aceptarCookie').click()
    driver.implicitly_wait(10)


    for i in range(2, 5):
  
        boton_elijo = driver.find_element("css selector", f'#periodo > option:nth-child({i})').click()
        driver.implicitly_wait(10)

        boton_consulta = driver.find_element("css selector", '#botonConsulSele').click()
        driver.implicitly_wait(10)

        # Acceder a los datos
        acceder_datos1 = driver.find_element('xpath', '/html/body/div[1]/main/ul/li/div/div/form[2]/button').click()
        driver.implicitly_wait(20)
        sleep(5)

        extraemos  = driver.find_element('xpath', '//*[@id="export"]/ul/li[4]/label').click()
        return None