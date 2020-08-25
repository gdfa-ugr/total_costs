from IPython.display import HTML


def lectura_fichero_entrada(ruta, n_lineas):
    fichero = open(ruta, 'r')
    lines = fichero.readlines()
    content = '<br>'.join(lines[0: n_lineas])
    HTML(content)

    return content
