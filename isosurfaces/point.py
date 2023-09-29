# to support ValuedPoint type inside ValuedPoint
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

Point = np.ndarray
Func = Callable[[Point], float]


@dataclass
class ValuedPoint:
    """A position associated with the corresponding function value"""

    pos: Point
    val: float = None

    def calc(self, fn: Func) -> ValuedPoint:
        self.val = fn(self.pos)
        return self

    def __repr__(self) -> str:
        return f"({self.pos[0]},{self.pos[1]}; {self.val})"

    @classmethod
    def midpoint(cls, p1: ValuedPoint, p2: ValuedPoint, fn: Func) -> ValuedPoint:
        mid = (p1.pos + p2.pos) / 2
        return cls(mid, fn(mid))

    @classmethod
    def intersectZero(cls, p1: ValuedPoint, p2: ValuedPoint, fn: Func) -> ValuedPoint:
        """Find the point on line p1--p2 with value 0"""
        denom = p1.val - p2.val
        k1 = -p2.val / denom
        k2 = p1.val / denom
        pt = k1 * p1.pos + k2 * p2.pos
        return cls(pt, fn(pt))


def binary_search_zero(p1: ValuedPoint, p2: ValuedPoint, fn: Func, tol: np.ndarray) -> tuple[ValuedPoint, bool]:
    """Returns a pair `(point, is_zero: bool)`

    Use is_zero to make sure it's not an asymptote like at x=0 on f(x,y) = 1/(xy) - 1"""
    if np.all(np.abs(p2.pos - p1.pos) < tol):
        # Binary search stop condition: too small to matter
        pt = ValuedPoint.intersectZero(p1, p2, fn)
        is_zero: bool = pt.val == 0 or (
            np.sign(pt.val - p1.val) == np.sign(p2.val - pt.val)
            # Just want to prevent ≈inf from registering as a zero
            and np.abs(pt.val < 1e200)
        )
        return pt, is_zero
    else:
        # binary search
        mid = ValuedPoint.midpoint(p1, p2, fn)
        if mid.val == 0:
            return mid, True
        # (Group 0 with negatives)
        elif (mid.val > 0) == (p1.val > 0):
            return binary_search_zero(mid, p2, fn, tol)
        else:
            return binary_search_zero(p1, mid, fn, tol)
