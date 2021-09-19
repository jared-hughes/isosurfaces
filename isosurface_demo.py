from isosurface import plot_isosurface
import numpy as np
from manim import *


metaball_pts = [np.array([0, 1.6, 0]), np.array([0, -1.6, 0])]


def fn(p):
    # metaballs
    # return sum(1 / np.linalg.norm(p - q) for q in metaball_pts) - 1
    # cone with singularity at origin
    return (p[0] - 0.5) ** 2 + p[1] ** 2 - p[2] ** 2


pmin = np.array([-4, -4, -4])
pmax = np.array([4, 4, 4])
simplices, faces = plot_isosurface(fn, pmin, pmax, 2, 64)
faces = list(faces)

# manim -pql isosurface_demo.py --renderer=opengl --enable_gui --fullscreen
class DemoScene(ThreeDScene):
    def construct(self):
        self.add(ThreeDAxes())
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)

        print(len(faces))
        surface = VGroup()
        for face_points in faces:
            face = ThreeDVMobject()
            face.set_points_as_corners([*face_points, face_points[0]])
            surface.add(face)
        surface.set_fill(color=BLUE_D, opacity=1)
        surface.set_stroke(opacity=0)
        self.add(*surface)

        # sgroup = VGroup()
        # for s in simplices[:16]:
        #     [a, b, c, d] = map(lambda p: p.pos, s)
        #     sgroup.add(
        #         Line(a, b), Line(b, c), Line(c, d), Line(d, a), Line(a, c), Line(b, d)
        #     )
        # self.add(sgroup)

        self.wait(20)
