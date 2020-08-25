import logging
import os

from timeit import default_timer as timer

from reparacion.main_alcances import main_alcances

if __name__ == '__main__':

    start = timer()

    # Ruta con los datos de entrada
    ruta_de = os.path.join('entrada')
    # Ruta con los datos de salida
    ruta_ds = os.path.join('salida')
    # Alcance del estudio
    alcance = 'PI'  #EP: Estudio previo o EA: Estudio de alternativas o EA_sencillo: Alcance I del estudio de alternativas  AP: AnteProyecto o PI: Proyecto de Inversion

    # estrategia = 'no_reparacion'
    estrategia = 'reparacion_inmediata_tiempo_real'

    # logging.basicConfig(level=logging.ERROR, format='%(levelname)s - %(funcName)s: %(message)s')
    direct = os.path.join(ruta_ds, 'debug_info.log')
    logging.basicConfig(filename=direct, level=logging.INFO, filemode='w')

    (salida) = main_alcances(ruta_de, ruta_ds, alcance, estrategia)

    end = timer()
    print(end - start)
