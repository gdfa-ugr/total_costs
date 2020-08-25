import ast

import numpy as np

from .util import dict_si_uno
from .util import dict_si_true

from . import constantes as c

# Nivel 1


def clasifica_fase_en_funcion_de_proximidad_de_temporal(comprobacion):
    """Funcion clasifica la fase en funcion de la proximidad de temporal a n_horas

    Args:
        comprobacion: Un diccionario que indica para cada agente:

        * ``c.NO_TEMPORAL``: si el temporal no se produce.
        * ``c.TEMPORAL``: si el temporal se produce antes de n_horas o en n_horas.
        * -1: si se produce algun problema en la funcion.

    Returns:
        Un valor que indica:

        * ``c.FASE_SIN_ALERTA``: si la fase se clasifica como sin alerta.
        * ``c.FASE_EN_ALERTA``: si la fase se clasifica como en alerta.
        * -1: si se produce algun problema en la funcion.

    """
    clasificacion = -1

    valor_maximo = max(comprobacion.values())

    # Se clasifica la fase a Nivel 0: En funcion de que haya o no haya temporal en las proximas horas.
    if valor_maximo == c.NO_TEMPORAL:
        clasificacion = c.FASE_SIN_ALERTA
    elif valor_maximo == c.TEMPORAL_N_HORAS:
        clasificacion = c.FASE_EN_ALERTA
    elif valor_maximo == c.TEMPORAL_ANTES_N_HORAS:
        clasificacion = c.FASE_EN_ALERTA

    return clasificacion


#def clasifica_comienzo_de_fase(comprobacion):
#    """Funcion que clasifica la fase en funcion de si ha empezado o no
#
#    Args:
#        comprobacion: Un booleano que indica si la comprobación se cumple o no
#
#    Returns:
#        Un valor que indica
#
#        * ``c.FASE_COMENZADA``: si la fase ya ha empezado.
#        * ``c.FASE_NO_COMENZADA``: si la fase aun no ha empezado.
#        * -1: si se produce algun problema en la funcion.
#
#    """
#
#    if comprobacion:
#        clasificacion = c.FASE_COMENZADA
#    else:
#        clasificacion = c.FASE_NO_COMENZADA
#
#    return clasificacion


def clasifica_si_fase_trabaja(comprobacion):
    """Funcion que clasifica si a la fase le toca trabajar o no

    Args:
        comprobacion: Un booleano que indica si la comprobación se cumple o no

    Returns:
        Un valor que indica

        * ``c.FASE_TRABAJA``: si a la fase le toca trabajar.
        * ``c.FASE_NO_TOCA_TRABAJAR``: si la fase no le toca trabajar.
        * -1: si se produce algun problema en la funcion.

    """

    if comprobacion:
        clasificacion = c.FASE_TRABAJA
    else:
        clasificacion = c.FASE_NO_TOCA_TRABAJAR

    return clasificacion


def clasifica_si_fase_deja_de_proteger(comprobacion):
    """Esta funcion clasifica si la fase sigue en protección o si la fase deja de proteger

    Args:
        comprobacion: Un diccionario que tiene para cada agente un booleano que indica si la comprobación se cumple
            o no.


    Returns:
        Un valor que indica

        * ``c.FASE_PROTEGIDA_POR_ESTRUCTURA``: si se supera el umbral de danos y la fase debe seguir protegida
        * ``c.FASE_SIN_PROTECCION``: si no se supera el umbral de danos y la fase puede dejar de proteger
        * -1: si se produce algun problema en la funcion.

    """

#    if dict_si_uno(comprobacion):
#        clasificacion = c.FASE_PROTEGIDA_POR_ESTRUCTURA
#    else:
#        clasificacion = c.FASE_SIN_PROTECCION

    if comprobacion:
        clasificacion = c.FASE_PROTEGIDA_POR_ESTRUCTURA
    else:
        clasificacion = c.FASE_SIN_PROTECCION

    return clasificacion


def clasifica_si_fase_deja_de_proceso_proteccion(comprobacion):
    """Esta funcion clasifica si la fase sigue en proceso de proteccion o si la fase deja de proteger

    Args:
        comprobacion: Un diccionario que tiene para cada agente un booleano que indica si la comprobación se cumple
            o no.


    Returns:
        Un valor que indica

        * ``c.FASE_EN_PROCESO_PROTECCION``: si se supera el umbral de danos y la fase debe seguir protegida
        * ``c.FASE_SIN_PROTECCION``: si no se supera el umbral de danos y la fase puede dejar de proteger
        * -1: si se produce algun problema en la funcion.

    """

#    if dict_si_uno(comprobacion):
#        clasificacion = c.FASE_EN_PROCESO_PROTECCION
#    else:
#        clasificacion = c.FASE_SIN_PROTECCION

    if comprobacion:
        clasificacion = c.FASE_EN_PROCESO_PROTECCION
    else:
        clasificacion = c.FASE_SIN_PROTECCION

    return clasificacion


def clasifica_fase_en_funcion_valor_anterior(comprobacion):
    """Esta funcion clasifica la fase en función del valor anterior

    Args:
        comprobacion: Un valor que indica el estado de la fase en la hora
        anterior

    Returns:
        Un valor que indica

        * ``c.FASE_NO_COMENZADA``: Si la fase aun no ha comenzado a trabajar
        * ``c.FASE_PROTEGIDA_POR_FASE_SIGUIENTE``: Si la fase esta completamente protegida por la fase siguiente.
        * ``c.FASE_PROTEGIDA_POR_ESTRUCTURA``: si se supera el umbral de daños y a fase debe seguir protegida
        * ``c.FASE_EN_PROCESO_PROTECCION``: Si la fase se encuentra en proceso de proteccion.
        * ``c.FASE_SIN_PROTECCION``: si no se supera el umbral de danos y la fase puede dejar de proteger
        * -1: si se produce algun problema en la funcion.

    """

    clasificacion = -1

    if comprobacion == c.FASE_NO_COMENZADA:
        clasificacion = c.FASE_NO_COMENZADA
    elif comprobacion == c.FASE_PROTEGIDA_POR_ESTRUCTURA:
        clasificacion = c.FASE_PROTEGIDA_POR_ESTRUCTURA
    elif comprobacion == c.FASE_EN_PROCESO_PROTECCION:
        clasificacion = c.FASE_EN_PROCESO_PROTECCION
    elif comprobacion == c.FASE_SIN_PROTECCION:
        clasificacion = c.FASE_SIN_PROTECCION
    elif comprobacion == c.FASE_PARADA_INVERNAL:
        clasificacion = c.FASE_PARADA_INVERNAL

    return clasificacion

# Nivel 2


def clasifica_superacion_umbral_dannos_en_proceso_proteccion(comprobacion):
    """Esta funcion clasifica una fase que se encuentra en proceso de proteccion en función de si se supera el
    umbral de danos o no

    Args:
        comprobacion: Un diccionario que tiene para cada agente un booleano que indica si la comprobación se cumple
            o no.


    Returns:
        Un valor que indica

        * ``c.FASE_EN_PROCESO_PROTECCION``: si no se supera el umbral de danos.
        * ``c.FASE_PERDIDAS``: si se supera el umbral y la fase tiene perdidas.

    """

    val = dict_si_true(comprobacion)
    if val:
        clasificacion = c.FASE_PERDIDAS
    else:
        clasificacion = c.FASE_EN_PROCESO_PROTECCION

    return clasificacion


def clasifica_superacion_umbral_dannos_fase_trabajo(comprobacion):
    """Esta funcion clasifica la fase que se encuentra en proceso de sin proteccion y puede trabajar
    en función de si se supera el umbral de daños o no

    Args:
        comprobacion: Un diccionario que tiene para cada agente
        un booleano que indica si la comprobación se cumple o no.


    Returns:
        Un valor que indica

        * ``c.FASE_TRABAJA``: si no se supera el umbral de danos.
        * ``c.FASE_PERDIDAS``: si se supera el umbral y la fase tiene perdidas.

    """

    val = dict_si_true(comprobacion)
    if val:
        clasificacion = c.FASE_PERDIDAS
    else:
        clasificacion = c.FASE_TRABAJA

    return clasificacion


def clasifica_superacion_umbral_dannos_fase_no_toca_trabajar(comprobacion):
    """Esta funcion clasifica una fase a la que no le toca trabajar en función de si se supera el umbral de danos o no

    Args:
        comprobacion: Un diccionario que tiene para cada agente
        un booleano que indica si la comprobación se cumple o no.


    Returns:
        Un valor que indica

        * ``c.FASE_NO_TOCA_TRABAJAR``: si no se supera el umbral de danos.
        * ``c.FASE_PERDIDAS``: si se supera el umbral y la fase tiene perdidas.

    """

    val = dict_si_true(comprobacion)
    if val:
        clasificacion = c.FASE_PERDIDAS
    else:
        clasificacion = c.FASE_NO_TOCA_TRABAJAR

    return clasificacion


def clasifica_superacion_umbral_dannos(comprobacion, clasificacion_3, longitudes, fase):
    """Esta funcion clasifica una fase en función de si se supera el umbral de daños o no

    Args:
        comprobacion: Un diccionario que tiene para cada agente un booleano que indica si la comprobación se cumple
            o no.
        clasificacion_3: Clasificacion de la fase a nivel III
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        fase: Fase constructiva


    Returns:
        Un valor que indica

        * ``c.FASE_PERDIDAS``: si se supera el umbral y la fase tiene perdidas.
        * ``FASE_NIVEL_III_ENTRADA``: si no se supera el umbral

    """

    # val = dict_si_true(comprobacion)

    # Si se supera el umbral y además la longitud desprotegida es mayor que 0. Si no no hay perdidas
    if ((comprobacion) & (longitudes.loc[longitudes.index[fase], 'l_desprotegida'] > 0)):
        clasificacion = c.FASE_PERDIDAS
    else:
        clasificacion = clasificacion_3

    return clasificacion


def clasifica_superacion_umbral_operativo(comprobacion, clasificacion_3):
    """Esta funcion clasifica la fase en funcion de si se supera el umbral de
        operatividad o no

    Args:
        comprobacion: Un diccionario que tiene para cada agente
        un booleano que indica si la comprobación se cumple o no.


    Returns:
        Un valor que indica

        * ``FASE_NIVEL_III_ENTRADA``: si no se supera el umbral de operatividad y la fase puede trabajar.
        * ``c.FASE_NO_TRABAJA_OPERATIVIDAD``: si se supera el umbral de operatividad y la fase.
        no puede trabajar.


    """

    val = dict_si_true(comprobacion)
    if val:
        clasificacion = c.FASE_NO_TRABAJA_OPERATIVIDAD
    else:
        clasificacion = clasificacion_3

    return clasificacion


def clasifica_si_fase_retrasada(comprobacion):
    """Esta funcion clasifica si la fase va retrasada o no

    Args:
        comprobacion: Un booleano que indica si la comprobación se cumple o no.


    Returns:
        Un valor que indica

        * ``c.FASE_TRABAJA_RETRASADA``: si a la fase le toca trabajar porque va retrasada
        * ``c.FASE_NO_TOCA_TRABAJA``: si a la fase no le toca trabajar
        * -1: si se produce algun problema en la funcion.

    """
    if comprobacion:
        clasificacion = c.FASE_TRABAJA_RETRASADA
    else:
        clasificacion = c.FASE_NO_TOCA_TRABAJAR

    return clasificacion


def clasifica_si_fase_tiene_restriccion_de_avance(de_tramo_0, fase, estado_real, hora, longitudes, restriccion,
                                                  tiene_restriccion):

    clasificacion = {}
    puede_trabajar = []

    if not tiene_restriccion:
        puede_trabajar = True
    else:
        restricciones = ast.literal_eval(restriccion['subfases'])
        fases = restricciones.keys()
        l_avance = list(restricciones.values())

        for pos, fase_restricc in enumerate(fases):

            # La subfase no trabajara si se dan las tres condiciones: (1) que la longitud avanzada por la subfase
            # restrictiva menos la longitud avanzada por la subfase en cuestion sea menor que la longitud de avance
            # definida para la subfase en cuestion. (2) que la subfase restrictiva no este acabada y (3) que la
            # subfase restrictiva no este finalizada
            if (((longitudes.loc[longitudes.index[int(fase_restricc)], 'l_avanzada'] - longitudes.loc[longitudes.index[fase], 'l_avanzada']) < l_avance[
                pos]) & (estado_real.iloc[(int(fase_restricc)), hora] != c.FASE_ACABADA) & (
                not np.isnan(estado_real.iloc[(int(fase_restricc)), hora]))):

                clasificacion[int(fase_restricc)] = False

            # En caso de no cumplirse alguna o todas de las tres condiciones, la subfase trabajara.
            else:
                clasificacion[int(fase_restricc)] = True

        clasificacion_total = clasificacion.values()
        puede_trabajar = all(clasificacion_total)

    return(puede_trabajar)
