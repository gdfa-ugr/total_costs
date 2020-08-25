import ast
import logging

import numpy as np
import pandas as pd
import math
from tqdm import tqdm

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
from .calculos import extraccion_resultados_alcances_ep_ea

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

from .clasificacion_main_ciclos import clasificacion_main_ciclos

from .datos_entrada import datos_entrada_planta
from .datos_entrada import datos_entrada_estudio_previo_estudio_alterntivas

from . import constantes as c


def simulacion_fase_conservacion(de_planta, de_diagrama_modos, de_arbol_fallo,
                                 de_esquema_division_dique, de_tipo_verificacion, clima_tramos, cadencia,
                                 de_verificacion_tramos, peralte, h_fin_sim,
                                 de_reparacion_disponibles, de_reparacion_necesarios, alcance,
                                 estrategia):

    # Inicializar las matrices de grado de averia para el dique, tramos, subsistemas y modos de fallo
    (ia_dique, ia_tramos, ia_subsistemas, ia_modos_fallo, averia_estado, averia_acum_estado,
     estado_modos_fallo, subsistemas, tramos, modos_fallo, estado_reparacion_modos,
     origen_maquinaria_reparacion_estado, origen_materiales_reparacion_estado,
     origen_mano_obra_reparacion_estado,
     datos_salida,
     datos_salida_prob_ini_averia,
     ini_reparacion, fin_reparacion) = inicializacion_matrices_grado_averia(de_esquema_division_dique, h_fin_sim)

     # Inicializacion de las matrices de materiales de reparacion que quedan disponibles en puerto y matrices de si
     # los elementos de reparacion se toman del puerto o se encargan para cada estado

    # Recorrido por los estados de la vida util
    for h in tqdm(range(1, h_fin_sim)):

        # Recorrido por los modos de fallo principales de cada subsistema de cada tramo
        for mst in de_esquema_division_dique.iterrows():
            # Obtencion del tramo, subsistema y modo de fallo
            mst = mst[1]
            tr = mst['tramo']
            ss = mst['subsistema']
            mf = mst['modo_fallo']
            # Se obtienen los datos del estado de mar para el tramo
            (hs, tp, u10, z, p90) = estado_de_mar_tramo(clima_tramos, tr, h)

            logging.info('Estado de mar. Hs: ' + str(hs))

#            if mf == 'MF_4':
#                print(mf)

            # Actualizacion del nivel de averia acumulado hasta este estado
            (averia_estado, averia_acum_estado) = actuliza_nivel_de_averia(averia_estado, averia_acum_estado, tr, ss,
                                                                           mf, h)
            # En primer lugar se comprueba si el estado corresponde a ciclo de solicitacion o no
            [datos_salida, averia_acum_estado, averia_estado, estado_modos_fallo, origen_maquinaria_reparacion_estado,
             origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado] = \
                   clasificacion_main_ciclos(hs, tp, u10, z, p90, h, tr, ss, mf, averia_acum_estado, averia_estado, de_reparacion_necesarios,
                       de_reparacion_disponibles, estado_reparacion_modos, origen_maquinaria_reparacion_estado,
                       origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado, alcance,
                       estrategia, datos_salida, estado_modos_fallo, ia_modos_fallo, cadencia, de_verificacion_tramos,
                       peralte, de_esquema_division_dique, de_arbol_fallo, de_tipo_verificacion, clima_tramos, de_diagrama_modos,
                       ia_tramos, ia_subsistemas, subsistemas, ia_dique, tramos, datos_salida_prob_ini_averia,
                                             de_planta, ini_reparacion, fin_reparacion)


        # Al final de cada iteracion actualizo los inicios de averia de los susbsistemas y tramos si alguno de los
        # elementos que lo conforman se encuentra en inicio de averia y si todos estan sin averia, el sussitema o
        # tramo deja de tener inicio de averia

            # Inicio de averia en subsistemas
            for s in subsistemas:
                if all(ia_modos_fallo.loc[(slice(None), s), 'ini_averia'] == 0):
                    ia_subsistemas.loc[(slice(None), s), 'ini_averia'] = 0
                elif any(ia_modos_fallo.loc[(slice(None), s), 'ini_averia'] == 1):
                    ia_subsistemas.loc[(slice(None), s), 'ini_averia'] = 1

            # Inicio de averia en tramos
            for t in tramos:
                if all(ia_subsistemas.loc[t, 'ini_averia'] == 0):
                    ia_tramos.loc[t, 'ini_averia'] = 0
                elif any(ia_subsistemas.loc[t, 'ini_averia'] == 1):
                    ia_tramos.loc[t, 'ini_averia'] = 1

        # Al final de cada iteracion se comprueba si el dique ha fallado, en caso afirmativo se corta la simulacion
        if ia_dique.loc[ia_dique.index[0], 'dest_total'] == 1:
            logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
                ss) + ' Modo_fallo: ' + str(mf) + ' El dique sufre destruccion total')
            break

    return(datos_salida, averia_acum_estado, averia_estado, estado_modos_fallo, origen_maquinaria_reparacion_estado,
           origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado, datos_salida_prob_ini_averia,
           ini_reparacion, fin_reparacion)


#def simulacion_estudio_previo_estudio_alternativas(ruta_de, alcance, ruta_ds):
#    """Funcion que verifica y calcula los costes de construccion del dique para los alcances de estudio previo y
#    estudio de alternativas.
#
#    Args:
#        ruta_de: cadena de texto con la ruta del directorio que contiene los datos de entrada
#        alcance: etiqueta con el alcance del estudio
#        ruta_ds: cadena de texto con la ruta del directorio que contiene los datos de salida
#
#    Returns:
#        Un diccionario con el valor del coste total de construccion para cada tramo
#
#    """
#
#    datos_salida = {}
#
#    # Lectura de los datos de entrada en planta
#    (de_planta_tramos) = datos_entrada_planta(ruta_de)
#
#    # Recorrido por los tramos del dique
#    for n, _ in de_planta_tramos.iterrows():
#        de_planta = de_planta_tramos.iloc[n, :]
#
#        # Lectura de los datos de entrada
#        (tabla_precios, unidades_obra) = \
#            datos_entrada_estudio_previo_estudio_alterntivas(n, ruta_de, alcance)
#
#        if alcance == '-':
#            # Se incluye en salida un diccionario para el tramo
#            datos_salida[n] = dict()
#
#            # Tipo de seccion elegida
#            seccion = de_planta.loc['tipo_seccion', de_planta.index[n]]
#            # Precio seccion
#            precio_lineal = float(tabla_precios.loc[seccion, tabla_precios.index[1]].replace('.', '').replace(',', '.'))
#            # Coste total
#            coste = precio_lineal*de_planta.loc['longitud', de_planta.index[n]]
#            datos_salida[n]['coste_total_dique'] = coste
#
#        elif ((alcance == 'EA') | (alcance == 'EP')):
#            # Se incluye en salida un diccionario para el tramo
#            datos_salida[n] = dict()
#
#            # Precio de las uniades de obra elegidas por unidad de medicion
#            precio_desglosado = tabla_precios.loc[unidades_obra.iloc[:, 0], 'PRECIO.MEDIO']
#            precio_desglosado = precio_desglosado.str.replace('.', '')
#            precio_desglosado = precio_desglosado.str.replace(',', '.')
#            precio_desglosado = pd.to_numeric(precio_desglosado)
#
#            # Coste total de las unidaes de obra elegidas para el tramo
#            coste = (precio_desglosado.values*unidades_obra.iloc[:, 1].values).sum()
#            datos_salida[n]['coste_total_tramo'] = coste
#
#    # Extraccion de resultados
#    datos_salida = extraccion_resultados_alcances_ep_ea(alcance, datos_salida, ruta_ds)
#
#    return(datos_salida)
