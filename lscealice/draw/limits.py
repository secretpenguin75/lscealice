import numpy as np

def compute_xlims(depth1,depth2,anchor1,anchor2):

    # dates as still used in the get_anchor functions
    # can use this again in the future but we want to add if statements in case
    # no metadata is specified

    # date1 = ALICE.cores[ALICE.profile_on_display]['time']
    # date2 = ALICE.cores['REF']['time']


    rangex1 = np.nanmax(depth1) - np.nanmin(depth1)
    rangex2 = np.nanmax(depth2) - np.nanmin(depth2)

    xlim1 = (np.nanmin(depth1) - rangex1 / 20, np.nanmax(depth1) + rangex1 / 20)
    xlim2 = (np.nanmin(depth2) - rangex2 / 20, np.nanmax(depth2) + rangex2 / 20)


    if np.isfinite(xlim1[0]):
        native_xlim1 = (
            anchor1 - max(anchor1 - xlim1[0], anchor2 - xlim2[0]),
            anchor1 + max(xlim1[1] - anchor1, xlim2[1] - anchor2),
        )
        native_xlim2 = (
            anchor2 - max(anchor1 - xlim1[0], anchor2 - xlim2[0]),
            anchor2 + max(xlim1[1] - anchor1, xlim2[1] - anchor2),
        )

    return native_xlim1,native_xlim2

def compute_anchors(ALICE):
        offset_mode_str = ALICE.offset_mode_StringVar.get()

        depth1 = ALICE.cores[ALICE.profile_on_display][ALICE.species_on_display]["depth"]
        depth2 = ALICE.cores["REF"][ALICE.species_on_display]["depth"]

        ########################
        # to implement: different accumulation values for different sites and compute the expected
        # depth shift

        accu = 7.83  # mean accumulation rate based on era5 w.e. precip and density of 320kg/m3

        # anchor lines will be at the same position visualy
        # anchor mode by depth: anchor1 = depth1[0] anchor2 = depth2[0]-depth1[0]
        # anchor mode by time shift: anchor1 = depth1, anchor2 = depth2+time_delta*accu
        # anchor mode manual: anchor1 = depth1[0], anchor2 = depth2[0]+manual shift

        if offset_mode_str == "time shift":
            # not in use, still need to implement in data structure

            anchor1 = depth1[0]

            date1 = ALICE.metadata[ALICE.profile_on_display]["date"]
            date2 = ALICE.metadata["REF"]["date"]

            time_delta = (date2 - date1).days / 365.25

            anchor2 = depth2[0] + time_delta * accu

        elif offset_mode_str == "common depth":
            anchor1 = depth1[0]
            anchor2 = depth1[0]

        elif offset_mode_str == "manual":
            anchor1 = depth1[0]
            anchor2 = depth2[0] + ALICE.manualoffsetvalue

        else:
            assert offset_mode_str == "match tops"
            anchor1 = depth1[0]
            anchor2 = depth2[0]

        return  anchor1, anchor2


def update_base_xlims(ALICE):

    depth1, _signal1, depth2, _signal2 = ALICE.get_linedata()


    # OFFSET

    #xlim will depend on the offset mode selected via anchors
    anchor1, anchor2 = ALICE.compute_anchors()

    # these are just graphical hints to ensure we have set the alignment right
    # between the two graphs
    # (shows the two values on the graph where they are supposed to be aligned)

    ALICE.vline1.set_xdata([anchor1])
    ALICE.vline2.set_xdata([anchor2])

    ALICE.base_xlim1,ALICE.base_xlim2 = compute_xlims(depth1,depth2,anchor1,anchor2)

    ALICE.ax3.set_xlim(np.nanmin(depth2),np.nanmax(depth2))

def update_base_ylims(ALICE):

    # TO IMPLEMENT:
    # USE THE MAX OF THE CURRENT VIEW, NOT THE MAX OF THE ENTIRE PROFILE!!!

    # date1 = ALICE.cores[ALICE.profile_on_display]['time']
    # date2 = ALICE.cores['REF']['time']

    _depth1, signal1, _depth2, signal2 = ALICE.get_linedata()

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
        if ALICE.minmaxscaling_BooleanVar.get() is True:
            ALICE.base_ylim1 = ylim1
            ALICE.base_ylim2 = ylim2
        else:
            ALICE.base_ylim1 = ylim
            ALICE.base_ylim2 = ylim

    ALICE.ax3.set_ylim(ALICE.base_ylim2)
