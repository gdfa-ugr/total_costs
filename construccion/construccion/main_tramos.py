import pandas as pd
import numpy as np

import math

import logging

from .comprobaciones import comprueba_fase_acabada
from .comprobaciones import comprueba_fase_finalizada

from .datos_entrada import datos_entrada_tramo
from .datos_entrada import datos_entrada_fase
from .datos_entrada import rendimientos_y_umbrales_datos_entrada

from .calculos import calcula_n_horas_proteger
from .calculos import actualiza_longitudes_fase_siguiente
from .calculos import recorte_matrices_resultantes
from .calculos import genera_matriz_volumen
from .calculos import genera_matriz_estado
from .calculos import genera_matriz_contador_proteccion_horas_fijas
from .calculos import actualiza_matrices_fases_finalizadas

from .clasificacion_main_fase_I import clasificacion_main_fase_I

from .fases_nivel_III import fase_parada_invernal


def simulacion_proceso_constructivo_tramo(n, de_planta, hora_acumulada, hora_inicio_tramos, p_invernal,
                                          alcance='AP', estrategia='avance_serie', ruta_de='.', rep_inmediata='si'):
    """Funcion que simula la fase de construccion para un tramo de dique determinado.

    Args:
        n: Etiqueta del tramo de dique
        de_planta: Matriz con los datos de entrada relativos a la planta del tramo

            * Etiqueta del tramo
            * Longitud del tramo
            * Tipologia del tramo

        hora_acumulada: Valor de la hora acumulada desde el inicio de la obra
        hora_inicio_tramos: Lista con los valores de la hora en la que empieza la construccion de cada uno de los
            tramo del dique
        p_invernal: Fechas de inicio y final de las paradas invernales previstar para la obra
        alcance: etiqueta con el alcance del estudio
        estrategia: etiqueta con la estrategia
        ruta_de: cadena de texto con la ruta del directorio que contiene los datos de entrada
        rep_inmediata: parametro que indica con un 0 o 1 si los dannos sufridos son reparados de forma inmediata

    Returns:
         Un tupla de la forma (avance_real, estado_real, vol_ejecutado, longitudes, hora, hora_acumulada,
               hora_inicio_tramos, clima, maquinaria_fases, plan_avance, de_tramo, com_fin_teorico, vol_perdido,
               eq_coste_fases, costes_fase).

        * ``vol_ejecutado``: Matriz con los volumenes ejecutados y/o perdidos para cada iteracion del proceso
            constructivo (m3).
        * ``longitudes``: Longitud ejecutada en una fase constructiva clasificada como perdidas al final de cada
            iteracion (m).

    """

    # Lectura de los datos de entrada del tramo a partir de ficheros (clima, organizacion proceso constructivo,
    # subfases constructivas etc)
    (de_tramo, plan_avance, clima, com_fin_teorico) = datos_entrada_tramo(de_planta, n, hora_inicio_tramos,
                                                                          alcance, estrategia, ruta_de,
                                                                          rep_inmediata)

    # Lectura de los datos de entrada de cada subfase: unds de obra, maquinaria, ecuaciones de danno, ecs de coste
    # y restricciones
    (maquinaria_fases, eq_danno_fases, eq_coste_fases, costes_fase,
     restricciones_fases) = datos_entrada_fase(de_planta, de_tramo, n, estrategia, alcance, ruta_de)

    # Calculo de los valores de rendimiento, n. de horas laborables al dia, n. de dias laborables a la semana, tiempos
    # de arranque y umbrales de operatividad a partir de los datos de las maquinarias de las unidades de obra y
    # asignacion al dataframe de datos del tramo
    de_tramo = rendimientos_y_umbrales_datos_entrada(de_tramo, maquinaria_fases, alcance)

    # Inicializacion del dataframe de longitudes
    columnas = ['l_avanzada', 'l_protegida', 'l_desprotegida']
    indices = range(plan_avance.shape[0])
    longitudes = pd.DataFrame(0, index=indices, columns=columnas)

    # Inicializacion del dataframe de volumen ejecutado
    vol_ejecutado = genera_matriz_volumen(plan_avance)
    # Inicializacion del dataframe de volumen perdido a causa de los temporales
    vol_perdido = genera_matriz_volumen(plan_avance)
    # Inicializacion del dataframe de avance real (estado de la fase a Nivel 2)
    avance_real = genera_matriz_estado(plan_avance)
    # Inicializacion del dataframe de estado real (estado de la fase a Nivel 3)
    estado_real = genera_matriz_estado(plan_avance)
    # Inicializacion a 0 de los contadores de proteccion para las subfases que tengan horas de proteccion fijas
    cont_pro_h_fijas = genera_matriz_contador_proteccion_horas_fijas(plan_avance)

    # Inicializacion a 0 de los contadores de tiempo de arranque, hora, hora laborable y dia laborable
    columnas = ['t_arranque']
    cont_t_arranque = pd.DataFrame(0, index=indices, columns=columnas)
    hora = 0
    hora_labor = 0
    dia_labor = 0

    # Inicializacion a False del datafrae de las sub fases constructivas finalizadas (acabdas + protegidas)
    fases_finalizadas = pd.Series(np.full(plan_avance.shape[0], False, dtype=np.bool))

    # Inicializacion de todas las subfases del tramo para la simulacion
    fase_pos = fases_finalizadas[fases_finalizadas == False]  # nopep8

    # Inicio del proceso constructivo. Simula hasta que todas las fases se encuentren finalizadas
    while not fases_finalizadas.all():
        logging.info('Hora: ' + str(hora) + 'hs: ' + str(clima.loc[hora, 'hs']) + 'vv: ' + str(clima.loc[hora, 'vv']) + 'eta: ' + str(clima.loc[hora, 'eta']) + 'calado: ' + str(clima.loc[hora, 'calado']))

        actualiza_matrices_fases_finalizadas(fases_finalizadas, estado_real, hora)

        # Para cada hora (varia con un contador) se recorren cada una de las subfases del tramo
        for fase, _ in fase_pos.iteritems():

            if ((hora_acumulada == 53) | (hora_acumulada == 31) | (hora_acumulada == 0)):
                print(hora_acumulada)

            # Se comprueba si esta hora se encuentra dentro de una parada invernal
            if hora_acumulada in p_invernal:
                (vol_ejecutado, longitudes) = fase_parada_invernal(fase, hora, de_tramo, longitudes, estado_real,
                                                                   vol_ejecutado, cont_t_arranque, avance_real,
                                                                   eq_danno_fases)

            else:

                # Para cada subfase, antes de comenzar la verificacion, se actualiza la longitud protegida en base a la
                # longitud avanzada por la fase siguiente. Limitando que la longitud protegida nunca sea mayor que la
                # avanzada.
                longitudes = actualiza_longitudes_fase_siguiente(fase, longitudes, plan_avance, de_tramo)

                # Se calcula para cada iteracion el numero de horas necesario para proteger la longitud desprotegida
                # de la subfase. Este dato se utilizara para clasificar la fase en funcion de que haya o no presencia
                # de temporal en las siguientes 'n_horas_fase' horas
                n_horas_fase = int(math.ceil(calcula_n_horas_proteger(de_tramo, longitudes, fase)))

                # Se inicia la verificacion: Para cada subfase en cada hora se obtiene un valor del volumen ejecutado,
                # el volumen perdido, la actualizacion de las longitudes avanzadaas, protegidas y desprotegidas y
                # la actualizacion de las matrices de estado y avance real.
                (vol_ejecutado, vol_perdido, longitudes,
                 cont_pro_h_fijas) = clasificacion_main_fase_I(fase, hora, clima, de_tramo, avance_real,
                                                               vol_ejecutado, longitudes, plan_avance,
                                                               n_horas_fase, estado_real, hora_labor,
                                                               cont_t_arranque, hora_acumulada,
                                                               com_fin_teorico, eq_danno_fases, vol_perdido,
                                                               restricciones_fases, dia_labor, cont_pro_h_fijas)

                # Tras la finalizacion de la simulacion de la subfase para el estado de mar se añade +1 al contador
                # de proteccion de horas fijas en caso de que ya se haya iniciado la proteccion, esto es que contador
                # para la subfase este activado (valor igual a 1)
                if cont_pro_h_fijas.loc[cont_pro_h_fijas.index[fase], 'activado'] == 1:
                    cont_pro_h_fijas.loc[cont_pro_h_fijas.index[fase], 'cont'] += 1

                # Se comprueba si la subfase ha acabado (volumen ejecutado >= volumen total de la subfase)
                comprueba_fase_acabada(
                    vol_ejecutado, de_tramo, estado_real, fase, hora, cont_t_arranque)

                # Se comprueba si la fase esta finalizada (acabada mas protegida)
                fases_finalizadas = comprueba_fase_finalizada(
                    plan_avance, fases_finalizadas, vol_ejecutado, de_tramo, fase, hora, cont_t_arranque)

        # Finaliza la verificacion para todas las subfases se avanza a la hora siguiente
        hora += 1
        # Se avanza la hora laborable
        hora_labor += 1
        # Se avanza la hora acumulada
        hora_acumulada += 1

        # Reinicio el contador cuando la hora laborable llega a 25 y avanzo 1 el dia laborable
        if hora_labor == 25:
            logging.info('Hora: ' + str(hora) + ' Reinicio contador hora laborable')
            logging.info('Hora: ' + str(hora) + ' Avanzo el contador de dia laborable')
            dia_labor += 1
            hora_labor = 0
        # Reinicio el contador dias laborables cuando llega a 7
        if dia_labor == 7:
            logging.info('Dia: ' + str(dia_labor) + ' Reinicio contador dia laborable')
            dia_labor = 0

        # Se extran las fases aun no finalizadas (acabadas + protegidas) para repetir la verificacion en la siguiente
        # hora
        fase_pos = fases_finalizadas[fases_finalizadas == False]  # nopep8

        if alcance == 'PI':
            print (['Hora_acumulada: ', hora_acumulada, 'LA F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_avanzada']),
                    'LA F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_avanzada']),
                    'LA F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_avanzada']),
                    'LA F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_avanzada']),
                    'LA F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_avanzada']),
                    'LA F5: ', np.round(longitudes.loc[longitudes.index[5], 'l_avanzada']),
                    'LA F6: ', np.round(longitudes.loc[longitudes.index[6], 'l_avanzada']),
                    'LD F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_desprotegida']),
                    'LD F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_desprotegida']),
                    'LD F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_desprotegida']),
                    'LD F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_desprotegida']),
                    'LD F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_desprotegida']),
                    'LD F5: ', np.round(longitudes.loc[longitudes.index[5], 'l_desprotegida']),
                    'LD F6: ', np.round(longitudes.loc[longitudes.index[6], 'l_desprotegida']),
                    'LP F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_protegida']),
                    'LP F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_protegida']),
                    'LP F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_protegida']),
                    'LP F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_protegida']),
                    'LP F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_protegida']),
                    'LP F5: ', np.round(longitudes.loc[longitudes.index[5], 'l_protegida']),
                    'LP F6: ', np.round(longitudes.loc[longitudes.index[6], 'l_protegida'])])

        else:

            print (['Hora_acumulada: ', hora_acumulada, 'LA F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_avanzada']),
                   'LA F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_avanzada']),
                   'LA F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_avanzada']),
                   'LA F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_avanzada']),
                   'LA F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_avanzada']),
                   'LA F5: ', np.round(longitudes.loc[longitudes.index[5], 'l_avanzada']),
                   'LA F6: ', np.round(longitudes.loc[longitudes.index[6], 'l_avanzada']),
                   'LA F7: ', np.round(longitudes.loc[longitudes.index[7], 'l_avanzada']),
                   'LA F8: ', np.round(longitudes.loc[longitudes.index[8], 'l_avanzada']),
                   'LA F9: ', np.round(longitudes.loc[longitudes.index[9], 'l_avanzada']),
                   'LA F10: ', np.round(longitudes.loc[longitudes.index[10], 'l_avanzada']),
                   'LD F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_desprotegida']),
                   'LD F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_desprotegida']),
                   'LD F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_desprotegida']),
                   'LD F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_desprotegida']),
                   'LD F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_desprotegida']),
                   'LD F5: ', np.round(longitudes.loc[longitudes.index[5], 'l_desprotegida']),
                   'LD F6: ', np.round(longitudes.loc[longitudes.index[6], 'l_desprotegida']),
                   'LD F7: ', np.round(longitudes.loc[longitudes.index[7], 'l_desprotegida']),
                   'LD F8: ', np.round(longitudes.loc[longitudes.index[8], 'l_desprotegida']),
                   'LD F9: ', np.round(longitudes.loc[longitudes.index[9], 'l_desprotegida']),
                   'LD F10: ', np.round(longitudes.loc[longitudes.index[10], 'l_desprotegida']),
                   'LP F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_protegida']),
                   'LP F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_protegida']),
                   'LP F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_protegida']),
                   'LP F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_protegida']),
                   'LP F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_protegida']),
                   'LP F5: ', np.round(longitudes.loc[longitudes.index[5], 'l_protegida']),
                   'LP F6: ', np.round(longitudes.loc[longitudes.index[6], 'l_protegida']),
                   'LP F7: ', np.round(longitudes.loc[longitudes.index[7], 'l_protegida']),
                   'LP F8: ', np.round(longitudes.loc[longitudes.index[8], 'l_protegida']),
                   'LP F9: ', np.round(longitudes.loc[longitudes.index[9], 'l_protegida']),
                   'LP F10: ', np.round(longitudes.loc[longitudes.index[10], 'l_protegida'])])



#        print (['Hora_acumulada: ', hora_acumulada, 'LA F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_avanzada']),
#                'LA F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_avanzada']),
#                'LD F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_desprotegida']),
#                'LD F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_desprotegida']),
#                'LP F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_protegida']),
#                'LP F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_protegida'])])

#        print (['Hora_acumulada: ', hora_acumulada, 'LA F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_avanzada']),
#                'LA F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_avanzada']),
#                'LA F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_avanzada']),
#                'LA F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_avanzada']),
#                'LA F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_avanzada']),
#                'LD F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_desprotegida']),
#                'LD F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_desprotegida']),
#                'LD F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_desprotegida']),
#                'LD F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_desprotegida']),
#                'LD F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_desprotegida']),
#                'LP F0: ', np.round(longitudes.loc[longitudes.index[0], 'l_protegida']),
#                'LP F1: ', np.round(longitudes.loc[longitudes.index[1], 'l_protegida']),
#                'LP F2: ', np.round(longitudes.loc[longitudes.index[2], 'l_protegida']),
#                'LP F3: ', np.round(longitudes.loc[longitudes.index[3], 'l_protegida']),
#                'LP F4: ', np.round(longitudes.loc[longitudes.index[4], 'l_protegida'])])

    # Finalizada la verificacion del tramo se annade la hora de finalizacion del tramo que es la misma que la de
    # inicio del tramo siguiente
    hora_inicio_tramos.append(hora_acumulada)

    # Recorte de matrices resultantes
    (clima, avance_real, estado_real, vol_ejecutado, vol_perdido) = recorte_matrices_resultantes(
        hora, clima, avance_real, estado_real, vol_ejecutado, vol_perdido)

    return (avance_real, estado_real, vol_ejecutado, longitudes, hora, hora_acumulada, hora_inicio_tramos, clima,
            maquinaria_fases, plan_avance, de_tramo, com_fin_teorico, vol_perdido, eq_coste_fases, eq_danno_fases,
            costes_fase)
