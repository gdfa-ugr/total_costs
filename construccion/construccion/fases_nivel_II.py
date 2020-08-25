import logging

from . import constantes as c

from .clasificacion_fase_II_fase_III import clasificacion_fase_II_fase_III_si_toca_trabajar
from .clasificacion_fase_II_fase_III import clasificacion_fase_III_si_deja_de_proteger
from .clasificacion_fase_II_fase_III import clasificacion_fase_III_si_deja_de_proceso_proteccion
from .clasificacion_fase_II_fase_III import clasificacion_fase_II_fase_III_umbral_dannos

from .calculos import actualiza_matriz

from .fases_nivel_III import fase_no_trabaja


def fase_sin_alerta_no_comenzada(hora, plan_avance, fase, vol_ejecutado, de_tramo_0, avance_real, clima,
                                 estado_real, longitudes, clasificacion_2, hora_labor, cont_t_arranque,
                                 hora_acumulada, com_fin_teorico, eq_danno_fases, vol_perdido,
                                 restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion para una fase constructiva clasificada como fase_sin_alerta_no_comenzada que llama a la funcion
    clasificacion_fase_II_fase_III_si_toca_trabajar para iniciar la clasificacion a nivel III.

    Args:
        hora: Hora (h)
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
        fase: Fase constructiva
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        clasificacion_2: Clasificacion de la fase a nivel II.
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

    # Se llama a la funcion de clasificacion para pasar de fases_nivel_II a fases_nivel_III.
    # Si la subfase se clasifica como sin alerta y no comenzada se comprueba si a la subfase le toca trabajar.
    (vol_ejecutado, vol_perdido, longitudes,
     cont_pro_h_fijas) = clasificacion_fase_II_fase_III_si_toca_trabajar(fase, hora, de_tramo_0,
                                                                         vol_ejecutado, avance_real,
                                                                         longitudes, estado_real, clima,
                                                                         plan_avance, clasificacion_2,
                                                                         hora_labor, cont_t_arranque,
                                                                         hora_acumulada, com_fin_teorico,
                                                                         eq_danno_fases, vol_perdido,
                                                                         restricciones_fases, dia_labor,
                                                                         cont_pro_h_fijas)

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def fase_sin_alerta_protegida_estructura(hora, plan_avance, fase, vol_ejecutado, de_tramo_0, avance_real, clima,
                                         estado_real, longitudes, hora_labor, cont_t_arranque, hora_acumulada,
                                         com_fin_teorico, eq_danno_fases, vol_perdido, restricciones_fases, dia_labor,
                                         cont_pro_h_fijas):
    """Funcion para una fase constructiva clasificada como fase_sin_alerta_no_comenzada que llama a la funcion
    clasificacion_fase_II_fase_III_si_toca_trabajar para iniciar la clasificacion a nivel III.

    Args:
        hora: Hora (h)
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
        fase: Fase constructiva
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        clasificacion_2: Clasificacion de la fase a nivel II.
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

    # Se llama a la funcion de clasificacion para pasar de fases_nivel_II a fases_nivel_III.
    # Si la subfase se clasifica como sin alerta y protegida por estructura se comprueba si la subfase puede
    # dejar de estar protegida y empezar a trabajar
    (vol_ejecutado, vol_perdido, longitudes,
     cont_pro_h_fijas) = clasificacion_fase_III_si_deja_de_proteger(fase, hora, de_tramo_0, clima,
                                                                    longitudes, vol_ejecutado, estado_real,
                                                                    avance_real, plan_avance, hora_labor,
                                                                    cont_t_arranque, hora_acumulada,
                                                                    com_fin_teorico, eq_danno_fases,
                                                                    vol_perdido, restricciones_fases, dia_labor,
                                                                    cont_pro_h_fijas)

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def fase_sin_alerta_en_proceso_proteccion(hora, plan_avance, fase, vol_ejecutado, de_tramo_0, avance_real, clima,
                                          estado_real, longitudes, clasificacion_2, hora_labor, cont_t_arranque,
                                          hora_acumulada, com_fin_teorico, eq_danno_fases, vol_perdido,
                                          restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion para una fase constructiva clasificada como fase_sin_alerta_en_proceso_proteccion que llama a la funcion
    clasificacion_fase_III_si_deja_de_proceso_proteccion para iniciar la clasificacion a nivel III.

    Args:
        hora: Hora (h)
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
        fase: Fase constructiva
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        clasificacion_2: Clasificacion de la fase a nivel II.
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

    # Se llama a la funcion de clasificacion para pasar de fases_nivel_II a fases_nivel_III.
    # Si la subfase se clasifica como sin alerta y en proceso de proteccion se comprueba si la subfase puede
    # dejar de estar en proceso de proteccion y empezar a trabajar
    (vol_ejecutado, vol_perdido, longitudes,
     cont_pro_h_fijas) = clasificacion_fase_III_si_deja_de_proceso_proteccion(fase, hora, de_tramo_0,
                                                                              vol_ejecutado, avance_real,
                                                                              longitudes, estado_real, clima,
                                                                              plan_avance, clasificacion_2,
                                                                              hora_labor, cont_t_arranque,
                                                                              hora_acumulada, com_fin_teorico,
                                                                              eq_danno_fases, vol_perdido,
                                                                              restricciones_fases, dia_labor,
                                                                              cont_pro_h_fijas)

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def fase_sin_alerta_sin_proteccion(hora, plan_avance, fase, vol_ejecutado, de_tramo_0, avance_real, clima,
                                   estado_real, longitudes, clasificacion_2, hora_labor, cont_t_arranque,
                                   hora_acumulada, com_fin_teorico, eq_danno_fases, vol_perdido,
                                   restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion para una fase constructiva clasificada como fase_sin_alerta_sin_proteccion que llama a la funcion
    clasificacion_fase_II_fase_III_si_toca_trabajar para iniciar la clasificacion a nivel III.

    Args:
        hora: Hora (h)
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
        fase: Fase constructiva
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        clasificacion_2: Clasificacion de la fase a nivel II.
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

    # Se llama a la funcion de clasificacion para pasar de fases_nivel_II a fases_nivel_III.
    # Si la subfase se clasifica como sin alerta y sin proteccion se comprueba si a la subfase le toca trabajar
    (vol_ejecutado, vol_perdido, longitudes,
     cont_pro_h_fijas) = clasificacion_fase_II_fase_III_si_toca_trabajar(fase, hora, de_tramo_0,
                                                                         vol_ejecutado, avance_real,
                                                                         longitudes, estado_real, clima,
                                                                         plan_avance, clasificacion_2,
                                                                         hora_labor, cont_t_arranque,
                                                                         hora_acumulada, com_fin_teorico,
                                                                         eq_danno_fases, vol_perdido,
                                                                         restricciones_fases, dia_labor,
                                                                         cont_pro_h_fijas)

    # Actualizo valor de la matriz de avance real para el dia actual
    clasificacion_2 = c.FASE_SIN_PROTECCION
    avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def fase_en_alerta_no_comenzada(
                                hora, fase, clasificacion_2, avance_real, estado_real, de_tramo_0, longitudes,
                                vol_ejecutado):
    """Funcion para una fase constructiva clasificada como fase_en_alerta_no_comenzada que automaticamente clasifica
    la fase a nivel III como fase_no_trabaja.

    Args:
        hora: Hora (h)
        fase: Fase constructiva
        clasificacion_2: Clasificacion de la fase a nivel II.
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Si la subfase se clasifica como en alerta y no comenzada se actualiza el estado en el dataframe de avance_real
    # pero la subfase no se mueve de su estado puesto que se encuentra en alerta
    avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Trabaja')

    # HINTS: La verificacion concluye que la fase_no_trabaja trabajar y se llama a la funcion
    # fase_no_trabaja
    (vol_ejecutado, longitudes) = fase_no_trabaja(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado)

    return (vol_ejecutado, longitudes)


def fase_en_alerta_protegida_estructura(
                                hora, fase, clasificacion_2, avance_real, estado_real, de_tramo_0, longitudes,
                                vol_ejecutado):
    """Funcion para una fase constructiva clasificada como fase_en_alerta_protegida_estructura que automaticamente
    clasifica la fase a nivel III como fase_no_trabaja.

    Args:
        hora: Hora (h)
        fase: Fase constructiva
        clasificacion_2: Clasificacion de la fase a nivel II.
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)

    Returns:
         Un tupla de la forma (vol_ejecutado, longitudes).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Si la subfase se clasifica como en alerta y protegida por estructura se actualiza el estado en el
    # dataframe de avance_real pero la subfase no se mueve de su estado puesto que se encuentra en alerta
    avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Trabaja')

    # HINTS: La verificacion concluye que la fase_no_trabaja trabajar y se llama a la funcion
    # fase_no_trabaja
    (vol_ejecutado, longitudes) = fase_no_trabaja(fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado)

    return (vol_ejecutado, longitudes)


def fase_en_alerta_en_proceso_proteccion(
                                hora, fase, clasificacion_2, avance_real, estado_real, de_tramo_0, longitudes,
                                vol_ejecutado, clima, hora_labor, cont_t_arranque, hora_acumulada, eq_danno_fases,
                                vol_perdido, restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion para una fase constructiva clasificada como fase_en_alerta_en_proceso_proteccion que llama a la funcion
    clasificacion_fase_II_fase_III_umbral_dannos para iniciar la clasificacion a nivel III.

    Args:
        hora: Hora (h)
        fase: Fase constructiva
        clasificacion_2: Clasificacion de la fase a nivel II.
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
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

    clasificacion_2 = c.FASE_EN_PROCESO_PROTECCION
    clasificacion_3 = c.FASE_PROTEGIENDO

    # Si la subfase se clasifica como en alerta y en proceso de proteccion se actualiza el estado en el
    # dataframe de avance_real y se comprueba si la longitud desprotegida de la subfase sufre dannos
    avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    (vol_ejecutado, vol_perdido, longitudes,
     cont_pro_h_fijas) = clasificacion_fase_II_fase_III_umbral_dannos(fase, hora, clasificacion_3,
                                                                      de_tramo_0, clima, longitudes,
                                                                      vol_ejecutado, estado_real,
                                                                      avance_real,
                                                                      clasificacion_2, hora_labor,
                                                                      cont_t_arranque, hora_acumulada,
                                                                      eq_danno_fases, vol_perdido,
                                                                      restricciones_fases, dia_labor,
                                                                      cont_pro_h_fijas)

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def fase_en_alerta_sin_proteccion(
                                hora, fase, clasificacion_2, avance_real, estado_real, de_tramo_0, longitudes,
                                vol_ejecutado, clima, plan_avance, hora_labor, cont_t_arranque, hora_acumulada,
                                com_fin_teorico, eq_danno_fases, vol_perdido, restricciones_fases, dia_labor,
                                cont_pro_h_fijas):
    """Funcion para una fase constructiva clasificada como fase_en_alerta_sin_proteccion que llama a las funciones
    clasificacion_fase_II_fase_III_umbral_dannos y clasificacion_fase_II_fase_III_si_toca_trabajar
    para iniciar la clasificacion a nivel III.

    Args:
        hora: Hora (h)
        fase: Fase constructiva
        clasificacion_2: Clasificacion de la fase a nivel II.
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
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

    # Si la subfase se clasifica como en alerta y sin proteccion se comprueba si el usuario toma la decisión de
    # proteger o no. Si el usuario no marca la opcion de PROTEGER:
    if de_tramo_0.loc[de_tramo_0.index[fase], 'decision_proteger'] == 1:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase en Proceso de Proteccion')

        # La subfase pasa a estado de EN_PROCESO_PROTECCION
        clasificacion_2 = c.FASE_EN_PROCESO_PROTECCION
        clasificacion_3 = c.FASE_PROTEGIENDO

        # Se comprueba si la longitud desprotegida de la subfase sufre dannos
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = clasificacion_fase_II_fase_III_umbral_dannos(fase, hora, clasificacion_3,
                                                                          de_tramo_0, clima, longitudes,
                                                                          vol_ejecutado, estado_real,
                                                                          avance_real,
                                                                          clasificacion_2, hora_labor,
                                                                          cont_t_arranque, hora_acumulada,
                                                                          eq_danno_fases, vol_perdido,
                                                                          restricciones_fases, dia_labor,
                                                                          cont_pro_h_fijas)
    # Si el usuario marca la opcion de NO PROTEGER:
    elif de_tramo_0.loc[de_tramo_0.index[fase], 'decision_proteger'] == 0:
        clasificacion_2 = c.FASE_SIN_PROTECCION

        # Se comprueba si a la subfase le toca trabajar
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = clasificacion_fase_II_fase_III_si_toca_trabajar(fase, hora, de_tramo_0,
                                                                             vol_ejecutado, avance_real,
                                                                             longitudes, estado_real, clima,
                                                                             plan_avance, clasificacion_2,
                                                                             hora_labor, cont_t_arranque,
                                                                             hora_acumulada, com_fin_teorico,
                                                                             eq_danno_fases, vol_perdido,
                                                                             restricciones_fases, dia_labor,
                                                                             cont_pro_h_fijas)

    else:
        logging.error('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Fase en Alerta Sin Proteccion')

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)
