import numpy as np
import pandas as pd
import os


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
        columnas = ['Coste_construccion_tramo', 'Coste_construccion_ponderado_clima_tramo', 'Coste_total_tramo']
        df = pd.DataFrame(np.random.randn(idx_tramo.size, 3), index=arrays, columns=columnas)

        for j in datos_salida.keys():
            df.iloc[j]['Coste_construccion_tramo'] = datos_salida[j]['coste_construccion_tramo']
            df.iloc[j]['Coste_construccion_ponderado_clima_tramo'] = \
                    datos_salida[j]['coste_construccion_tramo_ponderado_clima']
            df.iloc[j]['Coste_total_tramo'] = datos_salida[j]['coste_total_tramo']

        direct = os.path.join(ruta_ds, 'Coste_total_dique.html')
        df.to_html(direct, sparsify=False)

    return(datos_salida)
