# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 21:34:53 2017

@author: JUAN
"""
import os
import ast
import pandas as pd

tr = 'T_0'
ss = 'SS_2'
mf = 'MF_8'

ruta_de = os.path.join('Datos_entrada', 'Ejemplo_sencillo_anteproyecto_no_reparacion')

direct = os.path.join(ruta_de, 'arbol_modos_de_fallo', 'arbol_modos_de_fallo.txt')
de_arbol_fallo = pd.read_table(direct, sep=',', quoting=2, index_col=[0, 1, 2])

modos_rel = ast.literal_eval(de_arbol_fallo.loc[(tr, ss, mf), 'modos'])
na_modos_rel = ast.literal_eval(de_arbol_fallo.loc[(tr, ss, mf), 'nivel_averia'])