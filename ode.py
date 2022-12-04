import matplotlib.pyplot as plt 
from root import *
import numpy as np
import time

class ODESolver():
    def __init__(self, f_size=np.float64):
        self._INIT_AB = 0
        self._INIT_H = 0
        self._INIT_EQN = 0
        self._INIT_IVP = 0
        self.f_size = f_size

    def init(self, func, n, ivp, a=0e0, b=1e0, h=5e-2):
        self.n = int((b - a) / h)
        self.a = self.f_size(a)
        self.b = self.f_size(b)
        self.h = self.f_size(h)
        self.hs = [self.h] # list of step h (for recording adaptive step)
        self.f = func
        self.m = n

        self.x = np.array([a + i * self.h for i in range(self.n + 1)], dtype=self.f_size)
        self.y = np.zeros([self.n + 1, self.m], dtype=self.f_size)
        self.y[0] = ivp

    def _set_ab(self, a, b):
        self.a = self.f_size(a)
        self.b = self.f_size(b)
        self._INIT_AB = 1
        self._check_and_set_n()

    def _set_h(self, h):
        self.h = self.f_size(h)
        self.hs = [self.h]
        self._INIT_H = 1
        self._check_and_set_n()

    def _set_func(self, func, eq_n):
        self.f = func
        self.m = eq_n      
        self._INIT_EQN = 1  
        self._check_and_set_xy()
    
    def _set_ivp(self, ivp):
        self.ivp = ivp
        self._INIT_IVP = 1 
        self._check_and_set_xy()


    def _check_and_set_n(self):
        if self._INIT_AB * self._INIT_H == 1:
            self.n = int((self.b - self.a) / self.h)
        else:
            pass

    def _check_and_set_xy(self):
        if self._INIT_AB * self._INIT_H * self._INIT_EQN * self._INIT_IVP == 1:
            self.x = np.array([self.a + i * self.h for i in range(self.n + 1)], dtype=self.f_size)
            self.y = np.zeros([self.n + 1, self.m], dtype=self.f_size)
            self.y[0] = self.ivp
        else:
            pass
    
    def solve(self):
        start_t = time.time()

        self.advance()
        
        ent_t = time.time()
        self.solving_time = (ent_t - start_t)

    def advance(self):
        pass

    def plotn(self, row, column, labels):
        t = self.x
        fig, ax = plt.subplots(row, column, figsize=(12,6))

        for i in range(row):
            for j in range(column):
                # ax[i][j].set_title(f"{labels[i * column + j]}")
                ax[i, j].plot(self.x, self.y[:, i * column + j], color=f"C{i * column + j}", label=f"{labels[i * column + j]}")
                ax[i, j].set_xlabel('Time')
                ax[i, j].set_ylabel(f"{labels[i * column + j]}")
                ax[i, j].legend()
        fig.tight_layout()
        plt.show()

    def plot(self, label):
        plt.figure(figsize=(12, 6))

        for i in range(self.m):
            plt.plot(self.x, self.y[:,i], '--', label=label[i])

        plt.xlabel('t')
        plt.ylabel('Multiple')
        plt.legend()
        plt.show()

    def plotxy(self):
        plt.figure(figsize=(12, 6))


        plt.plot(self.y[:,0], self.y[:,1])

        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.show()   

class ForwardEuler(ODESolver):
    def advance(self):
        for i in range(self.n):
            self.y[i+1, :] = self.y[i, :] + self.h * self.f(self.x[i], self.y[i, :], self.y[i, :].copy())

class BackwardEuler(ODESolver):
    def advance(self):
        for i in range(self.n):

            for j in range(self.m):
                y_next = self.y[i, :]
                g = lambda y_hat: y_hat - self.y[i,j] - self.h * self.f(self.x[i+1], y_next, y_next.copy())[j]
                y_next[j] = Newton(g, y_next[j])
                self.y[i, j] = y_next[j]

            self.y[i+1, :] = y_next

class ForwardEulerCromer(ODESolver):
    def advance(self):
        for i in range(self.n):
            for j in range(self.m):
                self.y[i, j] = self.y[i, j] + self.h * self.f(self.x[i], self.y[i, :], self.y[i, :].copy())[j]
            self.y[i+1, :] = self.y[i, :]

class RungeKutta4(ODESolver):
    def advance(self):
        _h = self.f_size(1 / 6)

        for i in range(self.n):
            
            x_i = self.x[i]
            y_i = self.y[i, :]

            y1 = y_i
            f1 = y1.copy()
            k1 = self.h * self.f(x_i, y1, f1)

            y2 = y_i + 0.5 * k1
            f2 = y2.copy()
            k2 = self.h * self.f(x_i + 0.5 * self.h, y2, f2)

            y3 = y_i + 0.5 * k2
            f3 = y3.copy()
            k3 = self.h * self.f(x_i + 0.5 * self.h, y3, f3)


            y4 = y_i + k3
            f4 = y4.copy()
            k4 = self.h * self.f(x_i + self.h, y4, f4)

            for j in range(self.m):
                self.y[i, j] = self.y[i, j] + _h * (k1 + 2 * k2 + 2 * k3 + k4)[j]

            self.y[i+1, :] = self.y[i, :]    


class RungeKuttaFehlberg(ODESolver):
    """
    According to error estimation formula: (step_size, eps) = (1e-k, 1e-(k+6))
    k = 6 for p = 5 calculating O(h^6)
    Examples:
        - (1e-0, 1e-6)
        - (1e-2, 1e-8)
        - (1e-6, 1e-12)
    
    """
    def init(self, func, n, ivp, a=0e0, b=1e0, h=1e-2):
        self.n = n
        self.a = self.f_size(a)
        self.b = self.f_size(b)
        self.h = self.f_size(h)
        self.hs = [self.h] # list of step h (for recording adaptive step)
        self.f = func
        self.m = n
        self.eps = h * 1e-6

        self.x = np.zeros([1, 1], dtype=self.f_size)
        self.x[0][0] = self.a
        self.y = np.zeros([1, self.m], dtype=self.f_size)
        self.y[0] = ivp

    def _set_ab(self, a, b):
        self.a = self.f_size(a)
        self.b = self.f_size(b)
        self._INIT_AB = 1

    def _set_h(self, h):
        self.h = self.f_size(h)
        self.hs = [self.h]
        self.eps = h * 1e-6
        self._INIT_H = 1

    def _set_func(self, func, eq_n):
        self.f = func
        self.m = eq_n      
        self._INIT_EQN = 1  
        self._check_and_set_xy()
    
    def _set_ivp(self, ivp):
        self.ivp = ivp
        self._INIT_IVP = 1 
        self._check_and_set_xy()

    def _check_and_set_xy(self):
        if self._INIT_AB * self._INIT_H * self._INIT_EQN * self._INIT_IVP == 1:
            self.x = np.zeros([1, 1], dtype=self.f_size)
            self.x[0][0] = self.a
            self.y = np.zeros([1, self.m], dtype=self.f_size)
            self.y[0] = self.ivp
        else:
            pass

    def advance(self):
        # adaptive ODE solver
        # step size h keeps unchanges if err <= eps
        # step size h is reduced if err > eps

        # maximum acceptable error epsilon
        eps = 1e-8
        p = 5 # order of basic ODE solver

        a2, b21 = 1e0/4e0, 1e0/4e0
        a3, b31, b32 = 3e0/8e0, 3e0/32e0, 9e0/32e0
        a4, b41, b42, b43 = 12e0/13e0, 1932e0/2197e0, -7200e0/2197e0, 7296e0/2197e0
        a5, b51, b52, b53, b54 = 1e0, 439e0/216e0, -8e0, 3680e0/513e0, -845e0/4104e0
        a6, b61, b62, b63, b64, b65 = 1e0/2e0, -8e0/27e0, 2e0, -3544e0/2565e0, 1859e0/4104e0, -11e0/40e0

        c1, c3, c4, c5, c6 = 16e0/135e0, 6656e0/12825e0, 28561e0/56430e0, -9e0/50e0, 2e0/55e0
        e1, e3, e4, e5, e6 = 1e0/360e0, -128e0/4275e0, -2197e0/75240e0, 1e0/50e0, 2e0/55e0

        i = 0
        while self.x[i] < self.b:
            # For adaptive h, x_i varies each step
            x_i = self.x[i]
            x_next = x_i + self.h
            self.x = np.append(self.x, x_next)

            y_i = self.y[i, :]
            
            x1 = x_i
            y1 = y_i
            f1 = y1.copy()
            k1 = self.f(x1, y1, f1)

            x2 = x_i + a2 * self.h
            y2 = y_i + b21 * k1 * self.h
            f2 = y2.copy()
            k2 = self.f(x2, y2, f2)

            x3 = x_i + a3 * self.h
            y3 = y_i + b31 * k1 * self.h + b32 * k2 * self.h
            f3 = y3.copy()
            k3 = self.f(x3, y3, f3)

            x4 = x_i + a4 * self.h
            y4 = y_i + b41 * k1 * self.h + b42 * k2 * self.h + b43 * k3 * self.h
            f4 = y4.copy()
            k4 = self.f(x4, y4, f4)

            x5 = x_i + a5 * self.h
            y5 = y_i + b51 * k1 * self.h + b52 * k2 * self.h + b53 * k3 * self.h + b54 * k4 * self.h
            f5 = y5.copy()
            k5 = self.f(x5, y5, f5)

            x6 = x_i + a6 * self.h
            y6 = y_i + b61 * k1 * self.h + b62 * k2 * self.h + b63 * k3 * self.h + b64 * k4 * self.h + b65 * k5 * self.h
            f6 = y6.copy()
            k6 = self.f(x6, y6, f6)


            # update y
            y_next = self.y[i, :] + self.h * (c1 * k1 + c3 * k3 + c4 * k4 + c5 * k5 + c6 * k6)
            self.y = np.append(self.y, [y_next], axis=0)
            
            err = 0e0
            
            for j in range(self.m):
                
                # estimation of truncation error (in RK-Fehlberg method)
                erri = self.h * (e1 * k1 + e3 * k3 + e4 * k4 + e5 * k5 + e6 * k6)[j]
                y_updated = self.y[i+1, j]

                # refer to "relative error" = delta / | y_{m+1}|

                erri = abs(erri / y_updated) # relative error

                # if "relative error" become larger, replace the former one
                if err < erri:
                    err = erri


            # scaling factor for step size
            factor = 1e0
            if err:
                factor = 0.9e0 * pow(self.eps/err, 1e0/p)  # factor can be > 1 or < 1

            if factor > 5e0: # scaling factor not > 5x
                factor = 5e0

            # step size guess for next propagation

            h1 = factor * self.h

            # if err less then eps, keep step size h, continue
            if err <= self.eps:
                pass
            
            self.h = h1
            self.hs.append(self.h)

            i += 1

