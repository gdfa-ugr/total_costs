import logging
import os

from .main_alcances import main_alcances

if __name__ == '__main__':

    # Ruta con los datos de entrada
    ruta_de = os.path.join('Datos_entrada', 'Ejemplo_sencillo_estudio_alternativas_sencillo_tres_modos')
    # Ruta con los datos de salida
    ruta_ds = os.path.join('Datos_salida', 'Ejemplo_sencillo_estudio_alternativas_sencillo_tres_modos')
    # Alcance del estudio
    alcance = 'EA_sencillo'  #EP: Estudio previo o EA: Estudio de alternativas o EA_sencillo: Alcance I del estudio de alternativas  AP: AnteProyecto o PI: Proyecto de Inversion

    # estrategia = 'no_reparacion'
    estrategia = 'reparacion_inmediata_tiempo_real'

    # logging.basicConfig(level=logging.ERROR, format='%(levelname)s - %(funcName)s: %(message)s')
    direct = os.path.join(ruta_ds, 'debug_info.log')
    logging.basicConfig(filename=direct, level=logging.INFO)

    (salida) = main_alcances(ruta_de, ruta_ds, alcance, estrategia)