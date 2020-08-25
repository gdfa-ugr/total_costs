    """Funcion a la que le llega una fase clasificada a nivel I como EN ALERTA, a nivel II como EN PROCESO DE
    PROTECCION y la clasifica a Nivel III como:

    * FASE PERDIDAS -> Si se supera el umbral de daños
    * FASE EN PROCESO DE PROTECCION -> Si no se supera dicho umbral

        - FASE EN PROCESO DE PROTECCION -> Si aun no se ha protegido toda la longitud avanzada en la fase
        - FASE PROTEGIDA -> Si se consigue proteger toda la longitud avanzada en la fase

    Args:
        hora: Hora.
        fase: Fase.
        clasificacion1: Valor de la clasificacion a nivel I
        avance_real: Matriz que anota para cada hora el estado de la fase a nivel II
        estado_real: Matriz que anota para cada hora el estado de la fase a nivel III
        datos_entrada: Matriz con los datos de entrada introducidos por el usuario
        longitudes: Matriz donde se actualiza el valor de la longitud avanzada, protegida y desprotegida para cada fase
        vol_ejecutado: Matriz donde se actualiza para cada hora los volumenes ejecutados de cada una de las fases de
                       la obra.
        clima: Matriz con las series temporales climaticas simuladas en cada tramo

    Returns:
        Las matrices de longitudes y vol_ejecutado actualizados tras clasificar la fase para una hora dada.

    """