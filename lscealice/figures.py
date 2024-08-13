from typing import Union, cast, Optional
#from typing import Iterable, cast, Optional, Any, Callable

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.backend_bases import LocationEvent
from numpy.typing import NDArray
import numpy as np

from .plt import plt
from .magic import combine, transform

def _line(ax, color: str, lw: float = 1, ls: Optional[str] = None):
    plot = ax.plot([], [], color=color, lw=lw, ls=ls)  # type: ignore
    return plot[0]

def _vline(ax, color: str):
    return ax.axvline(np.nan, lw=0.5, color=color)  # type: ignore

def _scatter(ax, color: str):
    return ax.scatter([], [], color=color, s=50)  # type: ignore

def _text(ax, x: float, y: float, s: str):
    return ax.text(  # type: ignore
        x,
        y,
        s,
        transform=ax.transAxes,
        fontsize=12,
        fontweight="heavy",
    )

def _annotate(ax, text: str):
    return ax.annotate(  # type: ignore
        text, xy=(0, 0), xytext=(0, 0)
    )

def CreateFigure_main():
    subplots = plt.subplots  # type: ignore

    fig, ax1 = cast(
        tuple[Figure, tuple[Axes, Axes]],
        subplots(1),
    )

    ax1.tick_params(axis="x", colors="blue")  # type: ignore
    ax1.tick_params(axis="y", colors="blue")  # type: ignore


    ax2 = fig.add_subplot(111)  # type: ignore
    ax2.patch.set_alpha(0.0)

    ax2.xaxis.tick_top()
    ax2.yaxis.tick_right()

    ax2.tick_params(axis="x", colors="red")  # type: ignore
    ax2.tick_params(axis="y", colors="red")  # type: ignore

    ax2.xaxis.set_label_position("top")
    ax2.yaxis.set_label_position("right")

    # an axt Axes in abstract (0,1) coordinates to plot tiepoints and links
    axt = fig.add_subplot(111)

    axt.set_xlim(0,1)
    axt.set_ylim(0,1)
    # hide the axes completely, and only see the artists in axt
    axt.set_axis_off()

    # an axc Axes to receive click events
    axc = fig.add_subplot(111)
    axc.set_xlim(0,1)
    axc.set_ylim(0,1)
    #axc.set_axis_off()
    axc.patch.set_alpha(0) #make it completely transparent so we can see ax1 and ax2 underneath.
    axc.tick_params(axis="y",direction="in", pad=-22)
    axc.tick_params(axis="x",direction="in", pad=-15)


    #fig.tight_layout()

    ax = (ax1, ax2)

    ###################
    # This is just so that the plot doesn't show in Jupyter Notebook cell
    # when running tkinter window from jupyter
    plt.close()

    return fig, ax, axt, axc

def CreateFigure_preview():

    fig,ax = plt.subplots()
    # an axc Axes to receive click events

    axc = fig.add_subplot(111)
    axc.set_xlim(0,1)
    axc.set_ylim(0,1)
    axc.set_axis_off()
    #axc.patch.set_alpha(0)
    plt.close()

    return fig,ax,axc


Artist = Union[PathCollection, Line2D]


def eventdist(event: LocationEvent, artist: Artist):
    if isinstance(artist, PathCollection):
        xydata = artist.get_offsets()

    else:
        assert isinstance(artist, Line2D)
        xydata = artist.get_xydata()

    zipped = tuple(zip(*xydata))

    if not zipped:
        return None

    depth1: NDArray[np.float64] = zipped[0]
    signal1: NDArray[np.float64] = zipped[1]

    event_ax = event.inaxes
    assert event_ax is not None

    artist_ax = artist.axes
    assert artist_ax is not None

    assert event.xdata is not None
    assert event.ydata is not None
    pt_data0 = (event.xdata, event.ydata)

    combinedTransform = combine(event_ax.transData, artist_ax.transData)
    pt_data1 = transform(combinedTransform)(pt_data0)

    xlim1 = artist_ax.get_xlim()
    ylim1 = artist_ax.get_ylim()
    # xlim2 = ax2.get_xlim()
    # ylim2 = ax2.get_ylim()

    xrange1 = xlim1[1] - xlim1[0]
    yrange1 = ylim1[1] - ylim1[0]
    # xrange2 = xlim2[1]-xlim2[0]
    # yrange2 = ylim2[1]-ylim2[0]

    dist_to_artist = ((depth1 - pt_data1[0]) / xrange1) ** 2 + (
        (signal1 - pt_data1[1]) / yrange1
    ) ** 2

    # event has x and y in data coordinates for ax2:

    # Convert them into data coordinates for ax1:

    return dist_to_artist
