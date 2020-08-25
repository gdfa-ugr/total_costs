def comprueba_si_ciclo_de_solicitacion(hs, p90):
    comprobacion = -1
    if hs >= p90:
        comprobacion = True
    else:
        comprobacion = False
    return(comprobacion)


def comprueba_si_hay_inicio_de_averia(ia_modos_fallo, tr, ss, mf):
    comprobacion = -1
    ia = ia_modos_fallo.loc[(tr,ss,mf), 'ini_averia']

    if ia == 1:
        comprobacion = True
    elif ia == 0:
        comprobacion = False

    return comprobacion


def comprueba_si_se_supera_umbral_de_reparacion(averia_acum_estado, tr, ss, mf, h, de_reparacion_necesarios, alcance):
    comprobacion = -1

    if averia_acum_estado.loc[(tr, ss, mf), h] >= de_reparacion_necesarios.loc[(tr, ss, mf), 'na_umbral_ini_reparacion']:
        comprobacion = True
    else:
        comprobacion = False

    return(comprobacion)


def comprueba_si_el_modo_esta_reparando(estado_reparacion_modos, tr, ss, mf):
    if estado_reparacion_modos.loc[(tr, ss, mf), 'reparando'] == 1:
        comprobacion = True
    else:
        comprobacion = False
    return(comprobacion)


def comprueba_superacion_umbral(hs, u10, z, umbrales, alcance):
    comprobacion = -1

    if ((alcance == 'EA') | (alcance == 'EA_sencillo')):
        comprobacion = False
    else:
        # Altura de ola
        comp_hs = hs >= umbrales['hs']
        # Velocidad de viento
        comp_vv = u10 >= umbrales['vv']
        # Calado
        comp_calado = z <= umbrales['calado']

        if any([comp_hs, comp_vv, comp_calado]):
            comprobacion = True
        else:
            comprobacion = False

    return comprobacion


def comprueba_si_na_menor_na_umbral_fin_reparacion(tr, ss, mf, h, averia_acum_estado, de_reparacion_necesarios,
                                                   alcance):
    comprobacion = -1

    if averia_acum_estado.loc[(tr, ss, mf), h] <= de_reparacion_necesarios.loc[(tr, ss, mf), 'na_umbral_fin_reparacion']:
        comprobacion = True
    else:
        comprobacion = False

    return(comprobacion)
