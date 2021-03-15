import sympy as sp 

x = sp.symbols('x')
expr = -10*sp.cot(x) + 10*(sp.atan(x))**2 + 2

integral = sp.integrate(expr, x).doit()
print(expr, integral)