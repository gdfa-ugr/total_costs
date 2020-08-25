import numpy as np
import pandas as pd
import ast
import math
import os
import logging
import random

from . import constantes as c
from .wavnum import wavnum


def calculo_final_simulacion(de_planta, clima_tramos, cadencia):
    # De las vidas utiles de cada tramo, se toma la mayor
    vu = de_planta.loc[:, 'vida_util'].max()
    # Obtengo el estado de mar final de la simulacion
    h_fin_sim = vu*365*(24/cadencia)
    h_fin_sim = int(h_fin_sim)

    tramo = list(clima_tramos.keys())[0]

    if h_fin_sim > clima_tramos[tramo].shape[0]:
        h_fin_sim = clima_tramos[tramo].shape[0]
        logging.error(
            'La serie histórica es demasiado corta')

    return h_fin_sim


def inicializacion_matrices_grado_averia(de_esquema_division_dique, h_fin_sim):

    # Matriz de inicio_averia_destruccion_total
    columnas = ['ini_averia', 'dest_total']
    # Inicializar las matrices de grado de averia para el dique
    indices = ['dique']
    ia_dique = pd.DataFrame(0, index=indices, columns=columnas)
    # Inicializar las matrices de grado de averia para los tramos
    indices = de_esquema_division_dique.loc[:, 'tramo'].unique()
    ia_tramos = pd.DataFrame(0, index=indices, columns=columnas)
    # Inicializar las matrices de grado de averia para los subsistemas
    valores_indice = de_esquema_division_dique.iloc[:, 0:2]
    valores_indice = valores_indice.drop_duplicates()
    tuples = [tuple(x) for x in valores_indice.values]
    indices = pd.MultiIndex.from_tuples(tuples, names=['tr', 'ss'])
    ia_subsistemas = pd.DataFrame(0, index=indices, columns=columnas)
    ia_subsistemas.sort_index(inplace=True)
    # Inicializar las matrices de grado de averia para los modos de fallo
    valores_indice = de_esquema_division_dique
    tuples = [tuple(x) for x in valores_indice.values]
    indices = pd.MultiIndex.from_tuples(tuples, names=['tr', 'ss', 'mf'])
    ia_modos_fallo = pd.DataFrame(0, index=indices, columns=columnas)
    ia_modos_fallo.sort_index(inplace=True)

    # Matriz de porcentaje de evolucion de averia de los modos de fallo
    columnas = range(0, h_fin_sim)
    valores_indice = de_esquema_division_dique
    tuples = [tuple(x) for x in valores_indice.values]
    indices = pd.MultiIndex.from_tuples(tuples, names=['tr', 'ss', 'mf'])
    averia_estado = pd.DataFrame(0, index=indices, columns=columnas)
    averia_estado.sort_index(inplace=True)

    averia_acum_estado = pd.DataFrame(0, index=indices, columns=columnas)
    averia_acum_estado.sort_index(inplace=True)

    estado_modos_fallo = pd.DataFrame(np.nan, index=indices, columns=columnas)
    estado_modos_fallo.sort_index(inplace=True)

    origen_maquinaria_reparacion_estado = pd.DataFrame(np.nan, index=indices, columns=columnas)
    origen_maquinaria_reparacion_estado.sort_index(inplace=True)

    origen_materiales_reparacion_estado = pd.DataFrame(np.nan, index=indices, columns=columnas)
    origen_materiales_reparacion_estado.sort_index(inplace=True)

    origen_mano_obra_reparacion_estado = pd.DataFrame(np.nan, index=indices, columns=columnas)
    origen_mano_obra_reparacion_estado.sort_index(inplace=True)

    # Para seleccionar
    # averia_estado.loc[(slice(None), slice(None), ['MF_10', 'MF_15']), 'ini_averia'] = 1

    # Listado de modos de fallo, subsistemas y tramos
    subsistemas = de_esquema_division_dique.loc[:, 'subsistema']
    subsistemas = subsistemas.drop_duplicates()
    subsistemas.reset_index(drop=True)

    tramos = de_esquema_division_dique.loc[:, 'tramo']
    tramos = tramos.drop_duplicates()
    tramos.reset_index(drop=True)

    modos_fallo = de_esquema_division_dique.loc[:, 'modo_fallo']
    modos_fallo = modos_fallo.drop_duplicates()
    modos_fallo.reset_index(drop=True)

    # Matriz con el estado de si el modo esta en reparacion o no
    valores_indice = de_esquema_division_dique
    tuples = [tuple(x) for x in valores_indice.values]
    indices = pd.MultiIndex.from_tuples(tuples, names=['tr', 'ss', 'mf'])
    columnas = ['reparando', 't_rep']
    estado_reparacion_modos = pd.DataFrame(np.nan, index=indices, columns=columnas)

    # Matriz con los inicios de averia por modos
    columnas = modos_fallo.copy()
    columnas.iloc[-1] = 'clima'

    datos_salida_prob_ini_averia = pd.DataFrame(0, index=modos_fallo, columns=columnas.values)

    # Matriz con algunos datos de salida por modos, subsistemas y tramos
    columnas = ['vida_util', 'n_veces_ia', 'n_veces_dest_total', 'prob_ia', 'n_veces_danno', 'n_veces_ini_rep']
    datos_salida_modos = pd.DataFrame(0, index=modos_fallo.values, columns=columnas)
    datos_salida_subsistemas = pd.DataFrame(0, index=subsistemas.values, columns=columnas)
    datos_salida_tramos = pd.DataFrame(0, index=tramos.values, columns=columnas)
    datos_salida_dique = pd.DataFrame(0, index=['dique'], columns=columnas)
    datos_salida = {'datos_salida_modos': datos_salida_modos, 'datos_salida_subsistemas': datos_salida_subsistemas,
                    'datos_salida_tramos': datos_salida_tramos, 'datos_salida_dique': datos_salida_dique}

    # Matrices con los inicios y finales de reparacion
    valores_indice = de_esquema_division_dique
    tuples = [tuple(x) for x in valores_indice.values]
    indices = pd.MultiIndex.from_tuples(tuples, names=['tr', 'ss', 'mf'])
    columnas = [0]
    ini_reparacion = pd.DataFrame(np.nan, index=indices, columns=columnas)
    fin_reparacion = pd.DataFrame(np.nan, index=indices, columns=columnas)

    return (ia_dique, ia_tramos, ia_subsistemas, ia_modos_fallo, averia_estado, averia_acum_estado, estado_modos_fallo,
            subsistemas, tramos, modos_fallo, estado_reparacion_modos, origen_maquinaria_reparacion_estado,
            origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado, datos_salida,
            datos_salida_prob_ini_averia, ini_reparacion, fin_reparacion)


def estado_de_mar_tramo(clima_tramos, tr, h):
    hs = clima_tramos[tr].loc[clima_tramos[tr].index[h], 'hs']
    tp = clima_tramos[tr].loc[clima_tramos[tr].index[h], 'tp']
    u10 = clima_tramos[tr].loc[clima_tramos[tr].index[h], 'vv']
    z = clima_tramos[tr].loc[clima_tramos[tr].index[h], 'calado']

    p90 = np.percentile(clima_tramos[tr].loc[:, 'hs'], 90)  # Para la separacion en ciclos

    return(hs, tp, u10, z, p90)


def calcula_h_eq_n_olas(hs, tp, cadencia):
    # Se obtienen los datos del estado de mar para el tramo

    tm = tp/1.25

#    if tm < 10:
#        tm = 10

    h_eq = hs
    n_olas = (cadencia*3600)/tm
    return(h_eq, n_olas)


def calcula_danno(averia_estado, averia_acum_estado, h_eq, n_olas, tr, ss, mf, h, datos_salida, alcance,
                  de_tipo_verificacion, de_verificacion_tramos, peralte, de_planta, tp):
    # Se calcula el danno con las curvas 3D de evolucion de danno.


#   METODO SINTETICO
#    if (alcance == 'EA_sencillo'):
#        danno = 1  # Diseno a ELU (IA = DT)
#    elif ((alcance != 'PI') & (alcance != 'EA_sencillo')):
#        danno = random.randint(1, 2)/250
#    elif alcance == 'PI':
#        danno = random.randint(1, 2)/2500

#   METODO REAL

    if de_tipo_verificacion.loc[(tr, ss, mf), 'tipo_diseno'] == 'elu':
        averia_estado.loc[(tr, ss, mf), h] = 0.95
        averia_acum_estado.loc[(tr, ss, mf), h] = averia_acum_estado.loc[(tr, ss, mf), h - 1] + averia_estado.loc[(tr, ss, mf), h]

    elif de_tipo_verificacion.loc[(tr, ss, mf), 'tipo_diseno'] == 'els':

        # parametros de la ecuacion de acumulcion
        a = de_tipo_verificacion.loc[(tr, ss, mf), 'par_a']
        b = de_tipo_verificacion.loc[(tr, ss, mf), 'par_b']
        c = de_tipo_verificacion.loc[(tr, ss, mf), 'par_c']

        # Calculo del peralate
        k = wavnum(tp, de_planta.loc[de_planta.index[0], 'calado'])
        wavelen = 2 * np.pi / k
        per = h_eq/wavelen

        # Elimino los peraltes mayor que 1/7 por criterio de rotura
        if per > 0.14:
            per = 0.14
        elif per < 0:
            per = 0


        # Compruebo el dano
        dano = (((a*(per**c))**(1/b))*n_olas)**b

        # Si dano mayor que un 20% es porque el periodo es demasiado bajo y el numero de olas se dispara. Esto es debido a fallos en la simulacion numerica del clima y tenemos que corregirlo
        if (dano > 0.2) & (tp < 6):
            # Se recalcula el numero de olas aumentando el periodo
            tp = tp+2
            # Calculo n_olas
            n_olas = (3 * 3600) / (tp/1.25)

            # Calculo del peralate
            k = wavnum(tp, de_planta.loc[de_planta.index[0], 'calado'])
            wavelen = 2 * np.pi / k
            per = h_eq / wavelen

            dano = (((a * (per ** c)) ** (1 / b)) * n_olas) ** b

            if (dano > 0.2):
                # Se recalcula el numero de olas aumentando el periodo
                tp = tp+3
                # Calculo n_olas
                n_olas = (3 * 3600) / (tp / 1.25)

                # Calculo del peralate
                k = wavnum(tp, de_planta.loc[de_planta.index[0], 'calado'])
                wavelen = 2 * np.pi / k
                per = h_eq / wavelen

                dano = (((a * (per ** c)) ** (1 / b)) * n_olas) ** b


        # dano en el estado
        averia_estado.loc[(tr, ss, mf), h] = (((a*(per**c))**(1/b))*n_olas)**b

        # danno acumulado
        averia_acum_estado.loc[(tr, ss, mf), h] = (((averia_acum_estado.loc[(tr, ss, mf), h])**(1/b)) + ((a*(per**c))**(1/b))*n_olas)**b

        logging.info('a: ' + str(a) + ' b: ' + str(b) + ' c: ' + str(
            c) + ' peralte: ' + str(per) + ' n_olas: ' + str(n_olas) + ' averia_estado: ' + str(
            averia_estado.loc[(tr, ss, mf), h]) + ' averia_acumulada: ' + str(averia_acum_estado.loc[(tr, ss, mf), h]))


    if averia_acum_estado.loc[(tr, ss, mf), h] > 1:
        averia_estado.loc[(tr, ss, mf), h] = 1 - averia_acum_estado.loc[(tr, ss, mf), h - 1]
        averia_acum_estado.loc[(tr, ss, mf), h] = 1

    danno = averia_estado.loc[(tr, ss, mf), h]
    danno_acumulado = averia_acum_estado.loc[(tr, ss, mf), h]


    # Se actualizan los valores de salida
    datos_salida['datos_salida_modos'].loc[mf, 'n_veces_danno'] += 1
    datos_salida['datos_salida_subsistemas'].loc[ss, 'n_veces_danno'] += 1
    datos_salida['datos_salida_tramos'].loc[tr, 'n_veces_danno'] += 1
    datos_salida['datos_salida_dique'].loc['dique', 'n_veces_danno'] += 1

    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
        ss) + ' Modo_fallo: ' + str(mf) + ' Danno sufrido en el estado: ' + str(danno))

    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
        ss) + ' Modo_fallo: ' + str(mf) + ' Nivel de averia acumulado: ' + str(danno_acumulado))

    return(averia_estado, averia_acum_estado, datos_salida)


def calcula_inicio_averia_de_modos_asociados(h, ia_modos_fallo, de_arbol_fallo, tr, ss, mf, de_esquema_division_dique,
                                             datos_salida, averia_acum_estado,
                                             datos_salida_prob_ini_averia):

    # Extraccion de modos relacionados
    modos_rel = ast.literal_eval(de_arbol_fallo.loc[(tr, ss, mf), 'modos'])
    na_modos_rel = ast.literal_eval(de_arbol_fallo.loc[(tr, ss, mf), 'nivel_averia'])
    na_modo_estado = averia_acum_estado.loc[(tr, ss, mf), h]

    # Si la lista no esta vacia
    if modos_rel:
        cont = 0
        for modos in modos_rel:
            # Si el nivel de averia del modo es superior a lo niveles de averia del arbol para iniciar el fallo
            if na_modo_estado >= na_modos_rel[cont]:
                # Si el nivel de averia del modo aun no se ha iniciado
                if all(ia_modos_fallo.loc[(slice(None), slice(None), modos), 'ini_averia'] == 0):
                    # Se annade +1 a los inicio de averia del modo, subsistema y tramo
                    indices = ia_modos_fallo.loc[(slice(None), slice(None), modos), :].index[0]
                    datos_salida['datos_salida_modos'].loc[indices[2], 'n_veces_ia'] += 1
                    datos_salida['datos_salida_subsistemas'].loc[indices[1], 'n_veces_ia'] += 1
                    datos_salida['datos_salida_tramos'].loc[indices[0], 'n_veces_ia'] += 1
                    datos_salida['datos_salida_dique'].loc['dique', 'n_veces_ia'] += 1

                    # Se añade tambien a la matriz de datos de salida de inicios de averia
                    datos_salida_prob_ini_averia.loc[modos, mf] += 1

                    ia_modos_fallo.loc[(slice(None), slice(None), modos), 'ini_averia'] = 1

                    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                        ss) + ' Modo_fallo: ' + str(mf) + ' Inicio de averia en los modos relacionados: ' + str(modos_rel))

            cont += 1


    #                Acceso por indice (antiguo)
    #                averia_estado.loc[(slice(None), slice(None), ['MF_10', 'MF_15']), 'ini_averia'] = 1
    #                pos = de_esquema_division_dique[de_esquema_division_dique.loc[:, 'modo_fallo'] == modos].index[0]
    #                posicion = tuple(de_esquema_division_dique.iloc[pos, :])
    #                ia_modos_fallo.loc[(posicion), 'ini_averia'] = 1

    return (ia_modos_fallo, datos_salida, datos_salida_prob_ini_averia)


def calcula_si_inicio_de_averia(clima_tramos, h_eq, n_olas, ia_modos_fallo, tr, ss, mf, h, de_verificacion_tramos,
                                datos_salida, datos_salida_prob_ini_averia):

    # Inicializo
    ini_averia = False

    # ini_averia = de_verificacion_tramos.loc[h, (tr, ss, mf)]

    # Forma determinista, nunca dejo que falle el MF_1 porque es el que me produce DT
#    if h_eq >= np.percentile(clima_tramos[tr].loc[:, 'hs'], 91):
#        if mf == 'MF_1':
#            ini_averia = 0
#        else:
#            ini_averia = 1

    # Forma aleatoria
    if (mf == 'MF_1'):
        if h_eq >= np.percentile(clima_tramos[tr].loc[:, 'hs'], 99.9):
            umb = 0.8
            ini_averia1 = round(np.random.uniform(0, 1), 2)

            if (ini_averia1 > umb):
                ini_averia = True
                logging.info('Falla el MF_1')
            else:
                ini_averia = False

    elif (mf == 'MF_3'):
        if h_eq >= np.percentile(clima_tramos[tr].loc[:, 'hs'], 99.9):
            umb = 0.8
            ini_averia1 = round(np.random.uniform(0, 1), 2)
            ini_averia2 = round(np.random.uniform(0, 1), 2)
            ini_averia3 = round(np.random.uniform(0, 1), 2)

            if ((ini_averia1 > umb) & (ini_averia2 > umb) & (ini_averia3 > umb)):
                ini_averia = True
                logging.info('Falla el MF_1')
            else:
                ini_averia = False

    elif (mf == 'MF_2'):
        ini_averia1 = False

    if ini_averia == True:
        if all(ia_modos_fallo.loc[(slice(None), slice(None), mf), 'ini_averia'] == 0):
            # Se annade +1 a los inicio de averia del modo, subsistema y tramo
            datos_salida['datos_salida_modos'].loc[mf, 'n_veces_ia'] += 1
            datos_salida['datos_salida_subsistemas'].loc[ss, 'n_veces_ia'] += 1
            datos_salida['datos_salida_tramos'].loc[tr, 'n_veces_ia'] += 1
            datos_salida['datos_salida_dique'].loc['dique', 'n_veces_ia'] += 1

            # Se añade tambien a la matriz de datos de salida de inicios de averia
            datos_salida_prob_ini_averia.loc[mf, 'clima'] += 1

        ia_modos_fallo.loc[(slice(None), slice(None), mf), 'ini_averia'] = 1

    return(ia_modos_fallo, datos_salida, datos_salida_prob_ini_averia)


def extraccion_datos_reparacion_de_diccionario(
        fila, mat_entrada, mat_salida, col_mat_entrada, col_tipos_salida, col_num_salida, num_cant, t_ini,
        col_tiempo_salida, col_coste_salida, cadencia, col_umb_ope_entrada='', col_umb_ope_salida='',
        col_rend_entrada='', col_rend_salida=''):

    dic = ast.literal_eval(mat_entrada.loc[mat_entrada.index[fila], col_mat_entrada])
    tipos = dic.keys()
    num = []
    tiempo = []
    lista_hs = []
    lista_vv = []
    lista_nivel = []
    lista_calado = []
    coste = []

    for tipo in tipos:
        if col_mat_entrada == 'maquinaria_reparacion':
            hs = dic[tipo]['umb_ope']['hs']
            vv = dic[tipo]['umb_ope']['vv']
            nivel = dic[tipo]['umb_ope']['nivel']
            calado = dic[tipo]['umb_ope']['calado']
            coste_unit = dic[tipo]['coste_maq']
        elif col_mat_entrada == 'materiales_reparacion':
            coste_unit = dic[tipo]['coste_mat']
        elif col_mat_entrada == 'mano_obra_reparacion':
            coste_unit = dic[tipo]['coste_mo']



        numero = dic[tipo][num_cant]
        t = dic[tipo][t_ini]

        if col_mat_entrada == 'materiales_reparacion':
            coste_tot_elem = coste_unit
        else:
            coste_tot_elem = coste_unit*numero


        num.append(numero)
        tiempo.append(t)
        coste.append(coste_tot_elem)

        if col_mat_entrada == 'maquinaria_reparacion':
            lista_hs.append(hs)
            lista_vv.append(vv)
            lista_nivel.append(nivel)
            lista_calado.append(calado)

    # El tiempo mas restrictivo es el maximo
    tiempo = max(tiempo)
    coste_tot = sum(coste)

    if col_mat_entrada != 'materiales_reparacion':
        # Se pasa de euros/hora a euros/estado
        coste_tot = coste_tot*cadencia

    if col_mat_entrada == 'maquinaria_reparacion':
        # La hs mas restrictiva es la minima
        hs = min(lista_hs)
        # La vv mas restrictiva es la minima
        vv = min(lista_vv)
        # El nivel mas restrictivo es el minimo
        nivel = min(lista_nivel)
        # El calado mas restrictivo es el maximo
        calado = max(lista_calado)

    mat_salida.loc[mat_salida.index[fila], col_tipos_salida] = tipos
    mat_salida.loc[mat_salida.index[fila], col_num_salida] = num
    mat_salida.loc[mat_salida.index[fila], col_tiempo_salida] = tiempo
    mat_salida.loc[mat_salida.index[fila], col_coste_salida] = coste_tot

    if col_mat_entrada == 'maquinaria_reparacion':
        mat_salida.loc[mat_salida.index[fila], col_umb_ope_salida] = str({'hs': hs, 'vv': vv, 'nivel': nivel, 'calado': calado})

    return(mat_salida)


def extraccion_datos_reparacion_disponibles_de_diccionario(
        mat_entrada, mat_salida, col_mat_entrada, col_tipos_salida, col_num_salida, num_cant, col_coste_salida,
        fila_salida, fila_salida2, cadencia):

    dic = ast.literal_eval(mat_entrada.loc[mat_entrada.index[0], col_mat_entrada])
    tipos = dic.keys()
    num = []
    coste = []

    for tipo in tipos:
        numero = dic[tipo][num_cant]
        num.append(numero)
        if col_mat_entrada == 'maquinaria_disponible':
            coste_unit = dic[tipo]['coste_maq']
        elif col_mat_entrada == 'materiales_disponibles':
            coste_unit = dic[tipo]['coste_mat']
        elif col_mat_entrada == 'mano_obra_disponible':
            coste_unit = dic[tipo]['coste_mo']

        if col_mat_entrada == 'materiales_disponibles':
            coste_tot_elem = coste_unit
        else:
            coste_tot_elem = coste_unit*numero

        coste.append(coste_tot_elem)

    coste_tot = sum(coste)

    if col_mat_entrada != 'materiales_reparacion':
        # Se pasa de euros/hora a euros/estado
        coste_tot = coste_tot*cadencia

    mat_salida.loc[fila_salida, col_tipos_salida] = tipos
    mat_salida.loc[fila_salida, col_num_salida] = num
    mat_salida.loc[fila_salida, col_coste_salida] = coste_tot

    mat_salida.loc[fila_salida2, col_tipos_salida] = tipos
    mat_salida.loc[fila_salida2, col_num_salida] = num

    return(mat_salida)


def calcula_tiempo_necesario_para_iniciar_reparacion(tr, ss, mf, de_reparacion_necesarios, de_reparacion_disponibles,
                                                     origen_maquinaria_reparacion_estado,
                                                     origen_materiales_reparacion_estado,
                                                     origen_mano_obra_reparacion_estado, h, alcance):

    if alcance == 'PI':

        # Tiempo necesario para maquinaria
        num = 'num_maq'
        tipos = 'tipos_maq'
        t_ini = 't_maq_ini_rep'
        t_maq_ini_rep = calcula_tiempo_necesario_para_iniciar_reparacion_elemento(tr, ss, mf, de_reparacion_necesarios,
                                                                                  de_reparacion_disponibles, num, tipos,
                                                                                  t_ini,
                                                                                  origen_maquinaria_reparacion_estado, h)

        # Tiempo necesario para materiales
        num = 'cant_mat'
        tipos = 'tipos_mat'
        t_ini = 't_mat_ini_rep'
        t_mat_ini_rep = calcula_tiempo_necesario_para_iniciar_reparacion_elemento(tr, ss, mf, de_reparacion_necesarios,
                                                                                  de_reparacion_disponibles, num, tipos,
                                                                                  t_ini,
                                                                                  origen_materiales_reparacion_estado, h)

        # Tiempo necesario para mano de obra
        num = 'num_mo'
        tipos = 'tipos_mo'
        t_ini = 't_mo_ini_rep'
        t_mo_ini_rep = calcula_tiempo_necesario_para_iniciar_reparacion_elemento(tr, ss, mf, de_reparacion_necesarios,
                                                                                  de_reparacion_disponibles, num, tipos,
                                                                                  t_ini,
                                                                                  origen_mano_obra_reparacion_estado, h)

        t_ini_rep = max([t_maq_ini_rep, t_mat_ini_rep, t_mo_ini_rep])

    elif (alcance == 'AP'):
        t_ini_rep = 0  # En anteproyecto considero disponibilidad infinita de medios de reparacion

        # Indico que los elementos de reparacion se toman de puerto
        origen_maquinaria_reparacion_estado.loc[(tr, ss, mf), h] = c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION
        origen_materiales_reparacion_estado.loc[(tr, ss, mf), h] = c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION
        origen_mano_obra_reparacion_estado.loc[(tr, ss, mf), h] = c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION

    elif ((alcance == 'EA') | (alcance == 'EA_sencillo')):
        t_ini_rep = de_reparacion_necesarios.loc[(tr, ss, mf), 't_espera_ini_reparacion']

        # Indico que los elementos de reparacion se toman de puerto
        origen_maquinaria_reparacion_estado.loc[(tr, ss, mf), h] = c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION
        origen_materiales_reparacion_estado.loc[(tr, ss, mf), h] = c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION
        origen_mano_obra_reparacion_estado.loc[(tr, ss, mf), h] = c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION

    return(t_ini_rep)


def calcula_tiempo_necesario_para_iniciar_reparacion_elemento(tr, ss, mf, de_reparacion_necesarios,
                                                              de_reparacion_disponibles, num, tipos, t_ini,
                                                              matriz_origen_reparacion, h):
    # Primero compruebo si todos los tipos de maquinaria estan disposibles en el puerto
    elementos_necesarios = pd.DataFrame(
        de_reparacion_necesarios.loc[(tr, ss, mf), num], index=de_reparacion_necesarios.loc[(
            tr, ss, mf), tipos], columns=['cantidad'])

    elementos_disponibles = pd.DataFrame(
        de_reparacion_disponibles.loc['disponibles', num], index=de_reparacion_disponibles.loc[
            'disponibles', tipos], columns=['cantidad'])

    # Si se cumple que toda la maquinaria necesaria esta en el puerto
    if all([i in list(elementos_disponibles.index.values) for i in list(elementos_necesarios.index.values)]):
        # Se comprueba si hay cantidad suficiente
        if all([i[1].cantidad <= elementos_disponibles.loc[i[0], 'cantidad'] for i in elementos_necesarios.iterrows()]):
            # El tiempo necesario para iniciar la reparacion de ese elemento es 0
            t_elem_ini_rep = 0
            # Indico que los elementos de reparacion se toman de puerto
            matriz_origen_reparacion.loc[(tr, ss, mf), h] = c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION
            # Actualizo los elementos restantes que quedan disponibles en puerto
            de_reparacion_disponibles = \
                calcula_elementos_reparacion_restantes_en_puerto_al_inicio(elementos_disponibles, elementos_necesarios,
                                                                           num, de_reparacion_disponibles)


        # Si no hay elementos suficiente el tiempo necesario de inicio de maq es el contratcion
        else:
            t_elem_ini_rep = de_reparacion_necesarios.loc[(tr, ss, mf), t_ini]
            matriz_origen_reparacion.loc[(tr, ss, mf), h] = c.MODO_CONTRATA_ELEMENTO_REPARACION
    # Si no hay maquinaria suficiente el tiempo necesario de inicio de maq es el contratcion
    else:
        t_elem_ini_rep = de_reparacion_necesarios.loc[(tr, ss, mf), t_ini]
        matriz_origen_reparacion.loc[(tr, ss, mf), h] = c.MODO_CONTRATA_ELEMENTO_REPARACION

    return(t_elem_ini_rep)


def calcula_elementos_reparacion_restantes_en_puerto_al_inicio(elementos_disponibles, elementos_necesarios, num,
                                                               de_reparacion_disponibles):

    for i in elementos_necesarios.iterrows():
        elementos_disponibles.loc[i[0], 'cantidad'] = \
            elementos_disponibles.loc[i[0], 'cantidad'] - i[1].cantidad

    de_reparacion_disponibles.loc['disponibles', num] = list(elementos_disponibles.loc[:, 'cantidad'])

    return(de_reparacion_disponibles)


def calcula_elementos_reparacion_restantes_en_puerto_al_final(tr, ss, mf, h, de_reparacion_necesarios,
                                                              de_reparacion_disponibles,
                                                              origen_maquinaria_reparacion_estado,
                                                              origen_mano_obra_reparacion_estado):
    # Maquinaria
    if origen_maquinaria_reparacion_estado.loc[(tr, ss, mf), h] == c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION:

        elementos_necesarios = pd.DataFrame(
            de_reparacion_necesarios.loc[(tr, ss, mf), 'num_maq'], index=de_reparacion_necesarios.loc[(
                tr, ss, mf), 'tipos_maq'], columns=['cantidad'])

        elementos_disponibles = pd.DataFrame(
            de_reparacion_disponibles.loc['disponibles', 'num_maq'], index=de_reparacion_disponibles.loc[
                'disponibles', 'tipos_maq'], columns=['cantidad'])

        for i in elementos_necesarios.iterrows():
            elementos_disponibles.loc[i[0], 'cantidad'] = \
                elementos_disponibles.loc[i[0], 'cantidad'] + i[1].cantidad

        de_reparacion_disponibles.loc['disponibles', 'num_maq'] = list(elementos_disponibles.loc[:, 'cantidad'])


    # Mano de obra
    if origen_mano_obra_reparacion_estado.loc[(tr, ss, mf), h] == c.MODO_UTILIZA_ELEMENTO_PUERTO_REPARACION:

        elementos_necesarios = pd.DataFrame(
            de_reparacion_necesarios.loc[(tr, ss, mf), 'num_mo'], index=de_reparacion_necesarios.loc[(
                tr, ss, mf), 'tipos_mo'], columns=['cantidad'])

        elementos_disponibles = pd.DataFrame(
            de_reparacion_disponibles.loc['disponibles', 'num_mo'], index=de_reparacion_disponibles.loc[
                'disponibles', 'tipos_mo'], columns=['cantidad'])

        for i in elementos_necesarios.iterrows():
            elementos_disponibles.loc[i[0], 'cantidad'] = \
                elementos_disponibles.loc[i[0], 'cantidad'] + i[1].cantidad

        de_reparacion_disponibles.loc['disponibles', 'num_mo'] = list(elementos_disponibles.loc[:, 'cantidad'])

    return(de_reparacion_disponibles)


def calcula_nivel_averia_reparado(tr, ss, mf, de_reparacion_necesarios, averia_estado,
                                  averia_acum_estado, cadencia, h):
    # Rendimiento de reparacion por hora
    rend_hora = de_reparacion_necesarios.loc[(tr, ss, mf), 'rend']
    # Rendimiento por estado
    rend_estado = rend_hora*cadencia
    # Actualizacion de los niveles de averia
    averia_estado.loc[(tr, ss, mf), h] = -rend_estado
    # averia_acum_estado.loc[(tr, ss, mf), h] = sum(averia_estado.loc[(tr, ss, mf), :])
    averia_acum_estado.loc[(tr, ss, mf), h] = averia_acum_estado.loc[(tr, ss, mf), h - 1] - rend_estado

    # Si la reparacion me desciende por debajo del nivel de averia 0, lo limito a 0
    if averia_acum_estado.loc[(tr, ss, mf), h] < 0:
        averia_estado.loc[(tr, ss, mf), h] = -averia_acum_estado.loc[(tr, ss, mf), h-1]
        # averia_acum_estado.loc[(tr, ss, mf), h] = sum(averia_estado.loc[(tr, ss, mf), :])
        averia_acum_estado.loc[(tr, ss, mf), h] = 0

    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
        ss) + ' Modo_fallo: ' + str(mf) + ' Nivel de averia acumulado: ' + str(
        averia_acum_estado.loc[(tr, ss, mf), h]))

    return(averia_estado, averia_acum_estado)


def actuliza_nivel_de_averia(averia_estado, averia_acum_estado, tr, ss, mf, h):

    # Actualizacion de los niveles de averia
    averia_acum_estado.loc[(tr, ss, mf), h] = averia_acum_estado.loc[(tr, ss, mf), h - 1]


    logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
    ss) + ' Modo_fallo: ' + str(mf) + ' Nivel de averia acumulado: ' + str(averia_acum_estado.loc[(tr, ss, mf), h]))

    return(averia_estado, averia_acum_estado)

def actualiza_origen_elementos_reparacion(origen_maquinaria_reparacion_estado,
                                                               origen_materiales_reparacion_estado,
                                                               origen_mano_obra_reparacion_estado,
                                                               tr, ss, mf, h):


    serie = origen_maquinaria_reparacion_estado.loc[(tr, ss, mf), :]
    valor_maq = lectura_ultimo_valor_distinto_nan_en_series(serie)
    origen_maquinaria_reparacion_estado.loc[(tr, ss, mf), h] = valor_maq

    serie = origen_materiales_reparacion_estado.loc[(tr, ss, mf), :]
    valor_mat = lectura_ultimo_valor_distinto_nan_en_series(serie)
    origen_materiales_reparacion_estado.loc[(tr, ss, mf), h] = valor_mat

    serie = origen_mano_obra_reparacion_estado.loc[(tr, ss, mf), :]
    valor_mo = lectura_ultimo_valor_distinto_nan_en_series(serie)
    origen_mano_obra_reparacion_estado.loc[(tr, ss, mf), h] = valor_mo

    return(origen_maquinaria_reparacion_estado, origen_materiales_reparacion_estado,
           origen_mano_obra_reparacion_estado)


def lectura_ultimo_valor_distinto_nan_en_series(serie):
    serie_sin_nan = serie.dropna()
    valor = serie_sin_nan.iloc[-1]

    return(valor)


def extraccion_resultados(datos_salida, datos_salida_prob_ini_averia, de_planta, estado_modos_fallo, h_fin_sim,
                          ruta_ds, cadencia, ini_reparacion, fin_reparacion, averia_acum_estado):

    # Guardado de la averia acumulada en cada estado
    direct = os.path.join(ruta_ds, 'danno_mf_estado.html')
    averia_acum_estado.to_html(direct, sparsify=False)
    direct = os.path.join(ruta_ds, 'danno_mf_estado.csv')
    averia_acum_estado.to_csv(direct, sep='\t')

    # Correccion de los datos de salida
    # 1. sustituyo los valores de 0 en vida util por la vida util real de la obra
    datos_salida['datos_salida_modos'].loc[:, 'vida_util'].replace([0], [de_planta.loc[de_planta.index[0], 'vida_util']], inplace=True)
    datos_salida['datos_salida_subsistemas'].loc[:, 'vida_util'].replace([0], [de_planta.loc[de_planta.index[0], 'vida_util']], inplace=True)
    datos_salida['datos_salida_tramos'].loc[:, 'vida_util'].replace([0], [de_planta.loc[de_planta.index[0], 'vida_util']], inplace=True)
    datos_salida['datos_salida_dique'].loc[:, 'vida_util'].replace([0], [de_planta.loc[de_planta.index[0], 'vida_util']], inplace=True)

    # 2. calculo la probabilidad de inicio de averia
    datos_salida['datos_salida_modos'].loc[:, 'prob_ia'] = datos_salida['datos_salida_modos'].loc[:, 'n_veces_ia']/float(h_fin_sim*cadencia)
    datos_salida['datos_salida_subsistemas'].loc[:, 'prob_ia'] = datos_salida['datos_salida_subsistemas'].loc[:, 'n_veces_ia']/float(h_fin_sim*cadencia)
    datos_salida['datos_salida_tramos'].loc[:, 'prob_ia'] = datos_salida['datos_salida_tramos'].loc[:, 'n_veces_ia']/float(h_fin_sim*cadencia)
    datos_salida['datos_salida_dique'].loc[:, 'prob_ia'] = datos_salida['datos_salida_dique'].loc[:, 'n_veces_ia']/float(h_fin_sim*cadencia)

    # 3. calcula la probabilidad de sufrir dannos
    datos_salida['datos_salida_modos'].loc[:, 'prob_sufrir_danno'] = datos_salida['datos_salida_modos'].loc[:, 'n_veces_danno']/float(h_fin_sim*cadencia)
    datos_salida['datos_salida_subsistemas'].loc[:, 'prob_sufrir_danno'] = datos_salida['datos_salida_subsistemas'].loc[:, 'n_veces_danno']/float(h_fin_sim*cadencia)
    datos_salida['datos_salida_tramos'].loc[:, 'prob_sufrir_danno'] = datos_salida['datos_salida_tramos'].loc[:, 'n_veces_danno']/float(h_fin_sim*cadencia)
    datos_salida['datos_salida_dique'].loc[:, 'prob_sufrir_danno'] = datos_salida['datos_salida_dique'].loc[:, 'n_veces_danno']/float(h_fin_sim*cadencia)

    # 4. calcula probabilidad de parada operativa durante la reparacion
    for modo in estado_modos_fallo.iterrows():
        n_horas = modo[1].value_counts()
        tr = modo[0][0]
        ss = modo[0][1]
        mf = modo[0][2]
        if c.MODO_NO_REPARA_OPERATIVIDAD in n_horas.index.values:
            n_veces_operatividad = n_horas[2]
            datos_salida['datos_salida_modos'].loc[mf, 'n_veces_parada_operativa'] = n_veces_operatividad
            datos_salida['datos_salida_modos'].loc[mf, 'prob_parada_operativa'] = n_veces_operatividad/float(h_fin_sim)

    # 4.5 calcula duracion total de las reparaciones desde que se da la orden hasta que se repara
    # Creacion de un dataframe de salida
    datos_salida_reparacion = pd.DataFrame(-1, index=ini_reparacion.index, columns=['t_rep_medio', 't_rep_minimo',
                                                                                      't_rep_maximo'])

    for modo in ini_reparacion.iterrows():
        ini_averia = modo[1]
        ini_averia.dropna(inplace=True)

        fin_averia = fin_reparacion.loc[modo[0], :]
        fin_averia.dropna(inplace=True)

        # Comprobaciones
        if fin_averia.empty:
            print('Numero de reparaciones acabadas es nulo')
        else:
            # Comprobamos si el numero de finales es igual al numero de inicicios
            if len(fin_averia) != len(ini_averia):
                # Elimino el ultimo valor
                ini_averia = ini_averia[:-1]

            # Hacemos la diferencia
            t_rep = fin_averia.values - ini_averia.values
            t_medio_rep = np.mean(t_rep)*cadencia
            t_max_rep = np.max(t_rep)*cadencia
            t_min_rep = np.min(t_rep)*cadencia

            # Almaceno
            datos_salida_reparacion.loc[modo[0], 't_rep_medio'] = t_medio_rep
            datos_salida_reparacion.loc[modo[0], 't_rep_minimo'] = t_min_rep
            datos_salida_reparacion.loc[modo[0], 't_rep_maximo'] = t_max_rep

    # Guardo como HTML y CSV
    direct = os.path.join(ruta_ds, '0_datos_salida_tiempos_reparacion_modos.html')
    datos_salida_reparacion.to_html(direct, sparsify=False)
    direct = os.path.join(ruta_ds, '0_datos_salida_tiempos_reparacion_modos.csv')
    datos_salida_reparacion.to_csv(direct, sep='\t')

    # 5. duracion de las reparaciones desde que se inicia hasta que se corta por el motivo que sea
    for modo in estado_modos_fallo.iterrows():
        tr = modo[0][0]
        ss = modo[0][1]
        mf = modo[0][2]
        valores = modo[1]

        ini_danno = []
        ini_espera_rep = []
        ini_rep = []
        ini_par_ope = []

        fin_danno = []
        fin_espera_rep = []
        fin_rep = []
        fin_par_ope = []

        for j, _ in enumerate(valores):

            if (j == 0):

                if (valores[j] == c.MODO_SUFRE_DANNOS):
                    ini_danno.append(j)

                if (valores[j] == c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR):
                    ini_espera_rep.append(j)

                if (valores[j] == c.MODO_REPARANDO):
                    ini_rep.append(j)

                if (valores[j] == c.MODO_NO_REPARA_OPERATIVIDAD):
                    ini_par_ope.append(j)

            if ((j != (valores.shape[0] - 1)) & (j != 0)):

                if ((valores[j] == c.MODO_SUFRE_DANNOS) & (
                        valores[j - 1] != c.MODO_SUFRE_DANNOS)):
                    ini_danno.append(j)

                elif ((valores[j] != c.MODO_SUFRE_DANNOS) & (
                        valores[j - 1] == c.MODO_SUFRE_DANNOS)):
                    fin_danno.append(j)

                if ((valores[j] == c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR) & (
                        valores[j - 1] != c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR)):
                    ini_espera_rep.append(j)

                elif ((valores[j] != c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR) & (
                        valores[j - 1] == c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR)):
                    fin_espera_rep.append(j)

                if ((valores[j] == c.MODO_REPARANDO) & (
                        valores[j - 1] != c.MODO_REPARANDO)):
                    ini_rep.append(j)

                elif ((valores[j] != c.MODO_REPARANDO) & (
                        valores[j - 1] == c.MODO_REPARANDO)):
                    fin_rep.append(j)

                if ((valores[j] == c.MODO_NO_REPARA_OPERATIVIDAD) & (
                        valores[j - 1] != c.MODO_NO_REPARA_OPERATIVIDAD)):
                    ini_par_ope.append(j)

                elif ((valores[j] != c.MODO_NO_REPARA_OPERATIVIDAD) & (
                        valores[j - 1] == c.MODO_NO_REPARA_OPERATIVIDAD)):
                    fin_par_ope.append(j)

            if (j == (valores.shape[0] - 1)):

                if ((valores[j] == c.MODO_SUFRE_DANNOS)):
                    fin_danno.append(j)

                elif ((valores[j] != c.MODO_SUFRE_DANNOS) & (
                        valores[j - 1] == c.MODO_SUFRE_DANNOS)):
                    fin_danno.append(j)

                if ((valores[j] == c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR)):
                    fin_espera_rep.append(j)

                elif ((valores[j] != c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR) & (
                        valores[j - 1] == c.MODO_ESPERANDO_PARA_EMPEZAR_REPARAR)):
                    fin_espera_rep.append(j)

                if ((valores[j] == c.MODO_REPARANDO)):
                    fin_rep.append(j)

                elif ((valores[j] != c.MODO_REPARANDO) & (
                        valores[j - 1] == c.MODO_REPARANDO)):
                    fin_rep.append(j)

                if ((valores[j] == c.MODO_NO_REPARA_OPERATIVIDAD)):
                    fin_par_ope.append(j)

                elif ((valores[j] != c.MODO_NO_REPARA_OPERATIVIDAD) & (
                        valores[j - 1] == c.MODO_NO_REPARA_OPERATIVIDAD)):
                    fin_par_ope.append(j)

        ini_danno = np.array(ini_danno)
        ini_espera_rep = np.array(ini_espera_rep)
        ini_rep = np.array(ini_rep)
        ini_par_ope = np.array(ini_par_ope)
        fin_danno = np.array(fin_danno)
        fin_espera_rep = np.array(fin_espera_rep)
        fin_rep = np.array(fin_rep)
        fin_par_ope = np.array(fin_par_ope)

        # Se extrae el número, la media, el maximo, el minimo y la moda de los tres
        n_veces_danno_ini = ini_danno.size
        n_veces_danno_fin = fin_danno.size
        if n_veces_danno_fin == 0:
            dur_danno = 0
            dur_media_danno = 0
            dur_max_danno = 0
            dur_min_danno = 0
        elif ((n_veces_danno_ini == n_veces_danno_fin) & (n_veces_danno_ini != 0)):
            dur_danno = (fin_danno - ini_danno)*cadencia
            dur_media_danno = np.mean(dur_danno)
            dur_max_danno = np.max(dur_danno)
            dur_min_danno = np.min(dur_danno)
        else:
            print('Entradas y salidas de danno no coinciden')
            if ini_danno.size > fin_danno.size:
                ini_danno = ini_danno[0: fin_danno.size]
            elif fin_danno.size > ini_danno.size:
                fin_danno = fin_danno[0: ini_danno.size]
            dur_danno = (fin_danno - ini_danno)*cadencia
            dur_media_danno = np.mean(dur_danno)
            dur_max_danno = np.max(dur_danno)
            dur_min_danno = np.min(dur_danno)

        n_veces_espera_rep_ini = ini_espera_rep.size
        n_veces_espera_rep_fin = fin_espera_rep.size
        if n_veces_espera_rep_fin == 0:
            dur_espera_rep = 0
            dur_media_espera_rep = 0
            dur_max_espera_rep = 0
            dur_min_espera_rep = 0
        elif ((n_veces_espera_rep_ini == n_veces_espera_rep_fin) & (n_veces_espera_rep_ini != 0)):
            dur_espera_rep = (fin_espera_rep - ini_espera_rep)*cadencia
            dur_media_espera_rep = np.mean(dur_espera_rep)
            dur_max_espera_rep = np.max(dur_espera_rep)
            dur_min_espera_rep = np.min(dur_espera_rep)
        else:
            print('Entradas y salidas de espera reparacion no coinciden')
            ini_espera_rep = ini_espera_rep[0: fin_espera_rep.size]
            dur_espera_rep = (fin_espera_rep - ini_espera_rep)*cadencia
            dur_media_espera_rep = np.mean(dur_espera_rep)
            dur_max_espera_rep = np.max(dur_espera_rep)
            dur_min_espera_rep = np.min(dur_espera_rep)


        n_veces_rep_ini = ini_rep.size
        n_veces_rep_fin = fin_rep.size
        if n_veces_rep_fin == 0:
            dur_rep = 0
            dur_media_rep = 0
            dur_max_rep = 0
            dur_min_rep = 0
        elif ((n_veces_rep_ini == n_veces_rep_fin) & (n_veces_rep_ini != 0)):
            dur_rep = (fin_rep - ini_rep)*cadencia
            dur_media_rep = np.mean(dur_rep)
            dur_max_rep = np.max(dur_rep)
            dur_min_rep = np.min(dur_rep)
        else:
            print('Entradas y salidas de n veces reparacion no coinciden')
            ini_rep = ini_rep[0: fin_rep.size]
            dur_rep = (fin_rep - ini_rep)*cadencia
            dur_media_rep = np.mean(dur_rep)
            dur_max_rep = np.max(dur_rep)
            dur_min_rep = np.min(dur_rep)

        n_veces_par_ope_ini = ini_par_ope.size
        n_veces_par_ope_fin = fin_par_ope.size
        if n_veces_par_ope_fin == 0:
            dur_par_ope = 0
            dur_media_par_ope = 0
            dur_max_par_ope = 0
            dur_min_par_ope = 0
        elif ((n_veces_par_ope_ini == n_veces_par_ope_fin) & (n_veces_par_ope_ini != 0)):
            dur_par_ope = (fin_par_ope - ini_par_ope)*cadencia
            dur_media_par_ope = np.mean(dur_par_ope)
            dur_max_par_ope = np.max(dur_par_ope)
            dur_min_par_ope = np.min(dur_par_ope)
        else:
            print('Entradas y salidas de n parada operativa no coinciden')
            ini_par_ope = ini_par_ope[0: fin_par_ope.size]
            dur_par_ope = (fin_par_ope - ini_par_ope)*cadencia
            dur_media_par_ope = np.mean(dur_par_ope)
            dur_max_par_ope = np.max(dur_par_ope)
            dur_min_par_ope = np.min(dur_par_ope)

        # Se almacenan los valores
        datos_salida['datos_salida_modos'].loc[mf, 'dur_media_danno'] = dur_media_danno
        datos_salida['datos_salida_modos'].loc[mf, 'dur_max_danno'] = dur_max_danno
        datos_salida['datos_salida_modos'].loc[mf, 'dur_min_danno'] = dur_min_danno

        datos_salida['datos_salida_modos'].loc[mf, 'dur_media_espera_rep'] = dur_media_espera_rep
        datos_salida['datos_salida_modos'].loc[mf, 'dur_max_espera_rep'] = dur_max_espera_rep
        datos_salida['datos_salida_modos'].loc[mf, 'dur_min_espera_rep'] = dur_min_espera_rep

        datos_salida['datos_salida_modos'].loc[mf, 'dur_media_rep'] = dur_media_rep
        datos_salida['datos_salida_modos'].loc[mf, 'dur_max_rep'] = dur_max_rep
        datos_salida['datos_salida_modos'].loc[mf, 'dur_min_rep'] = dur_min_rep

        datos_salida['datos_salida_modos'].loc[mf, 'dur_media_par_ope'] = dur_media_par_ope
        datos_salida['datos_salida_modos'].loc[mf, 'dur_max_par_ope'] = dur_max_par_ope
        datos_salida['datos_salida_modos'].loc[mf, 'dur_min_par_ope'] = dur_min_par_ope

    # Guardado de resultados
    direct = os.path.join(ruta_ds, '1_datos_salida_modos.html')
    datos_salida['datos_salida_modos'].to_html(direct, sparsify=False)
    direct = os.path.join(ruta_ds, '1_datos_salida_modos.csv')
    datos_salida['datos_salida_modos'].to_csv(direct, sep='\t')

    direct = os.path.join(ruta_ds, '2_datos_salida_subsistemas.html')
    datos_salida['datos_salida_subsistemas'].to_html(direct, sparsify=False)

    direct = os.path.join(ruta_ds, '3_datos_salida_tramos.html')
    datos_salida['datos_salida_tramos'].to_html(direct, sparsify=False)

    direct = os.path.join(ruta_ds, '4_datos_salida_dique.html')
    datos_salida['datos_salida_dique'].to_html(direct, sparsify=False)

    # Matriz de inicios de averia
    direct = os.path.join(ruta_ds, '4_datos_salida_inicios_averia_modos.html')
    datos_salida_prob_ini_averia.to_html(direct, sparsify=False)
    direct = os.path.join(ruta_ds, '4_datos_salida_inicios_averia_modos.csv')
    datos_salida_prob_ini_averia.to_csv(direct, sep='\t')

    return(datos_salida, datos_salida_reparacion)


def calculo_costes(estado_modos_fallo, de_reparacion_necesarios, de_reparacion_disponibles, datos_salida,
                   de_planta, ruta_ds, alcance, estrategia, cadencia):

    datos_salida_modos = -1
    datos_salida_total = -1
    datos_salida_ea_sencillo = -1

    # 6. calculo de costes de reparacion durante la vida util
    if alcance == 'EA_sencillo':
        datos_salida_ea_sencillo = pd.DataFrame(0, index=estado_modos_fallo.index, columns=['costes_reparacion_total', 'costes_reparacion_medio_anual'])

    datos_salida_costes_reparacion_maquinaria = estado_modos_fallo.copy()
    datos_salida_costes_reparacion_mano_obra = estado_modos_fallo.copy()
    datos_salida_costes_reparacion_materiales = pd.DataFrame(0, index=estado_modos_fallo.index.values, columns=['coste_mat_total'])
    datos_salida_costes_rep_total_modos = pd.DataFrame(0, index=estado_modos_fallo.index.values, columns=['coste_rep_total'])

    if alcance == 'EA':
        datos_salida_costes_reparacion_total = estado_modos_fallo.copy()

    for modo in estado_modos_fallo.iterrows():
        tr = modo[0][0]
        ss = modo[0][1]
        mf = modo[0][2]

        if alcance == 'EA_sencillo':
            datos_salida_ea_sencillo.loc[(tr, ss, mf), 'costes_reparacion_total'] = de_reparacion_necesarios.loc[(tr, ss, mf), 'costes_reparacion']*datos_salida['datos_salida_modos'].loc[(mf), 'n_veces_ia']

            if datos_salida_ea_sencillo.loc[(tr, ss, mf), 'costes_reparacion_total'] != 0:
                n_annos_sim = de_planta.loc[de_planta.index[0], 'vida_util']
                datos_salida_ea_sencillo.loc[(tr, ss, mf), 'costes_reparacion_medio_anual'] = datos_salida_ea_sencillo.loc[(tr, ss, mf), 'costes_reparacion_total'] / n_annos_sim
            else:
                datos_salida_ea_sencillo.loc[(tr, ss, mf), 'costes_reparacion_medio_anual'] = 0

        else:

            if alcance == 'EA':
                if estrategia == 'reparacion_inmediata':
                    costes_reparacion_tot = de_reparacion_necesarios.loc[(tr, ss, mf), 'costes_reparacion']
                else:
                    costes_reparacion_tot = de_reparacion_necesarios.loc[(tr, ss, mf), 'costes_reparacion']*cadencia

            else:
                costes_reparacion_maq_unit = de_reparacion_necesarios.loc[(tr, ss, mf), 'coste_maq_rep']*cadencia
                costes_reparacion_mo_unit = de_reparacion_necesarios.loc[(tr, ss, mf), 'coste_mo_rep']*cadencia
                costes_reparacion_mat_unit = de_reparacion_necesarios.loc[(tr, ss, mf), 'coste_mat_rep']

            if alcance == 'PI':
                costes_mantenimiento = de_reparacion_disponibles.loc['iniciales', 'coste_maq_mant'] + \
                    de_reparacion_disponibles.loc['iniciales', 'coste_mat_mant'] + \
                    de_reparacion_disponibles.loc['iniciales', 'coste_mo_mant']
            elif alcance == 'AP':
                costes_mantenimiento = 0


            # Relleno las matrices de costes de maquinaria, mano de obra para cada estado
            if alcance != 'EA':
                fila = datos_salida_costes_reparacion_maquinaria.loc[(tr, ss, mf)].copy()
                fila[(fila != 3) & (fila != 4) & (fila != 5)] = costes_mantenimiento
                fila[(fila == 3) | (fila == 4) | (fila == 5)] = costes_reparacion_maq_unit
                datos_salida_costes_reparacion_maquinaria.loc[(tr, ss, mf)] = fila

                fila = datos_salida_costes_reparacion_mano_obra.loc[(tr, ss, mf)].copy()
                fila[(fila != 3) & (fila != 4) & (fila != 5)] = costes_mantenimiento
                fila[(fila == 3) | (fila == 4) | (fila == 5)] = costes_reparacion_mo_unit
                datos_salida_costes_reparacion_mano_obra.loc[(tr, ss, mf)] = fila

                datos_salida_costes_reparacion_materiales.loc[(tr, ss, mf), 'coste_mat_total'] = costes_reparacion_mat_unit*datos_salida['datos_salida_modos'].loc[mf, 'n_veces_ini_rep']

            elif alcance == 'EA':
                fila = datos_salida_costes_reparacion_maquinaria.loc[(tr, ss, mf)].copy()
                fila[(fila != 3) & (fila != 4) & (fila != 5)] = 0
                fila[(fila == 3) | (fila == 4) | (fila == 5)] = costes_reparacion_tot

                # En EA reparto el coste a partes iguales entre mano de obra y maquinaria

                datos_salida_costes_reparacion_maquinaria.loc[(tr, ss, mf)] = 0
                datos_salida_costes_reparacion_mano_obra.loc[(tr, ss, mf)] = 0
                datos_salida_costes_reparacion_materiales.loc[(tr, ss, mf)] = 0

                datos_salida_costes_reparacion_total.loc[(tr, ss, mf)] = fila

    if alcance == 'EA_sencillo':
        direct = os.path.join(ruta_ds, '5_datos_salida_costes_reparacion_totales_modos.html')
        datos_salida_ea_sencillo.to_html(direct, sparsify=False)

    else:

        # Guardar como txt la serie horaria de costes
        direct = os.path.join(ruta_ds, 'costes_rep_maq_estado.csv')
        datos_salida_costes_reparacion_maquinaria.to_csv(direct, sep='\t')

        direct = os.path.join(ruta_ds, 'costes_rep_mo_estado.csv')
        datos_salida_costes_reparacion_mano_obra.to_csv(direct, sep='\t')

        direct = os.path.join(ruta_ds, 'costes_rep_tot_estado.csv')
        datos_salida_coste_reparacion_totales = datos_salida_costes_reparacion_maquinaria + datos_salida_costes_reparacion_mano_obra
        datos_salida_coste_reparacion_totales.to_csv(direct, sep='\t')

        # Costes totales por modo
        datos_salida_costes_rep_maq_total_modos = datos_salida_costes_reparacion_maquinaria.sum(axis = 1)
        datos_salida_costes_rep_mo_total_modos = datos_salida_costes_reparacion_mano_obra.sum(axis = 1)
        datos_salida_costes_rep_mat_total_modos = datos_salida_costes_reparacion_materiales['coste_mat_total']

        if alcance == 'EA':
            datos_salida_costes_rep_total_modos = datos_salida_costes_reparacion_total.sum(axis=1)
        else:
            datos_salida_costes_rep_total_modos = datos_salida_costes_rep_maq_total_modos + datos_salida_costes_rep_mo_total_modos + datos_salida_costes_rep_mat_total_modos

        datos_salida_costes_rep_maq_total = datos_salida_costes_rep_maq_total_modos.sum()
        datos_salida_costes_rep_mo_total = datos_salida_costes_rep_mo_total_modos.sum()
        datos_salida_costes_rep_mat_total = datos_salida_costes_rep_mat_total_modos.sum()
        datos_salida_costes_rep_total = datos_salida_costes_rep_total_modos.sum()
        # datos_salida_costes_rep_total = datos_salida_costes_rep_total[0]

        # Coste medio anual por modo
        n_annos_sim = de_planta.loc[de_planta.index[0], 'vida_util']

        if datos_salida_costes_rep_maq_total != 0:
            datos_salida_coste_rep_maq_med_anno = datos_salida_costes_rep_maq_total / n_annos_sim
        else:
            datos_salida_coste_rep_maq_med_anno = 0

        if datos_salida_costes_rep_mo_total != 0:
            datos_salida_coste_rep_mo_med_anno = datos_salida_costes_rep_mo_total / n_annos_sim
        else:
            datos_salida_coste_rep_mo_med_anno = 0

        if datos_salida_costes_rep_mat_total != 0:
            datos_salida_coste_rep_mat_med_anno = datos_salida_costes_rep_mat_total / n_annos_sim
        else:
            datos_salida_coste_rep_mat_med_anno = 0

        if datos_salida_costes_rep_total != 0:
            datos_salida_coste_rep_total_med_anno = datos_salida_costes_rep_total / n_annos_sim
        else:
            datos_salida_coste_rep_total_med_anno = 0

        # Dataframe de salida
        datos_salida_modos = pd.DataFrame(0, index=estado_modos_fallo.index, columns=['coste_reparacion_total_maquinaria', 'coste_reparacion_total_materiales', 'coste_reparacion_total_mano_obra', 'coste_reparacion_total'])
        datos_salida_modos.loc[:, 'coste_reparacion_total_maquinaria'] = datos_salida_costes_rep_maq_total_modos
        datos_salida_modos.loc[:, 'coste_reparacion_total_materiales'] = datos_salida_costes_rep_mat_total_modos
        datos_salida_modos.loc[:, 'coste_reparacion_total_mano_obra'] = datos_salida_costes_rep_mo_total_modos
        datos_salida_modos.loc[:, 'coste_reparacion_total'] = datos_salida_costes_rep_total_modos.values

        direct = os.path.join(ruta_ds, '5_datos_salida_costes_reparacion_totales_modos.html')
        datos_salida_modos.to_html(direct, sparsify=False)
        direct = os.path.join(ruta_ds, '5_datos_salida_costes_reparacion_totales_modos.csv')
        datos_salida_modos.to_csv(direct, sep='\t')

        # Dataframe de salida
        datos_salida_total = pd.DataFrame(index=['coste_total_reparacion_maquinaria',
                                                 'coste_total_reparacion_materiales',
                                                 'coste_total_reparacion_mano_obra',
                                                 'coste_total_reparacion',
                                                 'coste_medio_anual_reparacion_maquinaria',
                                                 'coste_medio_anual_reparacion_materiales',
                                                 'coste_medio_anual_reparacion_mano_obra',
                                                 'coste_medio_anual_reparacion_total'], columns=['0'])

        datos_salida_total.loc['coste_total_reparacion_maquinaria', datos_salida_total.index[0]] = datos_salida_costes_rep_maq_total
        datos_salida_total.loc['coste_total_reparacion_materiales', datos_salida_total.index[0]] = datos_salida_costes_rep_mat_total
        datos_salida_total.loc['coste_total_reparacion_mano_obra', datos_salida_total.index[0]] = datos_salida_costes_rep_mo_total
        datos_salida_total.loc['coste_total_reparacion', datos_salida_total.index[0]] = datos_salida_costes_rep_total
        datos_salida_total.loc['coste_medio_anual_reparacion_maquinaria', datos_salida_total.index[0]] = datos_salida_coste_rep_maq_med_anno
        datos_salida_total.loc['coste_medio_anual_reparacion_materiales', datos_salida_total.index[0]] = datos_salida_coste_rep_mat_med_anno
        datos_salida_total.loc['coste_medio_anual_reparacion_mano_obra', datos_salida_total.index[0]] = datos_salida_coste_rep_mo_med_anno
        datos_salida_total.loc['coste_medio_anual_reparacion_total', datos_salida_total.index[0]] = datos_salida_coste_rep_total_med_anno


        direct = os.path.join(ruta_ds, '6_datos_salida_costes_reparacion_totales.html')
        datos_salida_total.to_html(direct, sparsify=False)
        direct = os.path.join(ruta_ds, '6_datos_salida_costes_reparacion_totales.csv')
        datos_salida_total.to_csv(direct, sep='\t')

    #    # 7. calculo de los costes de materiales de reparacion durante la vida util
    #    # Costes de materiales por cada evento de reparacion
    #    indice = estado_modos_fallo.index.values
    #    datos_salida_costes_mat_rep = pd.DataFrame(0, index=indice, columns=['coste_total_mat_rep'])
    #
    #    for modo in estado_modos_fallo.iterrows():
    #        tr = modo[0][0]
    #        ss = modo[0][1]
    #        mf = modo[0][2]
    #
    #        datos_salida_costes_mat_rep.loc[(tr, ss, mf), 'coste_total_mat_rep'] = de_reparacion_necesarios.loc[(tr, ss, mf), 'coste_mat_rep']*datos_salida['datos_salida_modos'].loc[mf, 'n_veces_ini_rep']
    #
    #    direct = os.path.join(ruta_ds, '5_datos_salida_costes_reparacion_mat.html')
    #    datos_salida_costes_mat_rep.to_html(direct)

    return(datos_salida_modos, datos_salida_total, datos_salida_ea_sencillo)


def extraccion_resultados_alcances_ep_ea(alcance, datos_salida, ruta_ds):

    if alcance == '-':
        idx_tramo = np.array(0)
        # Recorrido por los tramos
        for j in datos_salida.keys():
            idx_tramo = np.vstack((idx_tramo, j))

        idx_tramo = np.delete(idx_tramo, 0)
        arrays = [idx_tramo]
        columnas = ['Coste_total_dique']
        df = pd.DataFrame(np.random.randn(idx_tramo.size, 1), index=arrays, columns=columnas)

        for j in datos_salida.keys():
            df.iloc[j]['Coste_total_dique'] = datos_salida[j]['coste_total_dique']

        direct = os.path.join(ruta_ds, 'Coste_total_dique.html')
        df.to_html(direct, sparsify=False)

    elif ((alcance == 'EP') | (alcance == 'EA')):
        idx_tramo = np.array(0)
        # Recorrido por los tramos
        for j in datos_salida.keys():
            idx_tramo = np.vstack((idx_tramo, j))

        idx_tramo = np.delete(idx_tramo, 0)
        arrays = [idx_tramo]
        columnas = ['Coste_total_tramo']
        df = pd.DataFrame(np.random.randn(idx_tramo.size, 1), index=arrays, columns=columnas)

        for j in datos_salida.keys():
            df.iloc[j]['Coste_total_tramo'] = datos_salida[j]['coste_total_tramo']

        direct = os.path.join(ruta_ds, 'Coste_total_dique.html')
        df.to_html(direct, sparsify=False)

    return(datos_salida)
