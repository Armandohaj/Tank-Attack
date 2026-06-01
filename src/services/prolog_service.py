# prolog_service.py
# Conexión Python <-> SWI-Prolog usando PySwip

from pyswip import Prolog
from pyswip.prolog import PrologError


class PrologService:
    """
    Maneja toda la comunicación con el motor lógico en Prolog.
    """

    def __init__(self, ruta_logic_pl: str = "logic.pl"):
        self.prolog = Prolog()
        self.prolog.consult(ruta_logic_pl)

    def convertir_tipo_tanque(self, tipo_python):
        """
        Convierte los tipos de tanque usados en Python
        a los tipos que entiende Prolog.
        """

        conversion = {
            "light": "ligero",
            "heavy": "pesado",
            "sniper": "francotirador",
            "ligero": "ligero",
            "pesado": "pesado",
            "francotirador": "francotirador"
        }

        return conversion.get(tipo_python, "ligero")

    def cargar_nivel(
        self,
        ancho: int,
        alto: int,
        muros: list,
        objetivos: list,
        tanques: list,
        jugador: tuple
    ):
        """
        Limpia el nivel anterior y carga todos los hechos del nuevo nivel.

        muros: [(x, y), ...]
        objetivos: [(id, x, y, tipo), ...]
        tanques: [(id, x, y, tipo, vida), ...]
        jugador: (x, y)
        """

        list(self.prolog.query("limpiar_nivel"))
        list(self.prolog.query(f"cargar_tablero({ancho}, {alto})"))

        for x, y in muros:
            list(self.prolog.query(f"agregar_muro({x}, {y})"))

        for oid, x, y, tipo in objetivos:
            list(self.prolog.query(
                f"agregar_objetivo({oid}, {x}, {y}, {tipo})"
            ))

        for tanque in tanques:
            if len(tanque) == 5:
                tid, x, y, tipo, vida = tanque
            else:
                tid, x, y, tipo = tanque
                vida = 100

            tipo_prolog = self.convertir_tipo_tanque(tipo)

            list(self.prolog.query(
                f"agregar_tanque_enemigo({tid}, {x}, {y}, {tipo_prolog}, {int(vida)})"
            ))

        jx, jy = jugador
        list(self.prolog.query(f"actualizar_jugador({jx}, {jy})"))

    def actualizar_jugador(self, x: int, y: int):
        """
        Actualiza la posición del jugador en Prolog.
        """

        list(self.prolog.query(f"actualizar_jugador({x}, {y})"))

    def actualizar_tanque(self, tank_id, nx: int, ny: int, vida: int):
        """
        Actualiza la posición y la vida de un tanque enemigo en Prolog.
        """

        list(self.prolog.query(
            f"actualizar_tanque({tank_id}, {nx}, {ny}, {int(vida)})"
        ))

    def obtener_accion_y_ruta(self, tank_id) -> dict:
        """
        Pregunta a Prolog qué acción debe tomar el tanque y cuál es su ruta.
        Usa límite de tiempo para evitar congelamientos.
        """

        query = f"call_with_time_limit(0.05, accion_y_ruta({tank_id}, Accion, Ruta))"

        try:
            resultados = list(self.prolog.query(query, maxresult=1))

        except PrologError:
            return {
                "accion": "acercarse",
                "ruta": []
            }

        except Exception:
            return {
                "accion": "acercarse",
                "ruta": []
            }

        if not resultados:
            return {
                "accion": "acercarse",
                "ruta": []
            }

        res = resultados[0]

        accion = str(res["Accion"])
        ruta_raw = res["Ruta"]
        ruta = self._parsear_ruta(ruta_raw)

        return {
            "accion": accion,
            "ruta": ruta
        }

    @staticmethod
    def _parsear_ruta(ruta_prolog) -> list:
        """
        Convierte la lista Prolog [pos(X,Y), ...]
        en lista Python [(x, y), ...].
        """

        pasos = []

        for termino in ruta_prolog:
            try:
                s = str(termino)
                s = s.replace("pos(", "").replace(")", "")

                x, y = s.split(",")

                pasos.append(
                    (
                        int(x.strip()),
                        int(y.strip())
                    )
                )

            except Exception:
                pass

        return pasos


if __name__ == "__main__":
    svc = PrologService("logic.pl")

    svc.cargar_nivel(
        ancho=25,
        alto=19,
        muros=[(2, 2), (2, 3), (2, 4), (5, 1), (5, 2)],
        objetivos=[
            (1, 8, 8, "radar"),
            (2, 1, 7, "bunker")
        ],
        tanques=[
            (1, 7, 7, "light", 100),
            (2, 1, 6, "heavy", 100),
            (3, 9, 1, "sniper", 35)
        ],
        jugador=(0, 0)
    )

    for tid in [1, 2, 3]:
        resultado = svc.obtener_accion_y_ruta(tid)
        print(
            f"Tanque {tid}: "
            f"accion={resultado['accion']}, "
            f"ruta={resultado['ruta']}"
        )