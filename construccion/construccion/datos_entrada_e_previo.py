import os
import pandas as pd


def datos_entrada_planta(ruta_de='.'):

    # Forma en planta
    direct = os.path.join(ruta_de, 'planta', 'datos_entrada_planta.txt')
    de_planta = pd.read_csv(direct, sep=',', quoting=2)

    return de_planta


def datos_entrada_estudio_previo_estudio_alterntivas(n, ruta_de='.', alcance='EP'):

    unidades_obra = -1
    if alcance == '-':
        # Datos de coste lineal de cada tipo de seccion
        direct = os.path.join(ruta_de, 'tablas_precios')
        direct = os.path.join(direct, 'secciones_dique.csv')
        tabla_precios = pd.read_csv(direct, sep=',', index_col=0, decimal=',')
        unidades_obra = []

    elif (alcance == 'EP'):
        # Datos de coste lineal de cada unidad de obra
        direct = os.path.join(ruta_de, 'tablas_precios')
        direct = os.path.join(direct, 'precios_unitarios.csv')
        tabla_precios = pd.read_csv(direct, sep=',', index_col=0, decimal=',')

        # Datos con las unidades de obra elegidas por el usuario
        direct = os.path.join(ruta_de, 'tramos', n, 'unidades_obra', 'unidades_obra.txt')
        unidades_obra = pd.read_csv(direct, sep=',')

        # Datos con los coeficientes para la ponderacion de costes
        direct = os.path.join(ruta_de, 'coeficientes', 'coeficientes.txt')
        coeficientes = pd.read_csv(direct, sep=',')

    return (tabla_precios, unidades_obra, coeficientes)
