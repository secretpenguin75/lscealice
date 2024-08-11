from typing import Union, cast

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.backend_bases import LocationEvent
from numpy.typing import NDArray
import numpy as np

from .plt import plt
from .magic import combine, transform


def CreateFigure():
    subplots = plt.subplots  # type: ignore
    fig, (ax1, ax3) = cast(
        tuple[Figure, tuple[Axes, Axes]],
        subplots(2, gridspec_kw={"height_ratios": [3, 2]}),
    )

    # ax2 = ax1.twinx()

    ax2 = fig.add_subplot(211)  # type: ignore
    ax2.patch.set_alpha(0.5)

    ax2.xaxis.tick_top()
    ax2.yaxis.tick_right()
    # ax2.set_xlabel('x label 2', color='red')
    # ax2.set_ylabel('y label 2', color='red')
    ax2.tick_params(axis="x", colors="red")  # type: ignore
    ax2.tick_params(axis="y", colors="red")  # type: ignore
    # ax2.set_yticks([])
    ax2.xaxis.set_label_position("top")
    ax2.yaxis.set_label_position("right")

    # ax1.set_xlabel("x label 1", color='blue')
    # ax1.set_ylabel("y label 1", color='blue')
    ax1.tick_params(axis="x", colors="blue")  # type: ignore
    ax1.tick_params(axis="y", colors="blue")  # type: ignore

    fig.tight_layout()
    fig.subplots_adjust(wspace=0, hspace=0.2)

    ax = (ax1, ax2, ax3)

    ###################
    # This is just so that the plot doesn't show in Jupyter Notebook cell
    # when running tkinter window from jupyter
    plt.close()

    return fig, ax


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
