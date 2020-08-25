import logging
import os

from datos_entrada import datos_entrada_planta

from main_tramos import simulacion_proceso_constructivo_tramo

from representacion_v2 import representacion_resultados_tiempo
from representacion import representacion_resultados_costes

from calculos import calculo_costes
from calculos import calculo_longitudes_volumenes_acumulados
from calculos import extraccion_resultados

from simulacion_estudio_previo import simulacion_estudio_previo


if __name__ == '__main__':

    # Ruta con los datos de entrada
    ruta_de = os.path.join('Datos_entrada', 'Ejemplo_sencillo_estudio_alternativas_estrategia_serie_o_paralelo')
    # Ruta con los datos de salida
    ruta_ds = os.path.join('Datos_salida', 'Ejemplo_sencillo_estudio_alternativas_estrategia_serie_o_paralelo')
    # Alcance del estudio
    alcance = 'EA'  # PI: Proyecto de Inversion o AP: AnteProyecto o EA: Estudio de alternativas
    estrategia = 'cronograma_trabajos'  # avance_paralelo cronograma_trabajos
    # estrategia = 'avance_serie'
    #estrategia = 'cronograma_trabajos'
    # rep_inmediata = 'no'

    if alcance == 'EA':
        rep_inmediata = 'si'
    elif ((alcance == 'AP') | (alcance == 'PI')):
        rep_inmediata = 'no'
    # logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(funcName)s: %(message)s')
    direct = os.path.join(ruta_ds, 'debug_info.log')
    logging.basicConfig(filename=direct, level=logging.INFO)
    # logging.basicConfig(level=logging.ERROR)

    # Lectura de los datos de entrada de la planta
    (de_planta, p_invernal) = datos_entrada_planta(ruta_de, alcance, estrategia)

    # Calculo del numero de tramos del dique
    n_tramos = de_planta.shape[0]

    # Inicializacion de la variable hora que avanza con cada iteracion
    hora_acumulada = 0

    # Inicializacion de la hora de inicio del tramo 0
    hora_inicio_tramos = [0]

    # Inicializacion de las variables de salida
    de_tramo_total = []
    com_fin_teorico_total = []
    avance_real_total = []
    estado_real_total = []
    vol_ejecutado_total = []
    vol_perdido_total = []
    avance_real_total = []
    longitudes_total = []
    costes_ejecc_sf_unit_total = []
    costes_directos_sf_unit_total = []
    costes_ejecc_sf_total_total = []
    costes_directos_sf_total_total = []
    costes_sf_total_total = []


    if (alcance == 'EP'):

        (datos_salida) = simulacion_estudio_previo(ruta_de, alcance, ruta_ds)

    else:

        # Bucle que recorre los tramos del dique
        for n, _ in de_planta.iterrows():

            # Simulacion - Verificacion del proceso constructivo
            (avance_real, estado_real, vol_ejecutado, longitudes, hora, hora_acumulada, hora_inicio_tramos,
             clima, maquinaria_fases, plan_avance, de_tramo,
             com_fin_teorico, vol_perdido, eq_coste_fases, eq_danno_fases,
             costes_fase) = simulacion_proceso_constructivo_tramo(n, de_planta, hora_acumulada,
                                                                  hora_inicio_tramos, p_invernal, alcance, estrategia,
                                                                  ruta_de, rep_inmediata)

            # Adjudicacion de costes a la simulacion del proceso constructivo
            # if alcance != 'EA':
            (costes_ejecc_sf_unit, costes_directos_sf_unit, costes_ejecc_sf_total, costes_directos_sf_total,
                costes_sf_total) = calculo_costes(plan_avance, maquinaria_fases, estado_real, vol_perdido, eq_coste_fases,
                                                  eq_danno_fases, clima, costes_fase, vol_ejecutado)

            # Almaceno los resultados
            de_tramo_total.append(de_tramo)
            com_fin_teorico_total.append(com_fin_teorico)
            avance_real_total.append(avance_real)
            estado_real_total.append(estado_real)
            vol_ejecutado_total.append(vol_ejecutado)
            vol_perdido_total.append(vol_perdido)
            longitudes_total.append(longitudes)

            # if alcance != 'EA':
            costes_ejecc_sf_unit_total.append(costes_ejecc_sf_unit)
            costes_directos_sf_unit_total.append(costes_directos_sf_unit)
            costes_ejecc_sf_total_total.append(costes_ejecc_sf_total)
            costes_directos_sf_total_total.append(costes_directos_sf_total)
            costes_sf_total_total.append(costes_sf_total)

            (lon_ejecutada_total, lon_acumulada_total, vol_acumulado_total,
             lon_diferencia_total) = calculo_longitudes_volumenes_acumulados(estado_real_total, vol_ejecutado_total,
                                                                             de_tramo_total)

        # Representacion de resultados de tiempo de ejecucion
        representacion_resultados_tiempo(lon_acumulada_total, hora_inicio_tramos, estado_real_total, n, ruta_de, ruta_ds)
    #
    #    # Representacion resultados de costes
    #    representacion_resultados_costes(costes_fases_tiempo)

        # Se reajusta el plan de avance
    #    plan_avance = pd.read_csv('plan_avance.txt', delim_whitespace=True, header=None)
    #    plan_avance.index = plan_avance[0]  # asigna la primera columna como indice
    #    plan_avance.drop(plan_avance.columns[0], axis=1, inplace=True)  # elimina la primera columna
    #    plan_avance.columns = pd.Int64Index(range(len(plan_avance.columns)))  # genera un nuevo indice para las columnas
    #    plan_avance = plan_avance.astype(bool)  # convierte la matriz a booleanos
    #
    #    fin_teorico = com_fin_teorico_total[0].loc[:, 'fin_fase_teo'].max()
    #    fin_real = hora_inicio_tramos[1]
    #    ini_teorico = com_fin_teorico_total[1].loc[:, 'com_fase_teo'].min()
    #    ini_real = hora_inicio_tramos[1]
    #
    #    if fin_real < fin_teorico:
    #        # Obtengo las columnas a eliminar
    #        columnas = range(fin_real, int(fin_teorico))
    #        # Elimino las columnas innecesarias
    #        plan_avance = plan_avance.drop(columnas, axis=1)
    #        # Reordeno columnas
    #        plan_avance.columns = pd.Int64Index(range(len(plan_avance.columns)))
    #        plan_avance.to_csv

        # Extraccion de las variables de tiempos, probabilidades, volumenes y costes
        (df_duracion, df_horas, df_probabilidad, df_tiempos, df_volumen, df_costes_ejecucion, df_costes_directos,
         df_costes_totales) = extraccion_resultados(de_planta, n, estado_real_total, vol_acumulado_total,
         vol_ejecutado_total, de_tramo_total, hora_inicio_tramos, vol_perdido_total, costes_ejecc_sf_total_total,
         costes_directos_sf_total_total, costes_sf_total_total, com_fin_teorico_total, ruta_de, ruta_ds, alcance)
