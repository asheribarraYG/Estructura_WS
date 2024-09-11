import codecs
import glob
import json
import os
import shutil
import time
import datetime
from getpass import getuser
from shutil import move
from time import sleep
from datetime import datetime as dt
from typing import Any, TextIO
from pyshadow import main
from pyshadow.main import Shadow
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common import exceptions as ec
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager


class DatosJson:
    def __init__(self, archivo: str) -> None:
        """
            Inicializa la clase DatosJson.

            :param archivo: Ruta del archivo JSON que se va a leer.
        """
        self.archivo = codecs.open(archivo, "r", "utf-8")
        self.nombre_archivo = archivo
        self.tipo_archivo = "json"

    def obtener_datos(self) -> dict[str, Any]:
        """
        Obtiene los datos del archivo JSON.

        :return: Diccionario con los datos extraídos del archivo JSON.
        """
        datos = json.load(self.archivo)
        return datos


class WindowsFiles:
    def __init__(self, ruta: str) -> None:
        """
        Inicializa la clase WindowsFiles.

        :param ruta: Ruta del directorio donde se gestionarán los archivos.
        """
        self.ruta = ruta

    def descarga(self, ext: str) -> tuple[bool, str]:
        """
        Monitorea la descarga de un archivo con una extensión específica.

        :param ext: Extensión del archivo a descargar.
        :return: Una tuple que indica si se descargó el archivo y el nombre del archivo descargado.
        """
        filelist: list = []
        b = None
        print("Descargando Archivo", end=" ")

        initial: int = len(glob.glob(self.ruta + "\\" + "*." + ext))
        final: int = len(glob.glob(self.ruta + "\\" + "*." + ext))
        print("Initial:", initial, "Final:", final)

        down: bool = False
        cont: int = 0
        nombre1: str = ""

        while initial == final:

            sleep(1)
            cont += 1
            final = len(glob.glob(self.ruta + "\\" + "*." + ext))
            filelist = glob.glob(self.ruta + "\\" + "*." + ext)
            print("Filelist:", filelist)
            print(".", end=" ")

            down: bool = (initial != final)
            print("Down:", down)

            if cont == 90:
                break

        if down:
            print("\nSe descargo el archivo")

            if final > 1:
                c: list = []
                for i in filelist:
                    print('i', i)
                    fecha: time.struct_time = time.localtime(os.stat(i).st_mtime)
                    print('fecha:', fecha)
                    fecha1: datetime = datetime.datetime(fecha[0], fecha[1], fecha[2], fecha[3], fecha[4], fecha[5])
                    print('fecha_1', fecha1)
                    c.append(datetime.datetime.strftime(fecha1, "%d/%m/%Y"))
                    print(fecha1)

                    if b != 0:
                        if fecha[b - 1] < fecha[b]:
                            nombre: str = filelist[b]
                            nombre1: str = nombre.split(str("\\"))[-1]
                            print("Ultimo archivo: " + str(c[b]) + " " + filelist[b])
                        else:
                            print("Ultimo archivo: " + str(c[b - 1]) + " " + filelist[b - 1])
                    b = + 1
            else:
                nombre: str = filelist[0]
                nombre1: str = nombre.split(str("\\"))[-1]
        else:
            print("\nNo se pudo descargar archivo ...")

        return down, nombre1

    def mover_archivo(self, file_name: str, output_path: str) -> None:
        """
        Mueve un archivo a una ubicación de destino.

        :param file_name: Nombre del archivo a mover.
        :param output_path: Ruta de destino donde se moverá el archivo.
        """
        source: str = self.ruta + "\\" + file_name
        dest: str = output_path + "\\" + file_name
        repet: bool = os.path.isfile(dest)
        try:
            move(source, dest)
            if repet:
                texto: str = f"Se reemplazo el archivo: {file_name} existente en la ubicacion"
                Browser.log_file(texto)
                print(texto)
            else:
                texto: str = f"Se agrego el archivo: {file_name} en la ubicacion"
                Browser.log_file(texto)
                print(texto)
        except Exception as e:
            print(repr(e))
            pass

    def copiar_archivo(self, file_name: str, ext: str, output_path: str) -> None:
        """
        Copia un archivo a una ubicación de destino.

        :param file_name: Nombre del archivo a copiar.
        :param ext: Extensión del archivo a copiar.
        :param output_path: Ruta de destino donde se copiará el archivo.
        """
        source: str = self.ruta + file_name + "." + ext
        dest: str = output_path + file_name + "." + ext
        try:
            shutil.copy(source, dest)
        except FileNotFoundError:
            pass


class Browser:
    nav: WebDriver
    elmnt: WebElement
    elmnts: list

    def __init__(self, datos: dict[str, Any]) -> None:
        """
        Inicializa la clase Browser.

        :param datos: Diccionario con los datos de configuración para el navegador.
        """
        self.datos: dict[str, Any] = datos
        self.user: str = getuser()
        self.ruta_base: str = os.getcwd()
        self.ruta_driver: str = self.ruta_base + "\\chromedriver.exe"
        self.ruta_descarga: str = datos["Ruta_Descarga"]
        self.page: str = datos["Portal"]
        self.cookies: str = datos["Ruta_Banco"]
        self.current_url: str = datos["URL"]

    def open_chrome(self, url: str) -> None:
        try:
            chrome_options: Options = webdriver.ChromeOptions()
            prefs: dict[str, bool | str] = {"download.default_directory": self.ruta_descarga,
                                            "download.prompt_for_download": False,
                                            "download.directory_upgrade": False,
                                            "safebrowsing.enabled": True}
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument('user-data-dir=' + self.cookies)
            chrome_options.add_argument('--profile-directory=%s' % self.page)
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("excludeSwitches",
                                                   ["enable-automation", "enable-logging"])
            chrome_options.add_argument('--log-level=3')
            try:
                service: Service = Service(executable_path=self.ruta_driver, service_args=["--disable-build-check"])
                nav = webdriver.Chrome(service=service, options=chrome_options)
            except (ec.WebDriverException, ec.TimeoutException, ec.NoSuchDriverException):
                nav = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            nav.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            nav.maximize_window()
            nav.get(url)
            self.nav = nav
            # Depuración
            print("Navegador abierto exitosamente:", type(self.nav))
        except (ec.WebDriverException, ec.TimeoutException, ec.NoSuchDriverException):
            print("Error al abrir el navegador.")
            self.crear_log_chrome()

    @staticmethod
    def crear_log_chrome() -> None:
        """
        Crea un registro en caso de error al abrir Chrome.
        """
        log: TextIO = open("event_log.txt", "a")
        log.write("Error al abrir navegador, revisar conexión a internet o versión de Chromedriver | " +
                  str(dt.today()) + "\n")

    def crear_log_page(self, texto: str) -> None:
        """
        Crea un registro de eventos específicos de la página.

        :param texto: Texto a registrar en el archivo de eventos.
        """
        log: TextIO = open("event_log.txt", "a")
        log.write(texto + " | " + str.lower(self.page) + ": " + str(dt.today()) + "\n")

    def log_process(self, texto: str) -> None:
        """
        Crea un registro de procesos.

        :param texto: Texto a registrar en el archivo de procesos.
        """
        log: TextIO = open("process_log.txt", "a")
        log.write(texto + " | " + str.lower(self.page) + ": " + str(dt.today()) + "\n")

    @staticmethod
    def log_file(texto: str) -> None:
        """
        Crea un registro de eventos relacionados con archivos.

        :param texto: Texto a registrar en el archivo de logs de archivos.
        """
        log: TextIO = open("file_log.txt", "a")
        log.write(texto + ": " + dt.strftime(dt.today(), "%d/%m/%Y %H:%M") + "\n")

    def encontrar_elemento(self, option: By, elmnt_path: str) -> WebElement:
        """
        Encuentra un elemento en la página actual del navegador.

        :param option: Parámetro By del localizador de Selenium.
        :param elmnt_path: Ruta del elemento en la página web.
        :return: Elemento encontrado.
        """
        cont: int = 0
        while True:
            sleep(0.5)
            cont += 1
            try:
                self.elmnt = self.nav.find_element(option, elmnt_path)
                return self.elmnt
            except (ec.NoSuchElementException, ec.ElementNotInteractableException, ec.ElementNotVisibleException):
                if cont == 50:
                    break

    def encontrar_elementos(self, option: By, elmnt_path: str) -> list:
        """
        Encuentra múltiples elementos en la página actual del navegador.

        :param option: Parámetro By del localizador de Selenium.
        :param elmnt_path: Ruta de los elementos en la página web.
        :return: Lista de elementos encontrados.
        """
        cont: int = 0
        while True:
            sleep(0.5)
            cont += 1
            try:
                self.elmnts = self.nav.find_elements(option, elmnt_path)
                return self.elmnts
            except (ec.NoSuchElementException, ec.ElementNotInteractableException, ec.ElementNotVisibleException):
                if cont == 50:
                    break

    def ventana_verificacion(self, option: By, elmnt_path: str) -> None:
        """
        Encuentra una ventana de verificación y le da clik al botón deseado.

        :param option: Parámetro By del localizador de Selenium.
        :param elmnt_path: Ruta de los elementos en la página web.
        """
        cont: int = 0
        while True:
            sleep(0.5)
            cont += 1
            try:
                self.elmnt = self.nav.find_element(option, elmnt_path)
                click = False
                cont = 0
                while not click:
                    sleep(0.5)
                    cont += 1
                    try:
                        self.elmnt.click()
                        click = True
                    except ec.ElementClickInterceptedException:

                        if cont == 50:
                            break
                break
            except (ec.NoSuchElementException, ec.ElementNotInteractableException, ec.ElementNotVisibleException):
                if cont == 10:
                    break

    def seleccionar_elemento_shadow(self, elmnt_css: Any) -> WebElement:  # En revisión
        """
        Encuentra un shadow frame en el html y lo retorna.

        :param elmnt_css: Ruta de los elementos en la página web.
        :return: Elemento encontrado.
        """
        print("elemento shadow")
        nav_shadow: Shadow = main.Shadow(self.nav)
        cont = 0
        while True:
            sleep(0.5)
            cont += 1
            try:
                self.elmnt = nav_shadow.find_element(elmnt_css)
                return self.elmnt
            except (ec.NoSuchElementException, ec.ElementNotInteractableException, ec.ElementNotVisibleException):
                if cont == 50:
                    break

    def seleccionar_elemento_shadow_selector(self, elmnt_css):  # En revisión
        print("elemento shadow selector")
        nav_shadow = main.Shadow(self.nav)
        cont = 0
        while True:
            sleep(0.5)
            cont += 1
            try:
                self.elmnt = nav_shadow.find_element(By.CSS_SELECTOR, elmnt_css)
                return self.elmnt
            except (ec.NoSuchElementException, ec.ElementNotInteractableException, ec.ElementNotVisibleException):
                if cont == 50:
                    break

    def seleccionar_elemento_shadow_link(self, elmnt_css):  # En revisión
        print("elemento shadow link")
        nav_shadow = main.Shadow(self.nav)
        cont = 0
        while True:
            sleep(0.5)
            cont += 1
            try:
                self.elmnt = nav_shadow.find_element(By.LINK_TEXT, elmnt_css)
                return self.elmnt
            except (ec.NoSuchElementException, ec.ElementNotInteractableException, ec.ElementNotVisibleException):
                if cont == 50:
                    break

    def seleccionar_elementos_shadow(self, elmnt_css):  # En revisión
        print("elementos shadow")
        nav_shadow = main.Shadow(self.nav)
        cont = 0
        while True:
            sleep(0.5)
            cont += 1
            try:
                self.elmnt = nav_shadow.find_elements(elmnt_css)
                return self.elmnt
            except (ec.NoSuchElementException, ec.ElementNotInteractableException, ec.ElementNotVisibleException):
                if cont == 50:
                    break

    @staticmethod
    def click_elemento(elmnt: WebElement) -> None:
        """
        Hace clic en un elemento.

        :param elmnt: Elemento en el que se hará clic. Si no se proporciona, se usará el último elemento encontrado.
        """
        click: bool = False
        cont: int = 0
        while not click:
            sleep(0.5)
            cont += 1
            try:
                elmnt.click()
                click = True
            except ec.ElementClickInterceptedException:
                if cont == 50:
                    break
