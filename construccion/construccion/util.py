import numpy as np


def dict_si_uno(dic):
    """Esta funcion a partir de un diccionario de 0 y 1 clasifica si existe
    algun valor 1

    Args:
        dic: Un diccionario con un valor 0 y 1 para cada etiqueta

    Returns:
        Un valor que indica

        * 0: si no existe ningun valor igual a 1
        * 1: si existe algun valor igual a 1
        * -1: si se produce algun problema en la funcion.

    """
    salida = None

    val = (np.any(dic.values()) == 1)
    if val:
        salida = True
    else:
        salida = False

    return salida


def dict_si_true(dic):
    """Esta funcion a partir de un diccionario de booleanos clasifica si existe
    algun valor true

    Args:
        dic: Un diccionario con un booleano para cada etiqueta

    Returns:
        Un valor que indica

        * True: Si existe algún valor true
        * False: si no existe ningún true

    """

    val = dic.values()
    if True in val:
        salida = True
    else:
        salida = False

    return salida
    

