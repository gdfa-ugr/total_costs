import pandas as pd

from .datos_entrada_e_previo import datos_entrada_planta
from .datos_entrada_e_previo import datos_entrada_estudio_previo_estudio_alterntivas
from .extracciones_e_previo import extraccion_resultados_alcances_ep_ea


def simulacion_estudio_previo(ruta_de, alcance, ruta_ds):
    """Funcion que verifica y calcula los costes de construccion del dique para los alcances de estudio previo y
    estudio de alternativas.

    Args:
        ruta_de: cadena de texto con la ruta del directorio que contiene los datos de entrada
        alcance: etiqueta con el alcance del estudio
        ruta_ds: cadena de texto con la ruta del directorio que contiene los datos de salida

    Returns:
        Un diccionario con el valor del coste total de construccion para cada tramo

    """

    datos_salida = {}

    # Lectura de los datos de entrada en planta
    (de_planta_tramos) = datos_entrada_planta(ruta_de)

    # Recorrido por los tramos del dique
    for n, _ in de_planta_tramos.iterrows():
        de_planta = de_planta_tramos.loc[n, :]

        # Lectura de los datos de entrada
        (tabla_precios, unidades_obra, coeficientes) = \
            datos_entrada_estudio_previo_estudio_alterntivas(n, ruta_de, alcance)

        if alcance == '-':
            # Se incluye en salida un diccionario para el tramo
            datos_salida[n] = dict()

            # Tipo de seccion elegida
            seccion = de_planta.loc['tipo_seccion', n]
            # Precio seccion
            precio_lineal = float(tabla_precios.loc[tabla_precios.index[seccion], 1].replace('.', '').replace(',', '.'))
            # Coste total
            coste = precio_lineal*de_planta.loc['longitud', n]
            datos_salida[n]['coste_total_dique'] = coste

        elif (alcance == 'EP'):
            # Se incluye en salida un diccionario para el tramo
            datos_salida[n] = dict()

            # Precio de las uniades de obra elegidas por unidad de medicion
            precio_desglosado = tabla_precios.loc[tabla_precios.index[unidades_obra.iloc[:, 0]], 'PRECIO.MEDIO']
            precio_desglosado = precio_desglosado.str.replace('.', '')
            precio_desglosado = precio_desglosado.str.replace(',', '.')
            precio_desglosado = pd.to_numeric(precio_desglosado)

            # Coste total de las unidaes de obra elegidas para el tramo
            coste = (precio_desglosado.values*unidades_obra.iloc[:, 1].values).sum()
            datos_salida[n]['coste_construccion_tramo'] = coste
            datos_salida[n]['coste_construccion_tramo_ponderado_clima'] = coste*coeficientes.loc[n, 'clima']
            datos_salida[n]['coste_total_tramo'] = coste*coeficientes.loc[n, 'clima']*coeficientes.loc[n, 'coste_total']

    # Extraccion de resultados
    datos_salida = extraccion_resultados_alcances_ep_ea(alcance, datos_salida, ruta_ds)

    return(datos_salida)
