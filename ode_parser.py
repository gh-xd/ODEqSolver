import re
import types
from math import *

"""
math.xx is not supported, e.g., sin(x) is not defined
"""

def func_from_string(equations, constants=None):
    eqs_str, dep_dict, indep_dict = __process_eq_str(equations)

    if constants:
        cons_str = __process_const_str(constants)
        print(f"def func(_x_, _y_, _f_): {cons_str} {eqs_str}")
        return __func_from_string(f"def func(_x_, _y_, _f_): {cons_str} {eqs_str} return _f_"), dep_dict, indep_dict

    return __func_from_string(f"def func(_x_, _y_, _f_): {eqs_str} return _f_"), dep_dict, indep_dict

def c_str_from_string(equations, constants=None):
    eqs_str = __process_eq_str(equations)

    if constants:
        cons_str = __c_process_const_str(constants)
        # print("void template_func(double _x_, double _y_[], double _f_[])" + " {" + f"{cons_str} {eqs_str}" + "}")
        return "void template_func(double _x_, double _y_[], double _f_[])" + " { " + f"{cons_str} {eqs_str}" + "}", "void template_func(double _x_, double _y_[], double _f_[]);"

    return "void template_func(double _x_, double _y_[], double _f_[])" + " { " + f"{eqs_str}" + "}", "void template_func(double _x_, double _y_[], double _f_[]);"

def __func_from_string(func_str):
    module_code = compile(func_str, '', 'exec')
    function_code = [c for c in module_code.co_consts if isinstance(c, types.CodeType)][0]
    func = types.FunctionType(function_code, globals())
    return func


def __process_const_str(co_ls):
    
    # post-process constant strings
    __sup_semicolon(co_ls)

    # join all constant strings
    return "".join(co_ls)

def __c_process_const_str(co_ls):
    
    # post-process constant strings
    __c_sup_semicolon(co_ls)

    # join all constant strings
    return "".join(co_ls)

def __process_eq_str(eq_ls):

    # split lhs and rhs
    __lhs_ls, __rhs_ls = __hs_ls(eq_ls)

    # parse lhs to get/replace derivative variable
    dep_dict, indep_dict = __lhs_parse(eq_ls, __lhs_ls)

    # replace derivative at rhs
    __rhs_replace(eq_ls, dep_dict, indep_dict, __rhs_ls)

    # post-process equation strings
    __sup_semicolon(eq_ls)

    # join all equation strings
    return "".join(eq_ls), dep_dict, indep_dict


def __lhs_parse(eq_ls, lhs_ls):
    dep_dict = dict()
    indep_dict = dict()
    # rhs_ls = []
    for i in range(len(eq_ls)):

        eq_ls[i] = eq_ls[i].replace(lhs_ls[i], "_f_[{}]".format(i))

        dep_pattern = re.compile("^d([\D]*\w*)/") # get "d<>/"
        indep_pattern = re.compile("/d([\D]*\w*)")
        dep_var = dep_pattern.findall(lhs_ls[i])[0]
        indep_var = indep_pattern.findall(lhs_ls[i])[0]
        if dep_var:
            dep_dict['_y_[{}]'.format(i)] = dep_var
        if indep_var:
            indep_dict[indep_var] = "_x_"

    # rhs_ls.append(rhs)
    return dep_dict, indep_dict

def __rhs_replace(eq_ls, dep_dict, indep_dict, rhs):

    for i in range(len(rhs)):
        for k, v in dep_dict.items():
            # print(k, v)
            p = re.compile(r'(^|[\W])({})([\W]|$)'.format(v)) # (A: start or anything not \w - digits, letters and _)(B: target)(C: end or anything not \w - digits, letters and _)
            eq_ls[i] = re.sub(p, r'\1{}\3'.format(k), eq_ls[i]) # refer and keep (A:...) and (C:...), relplace (B:...)
            # print(eq_ls[i])

        for k, v in indep_dict.items():
            p = re.compile(r'(^|[\W])({})([\W]|$)'.format(k))
            eq_ls[i] = re.sub(p, r'\1{}\3'.format(v), eq_ls[i])


def __hs(s):
    s = s.split("=")
    return s[0].strip(), s[1].strip()

def __hs_ls(s):
    __lhs_ls = []
    __rhs_ls = []
    for i in range(len(s)):
        __lhs, __rhs = __hs(s[i])
        __lhs_ls.append(__lhs)
        __rhs_ls.append(__rhs)
    return __lhs_ls, __rhs_ls


def __sup_semicolon(ls):
    for i in range(len(ls)):
        ls[i] = ls[i] + "; "

def __c_sup_semicolon(ls):
    for i in range(len(ls)):
        ls[i] = "double " + ls[i] + "; "

'''
def func_template(_x_, _y_, _f_):
    _f_[0] = _y_[1] + _x_
    _f_[1] = -100 * _y_[0] * _x_
    return _f_

'''


func_str = '''def func(a, b): a = a*3; b=b*5; return a + b'''

if __name__ == '__main__':

    cauchy1 = ['dx/dt = y', 'dy/dt = -x']
    cauchy2 = ['dy/dt = z + t', 'dz/dt = -100 * y * t']
    lorenz = ['dx/dt = sigma * (y - x)', 'dy/dt = rho * x - y - x * z', 'dz/dt = x * y - beta * z']
    lorenz_con = ['sigma = 10e0', 'rho = 28e0', 'beta = 8e0 / 3e0']


    # a = 'z - x * y - beta * z'
    # p = re.compile(r'(^|[^_])(z)([^_]|$)')
    # b = re.findall(p, a)
    # # a = p.sub(r'\1_y_[2]\3',a)
    # print(b)

    print(func_from_string(lorenz, lorenz_con))


