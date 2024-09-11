import threading
from os import listdir, remove
from tkinter import messagebox
import schedule as horario
from operador import *


dia_actual: str = dt.strftime(dt.today(), "%A")
ruta: str = getcwd() + "\\Descarga\\"  # Apunta a la carpeta de descargas ubicada en el directorio origen
fecha: str = dt.strftime(dt.today(), "%d/%m/%Y")
dia: str = dt.strftime(dt.today(), "%d")
mes: str = dt.strftime(dt.today(), "%m")
anio: str = dt.strftime(dt.today(), "%Y")
mes_name: str = dt.strftime(dt.today(), "%b")
dia_semana: str = dt.strftime(dt.today(), "%w")


def main() -> None:
    """
    Obtiene las páginas de interés del JSON y verifica si la clase operador las contiene, de ser así creará un hilo por
    cada página para proceder a ejecutar sus procesos
    """
    threads: list = []
    ajustes: dict[str, Any] = DatosJson("ajustes.json").obtener_datos()

    for indicador_banco in ajustes:
        pagina: Any = get_operador(indicador_banco)
        if pagina:
            try:
                oprdr: Operador = Operador(ajustes[indicador_banco])
                try:
                    archivos: list = listdir(ajustes[indicador_banco]["Ruta_Descarga"])
                    for archivo in archivos:
                        remove(ajustes[indicador_banco]["Ruta_Descarga"] + "\\" + archivo)
                except [FileNotFoundError, PermissionError, OSError, TypeError, ValueError]:
                    pass
                t: threading.Thread = threading.Thread(name=ajustes[indicador_banco]["Portal"],
                                                       target=oprdr.start_web_scraping)
                threads.append(t)
            except KeyError:
                pass
    for func in threads:
        func.start()
        sleep(10)
    for func in threads:
        func.join()


def get_operador(pagina: str) -> dict[str, Any]:
    """
        Crea una instancia de las clases de los procesos que se usen en el programa.
    """
    portales: dict[str, Any] = {
            """
            Estructura:
            "Pagina1": Pagina1,
            ...
            "PaginaN": PaginaN
            """
            "Pago24": Pago24  # Ejemplo
    }
    try:
        return portales[pagina]
    except (KeyError, TypeError, AttributeError):
        print("No encontro ningún operador")


def crear_horarios(ajustes: Any) -> tuple[list[str], bool]:
    """
    A partir de los ajustes de horario del JSON crea los horarios en los qe se ejecutará el programa.

    :param ajustes:
    :return: Tuple que contiene una lista de horarios y un bool que indica si los horarios son válidos o no
    """
    horarios: list = []
    horario_correcto: bool = True
    try:
        hora_base: datetime = dt.strptime(ajustes["Hora_Inicio"], "%H:%M")
        intervalo: float = ajustes["Frecuencia_Dias"]
        hora_final: datetime = hora_base + datetime.timedelta(days=intervalo)
        horarios.append(dt.strftime(hora_final, "%H:%M"))

        while hora_final.time() > hora_base.time():
            hora_final += datetime.timedelta(days=intervalo)
            horarios.append(dt.strftime(hora_final, "%H:%M"))
        horarios.pop()
    except [ValueError, TypeError, AttributeError, NameError]:
        horario_correcto: bool = False
        texto: str = "Validar que las configuraciones de horario sean correctas en el archivo Ajustes.json: \n\n"
        texto += "Ejemplo:\n\n"
        texto += '"Hora_Inicio": "00:00"\n'
        texto += '"Frecuencia_Minutos": 5\n'

        messagebox.showerror(message=texto, title="Ajustes de horario invalidos")

    return horarios, horario_correcto


f: TextIO = open("ajustes.json", "r", encoding="utf-8")
ajustes_: Any = json.load(f)

if ajustes_["Parametros"]["Hora_Inicio"] != "":
    horarios_: list = (crear_horarios(ajustes_))[0]
    horario_correcto_: bool = (crear_horarios(ajustes_))[1]

    if horario_correcto_:
        horario.every().day.at(ajustes_["Parametros"]["Hora_Inicio"]).do(main)
        for hora in horarios_:
            horario.every().day.at(hora).do(main)
        while True:
            horario.run_pending()
            sleep(1)
else:
    main()
