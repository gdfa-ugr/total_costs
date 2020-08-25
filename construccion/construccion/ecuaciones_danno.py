import numpy as np
import pandas as pd
import math


def ecuacion_danno_exponencial(modo_fallo, archivo):

    x_0 = modo_fallo.loc[modo_fallo.index[0], 'x_0']
    x_max = modo_fallo.loc[modo_fallo.index[0], 'x_max']
    d_0 = modo_fallo.loc[modo_fallo.index[0], 'd_0']
    d_max = modo_fallo.loc[modo_fallo.index[0], 'd_max']

    x1 = np.linspace(0, x_0, 100)
    x2 = np.linspace(x_0, x_max, 100)

    d1 = x1*0
    d2 = d_0 + ((d_max - d_0) / (math.e - 1)) * (np.exp((x2 - x_0) / (x_max - x_0)) - 1)

    x = np.concatenate((x1, x2), axis=0)
    d = np.concatenate((d1, d2), axis=0)

    return (x, d)


def ecuacion_danno_lineal(modo_fallo, archivo):

    x_0 = modo_fallo.loc[modo_fallo.index[0], 'x_0']
    x_max = modo_fallo.loc[modo_fallo.index[0], 'x_max']
    d_0 = modo_fallo.loc[modo_fallo.index[0], 'd_0']
    d_max = modo_fallo.loc[modo_fallo.index[0], 'd_max']

    x1 = np.linspace(0, x_0, 100)
    x2 = np.linspace(x_0, x_max, 100)

    d1 = x1*0
    m = (d_max - d_0) / (x_max - x_0)
    d2 = d_0 + m * (x2 - x_0)

    x = np.concatenate((x1, x2), axis=0)
    d = np.concatenate((d1, d2), axis=0)

    return (x, d)


def ecuacion_danno_archivo(modo_fallo, archivo):

    datos = pd.read_csv(archivo, delim_whitespace=True, header=None)
    x = datos.iloc[:, 0]
    d = datos.iloc[:, 1]

    return(x, d)


def ecuacion_coste_exponencial(modo_fallo, archivo):

    d_max = modo_fallo.loc[modo_fallo.index[0], 'd_max']
    c_min = modo_fallo.loc[modo_fallo.index[0], 'c_min']
    c_max = modo_fallo.loc[modo_fallo.index[0], 'c_max']

    d = np.linspace(0, d_max, 100)

    c = c_min + ((c_max - c_min) / (math.e - 1)) * (np.exp((d - 0) / (d_max - 0)) - 1)

    return (d, c)


def ecuacion_coste_lineal(modo_fallo, archivo):

    d_max = modo_fallo.loc[modo_fallo.index[0], 'd_max']
    c_min = modo_fallo.loc[modo_fallo.index[0], 'c_min']
    c_max = modo_fallo.loc[modo_fallo.index[0], 'c_max']

    d = np.linspace(0, d_max, 100)

    m = (c_max - c_min) / (d_max - 0)
    c = c_min + m * (d - 0)

    return (d, c)


def ecuacion_coste_archivo(modo_fallo, archivo):

    datos = pd.read_csv(archivo, delim_whitespace=True, header=None)
    d = datos.iloc[:, 0]
    c = datos.iloc[:, 1]

    return(d, c)
