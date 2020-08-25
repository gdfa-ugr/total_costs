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

from .verificacion import verificacion_ciclo_calma
from .verificacion import verificacion_ciclo_solicitacion

from . import constantes as c


def clasificacion_main_ciclos(hs, tp, u10, z, p90, h, tr, ss, mf, averia_acum_estado, averia_estado, de_reparacion_necesarios,
                              de_reparacion_disponibles, estado_reparacion_modos, origen_maquinaria_reparacion_estado,
                              origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado, alcance,
                              estrategia, datos_salida, estado_modos_fallo, ia_modos_fallo, cadencia, de_verificacion_tramos,
                              peralte, de_esquema_division_dique, de_arbol_fallo, de_tipo_verificacion, clima_tramos, de_diagrama_modos,
                              ia_tramos, ia_subsistemas, subsistemas, ia_dique, tramos,
                              datos_salida_prob_ini_averia, de_planta, ini_reparacion, fin_reparacion):

    # En primer lugar se comprueba si el estado corresponde a ciclo de solicitacion o no
    comprobacion = comprueba_si_ciclo_de_solicitacion(hs, p90)
    clasificacion = clasifica_si_ciclo_solicitacion(comprobacion)


    if clasificacion == c.CICLO_CALMA:
        # Si estamos en ciclo de calma
        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
            ss) + ' Modo_fallo: ' + str(mf) + ' Ciclo de calma')

        [datos_salida, averia_acum_estado, averia_estado, estado_modos_fallo, origen_maquinaria_reparacion_estado,
         origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado,
         datos_salida_prob_ini_averia] = \
             verificacion_ciclo_calma(tr, ss, mf, h, averia_acum_estado, de_reparacion_necesarios,
                                      estado_reparacion_modos,
                                      de_reparacion_disponibles, origen_maquinaria_reparacion_estado,
                                      origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado,
                                      alcance, datos_salida, hs, u10, z, estado_modos_fallo, cadencia,
                                      de_verificacion_tramos, peralte, averia_estado, ia_modos_fallo,
                                      datos_salida_prob_ini_averia, ini_reparacion, fin_reparacion)


    elif clasificacion == c.CICLO_SOLICITACION:
        logging.info('Estado: ' + str(h) + ' Tramo: ' + str(tr) + ' Subsistema: ' + str(
            ss) + ' Modo_fallo: ' + str(mf) + ' Ciclo de solicitacion')

        [datos_salida, averia_acum_estado, averia_estado, estado_modos_fallo,
         datos_salida_prob_ini_averia] = \
            verificacion_ciclo_solicitacion(hs, tp, tr, ss, mf, ia_modos_fallo, h, averia_estado, averia_acum_estado,
                                            cadencia, de_verificacion_tramos, peralte, datos_salida, estado_modos_fallo,
                                            de_arbol_fallo, de_esquema_division_dique,
                                            de_tipo_verificacion, clima_tramos, de_diagrama_modos, ia_subsistemas, ia_tramos, ia_dique,
                                            subsistemas, datos_salida_prob_ini_averia, alcance, de_planta)

    return(datos_salida, averia_acum_estado, averia_estado, estado_modos_fallo, origen_maquinaria_reparacion_estado,
           origen_materiales_reparacion_estado, origen_mano_obra_reparacion_estado)
