from typing import Callable

from matplotlib.transforms import Transform


def combine(t1: Transform, t2: Transform) -> Transform:
    return t1 + t2.inverted()


def transform(t: Transform) -> Callable[[tuple[float, float]], tuple[float, float]]:
    return t.transform  # type: ignore
