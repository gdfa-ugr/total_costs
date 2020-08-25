import ast

import logging

from . import constantes as c

from .comprobaciones import comprueba_temporal

from .clasificaciones import clasifica_fase_en_funcion_de_proximidad_de_temporal

from .fases_nivel_I import fase_sin_alerta
from .fases_nivel_I import fase_en_alerta


def clasificacion_main_fase_I(
                              fase, hora, clima, de_tramo_0, avance_real, vol_ejecutado, longitudes, plan_avance,
                              n_horas_fase, estado_real, hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico,
                              eq_danno_fases, vol_perdido, restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion que clasifica a nivel I la fase constructiva en una fase sin alerta o en alerta.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
        n_horas_fase: Numero de horas necesario para proteger la fase constructiva. Igual al numero de horas utilizado
            para clasificar la fase en presencia de temporal.
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
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

    # Se clasifica la fase en funcion de la proximidad de temporal: Para ello comprueba si hay presencia de temporal
    # dentro las siguientes 'n_horas_fase' horas. 'n_horas_fase' es el numero de horas necesarias para proteger la
    # longitud desprotegida de la subfase
    comprobacion = comprueba_temporal(
        hora_acumulada, n_horas_fase, ast.literal_eval(de_tramo_0.loc[de_tramo_0.index[fase], 'umb_protecc']), clima)
    clasificacion = clasifica_fase_en_funcion_de_proximidad_de_temporal(comprobacion)

    # Si la fase se clasifica como FASE_SIN_ALERTA(no hay temporal en las proximas 'n_horas_fase')
    if clasificacion == c.FASE_SIN_ALERTA:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel I: Fase Sin Alerta')

        # Verificacion de la subfase clasificada como sin alerta
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = fase_sin_alerta(fase, hora, avance_real, de_tramo_0, clima,
                                             longitudes, estado_real, vol_ejecutado, plan_avance, hora_labor,
                                             cont_t_arranque, hora_acumulada, com_fin_teorico, eq_danno_fases,
                                             vol_perdido, restricciones_fases, dia_labor, cont_pro_h_fijas)
    # Si la fase se clasifica como FASE_EN_ALERTA(hay temporal en las proximas 'n_horas_fase')
    elif clasificacion == c.FASE_EN_ALERTA:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel I: Fase En Alerta')

        # Verificacion de la subfase clasificada como en alerta
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = fase_en_alerta(fase, hora, avance_real, de_tramo_0, clima,
                                            longitudes, estado_real, vol_ejecutado, plan_avance, hora_labor,
                                            cont_t_arranque, hora_acumulada, com_fin_teorico, eq_danno_fases,
                                            vol_perdido, restricciones_fases, dia_labor, cont_pro_h_fijas)

    else:
        logging.error('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion main fase I')

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)
