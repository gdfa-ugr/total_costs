import numpy as np
from wavnum import wavnum

tp = 12
calado =15
h_eq = 3.77
cadencia = 3
a = 0.67
b = 1.0
c = 3.3861

# Calculo del peralate
k = wavnum(tp, calado)
wavelen = 2 * np.pi / k
per = h_eq /wavelen

n_olas = (cadencia*3600)/(tp/1.25)

dano = (((a*(per**c))**(1/b))*n_olas)**b