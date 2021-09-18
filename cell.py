# to support Cell type inside Cell
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import List
from point import Point, ValuedPoint, Func, TOL
from collections import deque


def vertices_from_extremes(dim: int, pmin: Point, pmax: Point, fn: Func):
    """Requires pmin.x ≤ pmax.x, pmin.y ≤ pmax.y"""
    w = pmax - pmin
    return [
        ValuedPoint(np.array([pmin[d] + (i >> d & 1) * w[d] for d in range(dim)])).calc(
            fn
        )
        for i in range(1 << dim)
    ]


@dataclass
class Cell:
    dim: int
    # In 2 dimensions, vertices = [bottom-left, bottom-right, top-left, top-right] points
    vertices: List[ValuedPoint]
    depth: int
    # Children go in same order: bottom-left, bottom-right, top-left, top-right
    children: List[Cell]

    def compute_children(self, fn: Func):
        assert self.children == []
        for vertex in self.vertices:
            pmin = (self.vertices[0].pos + vertex.pos) / 2
            pmax = (self.vertices[-1].pos + vertex.pos) / 2
            vertices = vertices_from_extremes(self.dim, pmin, pmax, fn)
            new_quad = Cell(self.dim, vertices, self.depth + 1, [])
            self.children.append(new_quad)


def should_descend_deep_cell(cell: Cell):
    if np.max(cell.vertices[-1].pos - cell.vertices[0].pos) < TOL:
        return False
    elif all(np.isnan(v.val) for v in cell.vertices):
        # in a region where the function is undefined
        return False
    elif any(np.isnan(v.val) for v in cell.vertices):
        # straddling defined and undefined
        return True
    else:
        # simple approach: only descend if we cross the isoline
        # TODO: This could very much be improved, e.g. by incorporating gradient or second-derivative
        # tests, etc., to cancel descending in approximately linear regions
        return any(
            np.sign(v.val) != np.sign(cell.vertices[0].val) for v in cell.vertices[1:]
        )


def build_tree(
    dim: int, fn: Func, pmin: Point, pmax: Point, min_depth: int, max_cells: int
) -> Cell:
    branching_factor = 1 << dim
    # min_depth takes precedence over max_quads
    max_cells = max(branching_factor ** min_depth, max_cells)
    vertices = vertices_from_extremes(dim, pmin, pmax, fn)
    current_quad = root = Cell(dim, vertices, 0, [])
    quad_queue = deque([root])
    leaf_count = 1

    while len(quad_queue) > 0 and leaf_count < max_cells:
        current_quad = quad_queue.popleft()
        if current_quad.depth < min_depth or should_descend_deep_cell(current_quad):
            current_quad.compute_children(fn)
            quad_queue.extend(current_quad.children)
            # add 4 for the new quads, subtract 1 for the old quad not being a leaf anymore
            leaf_count += branching_factor - 1
    return root
