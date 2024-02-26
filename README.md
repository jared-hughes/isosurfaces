# Isosurfaces

Construct isolines/isosurfaces of a 2D/3D scalar field defined by a function, i.e. curves over which `f(x,y)=0` or surfaces over which `f(x,y,z)=0`. Most similar libraries use marching squares or similar over a uniform grid, but this uses a quadtree to avoid wasting time sampling many far from the implicit surface.

This library is based on the approach described in [Manson, Josiah, and Scott Schaefer. "Isosurfaces over simplicial partitions of multiresolution grids." Computer Graphics Forum. Vol. 29. No. 2. Oxford, UK: Blackwell Publishing Ltd, 2010](https://people.engr.tamu.edu/schaefer/research/iso_simplicial.pdf).

An example graph, including quad lines, of `y(x-y)^2 = 4x+8` (Python expression: `y*(x-y)**2 - 4*x - 8`)

<!-- Note: `src="assets/demo.svg"` is automatically replaced with a jsdelivr link for PyPI -->
<img src="assets/demo.svg" alt="Demo with grid lines" height=300>

## Installation

```sh
pip3 install isosurfaces
```

## Usage

```py
from isosurfaces import plot_isoline
import numpy as np

def f(x, y):
    return y * (x - y) ** 2 - 4 * x - 8

curves = plot_isoline(
    lambda u: f(u[0], u[1]),
    np.array([-8, -6]),
    np.array([8, 6]),
    # Increasing min_depth can help if you have small features
    min_depth=3,
    # Ensure max_quads is more than 4**min_depth to capture details better
    # than a 2**min_depth by 2**min_depth uniform grid
    max_quads=1000,
)

for curve in curves:
    print(', '.join(f"({p[0]:.3f},{p[1]:.3f})" for p in curve))
```

## Dev examples

```sh
python3 isoline_demo.py && xdg-open out/demo.svg
manim -pql isosurface_demo.py --renderer=opengl --enable_gui
```

Pyflakes, allowing manim star imports

```sh
python3 -m pyflakes . | grep -v "star imports: manim"
```

Build source archive and wheel:

```sh
rm -rf dist build isosurfaces.egg-info
python3 setup.py sdist bdist_wheel
twine check dist/*
# for test:
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# for actual
twine upload dist/*
```

## Code formatting

`isosurfaces` uses [`black`](https://github.com/psf/black) and [`isort`](https://github.com/PyCQA/isort). A Github Action will run to make sure it was applied.

## Related

Related projects:

- (2D, grid-based) https://pypi.org/project/meander/
- (2D, grid-based) https://pypi.org/project/contours/
- (Archived) https://github.com/AaronWatters/contourist

Other terms for an isoline:

- Contour
- Level curve
- Topographic map
