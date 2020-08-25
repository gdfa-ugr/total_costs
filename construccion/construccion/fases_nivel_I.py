from .clasificacion_fase_I_fase_II import clasificacion_fase_I_fase_II_sin_alerta
from .clasificacion_fase_I_fase_II import clasificacion_fase_I_fase_II_en_alerta


def fase_sin_alerta(fase, hora, avance_real, de_tramo_0, clima, longitudes, estado_real, vol_ejecutado,
                    plan_avance, hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico, eq_danno_fases,
                    vol_perdido, restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion para una fase constructiva clasificada como fase sin alerta que llama a la funcion
    clasificacion_fase_I_fase_II_sin_alerta para iniciar la clasificacion a nivel II.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
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

    # Se llama a la funcion de clasificacion para pasar de fases_nivel_I a fases_nivel_II
    (vol_ejecutado, vol_perdido, longitudes,
     cont_pro_h_fijas) = clasificacion_fase_I_fase_II_sin_alerta(fase, hora, avance_real, vol_ejecutado,
                                                                 de_tramo_0, clima, estado_real,
                                                                 longitudes, plan_avance, hora_labor,
                                                                 cont_t_arranque, hora_acumulada,
                                                                 com_fin_teorico, eq_danno_fases, vol_perdido,
                                                                 restricciones_fases, dia_labor,
                                                                 cont_pro_h_fijas)

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def fase_en_alerta(fase, hora, avance_real, de_tramo_0, clima, longitudes, estado_real, vol_ejecutado, plan_avance,
                   hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico, eq_danno_fases, vol_perdido,
                   restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion para una fase constructiva clasificada como fase en alerta que llama a la funcion
    clasificacion_fase_I_fase_II_en_alerta para iniciar la clasificacion a nivel II.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3)
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

    # Se llama a la funcion de clasificacion para pasar de fases_nivel_I a fases_nivel_II
    (vol_ejecutado, vol_perdido, longitudes,
     cont_pro_h_fijas) = clasificacion_fase_I_fase_II_en_alerta(fase, hora, avance_real, vol_ejecutado,
                                                                de_tramo_0, clima, estado_real,
                                                                longitudes, plan_avance, hora_labor,
                                                                cont_t_arranque, hora_acumulada,
                                                                com_fin_teorico, eq_danno_fases, vol_perdido,
                                                                restricciones_fases, dia_labor,
                                                                cont_pro_h_fijas)

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)
