import pandas as pd
import numpy as np

import math

from comprobaciones import comprueba_fase_acabada
from comprobaciones import comprueba_fase_finalizada

from datos_entrada import datos_entrada_tramo
from datos_entrada import datos_entrada_fase
from datos_entrada import rendimientos_y_umbrales_datos_entrada

from calculos import calcula_n_horas_proteger
from calculos import actualiza_longitudes_fase_siguiente
from calculos import recorte_matrices_resultantes
from calculos import genera_matriz_volumen
from calculos import genera_matriz_estado
from calculos import actualiza_matrices_fases_finalizadas

from clasificacion_main_fase_I import clasificacion_main_fase_I

from fases_nivel_III import fase_parada_invernal

import logging

import logging

import pandas as pd

from datos_entrada import datos_entrada_planta

from main_tramos import simulacion_proceso_constructivo_tramo

from representacion_v2 import representacion_resultados_tiempo
from representacion import representacion_resultados_costes

from calculos import calculo_costes
from calculos import calculo_longitudes_volumenes_acumulados

# Datos de entrada
(de_planta, p_invernal) = datos_entrada_planta()
n_tramos = de_planta.shape[0]
hora_acumulada = 0
hora_inicio_tramos = [0]

n = 'T_0'

(de_tramo, plan_avance, clima, com_fin_teorico) = datos_entrada_tramo(de_planta, n, hora_inicio_tramos)
vol_ejecutado = genera_matriz_volumen(plan_avance)

hora = 2500

vol_ejecutado = vol_ejecutado.reindex_axis(range(hora), axis=1)
vol_ejecutado.at[0, hora] = 0