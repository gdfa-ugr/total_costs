import pandas as pd
import os

import pickle

from .calculos import extraccion_datos_reparacion_de_diccionario
from .calculos import extraccion_datos_reparacion_disponibles_de_diccionario


def datos_entrada_planta(ruta_de='.'):

    # Forma en planta
    direct = os.path.join(ruta_de, 'planta', 'datos_entrada_planta.txt')
    de_planta = pd.read_table(direct, sep=',', quoting=2)

    return de_planta


def datos_entrada_diagrama_modos(ruta_de='.'):
    # Diagrama de modos para el dique
    direct = os.path.join(ruta_de, 'diagrama_de_modos', 'diagrama_modos_dique.txt')
    de_diagrama_modos_dique = pd.read_table(direct, sep=',', quoting=2, index_col=[0, 1])

    # Diagrama de modos para los tramo
    direct = os.path.join(ruta_de, 'diagrama_de_modos', 'diagrama_modos_tramos.txt')
    de_diagrama_modos_tramos = pd.read_table(direct, sep=',', quoting=2, index_col=[0, 1])

    # Diagrama de modos para los subsistemas
    direct = os.path.join(ruta_de, 'diagrama_de_modos', 'diagrama_modos_subsistemas.txt')
    de_diagrama_modos_subsistemas = pd.read_table(direct, sep=',', quoting=2, index_col=[0, 1, 2])

    de_diagrama_modos = {'de_diagrama_modos_dique': de_diagrama_modos_dique,
                         'de_diagrama_modos_tramos': de_diagrama_modos_tramos,
                         'de_diagrama_modos_subsistemas': de_diagrama_modos_subsistemas}

    # Codigo para leer esto
    # prueba = de_diagrama_modos['de_diagrama_modos_dique'].loc['Dique', 'opciones_de_destruccion_total']
    # prueba = ast.literal_eval(prueba)

    return de_diagrama_modos


def datos_entrada_arbol_fallo(alcance, de_esquema_division_dique, ruta_de='.'):

    if ((alcance == 'EA') | (alcance == 'EA_sencillo')):
        columnas = ['modos', 'nivel_averia']
        valores_indice = de_esquema_division_dique
        tuples = [tuple(x) for x in valores_indice.values]
        indices = pd.MultiIndex.from_tuples(tuples, names=['tr', 'ss', 'mf'])
        de_arbol_fallo = pd.DataFrame('0', index=indices, columns=columnas)
        de_arbol_fallo.sort_index(inplace=True)

    else:
        # Diagrama de modos para el dique
        direct = os.path.join(ruta_de, 'arbol_modos_de_fallo', 'arbol_modos_de_fallo.txt')
        de_arbol_fallo = pd.read_table(direct, sep=',', quoting=2, index_col=[0, 1, 2])
        # lista = ast.literal_eval(de_arbol_fallo.loc['T_0', 'SS_0', 'MF_2']['arbol_modos_de_fallo'])
        # prueba = ast.literal_eval(de_arbol_fallo.loc['T_0', 'SS_0']['arbol_modos_de_fallo'])

    return de_arbol_fallo


def datos_entrada_esquema_division_dique(ruta_de='.'):
    # Esquema con la division del dique en tramos, subsistemas y modos de fallo
    direct = os.path.join(ruta_de, 'esquema_division_dique', 'esquema_division_dique.txt')
    de_esquema_division_dique = pd.read_table(direct, sep=',', quoting=2)

    return de_esquema_division_dique


def datos_entrada_tipo_verificacion(ruta_de='.'):
    # Esquema con la division del dique en tramos, subsistemas y modos de fallo
    direct = os.path.join(ruta_de, 'tipo_verificacion_curva_acum_dano', 'tipo_verificacion_curva_acum_dano.txt')
    de_tipo_verificacion = pd.read_table(direct, sep=',', quoting=2)

    return de_tipo_verificacion


def datos_entrada_clima_tramos(de_esquema_division_dique, de_planta, ruta_de='.'):
    # Lectura de los tramos

    clima_tramos = {}
    # Obtencion de los tramos
    tramos = de_esquema_division_dique.loc[:, 'tramo'].unique()

    for j in tramos:
        # Lectura del clima para el tramo
        direct = os.path.join(ruta_de, 'clima', j, 'clima.csv.zip')
        clima = pd.read_table(direct, delim_whitespace=True)
        # Se annade el calado
        clima['calado'] = clima.loc[:, 'nivel'] + de_planta.loc[j, 'calado']
        clima = clima.reset_index(drop=True)

        # Correccion periodos
        clima.loc[clima.loc[:, 'tp'] <5, 'tp'] = 5

        # Se guarda como diccionario
        clima_tramos[j] = clima

    # Cadencia de los datos
    direct = os.path.join(ruta_de, 'cadencia_datos', 'cadencia_datos.txt')
    cadencia = pd.read_table(direct, delim_whitespace=True)
    cadencia = cadencia.loc[cadencia.index[0], 'cadencia']

    return (clima_tramos, cadencia)


def datos_entrada_elementos_reparacion_necesarios(ruta_de, cadencia, alcance, estrategia):

    if (alcance == 'EA'):
        # Lectura de los datos de reparacion
        direct = os.path.join(ruta_de, 'reparacion', 'elementos_necesarios_reparacion.txt')
        de_reparacion_necesarios = pd.read_table(direct, sep=',', quoting=2, index_col=[0, 1, 2])

        if estrategia == 'no_reparacion':
            de_reparacion_necesarios.loc[:, 'na_umbral_ini_reparacion'] = 2  # 200 % para que nunca inicie reparacion
            de_reparacion_necesarios.loc[:, 'na_umbral_fin_reparacion'] = 0
            de_reparacion_necesarios.loc[:, 't_espera_ini_reparacion'] = 0

        elif estrategia == 'reparacion_inmediata':
            de_reparacion_necesarios.loc[:, 'na_umbral_ini_reparacion'] = 0.01  # 1 % para que inicie reparacion siempre
            de_reparacion_necesarios.loc[:, 'na_umbral_fin_reparacion'] = 0
            de_reparacion_necesarios.loc[:, 't_espera_ini_reparacion'] = 0
            de_reparacion_necesarios.loc[:, 'rend'] = 1

        elif estrategia == 'reparacion_tiempo_real':
            de_reparacion_necesarios.loc[:, 'na_umbral_ini_reparacion'] = 0.01  # 1 % para que inicie reparacion siempre
            de_reparacion_necesarios.loc[:, 'na_umbral_fin_reparacion'] = 0




    else:
        # Lectura de los datos de reparacion
        direct = os.path.join(ruta_de, 'reparacion', 'elementos_necesarios_reparacion.txt')
        de_reparacion_auxiliar = pd.read_table(direct, sep=',', quoting=2, index_col=[0, 1, 2])

        columnas = ['na_umbral_ini_reparacion', 'na_umbral_fin_reparacion','tipos_maq', 'num_maq', 'tipos_mat', 'cant_mat', 'tipos_mo', 'num_mo',
                    't_maq_ini_rep', 't_mat_ini_rep', 't_mo_ini_rep', 'umb_ope', 'rend', 'coste_maq_rep', 'coste_mat_rep',
                    'coste_mo_rep']
        de_reparacion_necesarios = pd.DataFrame(index=de_reparacion_auxiliar.index, columns=columnas)

        # Extraccion del tipo y numero de maquinaria, materiales y mano de obra, tiempos necesarios para iniciar
        # la reparacion
        for j in range(0, de_reparacion_necesarios.shape[0]):

            extraccion_datos_reparacion_de_diccionario(
                    j, de_reparacion_auxiliar, de_reparacion_necesarios, 'maquinaria_reparacion', 'tipos_maq', 'num_maq',
                    'num', 't_maq', 't_maq_ini_rep', 'coste_maq_rep', cadencia, 'umb_ope', 'umb_ope')

            extraccion_datos_reparacion_de_diccionario(
                    j, de_reparacion_auxiliar, de_reparacion_necesarios, 'materiales_reparacion', 'tipos_mat', 'cant_mat',
                    'cant', 't_mat', 't_mat_ini_rep', 'coste_mat_rep', cadencia)

            extraccion_datos_reparacion_de_diccionario(
                    j, de_reparacion_auxiliar, de_reparacion_necesarios, 'mano_obra_reparacion', 'tipos_mo', 'num_mo',
                    'num','t_mo', 't_mo_ini_rep', 'coste_mo_rep', cadencia, j)

            # Extraccion del rendimiento de reparacion
            de_reparacion_necesarios.loc[de_reparacion_necesarios.index[j], 'rend'] = de_reparacion_auxiliar.loc[de_reparacion_auxiliar.index[j], 'rend_reparacion']

            if alcance == 'PI':
                de_reparacion_necesarios.loc[de_reparacion_necesarios.index[j], 'na_umbral_ini_reparacion'] = \
                    de_reparacion_auxiliar.loc[de_reparacion_auxiliar.index[j], 'na_umbral_ini_reparacion']

                de_reparacion_necesarios.loc[de_reparacion_necesarios.index[j], 'na_umbral_fin_reparacion'] = \
                    de_reparacion_auxiliar.loc[de_reparacion_auxiliar.index[j], 'na_umbral_fin_reparacion']

            elif ((alcance == 'AP') & (estrategia == 'no_reparacion')):
                de_reparacion_necesarios.loc[de_reparacion_necesarios.index[j], 'na_umbral_ini_reparacion'] = 2  # 200 % para que nunca inicie reparacion
                de_reparacion_necesarios.loc[de_reparacion_necesarios.index[j], 'na_umbral_fin_reparacion'] = 0
            elif ((alcance == 'AP') & (estrategia == 'reparacion_inmediata_tiempo_real')):
                de_reparacion_necesarios.loc[de_reparacion_necesarios.index[j], 'na_umbral_ini_reparacion'] = 0.01  # 1 % para que inicie reparacion siempre
                de_reparacion_necesarios.loc[de_reparacion_necesarios.index[j], 'na_umbral_fin_reparacion'] = 0


    return(de_reparacion_necesarios)


def datos_entrada_elementos_reparacion_disponibles(ruta_de, cadencia, alcance):
    if alcance == 'PI':
        # Lectura de los elementos de reparacion disponibles en el puerto
        direct = os.path.join(ruta_de, 'reparacion', 'elementos_puerto_reparacion.txt')
        de_reparacion_auxiliar = pd.read_table(direct, sep=',', quoting=2)

        columnas = ['tipos_maq', 'num_maq', 'tipos_mat', 'cant_mat', 'tipos_mo', 'num_mo', 'coste_maq_mant',
                    'coste_mat_mant', 'coste_mo_mant']
        indices = ['iniciales', 'disponibles']
        de_reparacion_disponibles = pd.DataFrame(index=indices, columns=columnas)

        extraccion_datos_reparacion_disponibles_de_diccionario(
                de_reparacion_auxiliar, de_reparacion_disponibles, 'maquinaria_disponible', 'tipos_maq', 'num_maq',
                'num', 'coste_maq_mant', 'iniciales', 'disponibles', cadencia)

        extraccion_datos_reparacion_disponibles_de_diccionario(
                de_reparacion_auxiliar, de_reparacion_disponibles, 'materiales_disponibles', 'tipos_mat',
                'cant_mat', 'cant', 'coste_mat_mant',  'iniciales', 'disponibles', cadencia)

        extraccion_datos_reparacion_disponibles_de_diccionario(
                de_reparacion_auxiliar, de_reparacion_disponibles, 'mano_obra_disponible', 'tipos_mo', 'num_mo',
                'num', 'coste_mo_mant', 'iniciales', 'disponibles', cadencia)
    else:
        de_reparacion_disponibles = 0

    return(de_reparacion_disponibles)


def datos_entrada_verificacion_dique(ruta_de, de_esquema_division_dique):
    direct = os.path.join(ruta_de, 'verificacion_dique', 'simulacion_ejemplo_0.h5')
    tramo_0 = pd.read_hdf(direct, 'datos')

    columnas = tramo_0.index
    valores_indice = de_esquema_division_dique
    valores_indice = valores_indice.drop_duplicates()
    tuples = [tuple(x) for x in valores_indice.values]
    indices = pd.MultiIndex.from_tuples(tuples, names=['tr', 'ss', 'mf'])
    de_verificacion_tramos = pd.DataFrame(index=columnas, columns=indices)
    de_verificacion_tramos.sort_index(inplace=True)

    de_verificacion_tramos.iloc[:, 0] = tramo_0.iloc[:, 0].values
    peralte = pd.DataFrame(index=columnas, columns=['peralte'])
    peralte.iloc[:,0] = tramo_0.iloc[:, 1].values

    # Elimino los peraltes mayor que 1/7 por criterio de rotura
    pos = peralte.iloc[:, 0] > 0.14
    peralte.iloc[pos[pos == True].index, 0] = 0.14

    pos = peralte.iloc[:, 0] < 0
    peralte.iloc[pos[pos == True].index, 0] = 0



#    direct = os.path.join(ruta_de, 'verificacion_dique', 'tramo_1.h5')
#    tramo_1 = pd.read_hdf(direct, 'tramo_1')
#
#    direct = os.path.join(ruta_de, 'verificacion_dique', 'tramo_2.h5')
#    tramo_2 = pd.read_hdf(direct, 'tramo_2')

    return(de_verificacion_tramos, peralte)


def datos_entrada_estudio_previo_estudio_alterntivas(n, ruta_de='.', alcance='EP'):

    unidades_obra = -1
    if alcance == '-':
        # Datos de coste lineal de cada tipo de seccion
        direct = os.path.join(ruta_de, 'tablas_precios')
        direct = os.path.join(direct, 'secciones_dique.csv')
        tabla_precios = pd.read_table(direct, sep=',', index_col=0, decimal=',')
        unidades_obra = []

    elif ((alcance == 'EP') | (alcance == 'EA')):
        # Datos de coste lineal de cada unidad de obra
        direct = os.path.join(ruta_de, 'tablas_precios')
        direct = os.path.join(direct, 'precios_unitarios.csv')
        tabla_precios = pd.read_table(direct, sep=',', index_col=0, decimal=',')

        # Datos con las unidades de obra elegidas por el usuario
        direct = os.path.join(ruta_de, 'tramos', n, 'unidades_obra', 'unidades_obra.txt')
        unidades_obra = pd.read_table(direct, sep=',')

    return (tabla_precios, unidades_obra)
