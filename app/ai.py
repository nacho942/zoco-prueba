# app/ai.py
from typing import List, Optional
from .models import Place

def clasificar_lugar_por_nombre(nombre: str) -> str:
    """
    Clasificación muy simple según el texto del nombre.
    No es perfecto, pero sirve para categorizar automáticamente.
    """
    n = nombre.lower()
    if "bar" in n or "beer" in n or "pub" in n:
        return "bar"
    if "cafe" in n or "café" in n:
        return "café"
    if "boliche" in n or "club" in n:
        return "boliche"
    if "recital" in n or "show" in n:
        return "recital"
    return "otro"


def _normalizar_nombre(nombre: str) -> str:
    """
    Normaliza el nombre para comparar similitud:
    - pasa a minúsculas
    - saca palabras genéricas
    - deja solo letras y números
    """
    n = nombre.lower()
    for palabra in ["bar", "cafe", "café", "cafeteria", "cerveceria", "cervecería", "pub"]:
        n = n.replace(palabra, "")
    return "".join(c for c in n if c.isalnum())


def detectar_posible_duplicado(
    nombre_candidato: str,
    lugares_existentes: List[Place],
    umbral_similitud: int = 5,
) -> dict:
    """
    Heurística muy básica para detectar duplicados:
    busca el lugar más parecido por nombre dentro de la misma ubicación.
    """
    cand_norm = _normalizar_nombre(nombre_candidato)

    mejor_match: Optional[Place] = None
    mejor_puntaje = 0

    for lugar in lugares_existentes:
        nombre_norm = _normalizar_nombre(lugar.name)
        # cantidad de caracteres en común entre ambos nombres normalizados
        comunes = len(set(cand_norm) & set(nombre_norm))
        if comunes > mejor_puntaje:
            mejor_puntaje = comunes
            mejor_match = lugar

    if mejor_match and mejor_puntaje >= umbral_similitud:
        return {
            "es_duplicado": True,
            "id_duplicado": mejor_match.id,
            "puntaje": mejor_puntaje,
        }

    return {
        "es_duplicado": False,
        "id_duplicado": None,
        "puntaje": mejor_puntaje,
    }
