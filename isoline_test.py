from isoline import plot_implicit
import numpy as np


def f(x, y):
    return y ** 2 - x ** 3 + x - 0.3


curves = plot_implicit(
    lambda u: f(u[0], u[1]),
    np.array([-2, -2]),
    np.array([2, 2]),
    min_depth=5,
    max_quads=1000,
)

for curve in curves:
    print([tuple(v) for v in curve])
