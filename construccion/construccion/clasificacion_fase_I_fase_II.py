import logging

from . import constantes as c

from .comprobaciones import comprueba_valor_anterior

from .clasificaciones import clasifica_fase_en_funcion_valor_anterior

from .fases_nivel_II import fase_sin_alerta_no_comenzada
from .fases_nivel_II import fase_sin_alerta_en_proceso_proteccion
from .fases_nivel_II import fase_sin_alerta_protegida_estructura
from .fases_nivel_II import fase_sin_alerta_sin_proteccion
from .fases_nivel_II import fase_en_alerta_no_comenzada
from .fases_nivel_II import fase_en_alerta_en_proceso_proteccion
from .fases_nivel_II import fase_en_alerta_protegida_estructura
from .fases_nivel_II import fase_en_alerta_sin_proteccion


def clasificacion_fase_I_fase_II_sin_alerta(fase, hora, avance_real, vol_ejecutado, de_tramo_0, clima, estado_real,
                                            longitudes, plan_avance, hora_labor, cont_t_arranque, hora_acumulada,
                                            com_fin_teorico, eq_danno_fases, vol_perdido, restricciones_fases,
                                            dia_labor, cont_pro_h_fijas):
    """Funcion que clasifica a nivel II la fase constructiva sin alerta en una fase no comenzada, protegida por
    estructura, en proceso de proteccion y sin proteccion.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
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

    # Se clasifica la subfase en funcion del valor anterior
    comprobacion = comprueba_valor_anterior(fase, hora, avance_real)
    clasificacion_2 = clasifica_fase_en_funcion_valor_anterior(comprobacion)

    # Si el valor anterior de la subfase era FASE_NO_COMENZADA o FASE_PARADA_INVERNAL
    if ((clasificacion_2 == c.FASE_NO_COMENZADA) | (clasificacion_2 == c.FASE_PARADA_INVERNAL)):
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase No Comenzada')

        # Se llama a la funcion de fase_sin_alerta_no_comenzada
        (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas) = fase_sin_alerta_no_comenzada(
            hora, plan_avance, fase, vol_ejecutado, de_tramo_0, avance_real, clima, estado_real, longitudes,
            clasificacion_2, hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico, eq_danno_fases,
            vol_perdido, restricciones_fases, dia_labor, cont_pro_h_fijas)

    # Si el valor anterior de la subfase era FASE_PROTEGIDA_POR_ESTRUCTURA
    elif clasificacion_2 == c.FASE_PROTEGIDA_POR_ESTRUCTURA:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase Protegida por Estructura')

        # Se llama a la funcion de fase_sin_alerta_protegida_estructura
        (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas) = fase_sin_alerta_protegida_estructura(
            hora, plan_avance, fase, vol_ejecutado, de_tramo_0, avance_real, clima, estado_real, longitudes,
            hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico, eq_danno_fases, vol_perdido,
            restricciones_fases, dia_labor, cont_pro_h_fijas)

    # Si el valor anterior de la subfase era FASE_PROCESO_PROTECCION
    elif clasificacion_2 == c.FASE_EN_PROCESO_PROTECCION:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase en Proceso de Proteccion')

        # Se llama a la funcion de fase_sin_alerta_en_proceso_proteccion
        (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas) = fase_sin_alerta_en_proceso_proteccion(
            hora, plan_avance, fase, vol_ejecutado, de_tramo_0, avance_real, clima, estado_real, longitudes,
            clasificacion_2, hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico, eq_danno_fases,
            vol_perdido, restricciones_fases, dia_labor, cont_pro_h_fijas)

    # Si el valor anterior de la subfase era FASE_SIN_PROTECCION
    elif clasificacion_2 == c.FASE_SIN_PROTECCION:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase Sin Proteccion')

        # Se llama a la funcion de fase_sin_proteccion
        (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas) = fase_sin_alerta_sin_proteccion(
            hora, plan_avance, fase, vol_ejecutado, de_tramo_0, avance_real, clima, estado_real, longitudes,
            clasificacion_2, hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico, eq_danno_fases,
            vol_perdido, restricciones_fases, dia_labor, cont_pro_h_fijas)

    else:
        logging.error('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion Fase I Fase II sin alerta')

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def clasificacion_fase_I_fase_II_en_alerta(fase, hora, avance_real, vol_ejecutado, de_tramo_0, clima, estado_real,
                                           longitudes, plan_avance, hora_labor, cont_t_arranque, hora_acumulada,
                                           com_fin_teorico, eq_danno_fases, vol_perdido, restricciones_fases,
                                           dia_labor, cont_pro_h_fijas):
    """Funcion que clasifica a nivel II la fase constructiva en alerta en una fase no comenzada, protegida por
    estructura, en proceso de proteccion y sin proteccion.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
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

    # Se clasifica la subfase en funcion del valor anterior
    comprobacion = comprueba_valor_anterior(fase, hora, avance_real)
    clasificacion_2 = clasifica_fase_en_funcion_valor_anterior(comprobacion)

    # Si el valor anterior de la subfase era FASE_NO_COMENZADA o FASE_PARADA_INVERNAL
    if ((clasificacion_2 == c.FASE_NO_COMENZADA) | (clasificacion_2 == c.FASE_PARADA_INVERNAL)):
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase No Comenzada')

        # Se llama a la funcion de fase_en_alerta_no_comenzada
        (vol_ejecutado, longitudes) = fase_en_alerta_no_comenzada(
                                                                  hora, fase, clasificacion_2, avance_real,
                                                                  estado_real, de_tramo_0, longitudes,
                                                                  vol_ejecutado)

    # Si el valor anterior de la subfase era FASE_PROTEGIDA_POR_ESTRUCTURA
    elif clasificacion_2 == c.FASE_PROTEGIDA_POR_ESTRUCTURA:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase Protegida por Estructura')

        # Se llama a la funcion de fase_en_alerta_protegida_estructura
        (vol_ejecutado, longitudes) = fase_en_alerta_protegida_estructura(
                                                                          hora, fase, clasificacion_2, avance_real,
                                                                          estado_real, de_tramo_0, longitudes,
                                                                          vol_ejecutado)
    # Si el valor anterior de la subfase era FASE_PROCESO_PROTECCION
    elif clasificacion_2 == c.FASE_EN_PROCESO_PROTECCION:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase en Proceso de Proteccion')

        # Se llama a la funcion de fase_en_alerta_en_proceso_proteccion
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = fase_en_alerta_en_proceso_proteccion(
                                                                  hora, fase, clasificacion_2, avance_real,
                                                                  estado_real, de_tramo_0, longitudes,
                                                                  vol_ejecutado, clima, hora_labor,
                                                                  cont_t_arranque, hora_acumulada,
                                                                  eq_danno_fases, vol_perdido,
                                                                  restricciones_fases, dia_labor,
                                                                  cont_pro_h_fijas)
    # Si el valor anterior de la subfase era FASE_SIN_PROTECCION
    elif clasificacion_2 == c.FASE_SIN_PROTECCION:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase Sin Proteccion')

        # Se llama a la funcion de fase_sin_proteccion
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = fase_en_alerta_sin_proteccion(
                                                           hora, fase, clasificacion_2, avance_real,
                                                           estado_real, de_tramo_0, longitudes,
                                                           vol_ejecutado, clima, plan_avance, hora_labor,
                                                           cont_t_arranque, hora_acumulada, com_fin_teorico,
                                                           eq_danno_fases, vol_perdido, restricciones_fases,
                                                           dia_labor, cont_pro_h_fijas)

    else:
        logging.error('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion Fase I Fase II en alerta')

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)
