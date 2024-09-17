import numpy as np
from numpy.typing import NDArray

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ALICE import ALICE


def compute_xlims(
    depth1: NDArray[np.float64],
    depth2: NDArray[np.float64],
    anchor1: float,
    anchor2: float,
):
    # no metadata is specified

    # date1 = alice.cores[alice.profile_on_display]['time']
    # date2 = alice.cores['REF']['time']

    rangex1 = np.nanmax(depth1) - np.nanmin(depth1)
    rangex2 = np.nanmax(depth2) - np.nanmin(depth2)

    xlim1 = (np.nanmin(depth1) - rangex1 / 20, np.nanmax(depth1) + rangex1 / 20)
    xlim2 = (np.nanmin(depth2) - rangex2 / 20, np.nanmax(depth2) + rangex2 / 20)

    assert np.isfinite(xlim1[0])

    native_xlim1 = (
        float(anchor1 - max(anchor1 - xlim1[0], anchor2 - xlim2[0])),
        float(anchor1 + max(xlim1[1] - anchor1, xlim2[1] - anchor2)),
    )
    native_xlim2 = (
        float(anchor2 - max(anchor1 - xlim1[0], anchor2 - xlim2[0])),
        float(anchor2 + max(xlim1[1] - anchor1, xlim2[1] - anchor2)),
    )

    return native_xlim1, native_xlim2


def compute_anchors(alice: "ALICE"):
    offset_mode_str = alice.offset_mode_StringVar.get()

    depth1 = alice.cores[alice.profile_on_display][alice.species_on_display]["depth"]
    depth2 = alice.cores["REF"][alice.species_on_display]["depth"]

    ########################
    # to implement: different accumulation values for different sites and compute the expected
    # depth shift

    accu = (
        7.83  # mean accumulation rate based on era5 w.e. precip and density of 320kg/m3
    )

    # anchor lines will be at the same position visualy
    # anchor mode by depth: anchor1 = depth1[0] anchor2 = depth2[0]-depth1[0]
    # anchor mode by time shift: anchor1 = depth1, anchor2 = depth2+time_delta*accu
    # anchor mode manual: anchor1 = depth1[0], anchor2 = depth2[0]+manual shift

    if offset_mode_str == "time shift":
        # not in use, still need to implement in data structure

        anchor1 = depth1[0]

        date1 = alice.metadata[alice.profile_on_display]["date"]
        date2 = alice.metadata["REF"]["date"]

        time_delta = (date2 - date1).days / 365.25

        anchor2 = depth2[0] + time_delta * accu

    elif offset_mode_str == "common depth":
        anchor1 = depth1[0]
        anchor2 = depth1[0]

    elif offset_mode_str == "manual":
        anchor1 = depth1[0]
        anchor2 = depth2[0] + alice.manualoffsetvalue

    else:
        assert offset_mode_str == "match tops"
        anchor1 = depth1[0]
        anchor2 = depth2[0]

    return anchor1, anchor2


def update_base_xlims(alice: "ALICE"):
    depth1, _signal1, depth2, _signal2 = alice.get_linedata()

    # OFFSET

    # xlim will depend on the offset mode selected via anchors
    anchor1, anchor2 = alice.compute_anchors()

    # these are just graphical hints to ensure we have set the alignment right
    # between the two graphs
    # (shows the two values on the graph where they are supposed to be aligned)

    alice.vline1.set_xdata([anchor1])
    alice.vline2.set_xdata([anchor2])

    alice.base_xlim1, alice.base_xlim2 = compute_xlims(depth1, depth2, anchor1, anchor2)

    alice.ax3.set_xlim(float(np.nanmin(depth2)), float(np.nanmax(depth2)))


def update_base_ylims(alice: "ALICE"):
    # TO IMPLEMENT:
    # USE THE MAX OF THE CURRENT VIEW, NOT THE MAX OF THE ENTIRE PROFILE!!!

    # date1 = alice.cores[alice.profile_on_display]['time']
    # date2 = alice.cores['REF']['time']

    _depth1, signal1, _depth2, signal2 = alice.get_linedata()

    rangey1 = np.abs(np.nanmax(signal1) - np.nanmin(signal1))
    rangey2 = np.abs(np.nanmax(signal2) - np.nanmin(signal2))

    ylim1 = (
        float(np.nanmin(signal1) - rangey1 / 20),
        float(np.nanmax(signal1) + rangey1 / 20),
    )
    ylim2 = (
        float(np.nanmin(signal2) - rangey2 / 20),
        float(np.nanmax(signal2) + rangey2 / 20),
    )

    ylim = (
        float(np.nanmin(np.array([ylim1[0], ylim2[0]]))),
        float(np.nanmax(np.array([ylim1[1], ylim2[1]]))),
    )

    if np.isfinite(ylim[0]):
        if alice.minmaxscaling_BooleanVar.get() is True:
            alice.base_ylim1 = ylim1
            alice.base_ylim2 = ylim2
        else:
            alice.base_ylim1 = ylim
            alice.base_ylim2 = ylim

    alice.ax3.set_ylim(alice.base_ylim2)
