import matplotlib.pyplot as plt

import numpy as np


def representacion_resultados_tiempo(
        fases_finalizadas, clima, avance_real, estado_real, plan_avance, vol_ejecutado, longitudes, de_tramo_0):

    fases_finalizadas.iloc[0] = False
    fases_finalizadas.iloc[1] = False
    fases_finalizadas.iloc[2] = False

    # Conversion de volumenes en longitudes. Inicializo con el dataframe pero .copy para que no me modifique
    # el dataframe original mas adelante. CUIDADO CON ESTO EN PYTHON
    lon_ejecutada = vol_ejecutado.copy()
    lon_acumulada = lon_ejecutada.copy()

    for fase, _ in enumerate(fases_finalizadas):

        lon_ejecutada.iloc[fase, :] = (vol_ejecutado.iloc[fase, :]) / (de_tramo_0.loc[de_tramo_0.index[fase], 'vol_subfase_unit'])
        print (lon_ejecutada.iloc[fase, :].sum())

        lon_acumulada.iloc[fase, :] = np.cumsum(lon_ejecutada.iloc[fase, :])

#    plt.plot(lon_acumulada.iloc[0, :], 'g')
#    plt.plot(lon_acumulada.iloc[1, :], 'y')
#    plt.plot(lon_acumulada.iloc[2, :], 'r')

    # Represento las diferencias entre las fases para comprobar longitud de avance
    lon_diferencia = lon_acumulada.copy()
    fases_finalizadas.iloc[2] = True

    fase_pos = fases_finalizadas[fases_finalizadas == False]  # nopep8

    for fase, _ in enumerate(fase_pos):
        lon_diferencia.iloc[fase, :] = lon_acumulada.iloc[fase, :] - lon_acumulada.iloc[fase + 1, :]

#    plt.plot(lon_diferencia.iloc[0, :], 'k')
#    plt.plot(lon_diferencia.iloc[1, :], 'k')

    plt.figure()
    plt.plot(lon_acumulada.iloc[0, :], 'g')
    plt.plot(lon_acumulada.iloc[1, :], 'y')
    plt.plot(lon_diferencia.iloc[0, :], 'k')

    plt.figure()
    plt.plot(lon_acumulada.iloc[1, :], 'y')
    plt.plot(lon_acumulada.iloc[2, :], 'r')
    plt.plot(lon_diferencia.iloc[1, :], 'k')

    val_max = vol_ejecutado.shape[1]
    x = range(0, val_max)
    y1_0 = avance_real.iloc[0, 0:val_max]
    y1_1 = avance_real.iloc[1, 0:val_max]
    y1_2 = avance_real.iloc[2, 0:val_max]

    y2_0 = estado_real.iloc[0, 0:val_max]
    y2_1 = estado_real.iloc[1, 0:val_max]
    y2_2 = estado_real.iloc[2, 0:val_max]
    y3 = clima.loc[clima.index[0:val_max - 1], 'hs']

    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(x, lon_acumulada.iloc[0, :], 'r',  label='Fase 0')
    plt.plot(x, lon_acumulada.iloc[1, :], 'g',  label='Fase 1')
    plt.plot(x, lon_acumulada.iloc[2, :], 'k',  label='Fase 2')
    plt.ylabel('Longitud avanzada acumulada', fontsize=16)
    plt.grid()
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(x, y2_0, 'r', label='Fase 0')
    plt.plot(x, y2_1, 'g', label='Fase 1')
    plt.plot(x, y2_2, 'k', label='Fase 2')
    plt.grid()
    plt.legend()
    plt.yticks([-1, 0, 1, 2, 3, 4, 5, 6, 7], [
        'No Trabaja', 'No Toca Trabajar', 'No Trabaja Restriccion', 'No Trabaja Operatividad',
        'Trabaja', 'Trabaja Retrasada', 'Protegiendo', 'Perdidas', 'Acabada'])

    plt.subplot(3, 1, 3)
    plt.plot(x, y3, 'b')
    plt.plot(x, y3*0 + 0.8, 'k')
    plt.ylabel('Hs (m)', fontsize=16)
    plt.xlabel('Tiempo (h)', fontsize=16)
    plt.grid()

    return


def representacion_resultados_costes(costes_fases_tiempo):

    costes_fases_tiempo_acumulada = costes_fases_tiempo.copy()

    for fase, _ in costes_fases_tiempo.iterrows():
        costes_fases_tiempo_acumulada.iloc[fase, :] = np.cumsum(costes_fases_tiempo.iloc[fase, :])

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(costes_fases_tiempo.iloc[0, :], 'r', label='Fase 0')
    plt.plot(costes_fases_tiempo.iloc[1, :], 'y', label='Fase 1')
    plt.plot(costes_fases_tiempo.iloc[0, :], 'g', label='Fase 2')
    plt.ylabel('Costes (euro)', fontsize=16)
    plt.grid()
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(costes_fases_tiempo_acumulada.iloc[0, :], 'r', label='Fase 0')
    plt.plot(costes_fases_tiempo_acumulada.iloc[2, :], 'y', label='Fase 1')
    plt.plot(costes_fases_tiempo_acumulada.iloc[1, :], 'g', label='Fase 2')
    plt.ylabel('Coste acumulado (euro)', fontsize=16)
    plt.xlabel('Tiempo (h)', fontsize=16)
    plt.grid()
    plt.legend()

    return
