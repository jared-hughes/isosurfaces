from __future__ import annotations
from typing import Generator, List, Union
import numpy as np
from .point import Point, ValuedPoint, Func, binary_search_zero
from .cell import (
    Cell,
    MinimalCell,
    build_tree,
)


def plot_isosurface(
    fn: Func,
    pmin: Point,
    pmax: Point,
    min_depth: int = 5,
    max_cells: int = 10000,
    tol: Union[np.ndarray, None] = None,
):
    """Returns the surface representing fn([x,y,z])=0 on
    pmin[0] ≤ x ≤ pmax[0] ∩ pmin[1] ≤ y ≤ pmax[1] ∩ pmin[2] ≤ z ≤ pmax[2]"""
    pmin = np.asarray(pmin)
    pmax = np.asarray(pmax)
    if tol is None:
        tol = (pmax - pmin) / 1000
    else:
        tol = np.asarray(tol)
    octtree = build_tree(3, fn, pmin, pmax, min_depth, max_cells, tol)
    simplices = list(SimplexGenerator(octtree, fn).get_simplices())
    faces = []
    for simplex in simplices:
        face = march_simplex(simplex, fn, tol)
        if face is not None:
            faces.append(face)
    return simplices, faces


TETRAHEDRON_TABLE = {
    0b0000: [],  # falsey
    0b0001: [(0, 3), (1, 3), (2, 3)],
    0b0010: [(0, 2), (1, 2), (3, 2)],
    0b0100: [(0, 1), (2, 1), (3, 1)],
    0b1000: [(1, 0), (2, 0), (3, 0)],
    0b0011: [(0, 2), (2, 1), (1, 3), (3, 0)],
    0b0110: [(0, 1), (1, 3), (3, 2), (2, 0)],
    0b0101: [(0, 1), (1, 2), (2, 3), (3, 0)],
}


def march_indices(simplex: List[ValuedPoint]):
    """Assumes the simplex is a tetrahedron, so this is marching tetrahedrons"""
    id = 0
    for p in simplex:
        # (Group 0 with negatives)
        id = 2 * id + (p.val > 0)
    if id in TETRAHEDRON_TABLE:
        return TETRAHEDRON_TABLE[id]
    else:
        return TETRAHEDRON_TABLE[0b1111 ^ id]


def march_simplex(simplex: List[ValuedPoint], fn: Func, tol: np.ndarray):
    indices = march_indices(simplex)
    if indices:
        points = []
        for i, j in indices:
            intersection, is_zero = binary_search_zero(simplex[i], simplex[j], fn, tol)
            assert is_zero
            points.append(intersection.pos)
        return points


class SimplexGenerator:
    def __init__(self, root: Cell, fn: Func):
        self.root = root
        self.fn = fn

    def get_simplices(self):
        return self.get_simplices_within(self.root)

    def get_simplices_within(self, oct: Cell):
        if oct.children:
            for child in oct.children:
                yield from self.get_simplices_within(child)
        else:
            for axis in [0, 1, 2]:
                for dir in [0, 1]:
                    adj = oct.walk_leaves_in_direction(axis, dir)
                    for leaf in adj:
                        if leaf is None:
                            # e.g. this is the rightmost cell with direction to the right
                            yield from self.get_simplices_between_face(
                                oct, oct.get_subcell(axis, dir)
                            )
                        else:
                            yield from self.get_simplices_between(oct, leaf, axis, dir)

    def get_simplices_between(
        self, a: Cell, b: Cell, axis: int, dir: int
    ) -> Generator[List[ValuedPoint]]:
        """
        Parameters axis and dir are same as Cell.get_leaves_in_direction.
        They denote the direction a→b
        """
        if a.depth > b.depth:
            [a, b] = [b, a]
            dir = 1 - dir
        # Now b is the same depth or deeper (smaller) than a
        face = b.get_subcell(axis, 1 - dir)
        for volume in [a, b]:
            yield from self.get_simplices_between_face(volume, face)

    def get_simplices_between_face(self, volume: Cell, face: MinimalCell):
        # Each simplex comes from:
        #   1 volume dual
        #   1 face dual
        #   1 edge dual (of an edge of their shared face)
        #   1 vertex dual (of a vertex of that edge)
        for i in range(4):
            edge = face.get_subcell(i % 2, i // 2)
            for v in edge.vertices:
                yield [
                    volume.get_dual(self.fn),
                    face.get_dual(self.fn),
                    edge.get_dual(self.fn),
                    v,
                ]
