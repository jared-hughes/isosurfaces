""" Code for demo-ing and experimentation. Prepare for a mess """
from isoline import Quad, plot_implicit, build_quad_tree, Triangulator, CurveTracer
import numpy as np
import cairo


def f(x, y):
    return y * (x - y) ** 2 - 4 * x - 8


# Typical usage
# curves = plot_implicit(
#     lambda u: f(u[0], u[1]),
#     np.array([-5, -5]),
#     np.array([5, 5]),
#     min_depth=5,
#     max_quads=1000,
# )

min_depth = 5
pmin = np.array([-8, -6])
pmax = np.array([8, 6])

# Here we directly use plot_implicit internals in order to see the quadtree
fn = lambda u: f(u[0], u[1])
quadtree = build_quad_tree(fn, pmin, pmax, min_depth, 5000)
triangles = Triangulator(quadtree, fn).triangulate()
curves = CurveTracer(triangles, fn).trace()

WIDTH = 640
HEIGHT = 480


def setup_context(c):
    # reflection to change math units to screen units
    scale = min(WIDTH / (pmax[0] - pmin[0]), HEIGHT / (pmax[1] - pmin[1]))
    c.scale(scale, -scale)
    c.translate(WIDTH / scale / 2, -HEIGHT / scale / 2)
    c.set_line_join(cairo.LINE_JOIN_BEVEL)


def draw_axes(c):
    c.save()
    c.set_line_width(0.1)
    c.move_to(0, -100)
    c.line_to(0, 100)
    c.stroke()
    c.move_to(-100, 0)
    c.line_to(100, 0)
    c.stroke()
    c.restore()


def draw_quad(c, quad: Quad):
    width = 0
    if quad.depth <= min_depth:
        width = 0.02
    elif quad.depth == min_depth + 1:
        width = 0.01
    else:
        width = 0.005
    c.set_line_width(0.5 * width)

    if quad.children:
        c.move_to(*((quad.vertices[0].pos + quad.vertices[1].pos) / 2))
        c.line_to(*((quad.vertices[2].pos + quad.vertices[3].pos) / 2))
        c.move_to(*((quad.vertices[0].pos + quad.vertices[2].pos) / 2))
        c.line_to(*((quad.vertices[1].pos + quad.vertices[3].pos) / 2))
        c.stroke()
        for child in quad.children:
            draw_quad(c, child)


def draw_quads(c):
    c.save()
    draw_quad(c, quadtree)
    c.restore()


def draw_bg(c):
    c.save()
    c.set_source_rgb(1, 1, 1)
    c.paint()
    c.restore()


def draw_curves(c):
    c.set_source_rgb(0.1, 0.1, 0.8)
    # draw curves
    c.save()
    c.set_line_width(0.03)
    for curve in curves:
        c.move_to(*curve[0])
        for v in curve:
            c.line_to(*v)
        c.stroke()
    c.restore()


with cairo.SVGSurface("out/demo.svg", WIDTH, HEIGHT) as surface:
    c = cairo.Context(surface)
    setup_context(c)
    draw_bg(c)
    draw_axes(c)
    draw_quads(c)
    draw_curves(c)
