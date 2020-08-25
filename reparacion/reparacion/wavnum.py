import numpy as np
from scipy.optimize import fsolve


def wavnum(t, h):
    g = 9.81
    gamma = (2 * np.pi / t) ** 2. * h / g
    sigma2 = (2 * np.pi / t) ** 2

    def func(k):
        return sigma2 / g - k * np.tanh(k * h)

    if gamma > np.pi ** 2.:
        ko = np.sqrt(gamma / h)
        k = fsolve(func, ko)
    else:
        ko = gamma / h
        k = fsolve(func, ko)

        k = abs(k)

    return k
