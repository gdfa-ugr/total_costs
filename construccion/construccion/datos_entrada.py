import pandas as pd
import ast
import os
import numpy as np

from .ecuaciones_danno import ecuacion_danno_exponencial
from .ecuaciones_danno import ecuacion_danno_lineal
from .ecuaciones_danno import ecuacion_danno_archivo
from .ecuaciones_danno import ecuacion_coste_exponencial
from .ecuaciones_danno import ecuacion_coste_lineal
from .ecuaciones_danno import ecuacion_coste_archivo

from .calculos import calcula_rendimientos


def datos_entrada_planta(ruta_de='.', alcance='AP', estrategia='avance_paralelo'):
    """Funcion que lee los datos de entrada relacionados con la forma en planta.

    Args:
        ruta_de: cadena de texto con la ruta del directorio que contiene los datos de entrada
        alcance: etiqueta con el alcance del estudio
        estrategia: etiqueta con la estrategia a seguir

    Returns:
         Un tupla de la forma (de_planta, p_invernal).

        * ``de_planta``: Matriz con los datos de la forma en planta.
        * ``p_invernal``: Matriz con los datos de las paradas invernales

    """

    # Lectura del fichero de los datos de entrada relacionados con la planta (longitud del tramo y tipologia)
    direct = os.path.join(ruta_de, 'planta', 'datos_entrada_planta.txt')
    de_planta = pd.read_csv(direct, sep=',', quoting=2)

    # La parada invernal solo la leo si el alcance es proyecto de inversion o si es anteproyecto con
    # estrategia de cronograma

    # Lectura del fichero de las paradas invernales, hora de inicio y de finalizacion
    direct = os.path.join(ruta_de, 'parada_invernal', 'parada_invernal.txt')
    parada_invernal = pd.read_csv(direct, sep=',', quoting=2)
    p_invernal = []

    for j, _ in enumerate(parada_invernal.iterrows()):
        ini = parada_invernal.loc[parada_invernal.index[j], 'comienzo']
        fin = parada_invernal.loc[parada_invernal.index[j], 'final']
        p_invernal = p_invernal + list(range(int(ini), int(fin) + 1))


    return (de_planta, p_invernal)


def datos_entrada_tramo(de_planta, n, hora_inicio_tramos, alcance='AP', estrategia='avance_serie', ruta_de='.',
                        rep_inmediata='si'):

    """Funcion que lee los datos de entrada relacionados con la descripción del proceso constructivo de cada tramo.

    Args:
        de_planta: Matriz con los datos de entrada relativos a la planta del tramo

            * Etiqueta del tramo
            * Longitud del tramo
            * Tipologia del tramo
        n: Etiqueta del tramo
        hora_inicio_tramos: Matriz con las horas de inicio reales de ejecucion de cada uno de los tramos del dique
        ruta_de: cadena de texto con la ruta del directorio que contiene los datos de entrada
        alcance: etiqueta con el alcance del estudio
        estrategia: etiqueta con la estrategia a seguir
        rep_inmediata: parametro que indica con un 0 o 1 si los dannos sufridos son reparados de forma inmediata

    Returns:
         Un tupla de la forma (de_tramo, plan_avance, clima, com_fin_teorico)

        * ``de_tramo``: Matriz con los datos de entrada para cada tramo.
        * ``plan_avance``: Matriz con el cronograma de avance de los trabajos
        * ``clima``: Matriz con los datos de las series climaticas
        * ``com_fin_teorico``: Matriz con los datos de comienzo y finalizacion teoricos de cada subfase

    """

    # Lectura de las parametros constructivos de cada subfase

    # Inicializacion de la matriz con los datos de entrada del tramo
    de_tramo = pd.DataFrame(np.full((3, 12), 0, dtype=np.float))

    # Lectura del fichero con las distintas subfases constructivas del tramo
    direct = os.path.join(ruta_de, 'sub_fases', n)
    fichero_sub_fases = os.path.join(direct, 'sub_fases.txt')
    fo = open(fichero_sub_fases, 'r')
    sub_fases = fo.readlines()

    par_constructivos = []

    # Recorrido por las diferentes subfases constructivas del tramo
    for fase in sub_fases:

        # Lectura del fichero de los parametros constructivos para cada subfase constructiva
        directorio = fase.strip()
        directorio = os.path.join(direct, 'parametros_constructivos', directorio)
        datos_fase = pd.read_csv(directorio, sep=',', quoting=2)

        # Si el alcance es de anteproyecto obligo a reparacion inmediata y quito las estrategias de proteccion durante
        # la fase de construccion
        if alcance == 'EA':
            datos_fase.loc[datos_fase.index[0], 'n_horas_protecc_fijas_o_var'] = 'fijas'
            datos_fase.loc[datos_fase.index[0], 'n_horas_protecc_fijas'] = 0
            datos_fase.loc[datos_fase.index[0], 'n_horas_protecc_metro'] = 0
            datos_fase.loc[datos_fase.index[0], 'n_horas_protecc_max'] = 0
            datos_fase.loc[datos_fase.index[0], 'umb_protecc'] = "{'hs': {'dur': 0, 'valor': 100}, 'vv': {'dur': 0, 'valor': 100}}"
            datos_fase.loc[datos_fase.index[0], 'decision_proteger'] = 0

            if rep_inmediata == 'si':
                datos_fase.loc[datos_fase.index[0], 'reparacion_inmediata'] = 1

            elif rep_inmediata == 'no':
                datos_fase.loc[datos_fase.index[0], 'reparacion_inmediata'] = 0

        elif ((alcance == 'AP') | (alcance == 'PI')):
            datos_fase.loc[datos_fase.index[0], 'reparacion_inmediata'] = 0

        par_constructivos.append(datos_fase)

    # Concatenacion de los parametros constructivos de cada subfase en un solo dataframe
    de_tramo = pd.concat(par_constructivos)

    # Recorrido por las distintas subfases constructivas del tramo para annadir la variable 'volumen de la subfase
    # unitario' a cada subfase dividiendo el volumen total entre la longitud del tramo.
    for fase, _ in enumerate(de_tramo.iterrows()):

        # Lectura del volumen de la subfase (m3 o bloques)
        vol = de_tramo.loc[de_tramo.index[fase], 'vol_subfase']
        # Calculo del volumen unitario (m3/m o bloque/m)
        vol_subfase_unit = float(vol) / de_planta.loc[n, 'longitud']
        # Adicion de la nueva variable al dataframe
        de_tramo.at[de_tramo.index[fase], 'vol_subfase_unit'] = vol_subfase_unit

    # Inicializo la matriz de tiempos de inicio teoricos y tiempos de finalizacion teoricos
    com_fin_teorico = pd.DataFrame({'com_fase_teo': pd.Series(np.zeros(3)), 'fin_fase_teo': pd.Series(np.zeros(3))})

    if (((alcance == 'AP') | (alcance == 'PI')) | ((alcance == 'EA') & (estrategia== 'cronograma_trabajos'))):

        # Lectura del fichero de planificacion teorica
        direct = os.path.join(ruta_de, 'organizacion_proceso_constructivo', 'plan_avance.txt')
        plan_avance = pd.read_csv(direct, delim_whitespace=True, header=None)
        plan_avance = plan_avance.transpose()
        plan_avance.index = plan_avance[0]  # asigna la primera columna como indice
        plan_avance.drop(plan_avance.columns[0], axis=1, inplace=True)  # elimina la primera columna
        plan_avance.columns = pd.Int64Index(range(len(plan_avance.columns)))  # genera un nuevo indice para las columnas
        plan_avance = plan_avance.astype(int)
        plan_avance = plan_avance.astype(bool)  # convierte la matriz a booleanos
        # se queda unicamente con las fases correspondiente al tramo.
        plan_avance = plan_avance.loc[n, :]

    else:
        indice = np.repeat(n, de_tramo.shape[0])
        columna = range(0, 100000)
        plan_avance = pd.DataFrame(True, index=indice, columns=columna)

    # Se calculan los inicio y finales teoricos de las subfases constructivas para dicho tramo. Recorro cada una de
    # de las subfases (columnas del plan de avance) del tramo.
    for fase, _ in enumerate(de_tramo.iterrows()):
        plan_avance_fase = plan_avance.iloc[fase, :]

        # Inicio teorico de la subfase constructiva
        com_fin_teorico.at[fase, 'com_fase_teo'] = plan_avance_fase[plan_avance_fase == True].index[0]  # nopep8

        # Final teorico de la subfase constructiva
        com_fin_teorico.at[fase, 'fin_fase_teo'] = plan_avance_fase[plan_avance_fase == True].index[-1]  # nopep8

    # Toma el rango horario desde que acaba el tramo anterior hasta el final
    plan_avance = plan_avance.loc[n, hora_inicio_tramos[-1]:plan_avance.columns[-1]]

    # Lectura de los datos de clima a partir de fichero
    direct = os.path.join(ruta_de, 'clima', n, 'clima.csv.zip')
    clima = pd.read_csv(direct, sep=',')
    clima = clima.reset_index(drop=True)

    # Adicion de la variable calado al dataframe de clima
    clima['calado'] = clima.loc[:, 'eta'] + de_planta.loc[n, 'calado']

    return (de_tramo, plan_avance, clima, com_fin_teorico)


def datos_entrada_fase(de_planta, de_tramo, n, estrategia='avance_serie', alcance='AP', ruta_de='.'):
    """Funcion que lee los datos de entrada relacionados con la descripción del proceso constructivo de cada tramo.

    Args:
        de_planta: Matriz con los datos de entrada relativos a la planta del tramo

            * Etiqueta del tramo
            * Longitud del tramo
            * Tipologia del tramo
        de_tramo: Matriz con los datos de entrada para cada tramo
        n: Etiqueta del tramo
        ruta_de: cadena de texto con la ruta del directorio que contiene los datos de entrada
        alcance: etiqueta con el alcance del estudio
        estrategia: etiqueta con la estrategia a seguir

    Returns:
         Un tupla de la forma (maquinaria_fases, eq_danno_fases, eq_coste_fases, costes_fase, restricciones_fases).

        * ``maquinaria_fases``: Matriz con los datos de la maquinaria.
        * ``eq_danno_fases``: Matriz con los datos relacionados con las ecuaciones de danno para cada subfase
        * ``eq_coste_fases``: Matriz con los datos relacionados con las ecuaciones de costes para cada subfase
        * ``costes_fase``: Matriz con los datos costes para cada subfase
        * ``restricciones_fases``: Matriz con los datos relacionados con las restricciones de avance entre las subfases

    """

    # Lectura del fichero con las distintas subfases constructivas del tramo
    maquinaria_fases = []
    direct = os.path.join(ruta_de, 'sub_fases', n)
    fichero_sub_fases = os.path.join(direct, 'sub_fases.txt')
    fo = open(fichero_sub_fases, 'r')
    sub_fases = fo.readlines()

    # Recorrido por las diferentes subfases constructivas del tramo
    for fase in sub_fases:

        # Lectura de las diferents unidades de obra con su maquinaria para cada subfase constructiva
        directorio = fase.strip()
        directorio = os.path.join(direct, 'maquinaria', directorio)
        datos_maquinaria = pd.read_csv(directorio, sep=',', quoting=2, float_precision=3)
        maquinaria_fases.append(datos_maquinaria)

    # Lectura del fichero con las distintas subfases constructivas del tramo
    # TODO: ELIMINAR ESTE BLOQUE, NO ES NECESARIO VOLVER A CALCULAR SUBFASES
    modos_fallo_fases = []
    direct = os.path.join(ruta_de, 'sub_fases', n)
    fichero_sub_fases = os.path.join(direct, 'sub_fases.txt')
    fo = open(fichero_sub_fases, 'r')
    sub_fases = fo.readlines()

    # Recorrido por las diferentes subfases constructivas del tramo
    for fase in sub_fases:
        # if alcance == 'EA':
#            columna = ['modo_fallo_ppal', 'agente', 'ecuacion_danno', 'x_0', 'x_max', 'd_0', 'd_max', 'archivo_dannos', 'ecuacion_coste', 'c_min', 'c_max', 'archivo_costes']
#            indice = ['0']
#            datos_subfases = pd.DataFrame(index=indice, columns=columna)
#            datos_subfases.loc[0, 'agente'] = 'hs'
#            datos_subfases.loc[0, 'ecuacion_danno'] = 'lineal'
#            datos_subfases.loc[0, 'x_0'] = 100
#            datos_subfases.loc[0, 'x_max'] = 200
#            datos_subfases.loc[0, 'd_0'] = 0
#            datos_subfases.loc[0, 'd_max'] = 1
#            datos_subfases.loc[0, 'archivo_dannos'] = np.nan
#            datos_subfases.loc[0, 'ecuacion_coste'] = 'lineal'
#            datos_subfases.loc[0, 'c_min'] = 0
#            datos_subfases.loc[0, 'c_max'] = 0
#            datos_subfases.loc[0, 'archivo_costes'] = np.nan

        # else:
            # Lectura del modo de fallo principal de la subfase constructiva
        directorio = fase.strip()
        directorio = os.path.join(direct, 'modos_fallo', directorio)
        datos_subfases = pd.read_csv(directorio, sep=',', quoting=2)
        modos_fallo_fases.append(datos_subfases)

    # Lectura del fichero con las distintas subfases constructivas del tramo
    # TODO: ELIMINAR ESTE BLOQUE, NO ES NECESARIO VOLVER A CALCULAR SUBFASES
    costes_fase = []
    direct = os.path.join(ruta_de, 'sub_fases', n)
    fichero_sub_fases = os.path.join(direct, 'sub_fases.txt')
    fo = open(fichero_sub_fases, 'r')
    sub_fases = fo.readlines()

    # Recorrido por las diferentes subfases constructivas del tramo
    for fase in sub_fases:

#        if alcance == 'EA':
#            columna = ['costes_materiales_unit', 'coste_mantenimiento', 'coste_proteccion', 'costes_indirectos']
#            indice = ['0']
#            datos_costes = pd.DataFrame(0, index=indice, columns=columna)
#        else:

        # Lectura los datos de costes asociados a cada una de la subfases constructivas
        directorio = fase.strip()
        directorio = os.path.join(direct, 'costes', directorio)
        datos_costes = pd.read_csv(directorio, sep=',', quoting=2)

        # Si el alcance es de anteproyecto quito las estrategias de proteccion durante
        # la fase de construccion con lo cual los costes de proteccion son 0
#        if alcance == 'AP':
#            datos_costes.loc[datos_costes.index[0], 'coste_proteccion'] = 0

        costes_fase.append(datos_costes)

    # Construccion de las ecuaciones de danno  partir de los datos leidos
    eq_danno_fases = []

    # Recorrido por las diferentes subfases
    for fase, ruta in enumerate(sub_fases):
        archivo = ''
        # Reconstruccion de las curvas de agente - danno a partir de los parametros leidos del archivo
        if modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'ecuacion_danno'] == 'lineal':
            (x, d) = ecuacion_danno_lineal(modos_fallo_fases[fase], archivo)
        elif modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'ecuacion_danno'] == 'exponencial':
            (x, d) = ecuacion_danno_exponencial(modos_fallo_fases[fase], archivo)
        elif modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'ecuacion_danno'] == 'archivo':
            archivo = modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'archivo_dannos']
            archivo = archivo.strip()
            archivo = os.path.join(ruta_de, 'modos_fallo', archivo)
            archivo = os.path.join(direct, archivo)
            (x, d) = ecuacion_danno_archivo(modos_fallo_fases[fase], archivo)

        # Almacenamiento de la curva de danno en un diccionario para cada subfase
        danno = {modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'agente']: {'agente': x, 'danno': d}}
        eq_danno_fases.append(danno.copy())

    # Repeticion del procedimiento para los costes
    eq_coste_fases = []
    for fase, ruta in enumerate(sub_fases):
        archivo = ''

        if modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'ecuacion_coste'] == 'lineal':
            (d, c) = ecuacion_coste_lineal(modos_fallo_fases[fase], archivo)
        elif modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'ecuacion_coste'] == 'exponencial':
            (d, c) = ecuacion_coste_exponencial(modos_fallo_fases[fase], archivo)
        elif modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'ecuacion_coste'] == 'archivo':
            archivo = modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'archivo_costes']
            archivo = archivo.strip()
            archivo = os.path.join(ruta_de, 'modos_fallo', archivo)
            archivo = os.path.join(direct, archivo)
            (d, c) = ecuacion_coste_archivo(modos_fallo_fases[fase], archivo)

        coste = {modos_fallo_fases[fase].loc[modos_fallo_fases[fase].index[0], 'agente']: {'danno': d, 'coste': c}}
        eq_coste_fases.append(coste.copy())

    # Lectura del fichero con las distintas subfases constructivas del tramo
    # TODO: ELIMINAR ESTE BLOQUE, NO ES NECESARIO VOLVER A CALCULAR SUBFASES
    restricciones = []
    direct = os.path.join(ruta_de, 'sub_fases', n)
    fichero_sub_fases = os.path.join(direct, 'sub_fases.txt')
    fo = open(fichero_sub_fases, 'r')
    sub_fases = fo.readlines()

    if ((alcance == 'AP') | ((alcance == 'PI'))):
        # Recorrido por las diferentes subfases
        for fase in sub_fases:

            # Lectura de las restricciones de avance de cada subfase con las demas a partir de fichero
            directorio = fase.strip()
            directorio = os.path.join(direct, 'restricciones', directorio)
            datos_restricciones = pd.read_csv(directorio, sep=',', quoting=2)
            restricciones.append(datos_restricciones)
            restricciones_fases = pd.concat(restricciones)

    else:
        indice = de_tramo.index.values
        columna = ['restriccion', 'subfases']
        restricciones_fases = pd.DataFrame(1, index=indice, columns=columna)
        if estrategia == 'avance_serie':
            cont = 0
            for ind in indice:
                if cont <= 9:
                    if int(ind[0]) == 0:
                        restricciones_fases.loc[ind, 'restriccion'] = 0
                        restricciones_fases.loc[ind, 'subfases'] = np.nan
                        cont += 1
                    else:
                        valor = str({str(int(ind[0]) - 1): de_planta.loc[n, 'longitud']})
                        restricciones_fases.loc[ind, 'subfases'] = valor
                        cont += 1
                else:
                    valor = str({str(int(ind[:2]) - 1): de_planta.loc[n, 'longitud']})
                    restricciones_fases.loc[ind, 'subfases'] = valor
                    cont += 1

        elif ((estrategia == 'avance_paralelo') | (estrategia == 'cronograma_trabajos')):
            cont = 0
            for ind in indice:
                if cont <= 9:
                    if int(ind[0]) == 0:
                        restricciones_fases.loc[ind, 'restriccion'] = 0
                        restricciones_fases.loc[ind, 'subfases'] = np.nan
                        cont += 1
                    else:
                        valor = str({str(int(ind[0]) - 1): 0})
                        restricciones_fases.loc[ind, 'subfases'] = valor
                        cont += 1
                else:
                    valor = str({str(int(ind[:2]) - 1): 0})
                    restricciones_fases.loc[ind, 'subfases'] = valor
                    cont += 1

    return (maquinaria_fases, eq_danno_fases, eq_coste_fases, costes_fase, restricciones_fases)


def rendimientos_y_umbrales_datos_entrada(de_tramo, maquinaria_fases, alcance):

    # Recorrido por cada una de las subfases de la obra
    for fase, _ in enumerate(maquinaria_fases):
        # Inicializacion de las variables a necesitar
        cont = 0
        rend = pd.Series()
        t_arranque = pd.Series()
        h_lab_dia = pd.Series()
        dia_lab_sem = pd.Series()
        # print(fase)
        # Extraccion las unidades de obra de la subfase
        uds_obra = maquinaria_fases[fase]

        # Recorrido por cada una de las unidades de obra de la subfase
        for u_obra, _ in enumerate(uds_obra.iterrows()):
            # Extraccion de las maquinarias empleadas en la unidad de obra
            maq = ast.literal_eval(uds_obra.loc[uds_obra.index[u_obra], 'maquinaria'])

            # Recorrido por cada una de las maquinarias de la unidad de obra
            for key in maq:
                # Calculo del rendimiento de cada unidad de obra
                rend.at[cont] = maq[key]['rend_unit']*maq[key]['num']
                # Calculo del tiempo de arranque de cada unidad de obra
                t_arranque.at[cont] = maq[key]['t_arranque']
                # Calculo de las horas laborables al dia de cada unidad de obra
                h_lab_dia.at[cont] = maq[key]['h_lab_dia']
                # Calculo de los dias laborables a la semana de cada unidad de obra
                dia_lab_sem.at[cont] = maq[key]['dia_lab_sem']
                cont += 1

        # Calculo de los rendimientos de cada subfase
        rend_fase = calcula_rendimientos(de_tramo, fase, rend)
        # Calculo del tiempo de arranque de cada subfase
        t_arranque_fase = t_arranque.max()
        # Calculo de las horas laborables al dia de cada subfase
        h_lab_dia_fase = h_lab_dia.min()
        # Calculo de los dias laborables a la semana de cada subfase
        dia_lab_sem_fase = dia_lab_sem.min()

        # Asigno los valores calculados a la matriz de datos de entrada
        de_tramo.at[de_tramo.index[fase], 'rendimiento'] = rend_fase
        de_tramo.at[de_tramo.index[fase], 't_arranque_fase'] = t_arranque_fase
        de_tramo.at[de_tramo.index[fase], 'h_lab_dia_fase'] = h_lab_dia_fase
        de_tramo.at[de_tramo.index[fase], 'dia_lab_sem_fase'] = dia_lab_sem_fase

    # Umbrales de operatividad
    de_tramo.loc[de_tramo.index[fase], 'umb_operatividad'] = 'A'  # lo hago así para crear una columna de tipo obj

    # Recorrido por cada una de las subfases de la obra
    for fase, _ in enumerate(maquinaria_fases):
        cont = 0
        # Extraigo las unidades de obra de la subfase
        uds_obra = maquinaria_fases[fase]

        # Inicializacion de la matriz de umbrales a 0
        umbrales = pd.DataFrame(np.full((1, 4), 0, dtype=np.float), index=[0])
        umbrales.columns = ['hs', 'vv', 'nivel', 'calado']

        # Recorrido por las diferentes unidades de obra de la subfase
        for u_obra, _ in enumerate(uds_obra.iterrows()):

            # Extraccion de las maquinarias de cada unidad de obra
            maq = ast.literal_eval(uds_obra.loc[uds_obra.index[u_obra], 'maquinaria'])

            # Recorrido por cada una de las maquinarias de la unidad de obra
            for key in maq:
                # Extraccion de los umbrales de operatividad de la maquinaria para cada agente
                umb_operatividad = maq[key]['umb_operatividad']

                # Almacenamiento de los valores de umbral en el dateframe umbrales
                umbrales.at[cont, 'hs'] = umb_operatividad['hs']
                umbrales.at[cont, 'vv'] = umb_operatividad['vv']
                umbrales.at[cont, 'nivel'] = umb_operatividad['nivel']
                umbrales.at[cont, 'calado'] = umb_operatividad['calado']
                cont = cont + 1

        # Obtencion de los valores umbrales de operatividad de cada subfase como el valor umbral minimo de las
        # distintas unidades de obra para cada agente
        hs_min = umbrales.loc[:, 'hs'].min()
        vv_min = umbrales.loc[:, 'vv'].min()
        nivel_min = umbrales.loc[:, 'nivel'].min()
        calado_min = umbrales.loc[:, 'calado'].min()
        umb_operatividad = {'hs': {'valor': hs_min}, 'vv': {'valor': vv_min}, 'eta': {'valor': nivel_min}, 'calado': {
            'valor': calado_min}}

        # Asigno el valor de umbral a la matriz de datos de entrada del tramo
        de_tramo.at[de_tramo.index[fase], 'umb_operatividad'] = umb_operatividad

    return (de_tramo)
