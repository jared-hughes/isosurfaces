import numpy as np
from manim import *

from isosurfaces import plot_isosurface

metaball_pts = [np.array([0, 1.6, 0]), np.array([0, -1.6, 0])]


def fn(p):
    # metaballs
    # return sum(1 / np.linalg.norm(p - q) for q in metaball_pts) - 1
    # cone with singularity at origin
    return p[0] ** 2 + p[1] ** 2 - p[2] ** 2


pmin = np.array([-4, -4, -4])
pmax = np.array([4, 4, 4])
simplices, faces = plot_isosurface(fn, pmin, pmax, 2, 64)
faces = list(faces)


class Isosurface(Surface):
    def __init__(self, faces, **kwargs):
        # Need the right resolution to trick the surface into rendering all of the faces
        # Each face is a triangle (list of three points)
        num_points = len(faces) * 3
        super().__init__(uv_func=None, resolution=(num_points, 1), **kwargs)
        s_points = [p for face in faces for p in face]
        # du_points and dv_points are used to compute vertex normals
        du_points = [p for face in faces for p in face[1:] + face[:1]]
        dv_points = [p for face in faces for p in face[2:] + face[:2]]
        # The three lists have equal length and are stored consecutively
        self.set_points(s_points + du_points + dv_points)


# manim -pql isosurface_demo.py --renderer=opengl --enable_gui --fullscreen
class DemoScene(ThreeDScene):
    def construct(self):
        self.add(ThreeDAxes())
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)

        self.add(Isosurface(faces))

        # sgroup = VGroup()
        # for s in simplices[:16]:
        #     [a, b, c, d] = map(lambda p: p.pos, s)
        #     sgroup.add(
        #         Line(a, b), Line(b, c), Line(c, d), Line(d, a), Line(a, c), Line(b, d)
        #     )
        # self.add(sgroup)

        self.wait(20)
