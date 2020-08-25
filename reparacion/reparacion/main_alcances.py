import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle

from .datos_entrada import datos_entrada_planta
from .datos_entrada import datos_entrada_diagrama_modos
from .datos_entrada import datos_entrada_arbol_fallo
from .datos_entrada import datos_entrada_esquema_division_dique
from .datos_entrada import datos_entrada_clima_tramos
from .datos_entrada import datos_entrada_verificacion_dique

from .calculos import calculo_final_simulacion
from .calculos import extraccion_resultados
from .calculos import calculo_costes
from .calculos import extraccion_resultados_alcances_ep_ea

from .datos_entrada import datos_entrada_elementos_reparacion_necesarios
from .datos_entrada import datos_entrada_elementos_reparacion_disponibles
from .datos_entrada import datos_entrada_estudio_previo_estudio_alterntivas
from .datos_entrada import datos_entrada_tipo_verificacion

from .simulaciones_fase_conservacion import simulacion_fase_conservacion

from . import constantes as c


def main_alcances(ruta_de, ruta_ds, alcance, estrategia='no_reparacion'):

    # lectura del esquema de division del dique
    (de_esquema_division_dique) = datos_entrada_esquema_division_dique(ruta_de)
    # Lectura de los datos de entrada en planta
    (de_planta) = datos_entrada_planta(ruta_de)
    # Lectura de los datos de entrada del diagrama de modos
    (de_diagrama_modos) = datos_entrada_diagrama_modos(ruta_de)
    # Lectura de los datos de entrada de arbol de fallo
    (de_arbol_fallo) = datos_entrada_arbol_fallo(alcance, de_esquema_division_dique, ruta_de)
    # Tipo de verificacion y curva de acumulacion de dano
    de_tipo_verificacion = datos_entrada_tipo_verificacion(ruta_de)
    # Lectura de los datos de clima para cada tramo
    (clima_tramos, cadencia) = datos_entrada_clima_tramos(de_esquema_division_dique, de_planta, ruta_de)
    # Calculo de la hora final de simulacion
    h_fin_sim = calculo_final_simulacion(de_planta, clima_tramos, cadencia)
    # Datos de entrada de reparacion necesario
    de_reparacion_necesarios = datos_entrada_elementos_reparacion_necesarios(ruta_de, cadencia, alcance,
                                                                             estrategia)
    # Datos de entrada de reparacion disponibles
    de_reparacion_disponibles = datos_entrada_elementos_reparacion_disponibles(ruta_de, cadencia, alcance)

    # Verificacion tramos del dique
    (de_verificacion_tramos, peralte) = datos_entrada_verificacion_dique(ruta_de, de_esquema_division_dique)

    # Conversion a formato de modos de fallo



     # Simulacion de la fase de conservacion
    (datos_salida, averia_acum_estado, averia_estado, estado_modos_fallo, origen_maquinaria_reparacion_estado,
     origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado,
     datos_salida_prob_ini_averia,
     ini_reparacion, fin_reparacion) = \
         simulacion_fase_conservacion(de_planta, de_diagrama_modos, de_arbol_fallo,
                                      de_esquema_division_dique, de_tipo_verificacion, clima_tramos, cadencia,
                                      de_verificacion_tramos, peralte, h_fin_sim, de_reparacion_disponibles,
                                      de_reparacion_necesarios, alcance, estrategia)
#

    # Representacion grafica
    col = ['r', 'g', 'k', 'y', 'b', 'c', 'm', 'r', 'g', 'k', 'y', 'b', 'c', 'm', 'r', 'g', 'k', 'y', 'b', 'c']
    display = ['MF_0', 'MF_1', 'MF_2', 'MF_3', 'MF_4', 'MF_5', 'MF_6', 'MF_7', 'MF_8', 'MF_9', 'MF_10', 'MF_11',
    'MF_12', 'MF_13', 'MF_14', 'MF_15', 'MF_16', 'MF_17', 'MF_18', 'MF_19', 'MF_20']

    cont = 1
    for mst in de_esquema_division_dique.iterrows():
        plt.figure(figsize=(25, 15))

        # Obtencion del tramo, subsistema y modo de fallo
        mst = mst[1]
        tr = mst['tramo']
        ss = mst['subsistema']
        mf = mst['modo_fallo']

        plt.suptitle('Modo ' + str(mf), fontsize=20)

        #ax1 = plt.subplot(de_esquema_division_dique.shape[0], 1, cont)
        ax1 = plt.subplot(4, 1, 1)
        x = range(0, cadencia * h_fin_sim, cadencia)
        ax1.plot(x, estado_modos_fallo.loc[(tr, ss, mf), :], color=col[cont], label=display[cont])
        plt.grid()
        plt.ylim(-1, 9)
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8 ,9], [
            'MODO_NO_REPARA', 'MODO_ESPERANDO_PARA_EMPEZAR_REPARAR', 'MODO_NO_REPARA_OPERATIVIDAD', 'MODO_REPARANDO',
            'MODO_FINALIZA_REPARACION', 'MODO_SALE_DE_INICIO_DE_AVERIA', 'MODO_SUFRE_DANNOS',
            'MODO_NO_ALCANZA_INICIO_AVERIA_NO_SUFRE_DANNOS', 'MODO_SUFRE_DESTRUCCION_TOTAL', 'MODO_SALE_DE_DESTRUCCION_TOTAL'])

        ax2 = plt.subplot(4, 1, 2, sharex=ax1)
        x = range(0, cadencia * h_fin_sim, cadencia)
        y = averia_acum_estado.loc[(tr, ss, mf), :]
        ax2.plot(x, y, color=col[cont], label=display[cont])
        plt.ylim(-0.25, 1.25)
        plt.grid()
        plt.ylabel('Nivel averia (%)', fontsize=16)

        ax3 = plt.subplot(4, 1, 3, sharex=ax1)
        x = range(0, cadencia * h_fin_sim, cadencia)
        hs = clima_tramos[tr].loc[clima_tramos[tr].index[0: h_fin_sim], 'hs']
        ax3.plot(x, hs, color='b', label='Hs (m)')
        plt.grid()
        cont += 1
        plt.xlabel('Tiempo (h)', fontsize=16)
        plt.ylabel('Hs (m)', fontsize=16)

        ax4 = plt.subplot(4, 1, 4, sharex=ax1)
        x = range(0, cadencia * h_fin_sim, cadencia)
        tp = clima_tramos[tr].loc[clima_tramos[tr].index[0: h_fin_sim], 'tp']
        ax4.plot(x, tp, color='r', label='Tp (s)')
        plt.grid()
        plt.xlabel('Tiempo (h)', fontsize=16)
        plt.ylabel('Tp (s)', fontsize=16)

        # Guardado de resultados
        name_fichero = ('Modo_' + str(mf) + '_estados.pdf')
        direct = os.path.join(ruta_ds, name_fichero)

        plt.savefig(direct)
        plt.show()

    direct = os.path.join('salida', 'states_temporal.csv')
    estado_modos_fallo.to_csv(direct)

    (datos_salida, datos_salida_reparacion) = extraccion_resultados(datos_salida, datos_salida_prob_ini_averia, de_planta,
                                                                    estado_modos_fallo, h_fin_sim, ruta_ds, cadencia,
                                                                    ini_reparacion, fin_reparacion, averia_acum_estado)

    (datos_salida_modos, datos_salida_total, datos_salida_ea_sencillo) = calculo_costes(estado_modos_fallo, de_reparacion_necesarios, de_reparacion_disponibles,
        datos_salida, de_planta, ruta_ds, alcance, estrategia, cadencia)


    return datos_salida, datos_salida_reparacion
