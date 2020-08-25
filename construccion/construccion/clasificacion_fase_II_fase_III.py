import ast

import logging

from . import constantes as c

from .comprobaciones import comprueba_si_fase_trabaja
from .comprobaciones import comprueba_superacion_umbral
from .comprobaciones import comprueba_si_fase_retrasada
from .comprobaciones import comprueba_si_fase_falla

from .clasificaciones import clasifica_si_fase_trabaja
from .clasificaciones import clasifica_superacion_umbral_operativo
from .clasificaciones import clasifica_superacion_umbral_dannos
from .clasificaciones import clasifica_si_fase_deja_de_proteger
from .clasificaciones import clasifica_si_fase_deja_de_proceso_proteccion
from .clasificaciones import clasifica_si_fase_retrasada

from .fases_nivel_III import fase_no_trabaja
from .fases_nivel_III import fase_no_toca_trabajar
from .fases_nivel_III import fase_perdidas
from .fases_nivel_III import fase_protegiendo
from .fases_nivel_III import fase_no_trabaja_operatividad
from .fases_nivel_III import fase_trabaja_retrasada
from .fases_nivel_III import fase_trabaja

from .calculos import actualiza_matriz


def clasificacion_fase_II_fase_III_si_toca_trabajar(fase, hora, de_tramo_0, vol_ejecutado, avance_real,
                                                    longitudes, estado_real, clima, plan_avance, clasificacion_2,
                                                    hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico,
                                                    eq_danno_fases, vol_perdido, restricciones_fases, dia_labor,
                                                    cont_pro_h_fijas):
    """Funcion que clasifica a nivel III si la fase constructiva le toca trabajar o no. Las dos opciones posibles son
       fase_no_toca_trabajar o clasificacion_fase_II_fase_III_si_fase_va_retrasada.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3).
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
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

    # Se comprueba si a la fase le toca trabajar
    comprobacion = comprueba_si_fase_trabaja(hora_acumulada, plan_avance, fase)
    clasificacion_3 = clasifica_si_fase_trabaja(comprobacion)

    # Si a la subfase no le toca trabajar
    if clasificacion_3 == c.FASE_NO_TOCA_TRABAJAR:
        # Si la subfase no le toca trabajar y esta clasificada como no comenzada o en parada invernal
        if ((clasificacion_2 == c.FASE_NO_COMENZADA) | (clasificacion_2 == c.FASE_PARADA_INVERNAL)):

            # Se comprueba si la subfase no comenzada se encuentra antes del inicio teorico, en cuyo caso:
            if hora_acumulada < com_fin_teorico.loc[com_fin_teorico.index[fase], 'com_fase_teo']:

                # A la fase aun no le toca trabajar y se clasifica como NO_COMENZADA
                clasificacion_2 = c.FASE_NO_COMENZADA
                avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

                logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Toca Trabaja')

                # HINTS: La verificacion concluye que la fase_no_toca trabajar y se llama a la funcion
                # fase_no_toca_trabajar
                (vol_ejecutado, longitudes) = fase_no_toca_trabajar(fase, hora, de_tramo_0, longitudes, estado_real,
                                                                    vol_ejecutado)

            # Se comprueba si la subfase no comenzada se encuentra despues del final teorico de la subfase, en cuyo
            # caso la subfase se clasifica como TRABAJA_RETRASADA
            elif hora_acumulada > com_fin_teorico.loc[com_fin_teorico.index[fase], 'fin_fase_teo']:

                logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase Trabaja Retrasada')

                # La subfase se clasifica como TRABAJA_RETRASADA
                clasificacion_3 = c.FASE_TRABAJA_RETRASADA

                # Antes de poder trabajar se comprueba si la subfase sufre dannos
                (vol_ejecutado, vol_perdido, longitudes,
                 cont_pro_h_fijas) = clasificacion_fase_II_fase_III_umbral_dannos(fase, hora, clasificacion_3,
                                                                                  de_tramo_0, clima, longitudes,
                                                                                  vol_ejecutado, estado_real,
                                                                                  avance_real, clasificacion_2,
                                                                                  hora_labor, cont_t_arranque,
                                                                                  hora_acumulada,
                                                                                  eq_danno_fases,
                                                                                  vol_perdido,
                                                                                  restricciones_fases,
                                                                                  dia_labor, cont_pro_h_fijas)
                # Actualizo valor de la matriz de avance real para el dia actual
                clasificacion_2 = c.FASE_SIN_PROTECCION
                avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

        # Si la subfase no le toca trabajar y la subfase no esta clasificada como no comenzada o en parada invernal,
        # entonces se comprueba si la subfase va retrasada
        else:

            (vol_ejecutado, vol_perdido, longitudes,
             cont_pro_h_fijas) = clasificacion_fase_II_fase_III_si_fase_va_retrasada(fase, hora,
                                                                                     vol_ejecutado,
                                                                                     de_tramo_0,
                                                                                     avance_real,
                                                                                     longitudes, estado_real,
                                                                                     clasificacion_3, clima,
                                                                                     clasificacion_2,
                                                                                     hora_labor,
                                                                                     cont_t_arranque,
                                                                                     hora_acumulada,
                                                                                     eq_danno_fases,
                                                                                     vol_perdido,
                                                                                     restricciones_fases,
                                                                                     dia_labor,
                                                                                     cont_pro_h_fijas)

            # Actualizo valor de la matriz de avance real para el dia actual
            clasificacion_2 = c.FASE_SIN_PROTECCION
            avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    # Si a la subfase le toca trabajar
    elif clasificacion_3 == c.FASE_TRABAJA:

        # Se comprueba si sufre dannos antes de poder trabajar
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = clasificacion_fase_II_fase_III_umbral_dannos(fase, hora, clasificacion_3,
                                                                          de_tramo_0, clima, longitudes,
                                                                          vol_ejecutado, estado_real,
                                                                          avance_real, clasificacion_2,
                                                                          hora_labor, cont_t_arranque,
                                                                          hora_acumulada, eq_danno_fases,
                                                                          vol_perdido, restricciones_fases,
                                                                          dia_labor, cont_pro_h_fijas)
    else:
        logging.error(
            'Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion Fase II Fase III si toca trabajar')

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def clasificacion_fase_II_fase_III_si_fase_va_retrasada(fase, hora, vol_ejecutado, de_tramo_0, avance_real,
                                                        longitudes, estado_real, clasificacion_3, clima,
                                                        clasificacion_2, hora_labor, cont_t_arranque, hora_acumulada,
                                                        eq_danno_fases, vol_perdido, restricciones_fases,
                                                        dia_labor, cont_pro_h_fijas):
    """Funcion que clasifica a nivel III si la fase constructiva va retrasada o no. Las dos opciones posibles son
       fase_trabaja_retrasada en donde se llama a la funcion de clasificacion_fase_II_fase_III_umbral_dannos
       o fase_no_toca_trabajar en donde se llama a la funcion de clasificacion_fase_II_fase_III_umbral_dannos.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3).
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        clasificacion_3: Clasificacion de la fase a nivel III.
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
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

    # Se comprueba si la fase va retrasada.
    comprobacion = comprueba_si_fase_retrasada(fase, hora, vol_ejecutado, de_tramo_0, avance_real, clasificacion_3)
    clasificacion_3 = clasifica_si_fase_retrasada(comprobacion)

    # Si la subfase va retrasada
    if clasificacion_3 == c.FASE_TRABAJA_RETRASADA:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase Trabaja Retrasada')

        # Se comprueba si sufre dannos antes de poder trabajar
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = clasificacion_fase_II_fase_III_umbral_dannos(fase, hora, clasificacion_3,
                                                                          de_tramo_0, clima, longitudes,
                                                                          vol_ejecutado, estado_real,
                                                                          avance_real, clasificacion_2,
                                                                          hora_labor, cont_t_arranque,
                                                                          hora_acumulada, eq_danno_fases,
                                                                          vol_perdido, restricciones_fases,
                                                                          dia_labor, cont_pro_h_fijas)

    # Si a la subfase no le toca trabajar
    elif clasificacion_3 == c.FASE_NO_TOCA_TRABAJAR:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Toca Trabajar')

        # Se comprueba si sufre dannos
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = clasificacion_fase_II_fase_III_umbral_dannos(fase, hora, clasificacion_3,
                                                                          de_tramo_0, clima, longitudes,
                                                                          vol_ejecutado, estado_real,
                                                                          avance_real, clasificacion_2,
                                                                          hora_labor, cont_t_arranque,
                                                                          hora_acumulada, eq_danno_fases,
                                                                          vol_perdido, restricciones_fases,
                                                                          dia_labor, cont_pro_h_fijas)
    else:
        logging.error(
            'Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion Fase II Fase III si fase va retrasada')

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def clasificacion_fase_II_fase_III_umbral_dannos(fase, hora, clasificacion_3, de_tramo_0, clima, longitudes,
                                                 vol_ejecutado, estado_real, avance_real, clasificacion_2, hora_labor,
                                                 cont_t_arranque, hora_acumulada, eq_danno_fases, vol_perdido,
                                                 restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion que clasifica a nivel III si la fase se encuentra en perdidas o no. Las diferentes opciones son: Si la
    fase se encuentra en perdidas y no ha comenzado la fase se clasifica como fase_no_trabaja. Si esta en perdidas,
    pero la fase ha comenzado la fase se clasifica como fase_perdidas. Y si la fase se encuentra en perdidas estando
    en proceso de proteccion se comprueba si la fase pasa a protegida o permanece en proceso de proteccion. Si la fase
    no se encuentra en perdidas y no le toca trabajar se clasifica como fase_no_toca_tarbajar. Si la fase no se
    encuentar en perdidas y se encuentra en proceso de proteccion, se analiza si la fase pasa a fase protegida o
    permanece en proceso de proteccion. Finalmente si la fase no se encuentra en perdidas y le toca trabajar se llama
    a la funcion clasificacion_fase_II_fase_III_umbral_operatividad.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        clasificacion_3: Clasificacion de la fase a nivel III
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3).
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
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

    # Se comprueba el umbral de dannos para ver si la subfase sufre perdidas
    comprobacion = comprueba_si_fase_falla(eq_danno_fases, fase, clima, hora_acumulada)
    clasificacion_3 = clasifica_superacion_umbral_dannos(comprobacion, clasificacion_3, longitudes, fase)

    # Si la subfase se clasifica como  que sufre perdidas
    if clasificacion_3 == c.FASE_PERDIDAS:

        # Y no ha comenzado
        if clasificacion_2 == c.FASE_NO_COMENZADA:
            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Trabaja')

            # HINTS: La verificacion concluye que la fase_no_trabaja y se llama a la funcion
            # fase_no_trabaja
            (vol_ejecutado, longitudes) = fase_no_trabaja(fase, hora, de_tramo_0, longitudes, estado_real,
                                                          vol_ejecutado)

            # Actualizo valor de la matriz de avance real para el dia actual
            avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

        # Si la subfase sufre perdidas y ha comenzado
        else:
            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase en Perdidas')

            # HINTS: La verificacion concluye que la fase_perdidas y se llama a la funcion
            # fase_perdidas
            (vol_ejecutado, vol_perdido, longitudes) = fase_perdidas(fase, hora, de_tramo_0, longitudes, estado_real,
                                                                     vol_ejecutado, cont_t_arranque, eq_danno_fases,
                                                                     clima, vol_perdido)

            # Si la subfase que ha comenzado y ha sufrido perdidas estaba clasificada como
            # FASE_EN_PROCESO_DE_PROTECCION
            if clasificacion_2 == c.FASE_EN_PROCESO_PROTECCION:
                # Se comprueba si la longitud protegida es igual a la longitud avanzada y se actualiza el estado de
                # subfase a FASE_PROTEGIDA_POR_ESTRUCTURA.
                if longitudes.loc[longitudes.index[fase], 'l_protegida'] >= longitudes.loc[longitudes.index[fase], 'l_avanzada']:
                    clasificacion_2 = c.FASE_PROTEGIDA_POR_ESTRUCTURA
                    avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)
                    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase Protegida')

                # Si la longitud protegida es menor que la longitud avanzada entonces la fase sigue en
                # FASE_EN_PROCESO_PROTECCION
                elif longitudes.loc[longitudes.index[fase], 'l_protegida'] < longitudes.loc[longitudes.index[fase], 'l_avanzada']:
                    clasificacion_2 = c.FASE_EN_PROCESO_PROTECCION
                    avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)
                    logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                        fase) + ' Nivel II: Fase en Proceso de Protección')
                else:
                    logging.error(
                        'Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion Fase II Fase III umbral dannos')

            # Si la subfase se encontraba en un estado distinto al de FASE_EN_PROCESO_DE_PROTECCION, sigue con el mismo
            else:

                # Se actualiza la matriz de avance real
                avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    # Si la subfase no sufre perdidas
    else:

        # Si la subfase que no sufre perdidas no le toca trabajar
        if clasificacion_3 == c.FASE_NO_TOCA_TRABAJAR:
            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Toca Trabajar')

            # HINTS: La verificacion concluye que la fase_no_toca_trabajar y se llama a la funcion
            # fase_no_toca_trabajar
            (vol_ejecutado, longitudes) = fase_no_toca_trabajar(fase, hora, de_tramo_0, longitudes, estado_real,
                                                                vol_ejecutado)

        # Si la subfase que no sufre perdidas se encuentra protegiendo
        elif clasificacion_3 == c.FASE_PROTEGIENDO:

            # HINTS: La verificacion concluye que la fase_protegiendo y se llama a la funcion
            # fase_protegiendo
            (vol_ejecutado, longitudes, cont_pro_h_fijas) = fase_protegiendo(
                fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado, cont_t_arranque, cont_pro_h_fijas)

            # Se comprueba si la longitud protegida es igual a la longitud avanzada y se actualiza el estado de la
            # subfase a FASE_PROTEGIDA_POR_ESTRUCTURA
            if longitudes.loc[longitudes.index[fase], 'l_protegida'] >= longitudes.loc[longitudes.index[fase], 'l_avanzada']:
                clasificacion_2 = c.FASE_PROTEGIDA_POR_ESTRUCTURA
                clasificacion_3 = c.FASE_NO_TRABAJA
                estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
                logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase Protegida')

            # Si la longitud protegida es menor que la longitud avanzada entonces la fase sigue en
            # FASE_EN_PROCESO_PROTECCION
            elif longitudes.loc[longitudes.index[fase], 'l_protegida'] < longitudes.loc[longitudes.index[fase], 'l_avanzada']:
                clasificacion_2 = c.FASE_EN_PROCESO_PROTECCION
                clasificacion_3 = c.FASE_PROTEGIENDO
                estado_real = actualiza_matriz(hora, fase, clasificacion_3, estado_real)
                logging.info('Hora: ' + str(hora) + ' Fase: ' + str(
                    fase) + ' Nivel III: Fase Protegiendo')
            else:
                logging.error(
                    'Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion Fase II Fase III umbral dannos')

            # Se actualiza la matriz de avance real (clasificando el estado del dia actual para la siguiente iteracion)
            avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

        # Si la subfase que no sufre perdidas se encuentra en otro estado diferente se comprueba
        # si se supera el umbral de operatividad antes de poder empezar a trabajar.
        else:
            (vol_ejecutado, longitudes) = clasificacion_fase_II_fase_III_umbral_operatividad(fase, hora,
                                                                                             clasificacion_3,
                                                                                             de_tramo_0, clima,
                                                                                             longitudes,
                                                                                             vol_ejecutado,
                                                                                             estado_real,
                                                                                             clasificacion_2,
                                                                                             avance_real, hora_labor,
                                                                                             cont_t_arranque,
                                                                                             hora_acumulada,
                                                                                             restricciones_fases,
                                                                                             dia_labor)

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def clasificacion_fase_II_fase_III_umbral_operatividad(fase, hora, clasificacion_3, de_tramo_0, clima,
                                                       longitudes, vol_ejecutado, estado_real, clasificacion_2,
                                                       avance_real, hora_labor, cont_t_arranque, hora_acumulada,
                                                       restricciones_fases, dia_labor):
    """Funcion que clasifica a nivel III si la fase puede trabajar o no en funcion del umbral de operatividad. Las
    diferentes opciones son: fase_no_trabaja_operatividad, fase_trabaja o fase_trabaja_reatrasada.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        clasificacion_3: Clasificacion de la fase a nivel III
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3).
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        clasificacion_2: Clasificacion de la fase a nivel II.
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
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

    # Se comprueba si se supera el umbral de operatividad de la subfase
    comprobacion = comprueba_superacion_umbral(hora_acumulada, de_tramo_0.loc[de_tramo_0.index[fase], 'umb_operatividad'], clima)
    clasificacion_3 = clasifica_superacion_umbral_operativo(comprobacion, clasificacion_3)

    # Si se supera el umbral de operatividad
    if clasificacion_3 == c.FASE_NO_TRABAJA_OPERATIVIDAD:
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Trabaja Operatividad')

        # HINTS: La verificacion concluye que la fase_no_trabaja_operatividad y se llama a la funcion
        # fase_no_trabaja_operatividad
        (vol_ejecutado, longitudes) = fase_no_trabaja_operatividad(fase, hora, de_tramo_0, longitudes, estado_real,
                                                                   vol_ejecutado)

        # Si la subfase no ha comenzado, la subfase se clasifica como no comenzada
        if clasificacion_2 == c.FASE_NO_COMENZADA:

            # Se actualiza la matriz de avance real
            avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

        # Si la subfase tiene otro estado, ese estado se mantiene
        else:
            avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    # Si no se supera el umbral de operatividad
    else:
        # Si la subfase establa clasificada como que podia trabajar
        if clasificacion_3 == c.FASE_TRABAJA:
            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase Trabaja')

            # HINTS: La verificacion concluye que la fase_trabaja y se llama a la funcion
            # fase_trabaja
            (vol_ejecutado, longitudes) = fase_trabaja(
                fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado, hora_labor, cont_t_arranque,
                restricciones_fases, dia_labor)

        # Si la subfase establa clasificada como trabaja retrasada
        elif clasificacion_3 == c.FASE_TRABAJA_RETRASADA:
            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase Trabaja Retrasada')

            # HINTS: La verificacion concluye que la fase_trabaja_retrasada y se llama a la funcion
            # fase_trabaja_retrasada
            (vol_ejecutado, longitudes) = fase_trabaja_retrasada(
                fase, hora, de_tramo_0, longitudes, estado_real, vol_ejecutado, hora_labor, cont_t_arranque,
                restricciones_fases, dia_labor)

        # Si la subfase estaba clasificada como no comenzada
        if clasificacion_2 == c.FASE_NO_COMENZADA:

            # La subfase pasa al estado de sin proteccion
            clasificacion_2 = c.FASE_SIN_PROTECCION
            # Se actualiza la matriz de avance real
            avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)
            logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase Sin Protección')
        else:
            avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    return (vol_ejecutado, longitudes)


def clasificacion_fase_III_si_deja_de_proteger(fase, hora, de_tramo_0, clima, longitudes, vol_ejecutado,
                                               estado_real, avance_real, plan_avance, hora_labor, cont_t_arranque,
                                               hora_acumulada, com_fin_teorico, eq_danno_fases, vol_perdido,
                                               restricciones_fases, dia_labor, cont_pro_h_fijas):
    """Funcion que clasifica a nivel III si la fase deja o no de proteger. Las diferentes opciones son:
    Si la fase se encuentra protegida por estructura la fase se clasifica como fase_no_trabaja y si la fase se
    clasifica como fase sin proteccion se llama a la funcion clasificacion_fase_II_fase_III_si_toca_trabajar.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3).
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
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

    # Se comprueba si se puede salir de la fase de proteccion
    comprobacion = comprueba_si_fase_falla(eq_danno_fases, fase, clima, hora_acumulada)
    clasificacion_2 = clasifica_si_fase_deja_de_proteger(comprobacion)

    # Si la subfase se clasifica como protegida por estructura
    if clasificacion_2 == c.FASE_PROTEGIDA_POR_ESTRUCTURA:

        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel III: Fase No Trabaja')

        # HINTS: La verificacion concluye que la fase_no_trabaja y se llama a la funcion
        # fase_no_trabaja
        (vol_ejecutado, longitudes) = fase_no_trabaja(fase, hora, de_tramo_0, longitudes, estado_real,
                                                      vol_ejecutado)

        # Actualizo valor de la matriz de avance real para el dia actual
        avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)

    # Si la subfase se clasifica como sin proteccion
    elif clasificacion_2 == c.FASE_SIN_PROTECCION:

        # Si la subfase puede dejar de proteger porque ha pasado el temporal, pongo a 0 el contador de protección de
        # horas fijas
        cont_pro_h_fijas.loc[cont_pro_h_fijas.index[fase], 'activado'] = 0
        cont_pro_h_fijas.loc[cont_pro_h_fijas.index[fase], 'cont'] = 0

        # La fase deja de proteger y se comprueba si a la fase le toca trabajar
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

        avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase Sin Protección')

    else:
        logging.error(
            'Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion fase III si deja de proteger')

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)


def clasificacion_fase_III_si_deja_de_proceso_proteccion(fase, hora, de_tramo_0, vol_ejecutado, avance_real,
                                                         longitudes, estado_real, clima, plan_avance, clasificacion_2,
                                                         hora_labor, cont_t_arranque, hora_acumulada, com_fin_teorico,
                                                         eq_danno_fases, vol_perdido, restricciones_fases, dia_labor,
                                                         cont_pro_h_fijas):
    """Funcion que clasifica a nivel III si la fase deja o no el proceso de proteccion. Las diferentes opciones son:
    Si la fase se encuentra en proceso de proteccion se llama a la funcion
    clasificacion_fase_II_fase_III_umbral_dannos. Y si la fase se encuentra sin proteccion se llama a la funcion
    clasificacion_fase_II_fase_III_si_toca_trabajar.

    Args:
        fase: Fase constructiva
        hora: Hora (h)
        de_tramo_0: Matriz con los datos de entrada introducidos por el usuario para el tramo de dique
        vol_ejecutado: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso constructivo
            (m3).
        avance_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel II (-1: Fase no comenzada, 0: Fase protegida por estructura, 1: Fase en proceso
            de proteccion, 2: Fase sin protecion).
        longitudes: DataFrame con las longitudes avanzadas, protegidas y desprotegidas para cada sub fase
            constructiva (m)
        estado_real: Matriz que guarda para cada hora (iteracion) del proceso constructivo el estado en el que se
            encuentra la fase a nivel III (-1: Fase no trabaja, 0: Fase no toca trabajar, 1: Fase no trabaja por
            restriccion, 2: Fase no trabaja operatividad, 3: Fase trabaja, 4: Fase trabaja retrasada, 5: Fase
            protegiendo, 6: Fase perdidas, 7: Fase acabada).
        clima: Matriz con las series temporales simuladas y propagadas al emplazamiento para cada agente
        plan_avance: Matriz de 0 y 1 donde 0 indica que para ese dia a esa fase no le corresponde trabajar y 1 indica
            que si le toca trabajar.
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

    # Se comprueba si se puede salir de la fase de proceso de proteccion
    comprobacion = comprueba_si_fase_falla(eq_danno_fases, fase, clima, hora_acumulada)
    clasificacion_2 = clasifica_si_fase_deja_de_proceso_proteccion(comprobacion)

    # Si la subfase se clasifica como en proceso de proteccion
    if clasificacion_2 == c.FASE_EN_PROCESO_PROTECCION:

        # La subfase permanece protegiendo y se comprueba si sufre dannos
        clasificacion_3 = c.FASE_PROTEGIENDO
        (vol_ejecutado, vol_perdido, longitudes,
         cont_pro_h_fijas) = clasificacion_fase_II_fase_III_umbral_dannos(fase, hora, clasificacion_3,
                                                                          de_tramo_0, clima, longitudes,
                                                                          vol_ejecutado, estado_real,
                                                                          avance_real, clasificacion_2,
                                                                          hora_labor, cont_t_arranque,
                                                                          hora_acumulada, eq_danno_fases,
                                                                          vol_perdido,
                                                                          restricciones_fases, dia_labor,
                                                                          cont_pro_h_fijas)

    # Si la subfase se clasifica como sin proteccion
    elif clasificacion_2 == c.FASE_SIN_PROTECCION:

        # La subfase deja de proteger y se comprueba si le toca trabajar
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

        avance_real = actualiza_matriz(hora, fase, clasificacion_2, avance_real)
        logging.info('Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Nivel II: Fase Sin Protección')

    else:
        logging.error(
            'Hora: ' + str(hora) + ' Fase: ' + str(fase) + ' Clasificacion Fase III si deja proceso de proteccion')

    return (vol_ejecutado, vol_perdido, longitudes, cont_pro_h_fijas)
