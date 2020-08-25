from . import constantes as c


def clasifica_si_ciclo_solicitacion(comprobacion):
    clasificacion = -1

    if comprobacion:
        clasificacion = c.CICLO_SOLICITACION
    else:
        clasificacion = c.CICLO_CALMA

    return (clasificacion)


def clasifica_si_inicio_de_averia(comprobacion):

    if comprobacion:
        clasificacion = c.CICLO_SOLICITACION
    else:
        clasificacion = c.CICLO_CALMA

    return (clasificacion)


def clasifica_si_se_supera_umbral_de_reparacion(comprobacion):
    clasificacion = -1

    if comprobacion:
        clasificacion = 1
    else:
        clasificacion = 0

    return (clasificacion)


def clasifica_si_el_modo_esta_reparando(comprobacion):
    clasificacion = -1

    if comprobacion:
        clasificacion = 1
    else:
        clasificacion = 0

    return (clasificacion)


def clasifica_superacion_umbral_operativo(comprobacion):
    clasificacion = -1

    if comprobacion:
        clasificacion = 1
    else:
        clasificacion = 0

    return(clasificacion)


def clasifica_si_na_menor_na_umbral_fin_reparacion(comprobacion):
    clasificacion = -1

    if comprobacion:
        clasificacion = 1
    else:
        clasificacion = 0

    return(clasificacion)

#    if comprobacion:
#        clasificacion = c.MODO_TIENE_AVERIA
#    else:
#        clasificacion = c.MODO_NO_TIENE_AVERIA
#
#        return (clasificacion)