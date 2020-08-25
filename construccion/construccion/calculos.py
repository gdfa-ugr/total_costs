import numpy as np
import pandas as pd
import math

import ast

import os

import logging

from . import constantes as c


def genera_matriz_volumen(plan_avance):

    if plan_avance.shape[1] <= 0:
        matriz = pd.DataFrame(np.full((plan_avance.shape[0], 10), 0, dtype=np.float))
    else:
        matriz = pd.DataFrame(np.full((plan_avance.shape[0], plan_avance.shape[1]), 0, dtype=np.float))

    return matriz


def genera_matriz_contador_proteccion_horas_fijas(plan_avance):

    if plan_avance.shape[1] <= 0:
        matriz = pd.DataFrame(np.full((plan_avance.shape[0], 10), 0, dtype=np.float), columns=['cont'])
    else:
        matriz = pd.DataFrame(np.full((plan_avance.shape[0], 2), 0, dtype=np.float), columns=['cont', 'activado'])

    return matriz


def genera_matriz_estado(plan_avance):

    if plan_avance.shape[1] <= 0:
        matriz = pd.DataFrame(np.full((plan_avance.shape[0], 10), None, dtype=np.float))
    else:
        matriz = pd.DataFrame(np.full((plan_avance.shape[0], plan_avance.shape[1]), None, dtype=np.float))

    return matriz


def calcula_n_horas_proteger(de_tramo, longitudes, fase):
    """Funcion que calcula el numero de horas necesario para proteger la fase constructiva. Es el numero de horas
       empleado para clasificar la fase en funcion de la proximidad de temporal

    Args:
        n_horas: Valor que indica el numero de horas necesarias para proteger un metro de una fase constructiva
        determinada (h).
        l: Valor que indica la longitud desprotegida de la fase constructiva (m).
        n_horas_max: Valor que indica el numero de horas maximas que se consideran para proteger la obra (h).

    Returns:
        Un valor que indica el numero de horas necesarias para proteger la fase constructiva


    """

    # Si las horas de proteccion de la longitud desprotegida son variables
    if de_tramo.loc[de_tramo.index[fase], 'n_horas_protecc_fijas_o_var'] == 'variable':
        # el numero de horas necesario para proteger la subfase se calcula como el producto del numero de horas
        # necesario para proteger un metro por la longitud desprotegida de la subfase
        n_horas_fase = math.ceil(de_tramo.loc[de_tramo.index[fase], 'n_horas_protecc_metro'] * longitudes.loc[
            longitudes.index[fase], 'l_desprotegida'])
        # Si el numero de horas necesario para proteger es mayor que el numero de horas maximo, me quedo con el maximo
        if n_horas_fase > de_tramo.loc[de_tramo.index[fase], 'n_horas_protecc_max']:
            n_horas_fase = de_tramo.loc[de_tramo.index[fase], 'n_horas_protecc_max']

    else:
        # Y si el numero de horas para proteger es fijo, me quedo con ese valor
        n_horas_fase = de_tramo.loc[de_tramo.index[fase], 'n_horas_protecc_fijas']
        # Si el numero de horas necesario para proteger es mayor que el numero de horas maximo, me quedo con el maximo
        if n_horas_fase > de_tramo.loc[de_tramo.index[fase], 'n_horas_protecc_max']:
            n_horas_fase = de_tramo.loc[de_tramo.index[fase], 'n_horas_protecc_max']

    return n_horas_fase


def actualiza_matriz(hora, fase, clasificacion, matriz):
    """Funcion que actualiza al final de cada iteracion (hora) el estado de la matriz:

    Args:
        hora: Hora (h).
        fase: Numero de la fase a actualizar
        clasificacion: Valor que indica el estado de la fase
        avance_real: Matriz que indica el estado de la fase constructiva a nivel II (no comenzada, protegida por
            estructura, proceso de proteccion y sin proteccion) y a nivel III (fase no trabaja, fase no toca
            trabajar, fase no trabaja restriccion, fase no trabaja operatividad, fase trabaja, fase trabaja retrasada
            fase protegiendo, fase perdidas, fase acabada).

    Returns:
        La matriz actualizada


    """
    if hora <= (matriz.columns[-1]):
        matriz.iloc[fase, hora] = clasificacion

    else:
        matriz.at[fase, hora] = clasificacion

    return matriz


def actualiza_longitudes_fase_siguiente(fase, longitudes, plan_avance, de_tramo):
    """Funcion que actualiza el valor de todas las longitudes de una fase constructiva al inicio de
       cada iteracion. Esta funcion comprueba si la longitud protegida y avanzada de una fase es como minimo la
       longitud avanzada por la fase siguiente, la cual sirve de proteccion a la fase anterior.

    Args:
        fase: Numero de fase constructiva a actualizar.
        rendimiento: Tiempo empleado en proteger un metro lineal de fase constructiva (h/m).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada fase
            constructiva (m)

    Returns:
        La matriz de longitudes actulizada


    """

    # Extraccion de la subfases que protegen a la subfase en cuestion en caso de haberlas
    proteccion = de_tramo.loc[de_tramo.index[fase], 'proteccion_por_subfases_siguientes']
    sf_protectora = de_tramo.loc[de_tramo.index[fase], 'subfase_protectora']

    # Si la subfase no es la ultima y alguna de las subfases siguientes la protege
    if ((fase != plan_avance.shape[0] - 1) & (proteccion == 1)):
        # Si la longitud protegida de la subfase es menor que la longitud avanzada por la subfase protectora,
        # se iguala la longitud protegida a la longitud avanzada
        if (longitudes.loc[fase, 'l_protegida'] < longitudes.loc[sf_protectora, 'l_avanzada']):

            longitudes.loc[longitudes.index[fase], 'l_protegida'] = longitudes.loc[sf_protectora, 'l_avanzada']

            # Si la longitud protegida es mayor que la longitud avanzada por la subfase proytectora, la longitud
            # protegida se reduce a la longitud avanzada por la sf protectora.
            if longitudes.loc[longitudes.index[fase], 'l_protegida'] > longitudes.loc[longitudes.index[fase], 'l_avanzada']:
                longitudes.loc[longitudes.index[fase], 'l_protegida'] = longitudes.loc[longitudes.index[fase], 'l_avanzada']
                longitudes.loc[
                    longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] - longitudes.loc[longitudes.index[fase], 'l_protegida']
            else:
                longitudes.loc[
                    longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] - longitudes.loc[longitudes.index[fase], 'l_protegida']

    logging.info(' Fase: ' + str(
        fase) + ' LA: ' + str(longitudes.loc[longitudes.index[fase], 'l_avanzada']) + ' LP: ' + str(longitudes.loc[
            longitudes.index[fase], 'l_protegida']) + ' LD: ' + str(longitudes.loc[longitudes.index[fase], 'l_desprotegida']))

    return longitudes


def actualiza_longitud_protegida(fase, rendimiento, longitudes, de_tramo_0, cont_pro_h_fijas):
    """Funcion que actualiza el valor de la longitud protegida y desprotegida de una fase constructiva

    Args:
        fase: Numero de fase constructiva a actualizar.
        rendimiento: Tiempo empleado en proteger un metro lineal de fase constructiva (h/m).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada fase
            constructiva (m)

    Returns:
        La matriz de longitudes actulizada


    """
    # Si el numero de horas de proteccion son fijas
    if de_tramo_0.loc[de_tramo_0.index[fase], 'n_horas_protecc_fijas_o_var'] == 'fijas':

        # Si el contador de proteccion de horas fijas es igual a 0, se inicia el contador para dar la orden de iniciar
        # el proceso de reparacion
        if cont_pro_h_fijas.loc[cont_pro_h_fijas.index[fase], 'activado'] == 0:
            # Se activa el contador
            cont_pro_h_fijas.loc[cont_pro_h_fijas.index[fase], 'activado'] = 1

        # Se comprueba si el contador iguala al numero de horas necesario para empezar a proteger
        if cont_pro_h_fijas.loc[cont_pro_h_fijas.index[fase], 'cont'] >= de_tramo_0.loc[de_tramo_0.index[fase], 'n_horas_protecc_fijas']:
            # La longitud protegida se iguala a la longitud avanzada, esto es, se protege toda la longitud
            # desprotegida de la subfase
            longitudes.loc[longitudes.index[fase], 'l_protegida'] = longitudes.loc[longitudes.index[fase], 'l_avanzada']

    # Si el numero de horas de proteccion son variables
    elif de_tramo_0.loc[de_tramo_0.index[fase], 'n_horas_protecc_fijas_o_var'] == 'variable':

        # Entonces la longotud protegida en el estado se calcula a partir del rendimiento
        longitudes.loc[longitudes.index[fase], 'l_protegida'] = longitudes.loc[longitudes.index[fase], 'l_protegida'] + math.ceil(1. / rendimiento)

    # Comprobacion 1: La longitud protegida nunca puede ser mayor que la longitud avanzada
    if longitudes.loc[longitudes.index[fase], 'l_protegida'] > longitudes.loc[longitudes.index[fase], 'l_avanzada']:
        longitudes.loc[longitudes.index[fase], 'l_protegida'] = longitudes.loc[longitudes.index[fase], 'l_avanzada']
        longitudes.loc[longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] - longitudes.loc[longitudes.index[fase], 'l_protegida']
    else:
        longitudes.loc[longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] - longitudes.loc[longitudes.index[fase], 'l_protegida']

    logging.info(' Fase: ' + str(
        fase) + ' LA: ' + str(longitudes.loc[longitudes.index[fase], 'l_avanzada']) + ' LP: ' + str(longitudes.loc[
            longitudes.index[fase], 'l_protegida']) + ' LD: ' + str(longitudes.loc[longitudes.index[fase], 'l_desprotegida']))

    return longitudes, cont_pro_h_fijas


def volumen_fase_perdidas(fase, hora, vol_unit, vol_ejecutado, vol_perdido, longitudes, eq_danno_fases, clima,
                          rep_inmed):
    """Funcion que calcula el volumen y la longitud avanzada de una fase constructiva clasificada como perdidas

    Args:
        fase: Numero de la fase a actualizar
        hora: Hora (h)
        vol_unit: Valor que indica el volumen unitario de la fase. Metros cubicos de fase por metro lineal (m3/m)
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)

        longitudes: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).


    """
    # Extraccion del agente principal respondable de producir dannos
    agente = list(eq_danno_fases[fase].keys())
    # Extraccion del valor del agente
    valor_agente = clima.loc[clima.index[hora], agente]
    # Indice de la ecuacion de danno mas cercano al valor del agente
    idx = (np.abs(eq_danno_fases[fase][agente[0]]['agente'] - valor_agente[0])).argmin()
    # Perdidas en m3/m (perdidas en la seccion)
    danno_unit = eq_danno_fases[fase][agente[0]]['danno'][idx]  # m3/m Perdidas en la seccion
    # Volumen de perdidas obtenido como el producto de los dannos en la seccion por la longitud desprotegida de
    # la subfase
    vol_perdidas = danno_unit * longitudes.loc[longitudes.index[fase], 'l_desprotegida']  # m3

    # Se calcula la longitud de perdidas
    long_perdidas = vol_perdidas / vol_unit
    # Si la longitud de perdidas es mayor que la longitud desprotegida
    if long_perdidas > longitudes.loc[longitudes.index[fase], 'l_desprotegida']:
        # Se iguala la longitud de perdidas a la longitud desprotegida
        long_perdidas = longitudes.loc[longitudes.index[fase], 'l_desprotegida']
        # El volumen de perdidas se restrinje unicamente a la longitud desprotegida
        vol_perdidas = long_perdidas*vol_unit

    # Se actualiza el valor del volumen ejecutado (las perdidas restan volumen)
    if hora <= (vol_ejecutado.columns[-1]):
        if rep_inmed:
            vol_ejecutado.iloc[fase, hora] = -(0)
        else:
            vol_ejecutado.iloc[fase, hora] = -(vol_perdidas)
    else:
        if rep_inmed:
            vol_ejecutado.at[fase, hora] = -(0)
        else:
            vol_ejecutado.at[fase, hora] = -(vol_perdidas)

    # Se comprueba que el volumen no es menor que 0. Y si lo es se deja en 0
    if vol_ejecutado.iloc[fase, :].sum() < 0:
        if hora <= (vol_ejecutado.columns[-1]):
            vol_ejecutado.iloc[fase, hora] = 0
        else:
            vol_ejecutado.at[fase, hora] = 0

    # Se actualiza el valor de la longitud avanzada (volumen ejecutado entre volumen unitario)
    longitudes.loc[longitudes.index[fase], 'l_avanzada'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] + (vol_ejecutado.iloc[fase, hora] / vol_unit)

    # Se actualiza el valor de la longitud desprotegida
    longitudes.loc[longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_desprotegida'] + (
        vol_ejecutado.iloc[fase, hora] / vol_unit)

    # Volumen perdido por daños
    if hora <= (vol_perdido.columns[-1]):
            vol_perdido.iloc[fase, hora] = -(vol_perdidas)
    else:
            vol_perdido = vol_perdido.reindex_axis(range(hora), axis=1)
            vol_perdido.at[fase, hora] = -(vol_perdidas)

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
        fase) + ' LA: ' + str(longitudes.loc[longitudes.index[fase], 'l_avanzada']) + ' LP: ' + str(longitudes.loc[
            longitudes.index[fase], 'l_protegida']) + ' LD: ' + str(longitudes.loc[longitudes.index[fase], 'l_desprotegida']))

    return (vol_ejecutado, vol_perdido, longitudes)


def volumen_fase_trabajo_retrasada(fase, hora, vol_unit, vol_ejecutado, longitudes, rendimiento):
    """Funcion que calcula el volumen y la longitud avanzada de una fase constructiva clasificada como trabaja
       retrasada.

    Args:
        fase: Numero de la fase a actualizar
        hora: Hora (h)
        vol_unit: Valor que indica el volumen unitario de la fase. Metros cubicos de fase por metro lineal (m3/m)
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)

        longitudes: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).


    """

    # Se actualiza el valor del volumen ejecutado (las perdidas restan volumen)
    if hora <= (vol_ejecutado.columns[-1]):
        vol_ejecutado.iloc[fase, hora] = rendimiento
    else:
        vol_ejecutado.at[fase, hora] = rendimiento

    # Se actualiza el valor de la longitud avanzada (volumen ejecutado entre volumen unitario)
    longitudes.loc[longitudes.index[fase], 'l_avanzada'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] + (vol_ejecutado.iloc[fase, hora] / vol_unit)

    # Se actualiza el valor de la longitud desprotegida
    longitudes.loc[longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_desprotegida'] + (
        vol_ejecutado.iloc[fase, hora] / vol_unit)

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
        fase) + ' LA: ' + str(longitudes.loc[longitudes.index[fase], 'l_avanzada']) + ' LP: ' + str(longitudes.loc[
            longitudes.index[fase], 'l_protegida']) + ' LD: ' + str(longitudes.loc[longitudes.index[fase], 'l_desprotegida']))

    return (vol_ejecutado, longitudes)


def volumen_fase_trabajo(fase, hora, vol_unit, vol_ejecutado, longitudes, rendimiento):
    """Funcion que calcula el volumen y la longitud avanzada de una fase constructiva clasificada como trabajo.

    Args:
        fase: Numero de la fase a actualizar
        hora: Hora (h)
        vol_unit: Valor que indica el volumen unitario de la fase. Metros cubicos de fase por metro lineal (m3/m)
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)

        longitudes: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).


    """

    # Se actualiza el valor del volumen ejecutado (las perdidas restan volumen)
    if hora <= (vol_ejecutado.columns[-1]):
        vol_ejecutado.iloc[fase, hora] = rendimiento
    else:
        vol_ejecutado.at[fase, hora] = rendimiento

    # Se actualiza el valor de la longitud avanzada (volumen ejecutado entre volumen unitario)
    longitudes.loc[longitudes.index[fase], 'l_avanzada'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] + (vol_ejecutado.iloc[fase, hora] / vol_unit)

    # Se actualiza el valor de la longitud desprotegida
    longitudes.loc[longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_desprotegida'] + (
        vol_ejecutado.iloc[fase, hora] / vol_unit)

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
        fase) + ' LA: ' + str(longitudes.loc[longitudes.index[fase], 'l_avanzada']) + ' LP: ' + str(longitudes.loc[
            longitudes.index[fase], 'l_protegida']) + ' LD: ' + str(longitudes.loc[longitudes.index[fase], 'l_desprotegida']))

    return (vol_ejecutado, longitudes)


def restitucion_volumen_fase_no_trabaja_restriccion(fase, hora, vol_unit, vol_ejecutado, longitudes):
    """Funcion que restituye el volumen y la longitud avanzada de una fase constructiva que no trabaja por
       restriccion con la fase anterior (longitud de avance). Devuelve la longitud y el volumen al estado de la
       iteracion anterior.

    Args:
        fase: Numero de la fase a actualizar
        hora: Hora (h)
        vol_unit: Valor que indica el volumen unitario de la fase. Metros cubicos de fase por metro lineal (m3/m)
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)

        longitudes: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).


    """

    # Se actualiza el valor de la longitud avanzada (volumen ejecutado entre volumen unitario)
    longitudes.loc[longitudes.index[fase], 'l_avanzada'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] - (vol_ejecutado.iloc[fase, hora] / vol_unit)

    # Se actualiza el valor de la longitud desprotegida
    longitudes.loc[longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_desprotegida'] - (
        vol_ejecutado.iloc[fase, hora] / vol_unit)

    # Se actualiza el valor del volumen ejecutado (las perdidas restan volumen)
    if hora <= (vol_ejecutado.columns[-1]):
        vol_ejecutado.iloc[fase, hora] = 0
    else:
        vol_ejecutado.at[fase, hora] = 0

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
        fase) + ' LA: ' + str(longitudes.loc[longitudes.index[fase], 'l_avanzada']) + ' LP: ' + str(longitudes.loc[
            longitudes.index[fase], 'l_protegida']) + ' LD: ' + str(longitudes.loc[longitudes.index[fase], 'l_desprotegida']))

    return (vol_ejecutado, longitudes)


def volumen_fase_no_trabaja(fase, hora, vol_unit, vol_ejecutado, longitudes):
    """Funcion que calcula el volumen y la longitud avanzada de una fase constructiva clasificada como  no trabaja.

    Args:
        fase: Numero de la fase a actualizar
        hora: Hora (h)
        vol_unit: Valor que indica el volumen unitario de la fase. Metros cubicos de fase por metro lineal (m3/m)
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)

        longitudes: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).


    """

    # Se actualiza el valor del volumen ejecutado (las perdidas restan volumen)
    if hora <= (vol_ejecutado.columns[-1]):
        vol_ejecutado.iloc[fase, hora] = 0
    else:
        vol_ejecutado.at[fase, hora] = 0

    return (vol_ejecutado, longitudes)

    # Se actualiza el valor de la longitud avanzada (volumen ejecutado entre volumen unitario)
    longitudes.loc[longitudes.index[fase], 'l_avanzada'] = longitudes.loc[longitudes.index[fase], 'l_avanzada'] + (vol_ejecutado.iloc[fase, hora] / vol_unit)

    # Se actualiza el valor de la longitud desprotegida
    longitudes.loc[longitudes.index[fase], 'l_desprotegida'] = longitudes.loc[longitudes.index[fase], 'l_desprotegida'] + (
        vol_ejecutado.iloc[fase, hora] / vol_unit)

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
        fase) + 'LA: ' + str(longitudes.loc[longitudes.index[fase], 'l_avanzada']) + 'LP: ' + str(longitudes.loc[
            longitudes.index[fase], 'l_protegida']) + 'LD: ' + str(longitudes.loc[longitudes.index[fase], 'l_desprotegida']))

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
        fase) + ' LA: ' + str(longitudes.loc[longitudes.index[fase], 'l_avanzada']) + ' LP: ' + str(longitudes.loc[
            longitudes.index[fase], 'l_protegida']) + ' LD: ' + str(longitudes.loc[longitudes.index[fase], 'l_desprotegida']))

    return (vol_ejecutado, longitudes)


def recorte_matrices_resultantes(hora, clima, avance_real, estado_real, vol_ejecutado, vol_perdido):
    clima = clima.iloc[0:hora, :]
    avance_real = avance_real.iloc[:, 0:hora]

    # Elimino los NaN si los hubiese
    estado_real = estado_real.fillna(-1)
    estado_real = estado_real.iloc[:, 0:hora]
    vol_ejecutado = vol_ejecutado.iloc[:, 0:hora]
    vol_perdido = vol_perdido.iloc[:, 0:hora]

    return (clima, avance_real, estado_real, vol_ejecutado, vol_perdido)


def calculo_costes(plan_avance, maquinaria_fases, estado_real, vol_perdido, eq_coste_fases, eq_danno_fases, clima,
                   costes_fase, vol_ejecutado):

    """Funcion que calcula la adjudicacion de costes tras la verificacion del proceso constructivo.

    Args:
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
        maquinaria_fases: Matriz con los datos de maquinaria de cada subfase
        estado_real: Matriz con el estado real de cada subfase de cada tramo en cada iteracion durante la verificación del proceso constructivo
        vol_perdido: Matriz con los volumenes perdidos para cada iteracion del proceso constructivo.
        eq_costes_fases: Matriz con la ecuacion de costes asociados al danno para cada subfase
        eq_dannos_fase: Matriz con la ecuacion de danno para cada valor del agente para cada subase
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        costes_fase: Matriz con los datos de costes asociados a las subfases constructivas
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)

    Returns:
         Un tupla de la forma (costes_ejecc_sf_unit, costes_directos_sf_unit, costes_ejecc_sf_total, costes_directos_sf_total,
            costes_sf_total).

        * ``costes_ejecc_sf_unit``: costes de ejecucion unitarios de cada subfase
        * ``costes_directos_sf_unit``: costes directos unitarios de cada subfase
        * ``costes_ejecc_sf_total``: costes de ejecucion totales para cada subfase
        * ``costes_directos_sf_total``: costes directos totales para cada subfase
        * ``costes_sf_total``: costes totales para cada subfase

    """

    # COSTES DE EJECUCION
    # Se inicializa a 0 la matriz con el desglose de los costes de ejecucion para cada subfase
    costes_ejecc_sf_unit = pd.DataFrame(np.full((estado_real.shape[0], 4), 0, dtype=np.float))
    costes_ejecc_sf_unit.columns = ['c_maquinaria_subfase_unit', 'c_mano_obra_subfase_unit',
                                    'c_adicional_subfase_unit', 'c_ejecucion_total_subfase_unit']

    # Relleno el df con los datos de entrada
    for fase, _ in enumerate(maquinaria_fases):
        cont = 0
        coste_maq_unit = pd.Series()  # Inicializo a vacio el coste de maquinaria unitario
        coste_mano_obra_unit = pd.Series()  # Inicializo a vacio el coste de mano de obra unitario
        coste_ejecucion_unit = pd.Series()  # Inicializo a vacio el coste de ejecucion unitario
        coste_adicional_unit = pd.Series()  # Inicializo a vacio el coste adiccional unitario

        # Extraccion de las unidades de obra de la subfase
        uds_obra = maquinaria_fases[fase]

        # Recorrido por cada una de las unidades de obra de la subfase
        for u_obra, _ in enumerate(uds_obra.iterrows()):
            # Extraccion de las maquinarias empleadas en la unidad de obra
            maq = ast.literal_eval(uds_obra.loc[uds_obra.index[u_obra], 'maquinaria'])

            # Recorrido por cada una de las maquinarias de la unidad de obra
            for key in maq:
                # Numero de maquinaria
                num_maq_aux = maq[key]['num']
                # Coste de una maquinaria unitario (en cada hora)
                coste_maq_unit_aux = maq[key]['coste_maq_unit']
                # Coste de todas las maq. unitario (cada hora) para cada tipo de maquinaria diferente en cada unidad
                # de obra
                coste_maq_unit_aux = coste_maq_unit_aux * num_maq_aux
                # Asignacion del coste de maq. unitario (cada hora) para cada tipo de maquinaria diferente en cada
                # unidad de obra
                coste_maq_unit.at[cont] = coste_maq_unit_aux
                # Asignacion del coste de mano de obra unitario (cada hora) para cada tipo de maquinaria diferente
                # en cda unidad de obra
                coste_mano_obra_unit.at[cont] = maq[key]['coste_mano_obra_unit']
                # Asignacion del coste adicional unitario (cada hora) para cada tipo de maquinaria diferente en cdada
                # unidad de obra
                coste_adicional_unit.at[cont] = maq[key]['coste_add_unit']
                # Coste de ejecucion unitario es la suma de los costes anteriores (cada hora) para cada tipo de
                # maquinaria diferente en cada unidad de obra
                coste_ejecucion_unit_aux = coste_maq_unit[cont] + coste_mano_obra_unit[cont] + coste_adicional_unit[
                    cont]
                coste_ejecucion_unit.at[cont] = coste_ejecucion_unit_aux

                cont = cont + 1

        # Obtengo los costes de maquinaria, mano de obra, adicionales y de ejecucion unitarios (cada hora) totales de
        # la subfase como la suma de los individuales para cada maquinaria en cada unidad de obra
        costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[fase], 'c_maquinaria_subfase_unit'] = coste_maq_unit.sum()
        costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[fase], 'c_mano_obra_subfase_unit'] = coste_mano_obra_unit.sum()
        costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[fase], 'c_adicional_subfase_unit'] = coste_adicional_unit.sum()
        costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[fase], 'c_ejecucion_total_subfase_unit'] = coste_ejecucion_unit.sum()

    # COSTES DIRECTOS
    # Se inicializa a 0 la matriz con el desglose de los costes directos para cada subfase
    costes_directos_sf_unit = pd.DataFrame(np.full((estado_real.shape[0], 5), 0, dtype=np.float))
    costes_directos_sf_unit.columns = ['c_materiales_subfase_unit', 'c_mantenimiento_subfase_unit',
                                       'c_proteccion_subfase_unit', 'c_ejecucion_subfase_unit',
                                       'c_directos_totales_subfase_unit']

    # Recorrido por cada una de las subfases de la obra
    # Relleno el df con los datos de entrada
    for fase, _ in enumerate(costes_fase):
        # Adicion al df de costes_directos los costes materiales unitarios de cada subfase
        costes_directos_sf_unit.loc[costes_directos_sf_unit.index[fase], 'c_materiales_subfase_unit'] = costes_fase[fase].loc[
            costes_fase[fase].index[0], 'costes_materiales_unit']
        # Adicion al df de costes_directos los costes de proteccion unitarios de cada subfase
        costes_directos_sf_unit.loc[costes_directos_sf_unit.index[fase], 'c_proteccion_subfase_unit'] = costes_fase[fase].loc[
            costes_fase[fase].index[0], 'coste_proteccion']
        # Adicion al df de costes_directos los costes de mantenimiento unitarios de cada subfase
        costes_directos_sf_unit.loc[costes_directos_sf_unit.index[fase], 'c_mantenimiento_subfase_unit'] = costes_fase[fase].loc[
            costes_fase[fase].index[0], 'coste_mantenimiento']
        # Adicion al df de costes_directos los costes de ejecucion unitarios de cada subfase
        costes_directos_sf_unit.loc[costes_directos_sf_unit.index[fase], 'c_ejecucion_subfase_unit'] = costes_ejecc_sf_unit.loc[
            costes_ejecc_sf_unit.index[fase], 'c_ejecucion_total_subfase_unit']
        # Adicion al df de costes_directos los costes directos totales unitarios de cada subfase como la suma
        # de los costes materiales, de proteccion, de mantenimiento y de ejecucion de cada subfase
        costes_directos_sf_unit.loc[costes_directos_sf_unit.index[fase], 'c_directos_totales_subfase_unit'] = costes_directos_sf_unit.loc[
            costes_directos_sf_unit.index[fase], 'c_materiales_subfase_unit'] + costes_directos_sf_unit.loc[
            costes_directos_sf_unit.index[fase], 'c_proteccion_subfase_unit'] + costes_directos_sf_unit.loc[
            costes_directos_sf_unit.index[fase], 'c_mantenimiento_subfase_unit'] + costes_directos_sf_unit.loc[costes_directos_sf_unit.index[fase], 'c_ejecucion_subfase_unit']

    # Se inicializan a 0 los df de costes totales definitivas que se iran rellenando a medida que se avance en la
    # matriz de estado real
    costes_ejecc_sf_total = pd.DataFrame(np.full((estado_real.shape[0], 4), 0, dtype=np.float))
    costes_ejecc_sf_total.columns = ['c_maquinaria_total', 'c_mano_obra_total',
                                     'c_adicional_total', 'c_ejecucion_total']

    costes_directos_sf_total = pd.DataFrame(np.full((estado_real.shape[0], 5), 0, dtype=np.float))
    costes_directos_sf_total.columns = ['c_materiales_total', 'c_mantenimiento_total',
                                        'c_proteccion_total', 'c_ejecucion_total',
                                        'c_directos_total']

    costes_sf_total = pd.DataFrame(np.full((estado_real.shape[0], 4), 0, dtype=np.float))
    costes_sf_total.columns = ['c_directos_total', 'c_indirectos_total',
                               'c_perdidas_total', 'c_total']

    # Se recorre la matriz de estado real para ir calculando los coste en cada estado de la fase
    for f, _ in estado_real.iterrows():
        for h, _ in estado_real.iteritems():

            # Si la subfase se clasifica como no trabaja
            if estado_real.loc[estado_real.index[f], h] == c.FASE_NO_TRABAJA:

                # Costes de mantenimiento
                c_mant_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_mantenimiento_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_mantenimiento_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_mantenimiento_total'] + c_mant_aux

            # Si la subfase se clasifica como no toca trabajar
            if estado_real.loc[estado_real.index[f], h] == c.FASE_NO_TOCA_TRABAJAR:

                # Costes de mantenimiento
                c_mant_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_mantenimiento_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_mantenimiento_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_mantenimiento_total'] + c_mant_aux

            # Si la subfase se clasifica como no trabaja por restriccion
            if estado_real.loc[estado_real.index[f], h] == c.FASE_NO_TRABAJA_RESTRICCION:

                # Costes de mantenimiento
                c_mant_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_mantenimiento_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_mantenimiento_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_mantenimiento_total'] + c_mant_aux

            # Si la subfase se clasifica como no trabaja por operatividad
            if estado_real.loc[estado_real.index[f], h] == c.FASE_NO_TRABAJA_OPERATIVIDAD:

                # Costes de mantenimiento
                c_mant_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_mantenimiento_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_mantenimiento_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_mantenimiento_total'] + c_mant_aux

            # Si la subfase se clasifica como trabaja
            if estado_real.loc[estado_real.index[f], h] == c.FASE_TRABAJA:

                # Costes de maquinaria
                c_maq_aux = costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[f], 'c_maquinaria_subfase_unit']
                costes_ejecc_sf_total.loc[costes_ejecc_sf_total.index[f], 'c_maquinaria_total'] = costes_ejecc_sf_total.loc[
                    costes_ejecc_sf_total.index[f], 'c_maquinaria_total'] + c_maq_aux

                # Costes de mano de obra
                c_mano_obra_aux = costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[f], 'c_mano_obra_subfase_unit']
                costes_ejecc_sf_total.loc[costes_ejecc_sf_total.index[f], 'c_mano_obra_total'] = costes_ejecc_sf_total.loc[
                    costes_ejecc_sf_total.index[f], 'c_mano_obra_total'] + c_mano_obra_aux

                # Costes de materiales
                c_mater_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_materiales_subfase_unit'] * vol_ejecutado.loc[vol_ejecutado.index[f], h]
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_materiales_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_materiales_total'] + c_mater_aux

                # Costes de mantenimiento
                c_mant_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_mantenimiento_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_mantenimiento_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_mantenimiento_total'] + c_mant_aux

            # Si la subfase se clasifica como trabaja retrasada
            if estado_real.loc[estado_real.index[f], h] == c.FASE_TRABAJA_RETRASADA:

                # Costes de maquinaria
                c_maq_aux = costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[f], 'c_maquinaria_subfase_unit']
                costes_ejecc_sf_total.loc[costes_ejecc_sf_total.index[f], 'c_maquinaria_total'] = costes_ejecc_sf_total.loc[
                    costes_ejecc_sf_total.index[f], 'c_maquinaria_total'] + c_maq_aux

                # Costes de mano de obra
                c_mano_obra_aux = costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[f], 'c_mano_obra_subfase_unit']
                costes_ejecc_sf_total.loc[costes_ejecc_sf_total.index[f], 'c_mano_obra_total'] = costes_ejecc_sf_total.loc[
                    costes_ejecc_sf_total.index[f], 'c_mano_obra_total'] + c_mano_obra_aux

                # Costes adicionales por retraso
                c_adic_aux = costes_ejecc_sf_unit.loc[costes_ejecc_sf_unit.index[f], 'c_adicional_subfase_unit']
                costes_ejecc_sf_total.loc[costes_ejecc_sf_total.index[f], 'c_adicional_total'] = costes_ejecc_sf_total.loc[
                    costes_ejecc_sf_total.index[f], 'c_adicional_total'] + c_adic_aux

                # Costes de materiales
                c_mater_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_materiales_subfase_unit'] * vol_ejecutado.loc[vol_ejecutado.index[f], h]
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_materiales_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_materiales_total'] + c_mater_aux

                # Costes de mantenimiento
                c_mant_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_mantenimiento_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_mantenimiento_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_mantenimiento_total'] + c_mant_aux

            # Si la subfase se clasifica como protegiendo
            if estado_real.loc[estado_real.index[f], h] == c.FASE_PROTEGIENDO:

                # Costes de mantenimiento
                c_mant_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_mantenimiento_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_mantenimiento_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_mantenimiento_total'] + c_mant_aux

                # Costes de proteccion
                c_protecc_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_proteccion_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_proteccion_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_proteccion_total'] + c_protecc_aux

            # Si la subfase se clasifica como en perdidas
            if estado_real.loc[estado_real.index[f], h] == c.FASE_PERDIDAS:

                # En primer lugar se calcula el daño unitario

                # Extraccion del agente principal respondable de producir dannos
                agente = list(eq_danno_fases[f].keys())
                # Extraccion del valor del agente
                valor_agente = clima.loc[clima.index[h], agente]
                # Indice de la ecuacion de danno mas cercano al valor del agente
                idx = (np.abs(eq_danno_fases[f][agente[0]]['agente'] - valor_agente[0])).argmin()
                # Perdidas en m3/m (perdidas en la seccion)
                danno_unit = eq_danno_fases[f][agente[0]]['danno'][idx]  # m3/m Perdidas en la seccion
                danno_unit = danno_unit

                # Danno total, obtenido como el producto del danno unitario por la longitud desprotegida
                danno = -vol_perdido.loc[vol_perdido.index[f], h]

                # Longitud desprotegida (m)
                l_desp = abs(danno/danno_unit)

                # Costes de perdidas

                # Extraccion del agente principal respondable de producir dannos
                agente = list(eq_coste_fases[f].keys())

                # Indice de la ecuacion de coste mas cercano al valor del danno unitario
                idx = (np.abs(eq_coste_fases[f][agente[0]]['danno'] - danno_unit)).argmin()
                # Coste de las perdidas unitario en la sección transversal
                c_perd_unit = eq_coste_fases[f][agente[0]]['coste'][idx]
                # Coste de las perdidas total en el estado de mar es igual al coste de las perdidas unitario por la
                # longitud desprotegida
                c_perd = c_perd_unit*l_desp

                costes_sf_total.loc[costes_sf_total.index[f], 'c_perdidas_total'] = costes_sf_total.loc[costes_sf_total.index[f], 'c_perdidas_total'] + c_perd

            # Si la subfase se clasifica como acabada
            if estado_real.loc[estado_real.index[f], h] == c.FASE_ACABADA:

                # Costes de mantenimiento
                c_mant_aux = costes_directos_sf_unit.loc[costes_directos_sf_unit.index[f], 'c_mantenimiento_subfase_unit']
                costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_mantenimiento_total'] = costes_directos_sf_total.loc[
                    costes_directos_sf_total.index[f], 'c_mantenimiento_total'] + c_mant_aux

    # Sumo los costes de ejecucion, directos y totales para tener el coste total incluyendo los costes indirectos
    for f, _ in costes_ejecc_sf_total.iterrows():
        costes_ejecc_sf_total.loc[costes_ejecc_sf_total.index[f], 'c_ejecucion_total'] = costes_ejecc_sf_total.loc[costes_ejecc_sf_total.index[f], :].sum()
        costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_ejecucion_total'] = costes_ejecc_sf_total.loc[costes_ejecc_sf_total.index[f], 'c_ejecucion_total']
        costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_directos_total'] = costes_directos_sf_total.loc[costes_directos_sf_total.index[f], :].sum()
        costes_sf_total.loc[costes_sf_total.index[f], 'c_indirectos_total'] = costes_fase[f].loc[
            costes_fase[f].index[0], 'costes_indirectos']*costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_directos_total']
        costes_sf_total.loc[costes_sf_total.index[f], 'c_directos_total'] = costes_directos_sf_total.loc[costes_directos_sf_total.index[f], 'c_directos_total']
        costes_sf_total.loc[costes_sf_total.index[f], 'c_total'] = costes_sf_total.loc[costes_sf_total.index[f], :].sum()

    return (costes_ejecc_sf_unit, costes_directos_sf_unit, costes_ejecc_sf_total, costes_directos_sf_total,
            costes_sf_total)


def calculo_longitudes_volumenes_acumulados(estado_real_total, vol_ejecutado_total, de_tramo_total):

    lon_ejecutada_total = []
    lon_acumulada_total = []
    vol_acumulado_total = []
    lon_diferencia_total = []

    for tramo, _ in enumerate(estado_real_total):
        lon_ejecutada = vol_ejecutado_total[tramo].copy()
        vol_ejecutado = vol_ejecutado_total[tramo]
        lon_acumulada = lon_ejecutada.copy()
        vol_acumulado = lon_ejecutada.copy()
        lon_diferencia = lon_acumulada.copy()

        for fase, _ in vol_ejecutado_total[tramo].iterrows():

            lon_ejecutada.iloc[fase, :] = (vol_ejecutado_total[tramo].iloc[fase, :]) / (de_tramo_total[tramo].loc[
                de_tramo_total[tramo].index[fase], 'vol_subfase_unit'])
            print (lon_ejecutada.iloc[fase, :].sum())

            lon_acumulada.iloc[fase, :] = np.cumsum(lon_ejecutada.iloc[fase, :])
            vol_acumulado.iloc[fase, :] = np.cumsum(vol_ejecutado.iloc[fase, :])

            if fase != vol_ejecutado_total[tramo].index[-1]:
                lon_diferencia.iloc[fase, :] = lon_acumulada.iloc[fase, :] - lon_acumulada.iloc[fase + 1, :]

        lon_ejecutada_total.append(lon_ejecutada)
        lon_acumulada_total.append(lon_acumulada)
        vol_acumulado_total.append(vol_acumulado)
        lon_diferencia_total.append(lon_diferencia)

    return (lon_ejecutada_total, lon_acumulada_total, vol_acumulado_total, lon_diferencia_total)


def actualiza_matrices_fases_finalizadas(fases_finalizadas, estado_real, hora):

    # Se annade None en cada hora en las que la subfase ya ha finalizado, pero no ha acabado (finalizada + protegida)

    # Filas con las subfases finalizadas
    fase_fin = fases_finalizadas[fases_finalizadas == True]  # nopep8

    if fase_fin.any():
        # Obtengo los indices de las filas
        idx = fase_fin.index

        # Annado None en las horas en las que la fase se encuentra finalizada pero no ha acabado
        # (finalizada + protegida)
        if hora <= (estado_real.columns[-1]):
            estado_real.iloc[idx, hora] = None

        else:
            estado_real.at[idx, hora] = None

    return()


def extraccion_resultados(de_planta, n, estado_real_total, vol_acumulado_total, vol_ejecutado_total,
                          de_tramo_total, hora_inicio_tramos, vol_perdido_total, costes_ejecc_sf_total_total,
                          costes_directos_sf_total_total, costes_sf_total_total, com_fin_teorico_total,
                          ruta_de='.', ruta_ds='.', alcance='EA'):

    """Funcion que extrae y organiza los resultados de la verificación del proceso constructivo de un tramo.

    Args:
        de_planta: Matriz con los datos de entrada relativos a la planta del tramo

            * Etiqueta del tramo
            * Longitud del tramo
            * Tipologia del tramo
        n: Etiqueta del tramo de dique
        estado_real_total: Matriz que guarda en cada tramo para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_acumulado_total: Matriz con los volumenes ejecutados y/o perdidos acumulados hasta cada iteracion del proceso constructivo.
        vol_ejecutado_total: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            para cada tramo
        de_tramo_total: Matriz con los datos de entrada introducidos por el usuario para cada tramo de dique
        hora_inicio_tramos: Matriz con las horas de inicio reales de ejecucion de cada uno de los tramos del dique
        vol_perdido_total: Matriz con los volumenes perdidos para cada iteracion del proceso constructivo
            para cada tramo
        costes_ejecc_sf_total_total: costes de ejecucion totales de cada subfase
        costes_directos_sf_total_total: costes directos totales de cada subfase
        costes_sf_total_total: costes totales de cada subfase
        com_fin_teorico_total: matriz con las horas de inicio y finalizacion teoricas de cada una de las subfases
        ruta_de: cadena de texto con la ruta del directorio que contiene los datos de entrada
        ruta_ds: cadena de texto con la ruta del directorio que contiene los datos de salida
        alcance: etiqueta con el alcance del estudio

    Returns:
         Un tupla de la forma (df_duracion, df_horas, df_probabilidad, df_tiempos, df_volumen, df_costes_ejecucion, df_costes_directos,
            df_costes_totales).

        * ``df_duracion``: Matriz con los resultados relacionados con los tiempos de ejecución de los trabajos.
        * ``df_horas``: Matriz con los resultados relacionados con los tiempos de parada de los trabajos
        * ``df_probabilidad``: Matriz con los resultados relacionados con la probabilidad de fallo y parada operativa
        * ``df_tiempos``: Matriz con los resultados relacionados con los tiempos de duracion de las paradas
        * ``df_volumen``: Matriz con los resultados relacionados con los volumenes ejecutados y perdidos durante la ejecución de los trabajos
        * ``df_costes_ejecucion``: Matriz con los resultados relacionados con los costes de ejecucion
        * ``df_costes_directos``: Matriz con los resultados relacionados con los costes directos
        * ``df_costes_totales``:Matriz con los resultados relacionados con los costes totales

    """

    # Lectura de las diferentes subfases a partir de archivo
    direct = os.path.join(ruta_de, 'sub_fases', n)
    fichero_sub_fases = os.path.join(direct, 'sub_fases.txt')
    fo = open(fichero_sub_fases, 'r')
    sub_fases = fo.readlines()

    subfases = []
    for val in sub_fases:
        val = val[: -5]
        subfases.append(val)

    idx_tramo = np.array(0)
    idx_subfase = np.array(0)

    for j in de_planta.index:
        for k in subfases:
            idx_tramo = np.vstack((idx_tramo, j))
            idx_subfase = np.vstack((idx_subfase, k))

    idx_tramo = np.delete(idx_tramo, 0)
    idx_subfase = np.delete(idx_subfase, 0)

    arrays = [idx_tramo, idx_subfase]

    columnas = ['t_ejecucion_tramo', 't_ini_subfase_teorico', 't_ini_subfase_real', 't_fin_subfase_teorico',
                't_fin_subfase_real', 't_ejecucion_subfase', 'n_horas_subfase_trabaja',
                'n_horas_subfase_trabaja_retrasada']

    df_tiempos = pd.DataFrame(np.random.randn(idx_tramo.size, 8), index=arrays, columns=columnas)

    cont = 0
    for j, _ in enumerate(estado_real_total):
        for k, _ in enumerate(estado_real_total[j].iterrows()):
            valores = estado_real_total[j].loc[estado_real_total[j].index[k], :]

            # Los convierto a enteros
            j = int(j)
            k = int(k)

            # Tiempo de ejecucion del tramo
            t = valores.size
            df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['t_ejecucion_tramo'] = t

            # Extraccion de la subfase protectora
            sf_pr = de_tramo_total[j].loc[de_tramo_total[j].index[k], 'subfase_protectora']
            # Si es nan es porque no tiene subfase protectora entonces sf_pr es ella misma
            if np.isnan(sf_pr):
                sf_pr = int(k)
            else:
                sf_pr = int(sf_pr)

            # Hora de finalizacion de cada subfase
            if k != (estado_real_total[j].shape[0] - 1):
                for l, _ in enumerate(vol_acumulado_total[j].loc[vol_acumulado_total[j].index[k], :]):
                    if (((vol_acumulado_total[j].loc[vol_acumulado_total[j].index[k], l] >= de_tramo_total[j].loc[de_tramo_total[j].index[k], 'vol_subfase']) | (
                        np.isnan(vol_acumulado_total[j].loc[vol_acumulado_total[j].index[k], l]))) & (
                            vol_acumulado_total[j].loc[vol_acumulado_total[j].index[sf_pr], l] >= de_tramo_total[j].loc[de_tramo_total[j].index[sf_pr], 'vol_subfase'])):
                        t_fin_rel = l
                        break

            else:
                t_fin_rel = valores.size

            # tiempo de finalizacion de la subfase real
            df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['t_fin_subfase_real'] = t_fin_rel + hora_inicio_tramos[j]

            # tiempo de finalizacion de la subfase teorico
            df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['t_fin_subfase_teorico'] = com_fin_teorico_total[j].loc[
                com_fin_teorico_total[j].index[k], 'fin_fase_teo']

            # Hora de inicio de cada subfase
            for l, _ in enumerate(vol_acumulado_total[j].loc[vol_acumulado_total[j].index[k], :]):
                if (((vol_acumulado_total[j].loc[vol_acumulado_total[j].index[k], l] == 0) & (vol_acumulado_total[j].loc[vol_acumulado_total[j].index[k], l + 1] > 0)) | (
                        vol_acumulado_total[j].loc[vol_acumulado_total[j].index[k], l] != 0)):
                    t_ini_rel = l
                    break

            # tiempo de inicio de la subfase real
            df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['t_ini_subfase_real'] = t_ini_rel + hora_inicio_tramos[j]

            # tiempo de inicio de la subfase teorico
            df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['t_ini_subfase_teorico'] = com_fin_teorico_total[j].loc[
                com_fin_teorico_total[j].index[k], 'com_fase_teo']

            # Duracion de cada subfase
            df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['t_ejecucion_subfase'] = df_tiempos.loc[idx_tramo[
                cont], idx_subfase[cont]]['t_fin_subfase_real'] - df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]][
                't_ini_subfase_real']

            cont = cont + 1

    # Número de horas que la subfase trabaja
    cont = 0

    for j, _ in enumerate(estado_real_total):
        for k, _ in enumerate(estado_real_total[j].iterrows()):
            valores = estado_real_total[j].loc[estado_real_total[j].index[k], df_tiempos.loc[idx_tramo[j], idx_subfase[k]][
                't_ini_subfase_real']:df_tiempos.loc[idx_tramo[j], idx_subfase[k]]['t_fin_subfase_real']]

            n_horas = valores.value_counts()

            if c.FASE_TRABAJA in n_horas:
                df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_trabaja'] = n_horas[c.FASE_TRABAJA]
            else:
                df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_trabaja'] = 0

            if c.FASE_TRABAJA_RETRASADA in n_horas:
                df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_trabaja_retrasada'] = n_horas[
                    c.FASE_TRABAJA_RETRASADA]
            else:
                df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_trabaja_retrasada'] = 0

            cont += 1

    # Guardado de resultados
    direct = os.path.join(ruta_ds, '1_tiempos_ejecucion_fase_construccion.html')
    df_tiempos.to_html(direct, sparsify=False)

    columnas = ['n_horas_subfase_no_trabaja_por_restriccion',
                'n_horas_subfase_no_trabaja_por_operatividad', 'n_horas_subfase_esta_protegiendo',
                'n_horas_subfase_esta_en_perdidas']

    df_horas = pd.DataFrame(np.random.randn(idx_tramo.size, 4), index=arrays, columns=columnas)

    # Número de horas que la subfase no trabaja
    cont = 0
    for j, _ in enumerate(estado_real_total):
        for k, _ in enumerate(estado_real_total[j].iterrows()):

            # De todos los valores de estado_real, para cada subfase me quedo con los que van desde el inicio real
            # de la subfase hasta el final real de la subfase
            valores = estado_real_total[j].loc[estado_real_total[j].index[k], df_tiempos.loc[idx_tramo[j], idx_subfase[k]][
                't_ini_subfase_teorico']:df_tiempos.loc[idx_tramo[j], idx_subfase[k]]['t_fin_subfase_real']]

            n_horas = valores.value_counts()

            if c.FASE_NO_TRABAJA_RESTRICCION in n_horas:
                df_horas.loc[idx_tramo[cont], idx_subfase[cont]][
                    'n_horas_subfase_no_trabaja_por_restriccion'] = n_horas[c.FASE_NO_TRABAJA_RESTRICCION]
            else:
                df_horas.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_no_trabaja_por_restriccion'] = 0

            if c.FASE_NO_TRABAJA_OPERATIVIDAD in n_horas:
                df_horas.loc[idx_tramo[cont], idx_subfase[cont]][
                    'n_horas_subfase_no_trabaja_por_operatividad'] = n_horas[c.FASE_NO_TRABAJA_OPERATIVIDAD]
            else:
                df_horas.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_no_trabaja_por_operatividad'] = 0

            if c.FASE_PROTEGIENDO in n_horas:
                df_horas.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_esta_protegiendo'] = n_horas[
                    c.FASE_PROTEGIENDO]
            else:
                df_horas.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_esta_protegiendo'] = 0

            if c.FASE_PERDIDAS in n_horas:
                df_horas.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_esta_en_perdidas'] = n_horas[
                    c.FASE_PERDIDAS]
            else:
                df_horas.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_esta_en_perdidas'] = 0

            cont += 1

    # Guardado de resultados
    direct = os.path.join(ruta_ds, '1_tiempos_parada_fase_construccion.html')
    df_horas.to_html(direct, sparsify=False)

    columnas = ['n_veces_perdidas', 'dur_minima_perdidas', 'dur_maxima_perdidas',
                'dur_media_perdidas', 'n_veces_operatividad', 'dur_minima_operatividad', 'dur_maxima_operatividad',
                'dur_media_operatividad', 'n_veces_proteccion', 'dur_minima_proteccion', 'dur_maxima_proteccion',
                'dur_media_proteccion']

    df_duracion = pd.DataFrame(np.random.randn(idx_tramo.size, 12), index=arrays, columns=columnas)

    columnas = ['volumen_ejecutado_teorico', 'volumen_ejecutado_real', 'volumen_minimo_perdidas_material',
                'volumen_maximo_perdidas_material', 'volumen_medio_perdidas_material',
                'volumen_total_perdidas_material']

    df_volumen = pd.DataFrame(np.random.randn(idx_tramo.size, 6), index=arrays, columns=columnas)

    # Número de paradas por operatividad, número de veces que se entra en perdidas y numero de veces que se
    # protege la obra
    cont = 0
    for j, _ in enumerate(estado_real_total):
        for k, _ in enumerate(estado_real_total[j].iterrows()):
            valores_orig = estado_real_total[j].loc[estado_real_total[j].index[k], df_tiempos.loc[idx_tramo[j], idx_subfase[k]][
                't_ini_subfase_teorico']:df_tiempos.loc[idx_tramo[j], idx_subfase[k]]['t_fin_subfase_real']]
            valores = valores_orig.reset_index(drop=True)

            ini_pro = []
            fin_pro = []
            ini_ope = []
            fin_ope = []
            ini_per = []
            fin_per = []

            for l, _ in enumerate(valores):

                if (l == 0):

                    if (valores[l] == c.FASE_PERDIDAS):
                        ini_per.append(l)

                    if (valores[l] == c.FASE_PROTEGIENDO):
                        ini_pro.append(l)

                    if (valores[l] == c.FASE_NO_TRABAJA_OPERATIVIDAD):
                        ini_ope.append(l)

                if ((l != (valores.shape[0] - 1)) & (l != 0)):

                    if ((valores[l] == c.FASE_PERDIDAS) & (
                            valores[l - 1] != c.FASE_PERDIDAS)):
                        ini_per.append(l)

                    elif ((valores[l] != c.FASE_PERDIDAS) & (
                            valores[l - 1] == c.FASE_PERDIDAS)):
                        fin_per.append(l)

                    if ((valores[l] == c.FASE_PROTEGIENDO) & (
                            valores[l - 1] != c.FASE_PROTEGIENDO)):
                        ini_pro.append(l)

                    elif ((valores[l] != c.FASE_PROTEGIENDO) & (
                            valores[l - 1] == c.FASE_PROTEGIENDO)):
                        fin_pro.append(l)

                    if ((valores[l] == c.FASE_NO_TRABAJA_OPERATIVIDAD) & (
                            valores[l - 1] != c.FASE_NO_TRABAJA_OPERATIVIDAD)):
                        ini_ope.append(l)

                    elif ((valores[l] != c.FASE_NO_TRABAJA_OPERATIVIDAD) & (
                            valores[l - 1] == c.FASE_NO_TRABAJA_OPERATIVIDAD)):
                        fin_ope.append(l)

                if (l == (valores.shape[0] - 1)):

                    if ((valores[l] == c.FASE_PERDIDAS)):
                        fin_per.append(l)

                    elif ((valores[l] != c.FASE_PERDIDAS) & (
                            valores[l - 1] == c.FASE_PERDIDAS)):
                            fin_per.append(l)

                    if ((valores[l] == c.FASE_PROTEGIENDO)):
                        fin_pro.append(l)

                    elif ((valores[l] != c.FASE_PROTEGIENDO) & (
                            valores[l - 1] == c.FASE_PROTEGIENDO)):
                            fin_pro.append(l)

                    if ((valores[l] == c.FASE_NO_TRABAJA_OPERATIVIDAD)):
                        fin_ope.append(l)

                    elif ((valores[l] != c.FASE_NO_TRABAJA_OPERATIVIDAD) & (
                            valores[l - 1] == c.FASE_NO_TRABAJA_OPERATIVIDAD)):
                            fin_ope.append(l)

            ini_per = np.array(ini_per)
            fin_per = np.array(fin_per)
            ini_ope = np.array(ini_ope)
            fin_ope = np.array(fin_ope)
            ini_pro = np.array(ini_pro)
            fin_pro = np.array(fin_pro)

            # Se extrae el número, la media, el maximo, el minimo y la moda de los tres
            n_veces_per = ini_per.size
            if n_veces_per == 0:
                dur_per = 0
                vol_min_per = 0
                vol_max_per = 0
                vol_media_per = 0
                vol_tot_per = 0
                dur_media_per = 0
                dur_max_per = 0
                dur_min_per = 0
            else:
                dur_per = (fin_per - ini_per)
                dur_media_per = np.mean(dur_per)
                dur_max_per = np.max(dur_per)
                dur_min_per = np.min(dur_per)
                vol_perdidas = np.array(0)

                # Hay que obtener los indices originales
                indices = valores_orig.index
                ini_per_orig = indices[ini_per]
                fin_per_orig = indices[fin_per]

                for pos, val in enumerate(ini_per_orig):
                    perdidas = vol_perdido_total[j].loc[vol_perdido_total[j].index[k], val:fin_per_orig[pos]].sum()
                    vol_perdidas = np.append(vol_perdidas, perdidas)
                vol_perdidas = np.delete(vol_perdidas, 0)
                vol_min_per = np.max(vol_perdidas)
                vol_max_per = np.min(vol_perdidas)
                vol_media_per = np.mean(vol_perdidas)
                vol_tot_per = vol_perdidas.sum()

            n_veces_ope = ini_ope.size
            if n_veces_ope == 0:
                dur_ope = 0
                dur_media_ope = 0
                dur_max_ope = 0
                dur_min_ope = 0
            else:
                dur_ope = (fin_ope - ini_ope)
                dur_media_ope = np.mean(dur_ope)
                dur_max_ope = np.max(dur_ope)
                dur_min_ope = np.min(dur_ope)

            n_veces_pro = ini_pro.size
            if n_veces_pro == 0:
                dur_pro = 0
                dur_media_pro = 0
                dur_max_pro = 0
                dur_min_pro = 0
            else:
                dur_pro = (fin_pro - ini_pro)
                dur_media_pro = np.mean(dur_pro)
                dur_max_pro = np.max(dur_pro)
                dur_min_pro = np.min(dur_pro)

            # Se almacenan los valores
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['n_veces_perdidas'] = n_veces_per
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_media_perdidas'] = dur_media_per
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_maxima_perdidas'] = dur_max_per
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_minima_perdidas'] = dur_min_per

            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['n_veces_operatividad'] = n_veces_ope
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_media_operatividad'] = dur_media_ope
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_maxima_operatividad'] = dur_max_ope
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_minima_operatividad'] = dur_min_ope

            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['n_veces_proteccion'] = n_veces_pro
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_media_proteccion'] = dur_media_pro
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_maxima_proteccion'] = dur_max_pro
            df_duracion.loc[idx_tramo[cont], idx_subfase[cont]]['dur_minima_proteccion'] = dur_min_pro

            df_volumen.loc[idx_tramo[cont], idx_subfase[cont]]['volumen_minimo_perdidas_material'] = vol_min_per
            df_volumen.loc[idx_tramo[cont], idx_subfase[cont]]['volumen_maximo_perdidas_material'] = vol_max_per
            df_volumen.loc[idx_tramo[cont], idx_subfase[cont]]['volumen_medio_perdidas_material'] = vol_media_per
            df_volumen.loc[idx_tramo[cont], idx_subfase[cont]]['volumen_total_perdidas_material'] = vol_tot_per

            # Volumen ejecutado teorico
            df_volumen.loc[idx_tramo[cont], idx_subfase[cont]][
                'volumen_ejecutado_teorico'] = de_tramo_total[j].loc[de_tramo_total[j].index[k], 'vol_subfase']
            # Volumen ejecutado real
            vol_ejecutado_tramo = vol_ejecutado_total[j].loc[vol_ejecutado_total[j].index[k], :]
            df_volumen.loc[idx_tramo[cont], idx_subfase[cont]]['volumen_ejecutado_real'] = vol_ejecutado_tramo[vol_ejecutado_tramo > 0].sum()

            cont = cont + 1

    # Guardado de resultados
    direct = os.path.join(ruta_ds, '2_duracion_paradas_fase_construccion.html')
    df_duracion.to_html(direct, sparsify=False)

    # Guardado de resultados
    direct = os.path.join(ruta_ds, '3_volumen_perdidas_fase_construccion.html')
    df_volumen.to_html(direct, sparsify=False)

    # Probabilidad de fallo (perdidas) y de parada operativa
    columnas = ['probabilidad_de_fallo', 'probabilidad_parada_operativa']

    df_probabilidad = pd.DataFrame(np.random.randn(idx_tramo.size, 2), index=arrays, columns=columnas)

    cont = 0
    for j, _ in enumerate(estado_real_total):
        for k, _ in enumerate(estado_real_total[j].iterrows()):

            dur_subfase = df_tiempos.loc[idx_tramo[cont], idx_subfase[cont]]['t_ejecucion_subfase']
            n_horas_perdidas = df_horas.loc[idx_tramo[cont], idx_subfase[cont]]['n_horas_subfase_esta_en_perdidas']
            n_horas_operatividad = df_horas.loc[idx_tramo[cont], idx_subfase[cont]][
                'n_horas_subfase_no_trabaja_por_operatividad']

            prob_fallo = n_horas_perdidas/dur_subfase
            prob_parada_operativa = n_horas_operatividad/dur_subfase

            df_probabilidad.loc[idx_tramo[cont], idx_subfase[cont]][
                'probabilidad_de_fallo'] = prob_fallo
            df_probabilidad.loc[idx_tramo[cont], idx_subfase[cont]][
                'probabilidad_parada_operativa'] = prob_parada_operativa

            cont = cont + 1

            # Guardado de resultados
            direct = os.path.join(ruta_ds, '4_probabilidad_fallo_parada_fase_construccion.html')
            df_probabilidad.to_html(direct, sparsify=False)

    # if alcance != 'EA':
    # Reestructuro las matrices de costes para mostrar las salidas para cada tramo
    columnas = ['c_maquinaria_total', 'c_mano_obra_total', 'c_adicional_total', 'c_ejecucion_total']
    df_costes_ejecucion = pd.DataFrame(np.random.randn(idx_tramo.size, 4), index=arrays, columns=columnas)

    columnas = ['c_materiales_total', 'c_mantenimiento_total', 'c_proteccion_total', 'c_ejecucion_total',
                'c_directos_total']
    df_costes_directos = pd.DataFrame(np.random.randn(idx_tramo.size, 5), index=arrays, columns=columnas)

    columnas = ['c_directos_total', 'c_indirectos_total', 'c_perdidas_total', 'c_total']
    df_costes_totales = pd.DataFrame(np.random.randn(idx_tramo.size, 4), index=arrays, columns=columnas)

    cont = 0
    for j, _ in enumerate(estado_real_total):
        for k, _ in enumerate(estado_real_total[j].iterrows()):
            df_costes_ejecucion.loc[idx_tramo[cont], idx_subfase[cont]][:] = costes_ejecc_sf_total_total[j].loc[costes_ejecc_sf_total_total[j].index[k], :]
            df_costes_directos.loc[idx_tramo[cont], idx_subfase[cont]][:] = costes_directos_sf_total_total[j].loc[costes_directos_sf_total_total[j].index[k], :]
            df_costes_totales.loc[idx_tramo[cont], idx_subfase[cont]][:] = costes_sf_total_total[j].loc[costes_sf_total_total[j].index[k], :]

            cont = cont + 1

    # Guardado de resultados
    direct = os.path.join(ruta_ds, '5_costes_ejecucion_fase_construccion.html')
    df_costes_ejecucion.to_html(direct, sparsify=False)

    # Guardado de resultados
    direct = os.path.join(ruta_ds, '5_costes_directos_fase_construccion.html')
    df_costes_directos.to_html(direct, sparsify=False)

    # Guardado de resultados
    direct = os.path.join(ruta_ds, '5_costes_totales_fase_construccion.html')
    df_costes_totales.to_html(direct, sparsify=False)

    return (df_duracion, df_horas, df_probabilidad, df_tiempos, df_volumen, df_costes_ejecucion, df_costes_directos,
            df_costes_totales)


def calcula_rendimientos(de_tramo, fase, rend):
    rend_fase = []

    if de_tramo.loc[de_tramo.index[fase], 'rend_uds_obra'] == 'min':
        rend_fase = rend.min()
    elif de_tramo.loc[de_tramo.index[fase], 'rend_uds_obra'] == 'sum':
        tiempo = [1 / x for x in rend]
        tiempo_total = sum(tiempo)
        rend_fase = (1 / tiempo_total)
    return rend_fase
