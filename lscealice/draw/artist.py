from typing import Optional

from matplotlib.collections import PathCollection
from matplotlib.text import Text
import numpy as np

from matplotlib.axes import Axes


def line(ax: Axes, color: str, lw: float = 1, ls: Optional[str] = None):
    plot = ax.plot([], [], color=color, lw=lw, ls=ls)  # type: ignore
    return plot[0]


def vline(ax: Axes, color: str):
    return ax.axvline(np.nan, lw=0.5, color=color)  # type: ignore


def scatter(ax: Axes, color: str):
    return ax.scatter([], [], color=color, s=50)  # type: ignore


def text(
    ax: Axes, x: float, y: float, s: str, fontsize: int = 12, fontweight: str = "normal"
):
    return ax.text(  # type: ignore
        x,
        y,
        s,
        transform=ax.transAxes,
        fontsize=fontsize,
        fontweight=fontweight,
    )


def annotate(ax: Axes, text: str):
    return ax.annotate(  # type: ignore
        text, xy=(0, 0), xytext=(0, 0)
    )


def update_scatter(
    scatter: PathCollection, xs: tuple[float, float], ys: tuple[float, float]
):
    scatter.set_offsets(np.c_[xs, ys])


def update_tag(tag: Text, x: float, y: float, tagstr: str):
    tag.set_text(tagstr)
    tag.set_x(x)
    tag.set_y(y)
