import math

import numpy as np

import logging

from . import constantes as c

# Nivel 1


def comprueba_temporal(hora, n_horas, umbrales, clima):
    """Funcion que comprueba para agente si el temporal se produce antes de n_horas, justo en n_horas o no se produce
       para una hora dada

    Args:
        hora: Hora.
        n_horas: Numero de horas que se consideran para comprobar el temporal.
        Son las horas especificados por el usuario como necesarias para proteger la obra.
        umbrales: Diccionario que incluye para cada agente su valor umbral (``valor``) y la duracion umbral (``dur``).
        df: Series de datos.

    Returns:
        Un diccionario que indica para cada agente

        * ``c.NO_TEMPORAL``: si el temporal no se produce.
        * ``c.TEMPORAL_N_HORAS``: si el temporal se produce en n_horas.
        * ``c.TEMPORAL_ANTES_N_HORAS``: si el temporal se produce antes de n_horas.
        * -1: si se produce algun problema en la funcion.

    """
    # Se comprueba si hay un temporal antes de n_horas para los umbrales
    # introducidos
    comprobacion = {}

    for j in umbrales:
        n = 0
        # Datos de clima en las proximas n_horas para el agente j
        data_nhoras = clima[j][hora:hora+n_horas]
        # Añado un +1 para que considere el último valor porque Python
        # considera el conjunto [) no inlcuyendo el último valor
        for k in data_nhoras:
            if k > umbrales[j]['valor']:
                n += 1

        if n >= umbrales[j]['dur'] and not data_nhoras.empty:
            comprobacion[j] = c.TEMPORAL_ANTES_N_HORAS

        # Si no hay temporal antes de n_horas, se comprueba si hay un temporal
        # justo en n_horas
        else:
            if clima[j][hora+n_horas] > umbrales[j]['valor']:
                # Del mismo modo añado un +2 al final del vector temp_nhoras
                # para que considere el ultimo valor
                temp_nhoras = clima[j][hora+n_horas:hora+n_horas+umbrales[j]['dur']]
                val = (temp_nhoras > umbrales[j]['valor'])
                if val.all():
                    comprobacion[j] = c.TEMPORAL_N_HORAS
                else:
                    comprobacion[j] = c.NO_TEMPORAL
            else:
                comprobacion[j] = c.NO_TEMPORAL

    return comprobacion


#def comprueba_comienzo_de_fase(hora, plan_avance, fase):
#    """Funcion que comprueba si la fase ha empezado o no a trabajar para una
#        hora dada
#
#    Args:
#        hora: Hora.
#        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
#            que si le toca trabajar.
#        fase: Numero de fase a comprobar
#
#    Returns:
#        Un valor que indica
#
#        * True: si la comprobacion es positiva.
#        * False: si la comprobacion esn negativa.
#
#    """
#    dia_ant = plan_avance.iloc[fase, 0: hora+1]
#    if dia_ant.any():
#        comprobacion = True
#    else:
#        comprobacion = False
#
#    return comprobacion


def comprueba_superacion_umbral(hora, umbrales, clima):
    """Funcion que comprueba para agente si se supera un umbral para una hora
    dada

    Args:
        hora: Hora.
        umbrales: Diccionario que incluye para cada agente su valor umbral
                  (``valor``) y la duracion umbral (``dur``).
        df: Series de datos.

    Returns:
        Un diccionario que indica para cada agente

        * True: si se supera el umbral.
        * False: si no se supera el umbral.

    """
    comprobacion = {}

    for j in umbrales:

        data = clima[j][hora]

        if j == 'calado':
            val = (data < umbrales[j]['valor'])
        else:
            val = (data > umbrales[j]['valor'])

        if val.all():
            comprobacion[j] = True
        else:
            comprobacion[j] = False

    return comprobacion


# Nivel 2

def comprueba_si_fase_trabaja(hora, plan_avance, fase):
    """Funcion que comprueba si para una hora dada a la fase le toca trabajar
    o no.

    Args:
        hora: Hora.
        plan_avance: Matriz de 0 y 1 donde 0 indica que para esa hora a esa
        fase no le corresponde trabajar y 1 indica que si le toca trabajar.
        fase: Numero de fase a comprobar

    Returns:
        Un booleano que indica

        * True: si la comprobacion es positiva
        * False: si la comprobacion es negativa

    Examples:
        >>> import pandas as pd
        >>> plan_avance = pd.read_csv('plan_avance.txt', delim_whitespace=True, header=None, dtype=bool,
        ...     true_values=['1'], false_values=['0'])
        >>> comprueba_si_fase_trabaja(28, plan_avance, 0)
        True
    """
    # Con esta comprobacion me aseguro que si hora se sale del plan de avance comprobacion valga siempre False
    # indicando que a la fase no le toca trabajar. Asi se evita el error a la hora de leer plan_avance fuera de rango.
    if plan_avance.shape[1] > 0:
        if hora <= (plan_avance.columns[-1]):
            if plan_avance.iloc[fase, hora]:
                comprobacion = True
            else:
                comprobacion = False
        else:
                comprobacion = False
    else:
                comprobacion = False

    return comprobacion


def comprueba_valor_anterior(fase, hora, avance_real):
    """Funcion que comprueba el valor anterior de la matriz de avance real

    Args:
        hora: Hora.
        fase: fase
        avance_real: Matriz de avance real que se va modificando a medida que
        avanza la obra

    Returns:
        Un valor que indica el estado de la fase en el dia anterior

    """
    # Se comprueba si hay un temporal antes de n_dias para los umbrales
    # introducidos

    comprobacion = avance_real.iloc[fase, hora-1]

    return comprobacion


def comprueba_si_fase_retrasada(fase, hora, vol_ejecutado, de_tramo_0, avance_real, clasificacion):
    """Funcion que comprueba si la fase se encuentra retrasada

    Args:
        hora: Hora.
        fase: fase
        avance_real: Matriz de avance real que se va modificando a medida que
        avanza la obra

    Returns:
        Un valor que indica el estado de la fase en el dia anterior

    """
    # Se comprueba si la fase va retrasada. (Que no le toque trabajar, que volumen ejecutado menor del total y
    # que la fase ya haya empezado o no haya acabado O que la fase ya haya acabado, pero no finalizado)
    if ((clasificacion == c.FASE_NO_TOCA_TRABAJAR) & (
       vol_ejecutado.iloc[fase, :].sum() < de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase']) & (
           avance_real.iloc[fase, hora-1] != -1)):
        comprobacion = True
    else:
        comprobacion = False

    return comprobacion


def comprueba_fase_acabada(vol_ejecutado, de_tramo_0, estado_real, fase, hora, cont_t_arranque):
    """Funcion que comprueba si la fase ha acabado (vol_ejecutado >= volumen total)

    Args:
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        fase: Fase constructiva
        hora: Hora (h)
        cont_t_arranque: Contador utilizado para considerar los tiempos de arranque, posicionamiento, etc que la
            maquinaria necesita antes de empezar a trabajar.

    Returns:
        Un valor que indica el estado de la fase en el dia anterior

    """
    # Si el volumen ejecutado supera o iguala al volumen de la subfase
    if vol_ejecutado.iloc[fase, :].sum() >= de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase']:

        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
            fase) + ' Nivel IV: Fase Acabada')

        # Cuando acaba la subfase se supone que me llevo la maquinaria de la obra.
        # Se pone el contador a 0 de tiempo de arranque
        cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] = 0

    return (estado_real)


def comprueba_fase_finalizada(plan_avance, fases_finalizadas, vol_ejecutado, de_tramo_0, fase, hora, cont_t_arranque):
    """Funcion que comprueba si la fase ha finalizada (acabada + protegida)

    Args:
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
        fases_finalizadas: Matriz que indica mediante booleanos las fases contructivas que ya han finalizado
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        fase: Fase constructiva
        hora: Hora (h)
        cont_t_arranque: Contador utilizado para considerar los tiempos de arranque, posicionamiento, etc que la
            maquinaria necesita antes de empezar a trabajar.

    Returns:
        Un matriz que indica mediante booleanos las fases que ya

    """

    # Si la subfase es la ultima o no se protege por ninguna sf siguiente y el volumen ejecutado de la fases actual son
    # mayores o iguales al volumen total de la fase

    # Extraccion de la subfase protectora
    proteccion = de_tramo_0.loc[de_tramo_0.index[fase], 'proteccion_por_subfases_siguientes']
    sf_protectora = de_tramo_0.loc[de_tramo_0.index[fase], 'subfase_protectora']

    # Si la subfase es flotante y no es nan, la convierto a entero
    if ((isinstance(sf_protectora, float)) & (not math.isnan(sf_protectora))):
        sf_protectora = int(sf_protectora)

    # si la subfase es distinta de la ultima y tiene subfase protectora
    if ((fase != plan_avance.shape[0] - 1) & (proteccion == 1)):
        # Si el volumen ejecutado es mayor que el volumen total de la subfase (subfase esta acabada) y si el volumen
        # ejecutado por la subfase protectora es mayor que el volumen total de la subfase protectora (subfase
        # protectora esta acabada)
        if ((vol_ejecutado.iloc[fase, :].sum() >= de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase']) &
                (vol_ejecutado.iloc[sf_protectora, :].sum() >= de_tramo_0.loc[de_tramo_0.index[sf_protectora], 'vol_subfase'])):

            # Entonces la subfase se considera finalizada (acabada más protegida)
            fases_finalizadas[fase] = True
            # Cuando finaliza la subfase me llevo la maquinaria de la obra. Pongo el contador a 0
            cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] = 0

            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                fase) + ' Nivel IV: Fase Finalizada')

    # Si la subfase es la ultima o no tiene subfase protectora
    if ((fase == plan_avance.shape[0] - 1) | (proteccion == 0)):
        # Si el volumen ejecutado por la subfase es mayor que el volumen total de la subfase
        if ((vol_ejecutado.iloc[fase, :].sum() >= de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase'])):

            # Entonces la subfase se considera finalizada
            fases_finalizadas[fase] = True
            # Cuando finaliza la subfase me llevo la maquinaria de la obra. Pongo el contador a 0
            cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] = 0

            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                fase) + ' Nivel IV: Fase Finalizada')

    return (fases_finalizadas)


def comprueba_si_fase_falla(eq_danno_fases, fase, clima, hora):

    comprobacion = {}

    agente = list(eq_danno_fases[fase].keys())
    valor_agente = clima.loc[clima.index[hora], agente]
    idx = (np.abs(eq_danno_fases[fase][agente[0]]['agente'] - valor_agente[0])).argmin()
    danno = eq_danno_fases[fase][agente[0]]['danno'][idx]

    if danno > 0:
        comprobacion = True
    else:
        comprobacion = False

    return (comprobacion)


def comprueba_si_fase_tiene_restriccion_de_avance(fase, restricciones_fases):

    tiene_restriccion = {}

    restriccion = restricciones_fases.iloc[fase, :]

    if restriccion['restriccion']:
        tiene_restriccion = True
    else:
        tiene_restriccion = False


    return(restriccion, tiene_restriccion)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, exclude_empty=True)
