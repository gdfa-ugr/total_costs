import ast
import logging

import numpy as np
import math

from .calculos import inicializacion_matrices_grado_averia
from .calculos import calcula_h_eq_n_olas
from .calculos import estado_de_mar_tramo
from .calculos import calcula_inicio_averia_de_modos_asociados
from .calculos import calcula_danno
from .calculos import calcula_si_inicio_de_averia
from .calculos import calcula_tiempo_necesario_para_iniciar_reparacion
from .calculos import calcula_nivel_averia_reparado
from .calculos import calcula_elementos_reparacion_restantes_en_puerto_al_final
from .calculos import actuliza_nivel_de_averia
from .calculos import actualiza_origen_elementos_reparacion

from .comprobaciones import comprueba_si_ciclo_de_solicitacion
from .comprobaciones import comprueba_si_hay_inicio_de_averia
from .comprobaciones import comprueba_si_se_supera_umbral_de_reparacion
from .comprobaciones import comprueba_si_el_modo_esta_reparando
from .comprobaciones import comprueba_superacion_umbral
from .comprobaciones import comprueba_si_na_menor_na_umbral_fin_reparacion

from .clasificaciones import clasifica_si_ciclo_solicitacion
from .clasificaciones import clasifica_si_inicio_de_averia
from .clasificaciones import clasifica_si_se_supera_umbral_de_reparacion
from .clasificaciones import clasifica_si_el_modo_esta_reparando
from .clasificaciones import clasifica_superacion_umbral_operativo
from .clasificaciones import clasifica_si_na_menor_na_umbral_fin_reparacion

from . import constantes as c


def verificacion_ciclo_calma(tr, ss, mf, h, averia_acum_estado, de_reparacion_necesarios, estado_reparacion_modos,
                             de_reparacion_disponibles, origen_maquinaria_reparacion_estado,
                             origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado,
                             alcance, datos_salida, hs, u10, z, estado_modos_fallo, cadencia,
                             de_verificacion_tramos, peralte, averia_estado,
                             ia_modos_fallo, datos_salida_prob_ini_averia, ini_reparacion, fin_reparacion):
    # Lo primero es comprobar si el nivel de averia acumulado para el modo supera el valor umbral
    # fijado en la estrategia para iniciar el tramite de reparacion o si las reparaciones ya se han
    # iniciado.
    comprobacion = \
        comprueba_si_se_supera_umbral_de_reparacion(averia_acum_estado,
                                                    tr, ss, mf, h, de_reparacion_necesarios, alcance)
    clasificacion1 = clasifica_si_se_supera_umbral_de_reparacion(comprobacion)

    comprobacion = comprueba_si_el_modo_esta_reparando(estado_reparacion_modos, tr, ss, mf)
    clasificacion2 = clasifica_si_el_modo_esta_reparando(comprobacion)

    if any([clasificacion1, clasificacion2]) == 1:

        # Esta funcion debe comprobar si ya se estaba reparando, el tiempo sera 0, si hay maquinaria
        # disponible el tiempo necesario sera 0 y si no se actualiza el tiempo restante
        if math.isnan(estado_reparacion_modos.loc[(tr, ss, mf), 'reparando']):
            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Inicia el tramite de reparacion')

            # En primer lugar se establece que el modo esta reparando para que en los siguientes
            # estado pueda entrar
            estado_reparacion_modos.loc[(tr, ss, mf), 'reparando'] = 1

            # Almaceno instante de inicio de reparacion
            ini_reparacion.loc[(tr, ss, mf), str(h)] = h

            t_ini_rep = \
                calcula_tiempo_necesario_para_iniciar_reparacion(tr, ss, mf,
                                                                 de_reparacion_necesarios,
                                                                 de_reparacion_disponibles,
                                                                 origen_maquinaria_reparacion_estado,
                                                                 origen_materiales_reparacion_estado,
                                                                 origen_mano_obra_reparacion_estado, h,
                                                                 alcance)

            estado_reparacion_modos.loc[(tr, ss, mf), 't_rep'] = t_ini_rep

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Tiempo restante para iniciar reparacion: ' + str(
                t_ini_rep))

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Origen de la maquinaria: ' + str(
                origen_maquinaria_reparacion_estado.loc[(tr, ss, mf), h]))

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Origen de los materiales: ' + str(
                origen_materiales_reparacion_estado.loc[(tr, ss, mf), h]))

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Origen de la mano de obra: ' + str(
                origen_mano_obra_reparacion_estado.loc[(tr, ss, mf), h]))

            # Actualizo los valores de salida
            datos_salida['datos_salida_modos'].loc[mf, 'n_veces_ini_rep'] += 1
            datos_salida['datos_salida_subsistemas'].loc[ss, 'n_veces_ini_rep'] += 1
            datos_salida['datos_salida_tramos'].loc[tr, 'n_veces_ini_rep'] += 1
            datos_salida['datos_salida_dique'].loc['dique', 'n_veces_ini_rep'] += 1

        # En caso de que el tiempo necesario para iniciar la reparacion ya haya sido calculado
        # se actualiza el valor del origen de la maquinaria, materiales y mano de obra copiando el
        # ultimo valor distinto de nan
        else:
            # Actualiza origen de los elementos de reparacion
            (origen_maquinaria_reparacion_estado,
             origen_materiales_reparacion_estado,
             origen_mano_obra_reparacion_estado) = \
             actualiza_origen_elementos_reparacion(origen_maquinaria_reparacion_estado,
                                                   origen_materiales_reparacion_estado,
                                                   origen_mano_obra_reparacion_estado,
                                                   tr, ss, mf, h)

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Origen de la maquinaria: ' + str(
                origen_maquinaria_reparacion_estado.loc[(tr, ss, mf), h]))

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Origen de los materiales: ' + str(
                origen_materiales_reparacion_estado.loc[(tr, ss, mf), h]))

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Origen de la mano de obra: ' + str(
                origen_mano_obra_reparacion_estado.loc[(tr, ss, mf), h]))

        # Si el tiempo de inicio de la reparacion alcanza el valor de 0, se puede reparar
        if estado_reparacion_modos.loc[(tr, ss, mf), 't_rep'] <= 0:

            # En primer lugar se establece que el modo esta reparando para que en los siguientes
            # estado pueda entrar
            estado_reparacion_modos.loc[(tr, ss, mf), 'reparando'] = 1

            # Se comprueba umbral de operatividad
            if ((alcance != 'EA') & (alcance != 'EA_sencillo')):
                umbrales = ast.literal_eval(de_reparacion_necesarios.loc[(tr, ss, mf), 'umb_ope'])
                comprobacion = comprueba_superacion_umbral(hs, u10, z, umbrales, alcance)
                clasificacion = clasifica_superacion_umbral_operativo(comprobacion)
            elif ((alcance == 'EA') | (alcance == 'EA_sencillo')):
                clasificacion = 0

            if clasificacion == 1:
                # La maquinaria no puede reparar porque se supera el umbral operativo de la maquinaria
                # Actualizo el estado del modo
                estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_NO_REPARA_OPERATIVIDAD

                logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                    ss) + ' Modo_fallo: ' + str(mf) +
                    ' La maquinaria no puede reparar por superacion de umbral operativo')

            else:
                # La maquinaria repara. Se calcula el nivel de averia reparado
                # Actualizo el estado del modo
                estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_REPARANDO

                logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                    ss) + ' Modo_fallo: ' + str(mf) +
                    ' La maquinaria repara')

                # Se produce la reparacion
                (averia_estado, averia_acum_estado) = \
                    calcula_nivel_averia_reparado(tr, ss, mf, de_reparacion_necesarios, averia_estado,
                                                  averia_acum_estado, cadencia, h)

                # Se comprueba si el nivel de averia del modo ya esta por debajo del nivel de averia
                # umbral hasta el que se decide reparar.
                comprobacion = comprueba_si_na_menor_na_umbral_fin_reparacion(tr, ss, mf, h,
                                                                              averia_acum_estado,
                                                                              de_reparacion_necesarios,
                                                                              alcance)

                clasificacion = clasifica_si_na_menor_na_umbral_fin_reparacion(comprobacion)

                if clasificacion == 1:
                    # La reparacion ha finalizado
                    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                        ss) + ' Modo_fallo: ' + str(mf) +
                        ' Se finaliza la reparacion del modo')

                    # Actualizo el estado del modo
                    estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_FINALIZA_REPARACION

                    # Comprobaciones necesarias
                    # Se finaliza el estado de reparando en el modo para que no entre la proxima vez
                    estado_reparacion_modos.loc[(tr, ss, mf), 'reparando'] = np.nan
                    # El tiempo restante de reparacion se pasa a nan
                    estado_reparacion_modos.loc[(tr, ss, mf), 't_rep'] = np.nan

                    # Almaceno instante de inicio de reparacion
                    fin_reparacion.loc[(tr, ss, mf), str(h)] = h

                    if alcance == 'PI':  # Solo se hace en el alcance de PI
                        # Devolucion de la maquinaria y mano de obra cogida al puerto
                        de_reparacion_disponibles = \
                            calcula_elementos_reparacion_restantes_en_puerto_al_final(tr, ss, mf, h,
                                                                                      de_reparacion_necesarios,
                                                                                      de_reparacion_disponibles,
                                                                                      origen_maquinaria_reparacion_estado,
                                                                                      origen_mano_obra_reparacion_estado)


                    # Se compruba si el nivel de averia es menor de 1 para poner dt del modo igual a 0
                    if all(averia_acum_estado.loc[(slice(None), slice(None), mf), h] <= 1):
                        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                            ss) + ' Modo_fallo: ' + str(mf) +
                            ' Sale de destruccion total')

                        # Actualizo el estado del modo
                        estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_SALE_DE_DESTRUCCION_TOTAL

                        # LLevo el inicio de averia del modo a 0
                        ia_modos_fallo.loc[(slice(None), slice(None), mf), 'dest_total'] = 0

                    # Se compruba si el nivel de averia es menor de 0 para poner ia del modo igual a 0
                    if all(averia_acum_estado.loc[(slice(None), slice(None), mf), h] <= 0):
                        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                            ss) + ' Modo_fallo: ' + str(mf) +
                            ' Sale de inicio de averia')

                        # Actualizo el estado del modo
                        estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_SALE_DE_INICIO_DE_AVERIA

                        # El nivel de averia nunca puede estar por debajo de 0
                        averia_acum_estado.loc[(slice(None), slice(None), mf), h] = 0
                        # LLevo el inicio de averia del modo a 0
                        ia_modos_fallo.loc[(slice(None), slice(None), mf), 'ini_averia'] = 0

        else:
            # Añado el paso del tiempo al tiempo restante para iniciar la reparacion
            valor_ant = estado_reparacion_modos.loc[(tr, ss, mf), 't_rep']
            estado_reparacion_modos.loc[(tr, ss, mf), 't_rep'] = valor_ant - cadencia

            # Actualizo el estado del modo
            estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Esperando_para_empezar_a_reparar')

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Tiempo restante para iniciar reparacion: ' + str(
                estado_reparacion_modos.loc[(tr, ss, mf), 't_rep']))

    else:
        # El modo no repara porque no se ha superado el nivel de avería umbral para iniciar la reparacion
        # Actualizo el estado del modo
        estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_NO_REPARA

        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
            ss) + ' Modo_fallo: ' + str(
            mf) + ' Modo_no_repara_porque_no_se_supera_na_umbral_para_iniciar_reparacion')

    return(datos_salida, averia_acum_estado, averia_estado, estado_modos_fallo, origen_maquinaria_reparacion_estado,
           origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado, datos_salida_prob_ini_averia)


def verificacion_ciclo_solicitacion(hs, tp, tr, ss, mf, ia_modos_fallo, h, averia_estado, averia_acum_estado,
                                    cadencia, de_verificacion_tramos, peralte, datos_salida, estado_modos_fallo,
                                    de_arbol_fallo, de_esquema_division_dique,
                                    de_tipo_verificacion, clima_tramos, de_diagrama_modos, ia_subsistemas, ia_tramos,
                                    ia_dique, subsistemas, datos_salida_prob_ini_averia, alcance, de_planta):

    # Si estamos en un ciclo de solicitacion, se realiza la conversion del estado de mar a
    # numero de olas y altura de ola equivalente
    (h_eq, n_olas) = calcula_h_eq_n_olas(hs, tp, cadencia)

    # Se comprueba si el modo de fallo en cuestion ha fallado, esto es, su daño acumulado es igual o
    # superior al inicio de averia
    comprobacion = comprueba_si_hay_inicio_de_averia(ia_modos_fallo, tr, ss, mf)
    clasificacion = clasifica_si_inicio_de_averia(comprobacion)

    # Si el modo se diseña como elu tengo que comprobar el inicio de averia en cada estado, no vale con que ya se haya
    # iniciado la averia en estados anteriores
    if de_tipo_verificacion.loc[(tr, ss, mf), 'tipo_diseno'] == 'elu':
        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
            ss) + ' Modo_fallo: ' + str(mf) + ' El modo se verifica a ELU')
        clasificacion == c.MODO_NO_TIENE_AVERIA
    else:
        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
            ss) + ' Modo_fallo: ' + str(mf) + ' El modo se verifica a ELS')

    # Si el modo tiene averia
    if clasificacion == c.MODO_TIENE_AVERIA:
        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
            ss) + ' Modo_fallo: ' + str(mf) + ' tiene nivel de averia por encima de inicio de averia')

        # Se calcula el danno producido por el estado
        (averia_estado,
         averia_acum_estado,
         datos_salida) = calcula_danno(
             averia_estado, averia_acum_estado, h_eq, n_olas, tr, ss, mf, h, datos_salida, alcance,
             de_tipo_verificacion, de_verificacion_tramos, peralte, de_planta, tp)

        # Actualizo el estado del modo
        estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_SUFRE_DANNOS

        # Se comprueban los arboles de fallo para llevar a inicio de averia los modos de fallo que fallan
        # a consecuencia del fallo del modo analizado
        (ia_modos_fallo, datos_salida,
         datos_salida_prob_ini_averia) = calcula_inicio_averia_de_modos_asociados(h, ia_modos_fallo, de_arbol_fallo,
                                                                                  tr, ss, mf, de_esquema_division_dique,
                                                                                  datos_salida, averia_acum_estado,
                                                                                  datos_salida_prob_ini_averia)

    # Si el modo no tiene averia
    elif clasificacion == c.MODO_NO_TIENE_AVERIA:
        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
            ss) + ' Modo_fallo: ' + str(mf) + ' No ha superado el inicio de averia')

        # Se comprueba si el estado produce inicio de averia
        (ia_modos_fallo, datos_salida,
         datos_salida_prob_ini_averia) = calcula_si_inicio_de_averia(clima_tramos, h_eq, n_olas,
                                                                     ia_modos_fallo, tr, ss, mf, h,
                                                                     de_verificacion_tramos,
                                                                     datos_salida, datos_salida_prob_ini_averia)

        # Se comprueba si el modo de fallo en cuestion ha fallado, esto es, su daño acumulado es igual o
        # superior al inicio de averia
        comprobacion = comprueba_si_hay_inicio_de_averia(ia_modos_fallo, tr, ss, mf)
        clasificacion = clasifica_si_inicio_de_averia(comprobacion)

        # Si el modo tiene averia
        if clasificacion == c.MODO_TIENE_AVERIA:
            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' Acaba de superar el inicio de averia')

            # Se calcula el danno producido por el estado
            (averia_estado,
             averia_acum_estado,
             datos_salida) = calcula_danno(
                 averia_estado, averia_acum_estado, h_eq, n_olas, tr, ss, mf, h, datos_salida, alcance,
                 de_tipo_verificacion, de_verificacion_tramos, peralte, de_planta, tp)

            # Actualizo el estado del modo
            estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_SUFRE_DANNOS

            # Se comprueban los arboles de fallo para llevar a inicio de averia los modos de fallo que
            # fallan a consecuencia del fallo del modo analizado
            (ia_modos_fallo, datos_salida,
             datos_salida_prob_ini_averia) = calcula_inicio_averia_de_modos_asociados(h, ia_modos_fallo, de_arbol_fallo,
                                                                                      tr, ss, mf, de_esquema_division_dique,
                                                                                      datos_salida, averia_acum_estado,
                                                                                      datos_salida_prob_ini_averia)

        elif clasificacion == c.MODO_NO_TIENE_AVERIA:
            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' No supera el inicio de averia en este estado')

            # Actualizo el estado del modo
            estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_NO_ALCANZA_INICIO_AVERIA_NO_SUFRE_DANNOS

    # Finalizado el calculo del danno se procede a comprobar si hay destruccion total del modo, subsistema
    # tramo o dique

    # Si la averia acumulada en el modo de fallo supera el 100 % entronces se produce la destruccion total
    if (averia_acum_estado.loc[(tr, ss, mf), h] >= 1):

        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
            ss) + ' Modo_fallo: ' + str(mf) + ' El modo sufre destruccion total')

        # Actualizo el estado del modo
        estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_SUFRE_DESTRUCCION_TOTAL

        # Solo lo compruebo si en el estado anterior no habia dt, o lo que es lo mismo, lo compruebo la primera vez
        # que se alcanza dt, y no lo vuelvo a comprobar hasta que se repara y se vuelve a alcanzar
        if (averia_acum_estado.loc[(tr, ss, mf), h - 1] != 1):

            clasificacion = c.MODO_TIENE_DESTRUCCION_TOTAL
            ia_modos_fallo.loc[(tr, ss, mf), 'dest_total'] = 1

            # Actualizo los valores de salida
            datos_salida['datos_salida_modos'].loc[mf, 'vida_util'] = h
            datos_salida['datos_salida_modos'].loc[mf, 'n_veces_dest_total'] += 1

            # Elimino el modo de fallo de la lista de componentes a la hora de iterar
    #        de_esquema_division_dique = \
    #            de_esquema_division_dique[de_esquema_division_dique.modo_fallo != mf]

            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' El modo sufre destruccion total')

            # Actualizo el estado del modo
            estado_modos_fallo.loc[(tr, ss, mf), h] = c.MODO_SUFRE_DESTRUCCION_TOTAL

            # Se comprueba si la destruccion total (dt) del modo implica la destruccion total del subsistema
            # y/o el tramo y/o el dique. la dt de un modo no produce la dt de otros modos, pero si puede
            # producir la dt de algun subsistema, este la dt de algun tramo y este la dt del dique

            # Cuando se produce la dt de un modo hay que comprobar uno a uno todos los subsistemas por si
            # se produce la dt de algun subsistema
            opciones = de_diagrama_modos['de_diagrama_modos_subsistemas']

            # Codigo para simular op en modo debug
            # op = next(opciones.iterrows())[0]
            for op in opciones.iterrows():
                ss_analizando = op[0][1]
                op = op[1]
                modos_que_producen_dt = ast.literal_eval(op[0])

                # Compruebo si todos los modos de fallo que producen el la dt del susbsistema estan en dt
                if all(ia_modos_fallo.loc[(slice(
                       None), slice(None), modos_que_producen_dt), 'dest_total'] == 1):
                    # Si se cumple, el subsistema pasa a dt
                    ia_subsistemas.loc[(slice(None), ss_analizando), 'dest_total'] = 1

                    # Actualizo los valores de salida
                    datos_salida['datos_salida_subsistemas'].loc[ss, 'vida_util'] = h
                    datos_salida['datos_salida_subsistemas'].loc[ss, 'n_veces_dest_total'] += 1

                    # Elimino el subsistema de la lista de componentes a la hora de iterar
#                    de_esquema_division_dique = \
#                        de_esquema_division_dique[de_esquema_division_dique.subsistema != ss]

                    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                        ss) + ' Modo_fallo: ' + str(mf) + ' El subsistema ' + str(
                        ss_analizando) + ' sufre destruccion total')
                    break

            # Cuando se produce la dt de un subsistema hay que comprobar uno a uno todos los tramos por si
            # se produce la dt de algun tramo
            opciones = de_diagrama_modos['de_diagrama_modos_tramos']

            for op in opciones.iterrows():
                tr_analizando = op[0][0]
                op = op[1]
                ss_que_producen_dt = ast.literal_eval(op[0])

                # Compruebo si todos los modos de fallo que producen el la dt del susbsistema estan en dt
                if all(ia_subsistemas.loc[(slice(None), ss_que_producen_dt), 'dest_total'] == 1):
                    # Si se cumple, el subsistema pasa a dt
                    ia_tramos.loc[(tr_analizando), 'dest_total'] = 1

                    # Actualizo los valores de salida
                    datos_salida['datos_salida_tramos'].loc[tr, 'vida_util'] = h
                    datos_salida['datos_salida_tramos'].loc[tr, 'n_veces_dest_total'] += 1

                    # Elimino el modo de fallo de la lista de componentes a la hora de iterar
#                    de_esquema_division_dique = \
#                        de_esquema_division_dique[de_esquema_division_dique.tramo != tr]

                    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                        ss) + ' Modo_fallo: ' + str(mf) + ' El tramo ' + str(
                            tr_analizando) + ' sufre destruccion total')
                    break

            # Cuando se produce la dt de un tramo hay que comprobar el dique por si
            # se produce la dt del mismo
            opciones = de_diagrama_modos['de_diagrama_modos_dique']

            for op in opciones.iterrows():
                op = op[1]
                tramos_que_producen_dt = ast.literal_eval(op[0])

                # Compruebo si todos los modos de fallo que producen el la dt del susbsistema estan en dt
                if all(ia_tramos.loc[tramos_que_producen_dt, 'dest_total'] == 1):
                    # Si se cumple, el subsistema pasa a dt
                    ia_dique.loc[ia_dique.index[0], 'dest_total'] = 1

                    # Actualizo los valores de salida
                    datos_salida['datos_salida_dique'].loc['dique', 'vida_util'] = h
                    datos_salida['datos_salida_dique'].loc['dique', 'n_veces_dest_total'] += 1

                    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                        ss) + ' Modo_fallo: ' + str(mf) + ' El dique sufre destruccion total')

                    break

    return(datos_salida, averia_acum_estado, averia_estado, estado_modos_fallo, datos_salida_prob_ini_averia)
