
class Example_Lorenz:
    equation_string = "dx/dt = sigma * (y - x); dy/dt = rho * x - y - x * z; dz/dt = x * y - beta * z;"
    const_string = "sigma = 10e0; rho = 28e0; beta = 8e0 / 3e0;"
    ivp = "0,1,0"

class Example_Mechanical:
    equation_string = '''
dp3/dt = - q4 * k4 + F;
dp2/dt = q4 * k4 - p2 * b1 / m2 - k3 * q3 + p1 * b1 / m1 - q1 * k1;
dp1/dt = p2 * b1 / m2 + q3 * k3 - p1 * b1 / m1 - q2 * k2;
dq4/dt = p3 / m3 - p2 / m2;
dq3/dt = p2 / m2 - p1 / m1;
dq2/dt = p1 / m1 - V;
dq1/dt = p2 / m2 - V;
'''
    const_string = '''
F = 10;
V = 0;
k1 = 1;
k2 = 1;
k3 = 1;
k4 = 1;
m1 = 1;
m2 = 2;
m3 = 3;
b1 = 2
        '''
    ivp = "0,0,0,0,0,0,0"


class Stiff:
    equation_string = '''
dy/dt = A * y + B * u
du/dt = C * y + D * u
'''
    const_string = '''
A = - 100e0;
B = 100.1e0;
C = 100.1e0;
D = -100e0;
'''