import os
import sys

from typing import Iterable, cast, Optional, Any, Callable

from matplotlib.patches import Rectangle
from matplotlib.text import Annotation, Text
import numpy as np
from numpy.ma import masked_array
from numpy.typing import NDArray
import pandas as pd

from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backend_bases import (
    KeyEvent,
    MouseButton,
    LocationEvent,
    MouseEvent,
    Event,
)
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D

import tkinter
from tkinter.filedialog import askopenfilenames, asksaveasfilename, Open
from tkinter.simpledialog import askstring

from .dic import Dic, Tiepoint, initAlignmentFile, load_dic_file, write_dic_file
from .figures import CreateFigure_main,CreateFigure_preview, eventdist
from .draw.artist import _line,_vline,_scatter,_text,_annotate
from .magic import combine, transform
from .utils import compute_links, depth_sqz_str, map_to_ax,af_func
from .system import resolve_path
from .export import load_alig_array
from .dialogs import export_to_csv,saveStateAs,saveState
from .draw.limits import update_base_xlims,update_base_ylims
from .draw.artist import update_tag,update_scatter


class ALICE(tkinter.Frame):
    parent: tkinter.Tk
    filename: str
    ax: tuple[Axes, Axes, Axes]
    line1: Line2D
    line2: Line2D
    line3: Line2D
    line4: Line2D
    vline1: Line2D
    vline2: Line2D
    points1: PathCollection
    points2: PathCollection
    links: Line2D
    text_species: Text
    text_profile: Text
    rect: Rectangle
    pointshl: PathCollection
    tagsshow: Annotation
    xp1hl: PathCollection

    def __init__(self, parent: tkinter.Tk,*args,filename=None):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent

        parent.title("ALICE - alignment interface for ice cores")
        path = os.path.dirname(os.path.realpath(sys.argv[0]))
        icon_file = resolve_path('icon/lapin.png')
        parent.iconphoto(False, tkinter.PhotoImage(file=icon_file))

        self.initFigure()
        self.initAligVariables()
        self.initUI()

        if not filename is None:
            self.filename = filename
            self.StartApp()

    ##########################################################################
    ##########################################################################
    ##########################################################################
    # function to initalize the interface

    def initFigure(self):
        # This will create the fig and ax objects
        # and all of the artists (lines, scatter plots) present in the axes
        # and assign them to self. variables to be udpated later.

        self.fig, self.ax, self.axt, self.axc = CreateFigure_main()

        self.fig3, self.ax3, self.ax3c = CreateFigure_preview()

        self.CreateObjects()



    def canvas_draw(self):

        self.fig.canvas.draw_idle()  # type: ignore
        self.fig3.canvas.draw_idle()  # type: ignore


    def CreateObjects(self):
        # line 1 shows profile of profile_key in center plot
        self.line1 = _line(self.ax[0], "blue")

        # line 2 shows profile of ref_pit in center plot
        self.line2 = _line(self.ax[1], "red")

        # vline for anchors
        self.vline1 = _vline(self.ax[0], "blue")
        self.vline2 = _vline(self.ax[1], "red")

        #################################
        # Aligned profile at the bottom
        # new preview: using depth2 and the interpolated signal from depth_new
        # directly shows the shape of the signal after squeeze and stretch
        self.line3 = _line(self.ax3, "darkblue", lw=1.5)

        # line5 is the profile of ref_pit at the bottom
        self.line4 = _line(self.ax3, "orange", lw=1.5)

        ##################################################
        # initialize empty scatter plot to show selected points

        self.points1 = _scatter(self.axt, "blue")
        self.points2 = _scatter(self.axt, "red")

        self.links = _line(self.axt, "grey", lw=0.5, ls="--")

        ################################
        # text

        self.text_species = _text(self.ax[1], 0.80, 0.9, "species")
        self.text_profile = _text(self.ax[1], 0.05, 0.9, "profile_key")

        # not in use
        # self.text_date = self.ax[1].text(0.05, 0.8, 'sample_date', transform=self.ax[1].transAxes,fontsize=12,fontweight='heavy')

        self.rect = Rectangle(
            (np.nan, np.nan),
            np.nan,
            np.nan,
            linewidth=1,
            ls="--",
            edgecolor="gray",
            facecolor="none",
        )
        self.ax3c.add_patch(self.rect)

        # for points highlight when hovering
        self.pointshl = _scatter(self.axt, "k")

        #tried to use annotate before for tagsshow but 
        # a weird bug makes it disapear when zooming...
        # but text seems to go all over the place...
        self.tagsshow = _text(self.axt,0,0, "",fontsize=8)

        # for xp1 selection indication
        self.xp1hl = _scatter(self.ax[0], "gray")

    def initAligVariables(self):
        #xp1selection records the depth that was selected on the first profile
        #while we way for the selection on the second profile
        self.xp1selection = None

        #hl_ind keeps track of the index of the tiepoint highlighted by hovering
        #so it can be deleted by right clicking
        self.hl_ind = None

    def initUI(self):
        # crate all the buttons and dropdown menus to be greyed out
        # before an alignment file is opened

        ## CANVAS
        # after fig and axes have been created, we asign them to the canvas
        # to be injected in the tkinter interface

        self.canvas = FigureCanvasTkAgg(
            self.fig, master=self.parent
        )  # A tk.DrawingArea.

        self.canvas_preview = FigureCanvasTkAgg(
            self.fig3, master=self.parent
        )  # A tk.DrawingArea.

        self.canvas.get_tk_widget().config(height=400)
        self.canvas_preview.get_tk_widget().config(height=200)

        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.canvas_preview.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        ## TOOLBAR
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.toolbar.update()

        self.pack(fill=tkinter.BOTH, expand=True)  # does it need to pack itself?

        menubar = tkinter.Menu(self.parent)
        self.parent.config(menu=menubar)


        ##########################################
        #### FILE MENU

        self.fileMenu = tkinter.Menu(menubar, tearoff=False)

        self.fileMenu.add_command(label="Open alignment file", command=self.onOpenAlig)

        self.fileMenu.add_command(
            label="New alignment file from data file(s)", command=self.open_popup
        )

        self.fileMenu.add_command(
            label="Export aligned data to csv",
            #command=export_to_csv(self),
            command=lambda: export_to_csv(self.filename, self.species_on_display),
            state="disabled",
        )

        self.fileMenu.add_command(
            label="Save as", command=saveStateAs(self), state="disabled"
        )

        menubar.add_cascade(label="File", menu=self.fileMenu)

        ############################################
        #### TOOL MENU

        self.toolsMenu = tkinter.Menu(menubar,tearoff=False)
        self.toolsMenu.add_command(label="Add tiepoint manually",command=self.open_tiepoint_popup,
                state="disabled")
        menubar.add_cascade(label="Tools",menu=self.toolsMenu)

        ##################################################
        # DEFINE STRING VAR

        self.offset_mode_StringVar = tkinter.StringVar(self.parent)
        self.offset_mode_StringVar.set("offset mode")

        self.profile_on_display_StringVar = tkinter.StringVar(self.parent)
        self.profile_on_display_StringVar.set("profile on display")

        self.species_on_display_StringVar = tkinter.StringVar(self.parent)
        self.species_on_display_StringVar.set("species_on_display")

        self.minmaxscaling_BooleanVar = tkinter.BooleanVar(self.parent)
        self.minmaxscaling_BooleanVar.set(False)

        ######################################################
        # EMPTY LISTS TO INIT SPCIES AND PROFILE MENU(?)

        default_list = [""]
        default_offset = 0

        self.species_keys = default_list
        self.profile_keys = default_list
        self.manualoffsetvalue = default_offset

        ######################################################
        # DEFINE BUTTONS

        self.resetview_button = tkinter.Button(
            master=self.parent, text="Reset View", command=self.relim_xy
        )
        self.resetview_button.configure(state="disabled")
        self.resetview_button.pack(side=tkinter.LEFT)

        offset_modes_list = ["match tops", "time shift", "common depth", "manual"]

        # set all buttons disabled by default (until an alignment file is opened)

        self.offset_mode_menu = tkinter.OptionMenu(
            self.parent, self.offset_mode_StringVar, *offset_modes_list
        )
        self.offset_mode_menu.configure(state="disabled")
        self.offset_mode_menu.pack(side=tkinter.LEFT)

        # undo redo: laissé en chantier pour l'instant
        # self.undo_button = Tkinter.Button(text='Undo',command = self.undo)
        # self.undo_button.configure(state="disabled")
        # self.undo_button.pack(side=tkinter.LEFT)

        # self.redo_button = Tkinter.Button(text='Redo',command = self.undo)
        # self.redo_button.configure(state="disabled")
        # self.redo_button.pack(side=tkinter.LEFT)

        self.manual_offset_value_button = tkinter.Button(
            text=str(default_offset), command=self.manual_offset_input
        )
        self.manual_offset_value_button.configure(state="disabled")
        self.manual_offset_value_button.pack(side=tkinter.LEFT)

        self.species_menu = tkinter.OptionMenu(
            self.parent, self.species_on_display_StringVar, *default_list
        )
        # tested but not working; combobox to have a scrollbar
        # self.species_menu = ttk.Combobox(self.parent, textvariable = self.species_on_display_StringVar, values = default_list)

        self.species_menu.configure(state="disabled")
        self.species_menu.pack(side=tkinter.LEFT)

        self.profile_menu = tkinter.OptionMenu(
            self.parent, self.profile_on_display_StringVar, *default_list
        )
        # tested but not working; combobox to have a scrollbar
        # self.profile_menu = ttk.Combobox(self.parent, textvariable = self.profile_on_display_StringVar, values = default_list)

        self.profile_menu.configure(state="disabled")
        self.profile_menu.pack(side=tkinter.LEFT)

        self.quit_button = tkinter.Button(
            master=self.parent, text="Quit", command=self._quit
        )
        self.quit_button.pack(side=tkinter.RIGHT)

        # can I do x and y in a single callback?

        self.axc.callbacks.connect(  # type: ignore
            "ylim_changed", self.relim_callback
        )

        self.axc.callbacks.connect(  # type: ignore
            "xlim_changed", self.relim_callback
        )


    def hover_quit(self):
        self.hl_ind = None
        self.pointshl.set_visible(False)
        self.tagsshow.set_visible(False)
        self.canvas_draw()

    def hover(self, event: Event):
        assert isinstance(event, LocationEvent)
        # vis = self.pointshl.get_visible()

        # Maybe a nicer way to do this?
        # I just want to ignore clicks when zoom or pan is selected
        if not self.toolbar.mode.name == "NONE":
            self.hover_quit()
            return

        if event.inaxes == self.axc:

            # we wish to find the closest point in points1 and points2
            dist1 = eventdist(event, self.points1)
            dist2 = eventdist(event, self.points2)

            if dist1 is not None and dist2 is not None:

                dist1 = dist1[: len(dist2)]
                dists = np.stack((dist1, dist2))

                ind = cast(
                    tuple[NDArray[np.int64], NDArray[np.int64]],
                    np.unravel_index(
                        masked_array(dists, mask=np.isnan(dists)).argmin(),  # type: ignore
                        dists.shape,
                    ),
                )[1]


                # TODO july 10th: instead of closest distance, use points2.contains(event)
                # and with a ghost scatter plot for points1 (alpha = 0)
                if np.min(dists[:, ind]) < 0.001:

                    self.hl_ind = ind

                    offsets1 = self.points1.get_offsets()
                    xi1,yi1 = offsets1[ind]

                    offsets2 = self.points2.get_offsets()
                    xi2,yi2 = offsets2[ind]

                    update_scatter(self.pointshl,(xi1, xi2), (yi1, yi2))
                    self.pointshl.set_visible(True)

                    tagstr = str(self.tiepoints[self.profile_on_display][ind]["species"])

                    update_tag(self.tagsshow,xi2, yi2, tagstr)
                    #self.tagsshow = self.axc.annotate(tagstr,xy=(xi2,yi2))
                    self.tagsshow.set_visible(True)
                    self.canvas_draw()

                else:
                    self.hover_quit()

            else:
                self.hover_quit()

    def get_linedata(self):

        depth1 = self.cores[self.profile_on_display][self.species_on_display]["depth"]
        depth2 = self.cores["REF"][self.species_on_display]["depth"]

        signal1 = self.cores[self.profile_on_display][self.species_on_display]["data"]
        signal2 = self.cores["REF"][self.species_on_display]["data"]

        return depth1, signal1, depth2, signal2

    def get_tiepoints(self):
        # convert the tiepoints stored in the dictionary to the xp1 and xp2 lists

        xp1 = [bob["profile_depth"] for bob in self.tiepoints[self.profile_on_display]]
        xp2 = [bob["ref_depth"] for bob in self.tiepoints[self.profile_on_display]]

        return xp1, xp2

    def createTiepoint(self,profile,profile_depth,ref_depth,species):
        new_tiepoint = Tiepoint(
            profile_depth=profile_depth,
            ref_depth=ref_depth,
            species=species,
        )

        self.tiepoints[profile].append(new_tiepoint)

    def on_pick(self, event: Event):
        assert isinstance(event, MouseEvent)

        vis = self.pointshl.get_visible()

        # change names later?
        ax1 = self.ax[0]
        ax2 = self.ax[1]

        axc = self.axc

        # Maybe a nicer way to do this?
        # I just want to ignore clicks when zoom or pan is selected
        if not self.toolbar.mode.name == "NONE":
            return

        # pick is collected by axc which is on top of ax1,ax2 and axt
        # we use combinedtransform to get the corresponding point
        # on ax1 based on the event coordinates

        # event has x and y in data coordinates for ax2:
        assert event.xdata is not None
        assert event.ydata is not None
        pt_data = (event.xdata, event.ydata)

        # extracting axes limits
        # 1) to compute the distance in normalized units
        # 2) to use for relim using bottom plot

        xlim1 = ax1.get_xlim()
        ylim1 = ax1.get_ylim()
        xlim2 = ax2.get_xlim()
        ylim2 = ax2.get_ylim()

        xrange1 = xlim1[1] - xlim1[0]
        yrange1 = ylim1[1] - ylim1[0]
        xrange2 = xlim2[1] - xlim2[0]
        yrange2 = ylim2[1] - ylim2[0]



        if event.inaxes is axc:

            combinedTransform1 = combine(axc.transData, ax1.transData)
            combinedTransform2 = combine(axc.transData, ax2.transData)


            # Convert them into data coordinates for ax1:
            pt_data1 = transform(combinedTransform1)(pt_data)
            pt_data2 = transform(combinedTransform2)(pt_data)

            # Left click: add point
            if event.button is MouseButton.LEFT:
                if self.xp1selection is None:
                    dist_to_line_1 = eventdist(event, self.line1)
                    assert dist_to_line_1 is not None
                    # depth1 = self.line1.get_xdata()

                    depth1, signal1 = zip(*self.line1.get_xydata())
                    ind = np.nanargmin(dist_to_line_1)
                    # xp1.append(depth1[ind])
                    # temporarily store value in a class variable
                    xi1 = depth1[ind]
                    self.xp1selection = xi1
                    yi1 = signal1[ind]

                    # show where the point was clicked
                    self.xp1hl.set_offsets(np.c_[xi1, yi1])
                    self.xp1hl.set_visible(True)

                else:
                    dist_to_line_2 = eventdist(event, self.line2)
                    assert dist_to_line_2 is not None

                    depth2 = cast(NDArray[np.float64], self.line2.get_xdata())
                    ind = int(np.nanargmin(dist_to_line_2))

                    self.createTiepoint(
                            self.profile_on_display,
                            self.xp1selection,
                            depth2[ind],
                            self.species_on_display)

                    # switch back to non selection mode
                    self.xp1hl.set_visible(False)
                    self.xp1selection = None

            # Right click: delete point
            if event.button is MouseButton.RIGHT:
                # a right click when marked points are all paired will remove the closest marked point
                if self.xp1selection is None:
                    #if len(self.tiepoints[self.profile_on_display]) > 0 and not self.hl_ind is None:
                    if not self.hl_ind is None:

                        # warning: here we rely on the fact that indices are the same
                        # for the scatter artist points1 xy data
                        # and for xp1,xp2 (a priori no reason that is it scrambled in points?...)
                        # we get the index of closest distance iwth points1 xy data
                        # and we use the same index to delete points in self.tiepoints
                        # watch out for bugs!

                        del self.tiepoints[self.profile_on_display][self.hl_ind]

                        self.hover_quit()

                    # a right click after selecting the first point simply removes the first point
                else:
                    self.xp1selection = None
                    self.xp1hl.set_visible(False)

        # self.tiepoints_history.append(self.tiepoints)
        # self.undo_redo_callback()

        self.updateTiepoints()

        self.canvas_draw()

        saveState(self)()

    def on_pick3(self,event: Event):


        # Maybe a nicer way to do this?
        # I just want to ignore clicks when zoom or pan is selected
        if not self.toolbar.mode.name == "NONE":
            return

        # event has x and y in data coordinates for ax2:
        assert event.xdata is not None
        assert event.ydata is not None

        pt_data = (event.xdata, event.ydata)

        xlim = self.axc.get_xlim()
        ylim = self.axc.get_ylim()

        xrange = xlim[1] - xlim[0]
        yrange = ylim[1] - ylim[0]

        if event.inaxes is self.ax3c:

            # center the view on the point clicked in the bottom plot
            self.axc.set_xlim(pt_data[0] - xrange / 2, pt_data[0] + xrange / 2)
            self.axc.set_ylim(pt_data[1] - yrange / 2, pt_data[1] + yrange / 2)

            # relim callbacks will take care of updating ax1 and ax2
            # and update rectangle view
            self.relim_callback(self.axc)
        
        self.updateTiepoints()
        self.canvas_draw()


    def on_press(self, event: Event):
        assert isinstance(event, KeyEvent)
        current_profile = self.profile_on_display
        current_species = self.species_on_display

        species_keys_available = [
            species
            for species in self.species_keys
            if species in self.cores[self.profile_on_display].keys()
        ]

        profile_keys_available = [
            profile
            for profile in self.profile_keys
            if self.species_on_display in self.cores[profile].keys()
        ]

        if event.key == "+":
            current_state = self.minmaxscaling_BooleanVar.get()
            self.minmaxscaling_BooleanVar.set(not (current_state))

        # we want to define special key bindings for species often used
        if event.key == "w":
            if "MSA" in species_keys_available:
                self.species_on_display_StringVar.set("MSA")

        if event.key == "s":
            # two different ways to write sulfate
            if "Sulfate" in species_keys_available:
                self.species_on_display_StringVar.set("Sulfate")
            elif "SO4" in species_keys_available:
                self.species_on_display_StringVar.set("SO4")

        if event.key == "up" or event.key == "down":
            n = species_keys_available.index(current_species)
            if event.key == "down" and n < len(species_keys_available) - 1:
                species = species_keys_available[n + 1]
                self.species_on_display_StringVar.set(species)

            if event.key == "up" and n > 0:
                species = species_keys_available[n - 1]
                self.species_on_display_StringVar.set(species)

        # change profile_key

        if event.key == "right" or event.key == "left":
            n = profile_keys_available.index(current_profile)
            if event.key == "right" and n < len(profile_keys_available) - 1:
                profile_key = profile_keys_available[n + 1]
                self.profile_on_display_StringVar.set(profile_key)

            if event.key == "left" and n > 0:
                profile_key = profile_keys_available[n - 1]
                self.profile_on_display_StringVar.set(profile_key)

        # callbacks will take care of updating all plots

    def offset_callback(self, *_: Any):
        # callback that catches any change to the offsetmode dropdown menu
        # and call to redraws the graph

        if self.offset_mode_StringVar.get() != "manual":
            self.manual_offset_value_button.config(state="disabled")
        else:
            self.manual_offset_value_button.config(state="normal")

        # self.updateUI()

        # update 100% view xlims
        update_base_xlims(self)
        
        self.relim_x()


    def relim_callback(self, axc: Axes):

        # callback function that catches any change to the axc limits
        # to pass it onto ax1 and ax2 and
        # to draw the rectangle of current view
        # in the bottom preview

        xlim = axc.get_xlim()
        ylim = axc.get_ylim()

        xlim = np.array(xlim)
        ylim = np.array(ylim)
        
        # first version: we have set the base limits of axc and axt to be (0,1)
        xlim1 = af_func(xlim,
                0,
                1,
                self.base_xlim1[0],
                self.base_xlim1[1])
        ylim1 = af_func(ylim,
                0,
                1,
                self.base_ylim1[0],
                self.base_ylim1[1])

        xlim2 = af_func(xlim,
                0,
                1,
                self.base_xlim2[0],
                self.base_xlim2[1])
        ylim2 = af_func(ylim,
                0,
                1,
                self.base_ylim2[0],
                self.base_ylim2[1])


        self.axt.set_xlim(xlim)
        self.axt.set_ylim(ylim)

        self.ax[0].set_xlim(xlim1)
        self.ax[0].set_ylim(ylim1)

        self.ax[1].set_xlim(xlim2)
        self.ax[1].set_ylim(ylim2)

        xrange = xlim[1] - xlim[0]
        yrange = ylim[1] - ylim[0]

        self.rect.set_xy((xlim[0], ylim[0]))
        self.rect.set_width(xrange)
        self.rect.set_height(yrange)

        self.updateTiepoints()
        self.canvas_draw()

    def updateUI(self):
        # function called upon change of species and change of profile
        # to gray out options in the drop down menu depending on what data are available.

        # only enable available species in species menu.
        menu = self.species_menu["menu"]
        nentries = menu.index("end")
        for index in range(nentries + 1):
            species = menu.entrycget(index, "label")
            if species in self.cores[self.profile_on_display].keys():
                menu.entryconfigure(species, state="normal")
            else:
                menu.entryconfigure(species, state="disabled")

        # only enable available profile in profile menu.
        menu = self.profile_menu["menu"]
        nentries = menu.index("end")
        for index in range(nentries + 1):
            profile = menu.entrycget(index, "label")
            if self.species_on_display in self.cores[profile].keys():
                menu.entryconfigure(profile, state="normal")
            else:
                menu.entryconfigure(profile, state="disabled")

        menu = self.offset_mode_menu["menu"]
        # check that both profiles have a date available
        if (
            self.profile_on_display in self.metadata.keys()
            and "date" in self.metadata[self.profile_on_display].keys()
        ) and ("REF" in self.metadata.keys() and "date" in self.metadata["REF"].keys()):
            menu.entryconfigure("time shift", state="normal")
        else:
            menu.entryconfigure("time shift", state="disabled")

    def Var_callback(self, *_: Any):

        self.profile_on_display = str(self.profile_on_display_StringVar.get())

        self.species_on_display = str(self.species_on_display_StringVar.get())

        self.updateUI()

        self.updateLines()

        # behaviour to discuss: do we keep the focus in the x direction
        # (for instance when switching between species at fixed profile)
        # at the moment, yes.

        # self.relim_x()

        self.relim_y()

        self.updateTiepoints()


        self.canvas_draw()

    def manual_offset_input(self):
        inputvalue = askstring(title="test", prompt="Enter manual offset value")
        assert inputvalue is not None

        self.manual_offset_value_button.configure(text=inputvalue)
        self.manualoffsetvalue = float(inputvalue)

        #changing offset mode will change the anchors and thus the relative
        #x limits of ax1 and ax2
        update_base_xlims(self)

        self.relim_x()

    def _quit(self):
        print("goodbye")
        self.parent.quit()  # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent

    ########################3
    ## NEXT: what happens when we open a file

    def loadData(self):
        # run only once at the opening of the file

        new_dic = load_dic_file(self.filename)

        # load tiepoints and cores data in separate dictionaries
        self.tiepoints = new_dic["tiepoints"]
        self.cores = new_dic["cores"]
        self.metadata = new_dic["metadata"]

        # NEW save previous state of tiepoints for restore
        # en chantier
        # self.tiepoints_history = []
        # self.tiepoints_history_position = 0
        # self.tiepoints_history.append(self.tiepoints.copy())

        # we also define lists of core and species name for the interface to navigate into
        self.profile_keys = [bob for bob in list(self.cores.keys()) if bob != "REF"]

        # only need consider species which are available on the reference profile
        self.species_keys = list(self.cores["REF"].keys())

        # VARIABLES USED BY THE INTERFACE TO MANAGE DISPLAY

        # initialize with a random profile and species, or something else..
        self.profile_on_display = self.profile_keys[0]

        if "SO4" in self.species_keys:
            # SO4 is a popular species used for alignment
            self.species_on_display = "SO4"
        elif "Sulfate" in self.species_keys:
            self.species_on_display = "Sulfate"
        else:
            self.species_on_display = self.species_keys[0]

        # initialize offset_mode
        self.offset_mode = "match tops"

    def updateLines(self):
        # function to asign x and y data to the lines ploted
        # should be called only upon change of species or change of profile to display

        depth1, signal1, depth2, signal2 = self.get_linedata()

        # Function to call when switching species or profile;
        # update lines data and redraw plot

        # triggered upon changing profile only

        # UPDATE DATA

        self.line1.set_xdata(depth1)
        self.line1.set_ydata(signal1)

        self.line2.set_xdata(depth2)
        self.line2.set_ydata(signal2)

        self.line4.set_xdata(depth2)  # redundent
        self.line4.set_ydata(signal2)

        # update 100% view xlims
        update_base_xlims(self)
        update_base_ylims(self)

        # self.text_date.set_text(date1.date())

        self.text_profile.set_text(self.profile_on_display)

        self.text_species.set_text(self.species_on_display)

    def compute_anchors(self):
        offset_mode_str = self.offset_mode_StringVar.get()

        depth1 = self.cores[self.profile_on_display][self.species_on_display]["depth"]
        depth2 = self.cores["REF"][self.species_on_display]["depth"]

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

            date1 = self.metadata[self.profile_on_display]["date"]
            date2 = self.metadata["REF"]["date"]

            time_delta = (date2 - date1).days / 365.25

            anchor2 = depth2[0] + time_delta * accu

        elif offset_mode_str == "common depth":
            anchor1 = depth1[0]
            anchor2 = depth1[0]

        elif offset_mode_str == "manual":
            anchor1 = depth1[0]
            anchor2 = depth2[0] + self.manualoffsetvalue

        else:
            assert offset_mode_str == "match tops"
            anchor1 = depth1[0]
            anchor2 = depth2[0]

        return  anchor1, anchor2

    def updateTiepoints(self):

        # A function to be called each time we manipulate tiepoints:
        # redraws the preview in the bottom graph
        # redraws the tiepoints and
        # redraws the links

        # defining shortnames for readability

        depth1, signal1, depth2, signal2 = self.get_linedata()

        # read tiepoints data from dictionaries
        xp1, xp2 = self.get_tiepoints()

        yp1 = np.interp(xp1, depth1, signal1)
        yp2 = np.interp(xp2, depth2, signal2)

        xp1t,yp1t = map_to_ax(self.ax[0],self.axt,xp1,yp1)
        xp2t,yp2t = map_to_ax(self.ax[1],self.axt,xp2,yp2)


        # update tiepoints


        self.points1.set_offsets(np.c_[xp1t, yp1t])
        self.points2.set_offsets(np.c_[xp2t, yp2t])
        # self.links.set_data(xp_links,yp_links)

        xp_links, yp_links = compute_links(xp1t, xp2t, yp1t, yp2t)
        self.links.set_data(xp_links, yp_links)

        # update preview

        depth_new = depth_sqz_str(depth1, xp1, xp2)

        signal_new = np.interp(depth2, depth_new, signal1, left=np.nan, right=np.nan)

        self.line3.set_xdata(depth2)  # redundent
        self.line3.set_ydata(signal_new)

        # Set highlight

        if self.xp1selection is None:
            self.line1.set_linewidth(3)
            self.line2.set_linewidth(1.5)

        else:
            self.line1.set_linewidth(1.5)
            self.line2.set_linewidth(3)

    def relim_xy(self):

        # weird behaviour; if we only call relim_x, the relim_callback function
        # will not be called

        self.relim_x()
        self.relim_y()

    def relim_x(self):
        # we only need to relim axc and relim_callback takes care of the other axes
        self.axc.set_xlim(0,1)

    def relim_y(self):
        self.axc.set_ylim(0,1)


    ## FILE DIALOG WINDOW

    def init_option_menu(self):
        # code from the internet
        # we will need to update the option menus upon loading a new file
        menu = self.profile_menu["menu"]
        menu.delete(0, "end")
        for string in self.profile_keys:
            menu.add_command(
                label=string,
                command=lambda value=string: self.profile_on_display_StringVar.set(
                    value
                ),
            )

        menu = self.species_menu["menu"]
        menu.delete(0, "end")
        for string in self.species_keys:
            menu.add_command(
                label=string,
                command=lambda value=string: self.species_on_display_StringVar.set(
                    value
                ),
            )

    def enableUI(self):
        default_offset_mode = "match tops"

        self.resetview_button.configure(state="normal")
        self.offset_mode_menu.configure(state="normal")
        self.offset_mode_StringVar.set(default_offset_mode)

        self.species_menu.configure(state="normal")
        self.species_on_display_StringVar.set(str(self.species_on_display))
        self.profile_menu.configure(state="normal")
        self.profile_on_display_StringVar.set(str(self.profile_on_display))

        self.init_option_menu()

        # only now attribute callbacks
        self.offset_mode_StringVar.trace_add("write", self.offset_callback)
        self.profile_on_display_StringVar.trace_add("write", self.Var_callback)
        self.species_on_display_StringVar.trace_add("write", self.Var_callback)
        self.minmaxscaling_BooleanVar.trace_add("write", self.Var_callback)

        # and attribute mpl connections
        # select tie points
        self.fig.canvas.mpl_connect("button_press_event", self.on_pick)

        self.fig3.canvas.mpl_connect("button_press_event", self.on_pick3)

        # switch between species and profiles with up/down and left/right arrows
        self.fig.canvas.mpl_connect("key_press_event", self.on_press)

        # highlight marked points when hovering
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        self.fileMenu.entryconfig("Save as", state="normal")
        self.fileMenu.entryconfig("Export aligned data to csv", state="normal")
        

        # and enable the tool menu
        self.toolsMenu.entryconfig("Add tiepoint manually", state="normal")

        # test
        # fig.canvas.mpl_connect("motion_notify_event", hover)

    def onOpenAlig(self):
        ftypes = [("Pickle files", "*.pkl"), ("All files", "*")]
        dlg = Open(self, filetypes=ftypes)
        fl: str = dlg.show()  # type: ignore

        # not really sure how things work here
        # closing window without making a selection
        # seem to result in () or '' sometimes...
        if fl:
            self.filename = fl

            self.StartApp()

    def StartApp(self):
        self.loadData()

        self.enableUI()
        self.updateUI()

        self.updateLines()
        self.relim_xy()
        #self.updateTiepoints()

        #self.canvas_draw()

    ################################################################
    ################################################################
    # Code below is to define the pop up window that allows the user to 
    # create a new tiepoint via the Tools menu

    def open_tiepoint_popup(self):

        self.top2 = tkinter.Toplevel(self)

        top = self.top2

        top.geometry("250x150")
        top.title("Insert new tiepoint manually")

        tkinter.Label(top, text="profile depth: ").pack(side=tkinter.TOP)

        top.profile_depth_sv = tkinter.StringVar()
        e = tkinter.Entry(top, width=6, textvariable=top.profile_depth_sv)
        e.pack(side=tkinter.TOP)


        tkinter.Label(top, text="reference depth: ").pack(side=tkinter.TOP)

        top.ref_depth_sv = tkinter.StringVar()
        top.maxdepth = tkinter.Entry(top, width=6, textvariable = top.ref_depth_sv)
        top.maxdepth.pack(side=tkinter.TOP)

        def callback(*args):
            try:
                float(top.ref_depth_sv.get())+float(top.profile_depth_sv.get())
                top.create_tiepointButton.configure(state="normal")
            except:
                top.create_tiepointButton.configure(state="disabled")

        top.ref_depth_sv.trace_add("write",callback)
        top.profile_depth_sv.trace_add("write",callback)

        def add_tiepoint(*args):

            self.createTiepoint(
                self.profile_on_display,
                float(top.profile_depth_sv.get()),
                float(top.ref_depth_sv.get()),
                'Manual')

            self.updateTiepoints()

            self.canvas_draw()

            saveState(self)()

            self.top2.destroy()

        top.create_tiepointButton = tkinter.Button(
            master=top, text="Create tiepoint", command=add_tiepoint
        )
        top.create_tiepointButton.configure(state="disabled")
        top.create_tiepointButton.pack(side=tkinter.BOTTOM)


    ################################################################
    ################################################################
    # Code below is to define the pop up window that allows the user to initialize
    # a new alignment file from raw data.

    def open_popup(self):
        ### NEED TO BE REWRITTEN
        # we dont need all the popup window variables as class variables...

        self.top = tkinter.Toplevel(self)

        top = self.top

        top.geometry("500x250")
        top.title("Create alignment from data files")

        self.opendataButton = tkinter.Button(
            master=top, text="Select data files", command=self.onOpenData
        )
        self.opendataButton.pack(side=tkinter.TOP)

        self.selected_datafiles = ()  # initialize with empty tuple

        self.selected_datafiles_Label = tkinter.Label(
            top, text="", font=("Mistral 10 bold")
        )
        self.selected_datafiles_Label.pack(side=tkinter.TOP)

        self.opendataButton = tkinter.Button(
            master=top, text="Select metadata files", command=self.onOpenMeta
        )
        self.opendataButton.pack(side=tkinter.TOP)

        self.selected_metadatafiles = ()  # initialize with empty tuple

        self.selected_metadatafiles_Label = tkinter.Label(
            top, text="", font=("Mistral 10 bold")
        )
        self.selected_metadatafiles_Label.pack(side=tkinter.TOP)

        self.reference_selected_StringVar = tkinter.StringVar(self.parent)
        self.reference_selected_StringVar.set("select ref")
        self.reference_selected_StringVar.trace_add(
            "write", self.reference_selected_StringVar_callback
        )

        default_list = [""]

        self.reference_menu = tkinter.OptionMenu(
            top, self.reference_selected_StringVar, *default_list
        )
        self.reference_menu.configure(state="disabled")
        self.reference_menu.pack(side=tkinter.TOP)

        tkinter.Label(top, text="min depth: ").pack(side=tkinter.LEFT)
        self.mindepth = tkinter.Entry(top, width=6, state="disabled")
        # self.mindepth.insert(0, "-infty")
        self.mindepth.pack(side=tkinter.LEFT)

        tkinter.Label(top, text="max depth: ").pack(side=tkinter.LEFT)
        self.maxdepth = tkinter.Entry(top, width=6, state="disabled")
        # self.maxdepth.insert(0, "+infty")
        self.maxdepth.pack(side=tkinter.LEFT)

        self.create_alignmentButton = tkinter.Button(
            master=top, text="Generate new file", command=self.createAlignmentFile
        )
        self.create_alignmentButton.configure(state="disabled")
        self.create_alignmentButton.pack(side=tkinter.BOTTOM)

    def createAlignmentFile(self):
        # collect all the parameters
        datafiles = self.selected_datafiles
        metadatafiles = self.selected_metadatafiles
        ref_lab = self.reference_selected_StringVar.get()
        min_depth = self.mindepth.get()
        max_depth = self.maxdepth.get()

        # We will have to make this work for datetimes too
        if min_depth == "":
            min_depth = -np.infty
        else:
            min_depth = int(min_depth)
            
        if max_depth == "":
            max_depth = np.infty
        else:
            max_depth = int(max_depth)


        # create the dictionary
        # this is a mess, rewrite later to only use one dictionary state
        new_dic = initAlignmentFile(
            datafiles, metadatafiles, ref_lab, min_depth, max_depth
        )

        # save the new state to a new file
        self.tiepoints = new_dic["tiepoints"]
        self.cores = new_dic["cores"]
        self.metadata = new_dic["metadata"]

        saveStateAs(self)()

        if hasattr(self, "filename"):
            self.StartApp()
            self.top.destroy()

    def reference_selected_StringVar_callback(self, *_: Any):
        if not self.reference_selected_StringVar.get() == "select ref":
            self.create_alignmentButton.configure(state="normal")

    def onOpenMeta(self):
        workdir = os.getcwd()

        ftypes = [("Excel files", "*.xlsx"), ("All files", "*")]
        filez = askopenfilenames(initialdir=workdir, filetypes=ftypes)
        self.selected_metadatafiles = filez

        # now just a couple lines to display them nicely without the full path
        filez_for_label = [file.removeprefix(workdir) for file in filez]
        string_for_label = " ".join([file + " \n " for file in filez_for_label])
        self.selected_metadatafiles_Label.configure(text=string_for_label)

    def onOpenData(self):
        workdir = os.getcwd()

        ftypes = [("Excel files", "*.xlsx"), ("All files", "*")]
        filez = cast(
            Iterable[str], askopenfilenames(initialdir=workdir, filetypes=ftypes)
        )
        self.selected_datafiles = filez

        # now just a couple lines to display them nicely without the full path
        filez_for_label = [file.removeprefix(workdir) for file in filez]
        string_for_label = " ".join([file + " \n " for file in filez_for_label])
        self.selected_datafiles_Label.configure(text=string_for_label)

        temp: list[str] = []

        for datafile in filez:
            xls = pd.ExcelFile(datafile)
            core_names = xls.sheet_names[:]
            temp.extend(map(str, core_names))

        references_available = set(temp)

        self.reference_menu.configure(state="normal")
        self.maxdepth.configure(state="normal")
        self.mindepth.configure(state="normal")
        # not here
        # self.create_alignmentButton.configure(state="normal")

        menu = self.reference_menu["menu"]
        menu.delete(0, "end")
        for string in references_available:
            menu.add_command(
                label=string,
                command=lambda value=string: self.reference_selected_StringVar.set(
                    value
                ),
            )
