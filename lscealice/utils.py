import numpy as np

from typing import Sequence, cast

from numpy.typing import NDArray
from matplotlib.axes import Axes

from .magic import combine, transform


def af_func(x: NDArray[np.float64], a0: float, a1: float, b0: float, b1: float):
    return b0 + (x - a0) * (a1 - a0) * (b1 - b0)


def depth_sqz_str(
    depth1: NDArray[np.float64], xp1: Sequence[float], xp2: Sequence[float]
):
    # Core function of the interpolation, future improvements to be made
    # JUNE2024: we still need to improve this function for coinciding xp1 points (hiatus)
    # for now, roughly the same as np.interp but no error if xp1 is empty

    if len(xp2) == 0:
        return cast(NDArray[np.float64], np.full(depth1.shape, np.nan))

    # sort points
    xp1, xp2 = zip(*sorted(zip(xp1, xp2)))
    return np.interp(depth1, xp1[: len(xp2)], xp2)


def map_to_ax(
    ax1: Axes, ax2: Axes, xp1: list[float], yp1: NDArray[np.float64]
) -> tuple[list[float], list[float]]:
    # map points with coordinate xp1,xp2 from ax0 to ax1

    combinedTransform = combine(ax2.transData, ax1.transData)
    combinedTransformInv = combinedTransform.inverted()
    t = transform(combinedTransformInv)

    xyp1 = list(map(t, zip(xp1, yp1)))
    xp1_on_ax2 = [bob[0] for bob in xyp1]
    yp1_on_ax2 = [bob[1] for bob in xyp1]

    return xp1_on_ax2, yp1_on_ax2


def compute_links(
    xp1: list[float],
    xp2: list[float],
    yp1: list[float],
    yp2: list[float],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    xp_links: NDArray[np.float64] = np.full(len(xp1) + 2 * len(xp2), np.nan)
    yp_links: NDArray[np.float64] = xp_links.copy()

    xp_links[::3] = xp1
    xp_links[1::3] = xp2

    yp_links[::3] = yp1
    yp_links[1::3] = yp2

    return xp_links, yp_links
