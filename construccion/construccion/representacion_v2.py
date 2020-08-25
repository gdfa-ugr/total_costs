import matplotlib.pyplot as plt

import pandas as pd
import os


def representacion_resultados_tiempo(lon_acumulada_total, hora_inicio_tramos, estado_real_total, n, ruta_de='.',
                                     ruta_ds='.'):
    # Represento la longitud acumulada
    col = ['r', 'g', 'k', 'y', 'b', 'c', 'm', 'r', 'g', 'k', 'y']
    plt.figure(figsize=(20, 15))
    for tramo, _ in enumerate(lon_acumulada_total):

        for fase, _ in lon_acumulada_total[tramo].iterrows():
            x = range(hora_inicio_tramos[tramo], hora_inicio_tramos[tramo] + lon_acumulada_total[tramo].iloc[fase, :].shape[0])
            plt.plot(x, lon_acumulada_total[tramo].iloc[fase, :], color=col[fase])

    # Guardado de resultados
    direct = os.path.join(ruta_ds, 'longitudes.pdf')
    plt.savefig(direct)
    plt.show()

    # Represento la longitud acumulada
    col = ['r', 'g', 'k', 'y', 'b', 'c', 'm', 'r', 'g', 'k', 'y']
    display = ['F0', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11']
    plt.figure(figsize=(20, 15))
    for tramo, _ in enumerate(lon_acumulada_total):

        ax1 = plt.subplot(3, 1, 1)

        for fase, _ in lon_acumulada_total[tramo].iterrows():
            x = range(hora_inicio_tramos[tramo], hora_inicio_tramos[tramo] + lon_acumulada_total[tramo].iloc[fase, :].shape[0])
            if tramo == 0:
                ax1.plot(x, lon_acumulada_total[tramo].iloc[fase, :], color=col[fase], label=display[fase])
                plt.legend()
                plt.ylabel('Longitud del tramo (m)', fontsize=16)
            else:
                ax1.plot(x, lon_acumulada_total[tramo].iloc[fase, :], color=col[fase])
            plt.grid()

        ax1 = plt.subplot(3, 1, 2, sharex=ax1)
        for fase, _ in estado_real_total[tramo].iterrows():
            x = range(hora_inicio_tramos[tramo], hora_inicio_tramos[tramo] + estado_real_total[tramo].iloc[fase, :].shape[0])
            if tramo == 0:
                ax1.plot(x, estado_real_total[tramo].iloc[fase, :], color=col[fase], label=display[fase])
                plt.legend()
            else:
                ax1.plot(x, estado_real_total[tramo].iloc[fase, :], color=col[fase])
            plt.grid()
            plt.ylim(-1.5, 7.5)
            plt.yticks([-1, 0, 1, 2, 3, 4, 5, 6, 7], [
                'No Trabaja', 'No Toca Trabajar', 'No Trabaja Restriccion', 'No Trabaja Operatividad',
                'Trabaja', 'Trabaja Retrasada', 'Protegiendo', 'Perdidas', 'Acabada'])

        ax1 = plt.subplot(3, 1, 3, sharex=ax1)

        # Lectura de los datos de clima a partir de fichero
        direct = os.path.join(ruta_de, 'clima', n, 'clima.csv.zip')
        clima = pd.read_csv(direct, sep=',')
        clima = clima.reset_index(drop=True)

        x = range(hora_inicio_tramos[0], hora_inicio_tramos[-1])
        y = clima.loc[clima.index[0: hora_inicio_tramos[-1]], 'hs']
        plt.plot(x, y, color='b')
        plt.ylabel('Hs (m)', fontsize=16)
        plt.xlabel('Tiempo (h)', fontsize=16)
        plt.grid()

    # Guardado de resultados
    direct = os.path.join(ruta_ds, 'estados.pdf')

    plt.savefig(direct)
    plt.show()

