import numpy as np

import logging

from . import constantes as c

from .calculos import actualiza_matriz
from .calculos import volumen_fase_no_trabaja
from .calculos import actualiza_longitud_protegida
from .calculos import volumen_fase_perdidas
from .calculos import volumen_fase_trabajo_retrasada
from .calculos import volumen_fase_trabajo
from .calculos import restitucion_volumen_fase_no_trabaja_restriccion

from .comprobaciones import comprueba_si_fase_tiene_restriccion_de_avance
from .clasificaciones import clasifica_si_fase_tiene_restriccion_de_avance


def fase_no_trabaja(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado):
    """Funcion que calcula el volumen ejecutado y longitud avanzada para una fase constructiva clasificada a nivel III
       como fase_no_trabaja.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Si el volumen ejecutado es mayor o igual al volumen total de la subfase
    if vol_ejecutado.iloc[fase, :].sum() >= de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase']:

        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
            fase) + ' Nivel IV: Fase Acabada')

        # HINTS: La verificacion concluye que la subfase es una FASE_ACABADA.
        clasificacion_3 = c.FASE_ACABADA
        estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)

    # Si el volumen ejecutado es menor que el volumen total de la subfase
    else:

        # Se calculan las volumenes (0 en este caso) de una subfase que no trabaja
        (vol_ejecutado, longitudes) = volumen_fase_no_trabaja(
            fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes)

        # HINTS: La verificacion concluye que la subfase es una FASE_NO_TRABAJA.
        clasificacion_3 = c.FASE_NO_TRABAJA
        estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Trabaja')

    return(vol_ejecutado, longitudes)


def fase_no_toca_trabajar(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado):
    """Funcion que calcula el volumen ejecutado y longitud avanzada para una fase constructiva clasificada a nivel III
       como fase_no_toca_trabajar.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Si el volumen ejecutado es mayor o igual al volumen total de la subfase
    if vol_ejecutado.iloc[fase, :].sum() >= de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase']:

        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
            fase) + ' Nivel IV: Fase Acabada')

        # HINTS: La verificacion concluye que la subfase es una FASE_ACABADA.
        clasificacion_3 = c.FASE_ACABADA
        estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)

    # Si el volumen ejecutado es menor que el volumen total de la subfase
    else:

        # Se calculan las volumenes (0 en este caso) de una subfase que no trabaja
        (vol_ejecutado, longitudes) = volumen_fase_no_trabaja(
            fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes)

        # HINTS: La verificacion concluye que la subfase es una FASE_NO_TOCA_TRABAJAR.
        clasificacion_3 = c.FASE_NO_TOCA_TRABAJAR
        estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Toca Trabaja')

    return(vol_ejecutado, longitudes)


def fase_perdidas(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado, cont_t_arranque, eq_danno_fases,
                  clima, vol_perdido):
    """Funcion que calcula el volumen ejecutado y longitud avanzada para una fase constructiva clasificada a nivel III
       como fase_perdidas.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        cont_t_arranque: Contador utilizado para considerar los tiempos de arranque, posicionamiento, etc que la
            maquinaria necesita antes de empezar a trabajar.

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Se calculan las perdidas
    (vol_ejecutado, vol_perdido, longitudes) = volumen_fase_perdidas(
        fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, vol_perdido, longitudes, eq_danno_fases,
        clima, de_tramo_0.loc[de_tramo_0.index[fase], 'reparacion_inmediata'])

    # HINTS: La verificacion concluye que la subfase es una FASE_PERDIDAS.
    clasificacion_3 = c.FASE_PERDIDAS
    estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase Perdidas')

    # Cuando aparece un temporal me llevo la maquinaria de la obra. Pongo el contador a de tiempo de arranque a 0
    cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] = 0

    return(vol_ejecutado, vol_perdido, longitudes)


def fase_protegiendo(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado, cont_t_arranque,
                     cont_pro_h_fijas):
    """Funcion que calcula el volumen ejecutado y longitud avanzada para una fase constructiva clasificada a nivel III
       como fase_protegiendo.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        cont_t_arranque: Contador utilizado para considerar los tiempos de arranque, posicionamiento, etc que la
            maquinaria necesita antes de empezar a trabajar.

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Se avanza la longitud protegida de la subfase
    (longitudes, cont_pro_h_fijas) = actualiza_longitud_protegida(fase, de_tramo_0.loc[de_tramo_0.index[fase], 'n_horas_protecc_metro'],
                                                                  longitudes, de_tramo_0, cont_pro_h_fijas)

    # Se calculan las volumenes (0 en este caso) de una subfase que no trabaja
    (vol_ejecutado, longitudes) = volumen_fase_no_trabaja(
        fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes)

    # HINTS: La verificacion concluye que la subfase es una FASE_PROTEGIENDO.
    clasificacion_3 = c.FASE_PROTEGIENDO
    estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase Protegiendo')

    # Cuando aparece un temporal me llevo la maquinaria de la obra. Pongo el contador a 0
    cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] = 0

    return(vol_ejecutado, longitudes, cont_pro_h_fijas)


def fase_no_trabaja_operatividad(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado):
    """Funcion que calcula el volumen ejecutado y longitud avanzada para una fase constructiva clasificada a nivel III
       como fase_no_trabaja_operatividad.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Si el volumen ejecutado es mayor o igual al volumen total de la subfase
    if vol_ejecutado.iloc[fase, :].sum() >= de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase']:

        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
            fase) + ' Nivel IV: Fase Acabada')

        # HINTS: La verificacion concluye que la subfase es una FASE_ACABADA.
        clasificacion_3 = c.FASE_ACABADA
        estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)

    # Si el volumen ejecutado es menor que el volumen total de la subfase
    else:

        # Se calculan las volumenes (0 en este caso) de una subfase que no trabaja
        (vol_ejecutado, longitudes) = volumen_fase_no_trabaja(
            fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes)

        # HINTS: La verificacion concluye que la subfase es una FASE_NO_TRABAJA_OPERATIVIDAD.
        clasificacion_3 = c.FASE_NO_TRABAJA_OPERATIVIDAD
        estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Toca Trabaja Operatividad')

    return(vol_ejecutado, longitudes)


def fase_trabaja_retrasada(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado, hora_labor,
                           cont_t_arranque, restricciones_fases, dia_labor):
    """Funcion que calcula el volumen ejecutado y longitud avanzada para una fase constructiva clasificada a nivel III
       como fase_trabaja_retrasada.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        hora_labor: Contador utilizado para contar las horas desde 0 hasta 24 para poder decidir si la fase se
            encuentra dentro de las horas laborables dentro del dia o no.
        cont_t_arranque: Contador utilizado para considerar los tiempos de arranque, posicionamiento, etc que la
            maquinaria necesita antes de empezar a trabajar.

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Si el volumen ejecutado es mayor o igual al volumen total de la subfase
    if vol_ejecutado.iloc[fase, :].sum() >= de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase']:

        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
            fase) + ' Nivel IV: Fase Acabada')

        # HINTS: La verificacion concluye que la subfase es una FASE_ACABADA.
        clasificacion_3 = c.FASE_ACABADA
        estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)

        # Cuando acaba la fase me llevo la maquinaria de la obra. Pongo el contador a 0
        cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] = 0

    # Si el volumen ejecutado es menor que el volumen total de la subfase
    else:

        # Si la hora es una hora laborable y el tiempo de arranque ha superado el tiempo de arranque necesario de la
        # subfase y el dia es un dia laborable
        if ((hora_labor >= 0) & (hora_labor <= de_tramo_0.loc[de_tramo_0.index[fase], 'h_lab_dia_fase']) & (
                cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] >= de_tramo_0.loc[de_tramo_0.index[fase], 't_arranque_fase']) & (
                (dia_labor >= 0) & (dia_labor <= de_tramo_0.loc[de_tramo_0.index[fase], 'dia_lab_sem_fase']))):

            # Se calculan las volumenes de la subfase que trabaja retrasada
            (vol_ejecutado, longitudes) = volumen_fase_trabajo_retrasada(
                fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes,
                de_tramo_0.loc[de_tramo_0.index[fase], 'rendimiento'])

            # Calculado el volumen se comprueba si la subfase tiene alguna restriccion de avance con respecto al resto
            # de las subfases.
            (restriccion, tiene_restriccion) = comprueba_si_fase_tiene_restriccion_de_avance(fase, restricciones_fases)
            (puede_trabajar) = clasifica_si_fase_tiene_restriccion_de_avance(de_tramo_0, fase, estado_real, hora,
                                                                             longitudes, restriccion,
                                                                             tiene_restriccion)

            # Si la subfase es distinta de la 0
            if (fase != 0):
                # Si la subfase tiene alguna restriccion de avance y no puede trabajar
                if not puede_trabajar:

                    # Se restan los volumenes y longitudes ejecutados
                    (vol_ejecutado, longitudes) = restitucion_volumen_fase_no_trabaja_restriccion(
                        fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes)

                    # HINTS: La verificacion concluye que la subfase es una FASE_NO_TRABAJA_RESTRICCION.
                    clasificacion_3 = c.FASE_NO_TRABAJA_RESTRICCION
                    estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
                    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                        fase) + ' Nivel III: Fase No Toca Trabaja Rrestriccion')

                # Si la subfase no tiene ninguna restriccion de avance y si puede trabajar
                else:

                    # HINTS: La verificacion concluye que la subfase es una FASE_TRABAJA_RETRASADA.
                    clasificacion_3 = c.FASE_TRABAJA_RETRASADA
                    estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
                    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                        fase) + ' Nivel III: Fase Trabaja retrasada')

            # Si la subfase es distinta de la 0
            else:

                # HINTS: La verificacion concluye que la subfase es una FASE_TRABAJA_RETRASADA.
                clasificacion_3 = c.FASE_TRABAJA_RETRASADA
                estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
                logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                            fase) + ' Nivel III: Fase Trabaja retrasada')

        # Si la hora es una hora no laborable o el tiempo de arranque no ha superado el tiempo de arranque necesario
        # de la subfase o si el dia es un dia no laborable
        else:

            # HINTS: La verificacion concluye que la subfase es una FASE_NO_TRABAJA.
            (vol_ejecutado, longitudes) = fase_no_trabaja(
                fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado)

            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                fase) + ' Nivel IV: Fase No Trabaja (Horas Laborables y/o Tiempo Arranque)')

        # Se avanza el contador de tiempo de arranque de la fase
        cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] += 1

    return(vol_ejecutado, longitudes)


def fase_trabaja(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado, hora_labor, cont_t_arranque,
                 restricciones_fases, dia_labor):
    """Funcion que calcula el volumen ejecutado y longitud avanzada para una fase constructiva clasificada a nivel III
       como fase_trabaja.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        hora_labor: Contador utilizado para contar las horas desde 0 hasta 24 para poder decidir si la fase se
            encuentra dentro de las horas laborables dentro del dia o no.
        cont_t_arranque: Contador utilizado para considerar los tiempos de arranque, posicionamiento, etc que la
            maquinaria necesita antes de empezar a trabajar.

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """
    # Si el volumen ejecutado es mayor o igual al volumen total de la subfase
    if vol_ejecutado.iloc[fase, :].sum() >= de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase']:

        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
            fase) + ' Nivel IV: Fase Acabada')

        # HINTS: La verificacion concluye que la subfase es una FASE_ACABADA.
        clasificacion_3 = c.FASE_ACABADA
        estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)

        # Cuando acaba la fase me llevo la maquinaria de la obra. Pongo el contador a 0
        cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] = 0

    # Si el volumen ejecutado es menor que el volumen total de la subfase
    else:

        # Si la hora es una hora laborable y el tiempo de arranque ha superado el tiempo de arranque necesario de la
        # subfase y el dia es un dia laborable
        if ((hora_labor >= 0) & (hora_labor <= de_tramo_0.loc[de_tramo_0.index[fase], 'h_lab_dia_fase']) & (
                cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] >= de_tramo_0.loc[de_tramo_0.index[fase], 't_arranque_fase']) & (
                (dia_labor >= 0) & (dia_labor <= de_tramo_0.loc[de_tramo_0.index[fase], 'dia_lab_sem_fase']))):

            # Se calculan las volumenes de la subfase que trabaja
            (vol_ejecutado, longitudes) = volumen_fase_trabajo(
                fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes,
                de_tramo_0.loc[de_tramo_0.index[fase], 'rendimiento'])

            # Calculado el volumen se comprueba si la subfase tiene alguna restriccion de avance con respecto al resto
            # de las subfases.
            (restriccion, tiene_restriccion) = comprueba_si_fase_tiene_restriccion_de_avance(fase, restricciones_fases)
            (puede_trabajar) = clasifica_si_fase_tiene_restriccion_de_avance(de_tramo_0, fase, estado_real, hora,
                                                                             longitudes, restriccion,
                                                                             tiene_restriccion)

            # Si la subfase es distinta de la 0
            if (fase != 0):
                # Si la subfase tiene alguna restriccion de avance y no puede trabajar
                if not puede_trabajar:

                    # Se restan los volumenes y longitudes ejecutados
                    (vol_ejecutado, longitudes) = restitucion_volumen_fase_no_trabaja_restriccion(
                        fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes)

                    # HINTS: La verificacion concluye que la subfase es una FASE_NO_TRABAJA_RESTRICCION.
                    clasificacion_3 = c.FASE_NO_TRABAJA_RESTRICCION
                    estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
                    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                        fase) + ' Nivel III: Fase No Trabaja Restricción')

                # Si la subfase no tiene ninguna restriccion de avance y si puede trabajar
                else:

                    # HINTS: La verificacion concluye que la subfase es una FASE_TRABAJA
                    clasificacion_3 = c.FASE_TRABAJA
                    estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
                    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                        fase) + ' Nivel III: Fase Trabaja')

            # Si la subfase es la 0
            else:
                # HINTS: La verificacion concluye que la subfase es una FASE_TRABAJA
                clasificacion_3 = c.FASE_TRABAJA
                estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
                logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                        fase) + ' Nivel III: Fase Trabaja')

        # Si la hora es una hora no laborable o el tiempo de arranque no ha superado el tiempo de arranque necesario
        # de la subfase o si el dia es un dia no laborable
        else:

            # HINTS: La verificacion concluye que la subfase es una FASE_NO_TRABAJA.
            (vol_ejecutado, longitudes) = fase_no_trabaja(
                fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado)

            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                fase) + ' Nivel IV: Fase No Trabaja (Horas Laborables y/o Tiempo Arranque)')

        # Se avanza el contador de tiempo de arranque de la fase
        cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] += 1

    return(vol_ejecutado, longitudes)


def fase_parada_invernal(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado, cont_t_arranque, avance_real,
                         eq_danno_fases):
    """Funcion que calcula el volumen ejecutado y longitud avanzada para una fase constructiva clasificada a nivel III
       como fase_perdidas.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        cont_t_arranque: Contador utilizado para considerar los tiempos de arranque, posicionamiento, etc que la
            maquinaria necesita antes de empezar a trabajar.

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # De momento lo dejamos como fase no trabaja
    (vol_ejecutado, longitudes) = volumen_fase_no_trabaja(
        fase, hora, de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'], vol_ejecutado, longitudes)

    # Se actualiza la matriz de avance real
    clasificacion_2 = c.FASE_PARADA_INVERNAL
    avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    # Se actualiza la matriz de estado real
    clasificacion_3 = c.FASE_NO_TRABAJA
    estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)

    # Cuando aparece un temporal me llevo la maquinaria de la obra. Pongo el contador a 0
    cont_t_arranque.loc[cont_t_arranque.index[fase], 't_arranque'] = 0

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
        fase) + ' PARADA INVERNAL')

    return(vol_ejecutado, longitudes)
