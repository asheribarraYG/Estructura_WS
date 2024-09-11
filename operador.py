from os import getcwd
from automate_browser_files import *


class Operador:
    dia_actual: str = dt.strftime(dt.today(), "%A")
    ruta: str = getcwd() + "\\Descarga\\"
    dia_semana: str = dt.strftime(dt.today(), "%w")
    nav: WebDriver
    if dia_semana != '1':
        fecha_real: datetime = dt.today() - datetime.timedelta(days=1)
    else:
        fecha_real: datetime = dt.today() - datetime.timedelta(days=3)
    fecha: str = dt.strftime(dt.today(), "%d/%m/%Y")
    dia: str = dt.strftime(dt.today(), "%d")
    mes: str = dt.strftime(dt.today(), "%m")
    anio: str = dt.strftime(dt.today(), "%Y")
    mes_name: str = dt.strftime(dt.today(), "%b").split(".")[0]

    mes_anio_ant: str = dt.strftime(fecha_real, "%b_%Y")
    dia_ant: str = dt.strftime(fecha_real, "%d")

    mes_anio_an: str = mes_anio_ant.split("_")
    mes_anio_ant: str = mes_anio_an[0] + mes_anio_an[1]
    mes_num: str = dt.strftime(fecha_real, "%m")

    today_: datetime = dt.today()
    yesterday_: datetime = today_ - datetime.timedelta(days=1)
    last_yesterday_: datetime = today_ - datetime.timedelta(days=2)
    last_yesterday_2_: datetime = today_ - datetime.timedelta(days=3)
    today: str = today_.strftime("%d/%m/%y")
    yesterday: str = yesterday_.strftime("%d/%m/%Y")
    yesterday_2: str = yesterday_.strftime("%d-%m-%y")
    last_yesterday: str = last_yesterday_.strftime("%d/%m/%y")
    last_yesterday_2: str = last_yesterday_2_.strftime("%d/%m/%y")

    def __init__(self, datos: dict[str, Any]) -> None:
        """
            Inicializa la clase Operator.

            :param datos: Diccionario con los datos extraídos del archivo JSON.
        """
        self.datos = datos
        self.brwr: Browser = Browser(datos)
        self.name: str = datos["Portal"]
        self.url: str = datos["URL"]
        self.xpaths: Any = json.load(codecs.open(datos["Xpaths"], "r", "utf-8"))

    def get_operador(self) -> dict[str, Any]:
        """
            Crea una instancia de las clases de los procesos que se usen en el programa.
        """
        portales: dict[str, Any] = {
            """
            Estructura:
            "Página1": Página1,
            ...
            "PáginaN": PáginaN
            """
            "Pago24": Pago24  # Ejemplo
        }
        try:
            return portales[self.name]
        except (KeyError, TypeError, AttributeError):
            print("Sin operador")

    def start_web_scraping(self) -> None:
        """
        Inicializa con los procesos de scrapping.
        """
        try:
            opdr = self.get_operador()
            if opdr:
                if opdr == Pago24:
                    self.brwr.open_chrome(self.url)
                    self.nav = self.brwr.nav
                    """ 
                    Insertar la lógica del proceso
                    """
                    self.nav.quit()
                else:
                    self.brwr.open_chrome(self.url)
                    self.nav = self.brwr.nav
                    """ 
                    Insertar la lógica de los siguientes procesos
                    """
                    self.nav.quit()
            self.brwr.log_process(f"Descarga con exito")
        except ValueError as e:
            self.brwr.crear_log_page(f"No se pudo descargar la información del Banco, motivo: {e}:")
            self.brwr.log_process(f"Descarga sin exito")
            self.nav.quit()


class Pago24(Operador):
    def __init__(self, datos):
        super().__init__(datos)
