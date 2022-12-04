import numpy as np
import os

def Newton(Func, x):
    """
    For solving g(x) = y[i+1] - y[i] - f(x[i+1], y[i+1]) = 0,
    - known: y[i], x[i+1]
    - unknown: y[i+1] -> as input 'x'
    - (a, b) = (y[i], ?) -? 
    """

    eps = 1e-10
    itmax = 100

    for i in range(1, itmax+1):
        f = Func(x)

        if x == 0:
            dx = eps
        else:
            dx = eps * abs(x)

        df = (Func(x + dx) - f) / dx

        if abs(df) > eps:
            dx = -f / df
        else:
            dx = -f

        x += dx

        # if (x < a) or (x > b):
        #     return (x, 1)

        if abs(dx) <= eps * abs(x):

            return x
    return x


if __name__ == '__main__':

    def func(x):
        return x - np.sin(x) - 0.25

    sol = Newton(func, 1.17)
    print(sol)