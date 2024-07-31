#!/usr/bin/env python
# coding: utf-8

# In[24]:


## standard packages
import os

import tkinter
from tkinter import ttk

import datetime

import pickle


## additional packages

#pandas
import pandas as pd

#numpy
import numpy as np

#matplotlib
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.backend_bases import MouseButton


# In[3]:


#%run ./load_code.ipynb


# # PRELIMINARY CODE

# ## basic file handling

# In[4]:


def load_dic_file(filename):
    
    with open(filename, 'rb') as fp:
        dic = pickle.load(fp)
        
    return dic

def write_dic_file(dic,filename):
    
    with open(filename, 'wb') as fp:
        pickle.dump(dic, fp) 


# ## utilities

# In[5]:


def common_depth_scale(depthdictionary,dz):
    
    dz = 3
    zmin = min([min(value) for key,value in depthdictionary.items()])
    zmax = max([max(value) for key,value in depthdictionary.items()])
    depth_scale = np.arange(zmin,zmax,dz)
    
    return depth_scale


# In[6]:


def depth_sqz_str(depth1,xp1,xp2):
    # Core function of the interpolation, future improvements to be made
    # JUNE2024: we still need to improve this function for coinciding xp1 points (hiatus)
    # for now, roughly the same as np.interp but no error if xp1 is empty
    
    
    depth_out = np.full(depth1.shape,np.nan)
    if len(xp2)>0:
        # sort points
        xp1,xp2 = zip(*sorted(zip(xp1,xp2)))
        depth_out = np.interp(depth1,xp1[:len(xp2)],xp2)
    return depth_out


# In[7]:


def get_links(ax,xp1,xp2,yp1,yp2):
    
    combinedTransform = ax[1].transData + ax[0].transData.inverted()

    
    xyp1 = [combinedTransform.inverted().transform(bob) for bob in zip(xp1,yp1)]
    xp1_on_ax2 = [bob[0] for bob in xyp1]
    yp1_on_ax2 = [bob[1] for bob in xyp1]
        
    xp_links = np.full(len(xp1)+2*len(xp2),np.nan)
    yp_links = xp_links.copy()
    
    xp_links[::3] = xp1_on_ax2.copy()
    xp_links[1::3] = xp2.copy()
    
    yp_links[::3] = yp1_on_ax2.copy()
    yp_links[1::3] = yp2.copy()

    return xp_links,yp_links


# In[ ]:





# # loading data

# In[8]:


def load_marked_points(aligfile):
        # convert the tiepoints stored in the dictionary to the xp1 and xp2 lists
        
        new_dic = load_dic_file(aligfile)
        
        xp1_dic = {}
        xp2_dic = {}
        
        for profile_key in new_dic['tiepoints'].keys():
        
            tiepoints = new_dic['tiepoints'][profile_key]
            xp1 = [bob['profile_depth'] for bob in tiepoints]
            xp2 = [bob['ref_depth'] for bob in tiepoints]
        
            if len(xp2)>0:
                # sort points
                xp1,xp2 = zip(*sorted(zip(xp1,xp2)))

            xp1_dic[profile_key] = xp1
            xp2_dic[profile_key] = xp2
        
        return xp1_dic,xp2_dic


# In[9]:


def load_profiles_data(aligfile):
    
    full_dic = load_dic_file(aligfile)
    
    cores_dic = {key:value for key,value in full_dic['cores'].items() if key !='REF'}
    ref_dic = full_dic['cores']['REF']
    
    return ref_dic,cores_dic


# In[ ]:





# # export to csv

# In[10]:


def load_alig_array(aligfile,species,vertical_scale= None,labels = None):
    
    # create an array with 
    
    ref_dic,cores_dic = load_profiles_data(aligfile)
    
    xp1_dic,xp2_dic = load_marked_points(aligfile)

    
    if vertical_scale is None:
        vertical_scale = ref_dic[species]['depth'].copy()
             
    if labels is None: 
        labels = cores_dic.keys()
        
    npits = len(labels)
    
    #data = chem_profiles[species]
    
    out = {}
        
    for profile in labels:
        if species in cores_dic[profile] and profile in xp1_dic.keys():
            
            depth_new = depth_sqz_str(cores_dic[profile][species]['depth'],xp1_dic[profile],xp2_dic[profile])
    
            signal_new = np.interp(vertical_scale,depth_new,cores_dic[profile][species]['data']
                                   ,left=np.nan,right=np.nan)
    
            out[profile] = signal_new.copy()
    
        else:
            print('missing data or tiepoints for ',profile)
            out[profile] = np.full(len(vertical_scale),np.nan)
            

    df = pd.DataFrame(data=out)
    df.index = vertical_scale.copy()
    
    return df


# ### UI preliminaries:
# ### some utilities functions that can be defined outside of the tkinter frame class

# In[12]:


def CreateFigure():

    fig, (ax1,ax3) = plt.subplots(2,gridspec_kw={'height_ratios': [3,2]})

    #ax2 = ax1.twinx()

    ax2 = fig.add_subplot(211)
    ax2.patch.set_alpha(0.5)

    ax2.xaxis.tick_top()
    ax2.yaxis.tick_right()
    #ax2.set_xlabel('x label 2', color='red') 
    #ax2.set_ylabel('y label 2', color='red')
    ax2.tick_params(axis='x', colors='red')
    ax2.tick_params(axis='y', colors='red')
    #ax2.set_yticks([])
    ax2.xaxis.set_label_position('top') 
    ax2.yaxis.set_label_position('right') 

    #ax1.set_xlabel("x label 1", color='blue')
    #ax1.set_ylabel("y label 1", color='blue')
    ax1.tick_params(axis='x', colors='blue')
    ax1.tick_params(axis='y', colors='blue')
    
            
    fig.tight_layout()
    fig.subplots_adjust(wspace=0, hspace=.2)

    ax = (ax1,ax2,ax3)
    
    ###################
    # This is just so that the plot doesn't show in Jupyter Notebook cell
    # when running tkinter window from jupyter
    plt.close()
    
    return fig,ax


# In[ ]:





# In[20]:


def eventdist(event,artist):
    
    if type(artist) == matplotlib.collections.PathCollection:
        offsets = artist.get_offsets()
        if len(offsets):
            depth1,signal1 = zip(*offsets)
        else:
            return
        
    if type(artist) == matplotlib.lines.Line2D:
        xydata = artist.get_xydata()
        if len(xydata)>0:
            depth1,signal1 = zip(*xydata)
        else:
            return
        
        
    event_ax = event.inaxes
    artist_ax = artist.axes
    
    pt_data0 = [event.xdata, event.ydata]
    
    combinedTransform = event_ax.transData + artist_ax.transData.inverted()
    
    pt_data1 = combinedTransform.transform(pt_data0)


    
    
    xlim1 = artist_ax.get_xlim()
    ylim1 = artist_ax.get_ylim()
    #xlim2 = ax2.get_xlim()
    #ylim2 = ax2.get_ylim()
        
    xrange1 = xlim1[1]-xlim1[0]
    yrange1 = ylim1[1]-ylim1[0]
    #xrange2 = xlim2[1]-xlim2[0]
    #yrange2 = ylim2[1]-ylim2[0]
    
    dist_to_artist = ((depth1-pt_data1[0])/xrange1)**2+((signal1-pt_data1[1])/yrange1)**2
    
    # event has x and y in data coordinates for ax2:

    # Convert them into data coordinates for ax1:

    return dist_to_artist


# In[21]:


def initAlignmentFile(datafiles,metadatafiles,ref_lab,min_depth,max_depth):
    
    new_dic = {'cores':{},'metadata':{},'tiepoints':{}}
    
    for datafile in datafiles:
        xls = pd.ExcelFile(datafile)
        core_names = xls.sheet_names[:]
        for i,lab in enumerate(core_names):
            df = pd.read_excel(datafile,sheet_name=i,skiprows = 0, header = None).replace('n.a.', np.nan)
        
            ## todo later: adjust the code for then sample_date is not defined
            #sample_date = datetime.date(2000,1,1) # just a random date for now
        
            core_depth = df.to_numpy()[1:,0].astype(None)
        
            if not lab in new_dic['tiepoints'].keys():
                #initialize tiepoints with empty lists
                new_dic['tiepoints'][lab] = []
            
            if not lab in new_dic['cores'].keys():
                new_dic['cores'][lab] = {}      
        
            for i in range(1,len(df.T)):
                chem_name = df.to_numpy()[0,i]
                chem_profile = df.to_numpy()[1:,i].astype(None)
            
                # for Agnese in july 2024: restrict to the first 18 meters
                ind = np.logical_and(core_depth>min_depth,core_depth<max_depth)
            
                new_dic['cores'][lab][chem_name] = {}
                new_dic['cores'][lab][chem_name]['data'] = chem_profile[ind].copy()
                new_dic['cores'][lab][chem_name]['depth'] = core_depth[ind].copy()
                
    for datafile in metadatafiles:
        
        xls = pd.ExcelFile(datafile)
        core_names = xls.sheet_names[:]
        for i,lab in enumerate(core_names):
            df = pd.read_excel(datafile,sheet_name=i,skiprows = 0, header = None).replace('n.a.', np.nan)
            if not lab in new_dic['metadata'].keys():
                #initialize tiepoints with empty lists
                new_dic['metadata'][lab] = {}
            for i in range(0,len(df.T)):
                #metadata_name = df.to_numpy()[0,i]
                metadata_name = df.iloc[0,i]

                #metadata_value = df.to_numpy()[1,i]
                metadata_value = df.iloc[1,i]

                new_dic['metadata'][lab][metadata_name] = metadata_value
                
    new_dic['cores']['REF'] = new_dic['cores'][ref_lab].copy()
    
    if ref_lab in new_dic['metadata'].keys():
        new_dic['metadata']['REF'] = new_dic['metadata'][ref_lab].copy()
                
    return new_dic


# In[22]:


# remove matplotlib keybord shortcuts to use our owns
if 'f' in plt.rcParams['keymap.fullscreen']: plt.rcParams['keymap.fullscreen'].remove('f')
if 'r' in plt.rcParams['keymap.home']: plt.rcParams['keymap.home'].remove('r')
if 's' in plt.rcParams['keymap.save']: plt.rcParams['keymap.save'].remove('s')
if 'c' in plt.rcParams['keymap.back']: plt.rcParams['keymap.back'].remove('c')
if 'g' in plt.rcParams['keymap.grid']: plt.rcParams['keymap.grid'].remove('g')
#if 'o' in plt.rcParams['keymap.zoom']: plt.rcParams['keymap.zoom'].remove('o')
if 'q' in plt.rcParams['keymap.quit']: plt.rcParams['keymap.quit'].remove('q')
#if 'p' in plt.rcParams['keymap.pan']: plt.rcParams['keymap.pan'].remove('p')
if 'left' in plt.rcParams['keymap.back']: plt.rcParams['keymap.back'].remove('left')
if 'right' in plt.rcParams['keymap.forward']:plt.rcParams['keymap.forward'].remove('right')


# # TKINTER APP

# In[ ]:





# In[23]:


class ALICE(tkinter.Frame):
   

    def __init__(self, parent):
        
        tkinter.Frame.__init__(self, parent)   

        self.parent = parent  
        
        self.initFigure()
        
        self.initAligVariables()
        
        self.initUI()
        
     
    ##########################################################################
    ##########################################################################
    ##########################################################################
    # function to initalize the interface
        
    def initFigure(self):
        
        # This will create the fig and ax objects
        # and all of the artists (lines, scatter plots) present in the axes
        # and assign them to self. variables to be udpated later.
        
        self.fig,self.ax = CreateFigure()

        self.CreateObjects()

        # after fig and axes have been created, we asign them to the canvas
        # to be injected in the tkinter interface
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    
        
    def CreateObjects(self):

        # line 1 shows profile of profile_key in center plot
        self.line1, = self.ax[0].plot([],[],color='blue')

        # line 2 shows profile of ref_pit in center plot
        self.line2, = self.ax[1].plot([],[],color='red')

        # vline for anchors
        self.vline1 = self.ax[0].axvline(np.nan,lw=.5,color='blue');
        self.vline2 = self.ax[1].axvline(np.nan,lw=.5,color='red')


        #################################
        # Aligned profile at the bottom
        # new preview: using depth2 and the interpolated signal from depth_new
        # directly shows the shape of the signal after squeeze and stretch
        self.line3, = self.ax[2].plot([],[],color='darkblue',linewidth = 1.5)

        #line5 is the profile of ref_pit at the bottom
        self.line4, = self.ax[2].plot([],[],color='orange',linewidth = 1.5)
    
        ##################################################
        # initialize empty scatter plot to show selected points

        self.points1 = self.ax[0].scatter([],[],color='blue',s=50)
        self.points2 = self.ax[1].scatter([],[],color='red',s=50)

        self.links, = self.ax[1].plot([],[],color='grey',lw=.5,ls='--')
    
        ################################
        # text
    
        self.text_species = self.ax[1].text(0.80, 0.9, 'species', transform=self.ax[1].transAxes,fontsize=12,fontweight='heavy')
        self.text_profile = self.ax[1].text(0.05, 0.9, 'profile_key', transform=self.ax[1].transAxes,fontsize=12,fontweight='heavy')
        
        #not in use
        #self.text_date = self.ax[1].text(0.05, 0.8, 'sample_date', transform=self.ax[1].transAxes,fontsize=12,fontweight='heavy')
    
        self.rect = plt.Rectangle((np.nan, np.nan), np.nan, np.nan, linewidth=1,ls='--', edgecolor='gray', facecolor='none')
        self.ax[2].add_patch(self.rect)
        
        #for points highlight when hovering
        self.pointshl = self.ax[1].scatter([],[],s=50,color='k')
        self.tagsshow = self.ax[1].annotate("",xy = (0,0),xytext=(0,0))
        
        #for xp1 selection indication
        self.xp1hl = self.ax[0].scatter([],[],s=50,color='gray')

        
    def initAligVariables(self):
        
        self.xp1selection = None
        
        
    def initUI(self):
        
        # crate all the buttons and dropdown menus to be greyed out
        # before an alignment file is opened
        
        ## TOOLBAR
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        self.toolbar.update()
        
        self.pack(fill=tkinter.BOTH, expand=1) # does it need to pack itself?

        menubar = tkinter.Menu(self.parent)
        self.parent.config(menu=menubar)

        self.fileMenu = tkinter.Menu(menubar, tearoff = 'off')
        
        self.fileMenu.add_command(label="Open alignemnt file", command=self.onOpenAlig)
        
        self.fileMenu.add_command(label="New alignment file from data file(s)", command=self.open_popup)
        
        self.fileMenu.add_command(label="Export aligned data to csv",command = self.export_to_csv,state="disabled")

        self.fileMenu.add_command(label= "Save as", command= self.saveStateas, state="disabled")
        
        menubar.add_cascade(label="File", menu=self.fileMenu)
        
        
        
        
        ##################################################
        # DEFINE STRING VAR
        
        self.offset_mode_StringVar = tkinter.StringVar(self.parent)
        self.offset_mode_StringVar.set('offset mode')
    
        self.profile_on_display_StringVar = tkinter.StringVar(self.parent)
        self.profile_on_display_StringVar.set('profile on display') 

        self.species_on_display_StringVar = tkinter.StringVar(self.parent)
        self.species_on_display_StringVar.set('species_on_display')
        
        self.minmaxscaling_BooleanVar = tkinter.BooleanVar(self.parent)
        self.minmaxscaling_BooleanVar.set(False)
        
        ######################################################
        #EMPTY LISTS TO INIT SPCIES AND PROFILE MENU(?)
        
        default_list = ['']
        default_offset = 0
        
        self.species_keys = default_list
        self.profile_keys = default_list
        self.manualoffsetvalue = default_offset
        
        ######################################################
        # DEFINE BUTTONS
        
        self.resetview_button = tkinter.Button(master=self.parent, text="Reset View", command=self.updateXYlims)
        self.resetview_button.configure(state="disabled")
        self.resetview_button.pack(side=tkinter.LEFT)

        offset_modes_list = ['match tops','time shift','common depth','manual']

        
        # set all buttons disabled by default (until an alignment file is opened)

        self.offset_mode_menu = tkinter.OptionMenu(self.parent,self.offset_mode_StringVar,*offset_modes_list)
        self.offset_mode_menu.configure(state="disabled")
        self.offset_mode_menu.pack(side=tkinter.LEFT)
        
        #undo redo: laissé en chantier pour l'instant
        #self.undo_button = Tkinter.Button(text='Undo',command = self.undo)
        #self.undo_button.configure(state="disabled")
        #self.undo_button.pack(side=tkinter.LEFT)
        
        #self.redo_button = Tkinter.Button(text='Redo',command = self.undo)
        #self.redo_button.configure(state="disabled")
        #self.redo_button.pack(side=tkinter.LEFT)
        

        self.manual_offset_value_button = tkinter.Button(text=str(default_offset),command=self.offset_input)
        self.manual_offset_value_button.configure(state="disabled")
        self.manual_offset_value_button.pack(side=tkinter.LEFT)

        self.species_menu = tkinter.OptionMenu(self.parent, self.species_on_display_StringVar, *default_list)
        #tested but not working; combobox to have a scrollbar
        #self.species_menu = ttk.Combobox(self.parent, textvariable = self.species_on_display_StringVar, values = default_list)

        self.species_menu.configure(state="disabled")
        self.species_menu.pack(side=tkinter.LEFT)

        self.profile_menu = tkinter.OptionMenu(self.parent, self.profile_on_display_StringVar, *default_list)
        #tested but not working; combobox to have a scrollbar
        #self.profile_menu = ttk.Combobox(self.parent, textvariable = self.profile_on_display_StringVar, values = default_list)

        self.profile_menu.configure(state="disabled")
        self.profile_menu.pack(side=tkinter.LEFT)

        self.quit_button = tkinter.Button(master=self.parent, text="Quit", command=self._quit)
        self.quit_button.pack(side=tkinter.RIGHT)

        cb_registry = self.ax[1].callbacks
        cid = cb_registry.connect('ylim_changed', self.relim_callback)
        
        
    #####################################################################
    #####################################################################
    #####################################################################
    ##### FUNCTIONS FOR THE "FILE" dropdown menu
        
    def export_to_csv(self):
        
        workdir = os.getcwd()

        ftypes = [('CSV files', '*.csv'), ('All files', '*')]

        csvfilename = tkinter.filedialog.asksaveasfilename(initialdir = workdir,initialfile = 'Untitled.csv',
                defaultextension=".csv",filetypes=ftypes)
        
        out = load_alig_array(self.filename,self.species_on_display)
        
        if csvfilename:
            out.to_csv(csvfilename, index=True)  
        
        
    def saveStateas(self):
        workdir = os.getcwd()

        ftypes = [('Pickle files', '*.pkl'), ('All files', '*')]

        newfilename = tkinter.filedialog.asksaveasfilename(initialdir = workdir,initialfile = 'Untitled.pkl',
                defaultextension=".pkl",filetypes=ftypes)
        
        new_dic = {}
        new_dic['tiepoints'] = self.tiepoints.copy()
        new_dic['cores'] = self.cores.copy()
        new_dic['metadata'] = self.metadata.copy()
        
        if newfilename: # asksaveasfile return `None` if dialog closed with "cancel".
            write_dic_file(new_dic,newfilename)
            self.filename = newfilename
        
        
    def saveState(self):
        
        
        new_dic = load_dic_file(self.filename)
        new_dic['tiepoints'] = self.tiepoints.copy()
        #new_dic
        
        #new_dic['cores'] = self.cores.copy()
        
        write_dic_file(new_dic,self.filename)
        
    def hover(self,event):
        
        vis = self.pointshl.get_visible()
        
        

        if event.inaxes == self.ax[1]:
            #dist = (np.array(x)-mousedata[0])**2+(np.array(y)-mousedata[1])**2
            dist1 = eventdist(event,self.points1)
            dist2 = eventdist(event,self.points2)
            
        
            if not dist1 is None and not dist2 is None:
                
                offsets1 = self.points1.get_offsets()
                xp1,yp1 = zip(*offsets1)
                
                combinedTransform = self.ax[0].transData + self.ax[1].transData.inverted()
        
                offsets2 = self.points2.get_offsets()
                xp2,yp2 = zip(*offsets2)
        
                dist1 = dist1[:len(dist2)]
                dists = np.stack([dist1,dist2])

                ind = np.unravel_index(np.ma.masked_array(dists,mask=np.isnan(dists)).argmin(),dists.shape)[1]
            
                # TODO july 10th: instead of closest distance, use points2.contains(event)
                # and with a ghost scatter plot for points1 (alpha = 0)
                if np.min(dists[:,ind])<.001:
                    xi1 = xp1[ind]
                    yi1 = yp1[ind]
                    
                    xi1_on_ax2,yi1_on_ax2 = combinedTransform.transform([xi1,yi1])
                    
                    xi2 = xp2[ind]
                    yi2 = yp2[ind]
                
                    self.update_hl([xi1_on_ax2,xi2],[yi1_on_ax2,yi2])
                    self.pointshl.set_visible(True)
                    
                    tag = str(self.tiepoints[self.profile_on_display][ind]['species'])
                    self.update_tagsshow(xi2,yi2,tag)
                    self.tagsshow.set_visible(True)
                    self.fig.canvas.draw_idle()
                
                else:
                    self.pointshl.set_visible(False)
                    self.tagsshow.set_visible(False)
                    self.fig.canvas.draw_idle()
                
            else:
                self.pointshl.set_visible(False)
                self.tagsshow.set_visible(False)
                self.fig.canvas.draw_idle()
                
                
    def get_linedata(self):
        
        depth1 = self.cores[self.profile_on_display][self.species_on_display]['depth']
        depth2 = self.cores['REF'][self.species_on_display]['depth']
        
        signal1 = self.cores[self.profile_on_display][self.species_on_display]['data']
        signal2 = self.cores['REF'][self.species_on_display]['data']
        
        return depth1,signal1,depth2,signal2
    
                
    def get_tiepoints(self):
        # convert the tiepoints stored in the dictionary to the xp1 and xp2 lists
        
        xp1 = [bob['profile_depth'] for bob in self.tiepoints[self.profile_on_display]]
        xp2 = [bob['ref_depth'] for bob in self.tiepoints[self.profile_on_display]]
        
        return xp1,xp2
        
        
    def on_pick(self,event):
        
        vis = self.pointshl.get_visible()
        
        
        # change names later?
        ax1 = self.ax[0]
        ax2 = self.ax[1]
        ax3 = self.ax[2]
                
        
            
        # Maybe a nicer way to do this? 
        # I just want to ignore clicks when zoom or pan is selected
        if not self.toolbar.mode.name == 'NONE':
            return
    
        # pick is collected by ax2 which is on top of ax1
        # we use combinedtransform to get the corresponding point
        # on ax1 based on the event coordinates
            
        combinedTransform = ax2.transData + ax1.transData.inverted()

        # event has x and y in data coordinates for ax2:
        pt_data2 = [event.xdata, event.ydata]
    
        # extracting axes limits 
        # 1) to compute the distance in normalized units
        # 2) to use for relim using bottom plot
    
        xlim1 = ax1.get_xlim()
        ylim1 = ax1.get_ylim()
        xlim2 = ax2.get_xlim()
        ylim2 = ax2.get_ylim()
        
        xrange1 = xlim1[1]-xlim1[0]
        yrange1 = ylim1[1]-ylim1[0]
        xrange2 = xlim2[1]-xlim2[0]
        yrange2 = ylim2[1]-ylim2[0]
        
            
        if event.inaxes is ax3:
            
            # Convert them into data coordinates for ax1:
            pt_data1 = combinedTransform.transform(pt_data2)
        
            # center the view on the point clicked in the bottom plot
            ax1.set_xlim(pt_data1[0]-xrange1/2,pt_data1[0]+xrange1/2)
            ax1.set_ylim(pt_data1[1]-yrange1/2,pt_data1[1]+yrange1/2)
            ax2.set_xlim(pt_data2[0]-xrange1/2,pt_data2[0]+xrange2/2)
            ax2.set_ylim(pt_data2[1]-yrange1/2,pt_data2[1]+yrange2/2)

            # update rectangle view
            self.relim_callback(ax2)
    
        if event.inaxes is ax2:
            
            # Convert them into data coordinates for ax1:
            pt_data1 = combinedTransform.transform(pt_data2)
    
            #Left click: add point
            if event.button is MouseButton.LEFT:
                if self.xp1selection is None:
                    dist_to_line_1 = eventdist(event,self.line1)
                    #depth1 = self.line1.get_xdata()
                    
                    depth1,signal1 = zip(*self.line1.get_xydata())
                    ind = np.nanargmin(dist_to_line_1)
                    #xp1.append(depth1[ind])
                    #temporarily store value in a class variable
                    xi1 = depth1[ind]
                    self.xp1selection = xi1
                    yi1 = signal1[ind]
                    
                    #show where the point was clicked
                    self.xp1hl.set_offsets(np.c_[xi1,yi1])
                    self.xp1hl.set_visible(True)
                    
                else:
                    dist_to_line_2 = eventdist(event,self.line2)
                    depth2 = self.line2.get_xdata()
                    ind = np.nanargmin(dist_to_line_2)
                    
                    new_tiepoint = {
                        'profile_depth':self.xp1selection,
                        'ref_depth':depth2[ind],
                        'species':self.species_on_display
                        }
                    self.tiepoints[self.profile_on_display].append(new_tiepoint)
                    
                    #switch back to non selection mode
                    self.xp1hl.set_visible(False)
                    self.xp1selection = None
                    
    
            #Right click: delete point
            if event.button is MouseButton.RIGHT:
                # a right click when marked points are all paired will remove the closest marked point
                if self.xp1selection is None:
                    if len(self.tiepoints[self.profile_on_display])>0 and vis is True:
                        
                        # warning: here we rely on the fact that indices are the same
                        # for the scatter artist points1 xy data
                        # and for xp1,xp2 (a priori no reason that is it scrambled in points?...)
                        # we get the index of closest distance iwth points1 xy data
                        # and we use the same index to delete points in self.tiepoints
                        # watch out for bugs!
                    
                        xpdist1 = eventdist(event,self.points1)
                        xpdist2 = eventdist(event,self.points2)
                        # to delete closest point, either on line1 or line2
                        xp_dists= np.stack((xpdist1,xpdist2))
            
                        ind = np.unravel_index(np.ma.masked_array(xp_dists,mask=np.isnan(xp_dists)).argmin(),xp_dists.shape)
            
                        i = ind[1]
            
                        del self.tiepoints[self.profile_on_display][i]
                        self.pointshl.set_visible(False)

                
                    # a right click after selecting the first point simply removes the first point    
                else:
                    self.xp1selection = None
                    self.xp1hl.set_visible(False)
                

        
        #self.tiepoints_history.append(self.tiepoints)
        #self.undo_redo_callback()
        
        self.updateTiepoints()
        self.updateLinks()
        
        self.canvas.draw()
        
        self.saveState()
            
        
    def on_press(self,event):
            
        current_profile = self.profile_on_display
        current_species = self.species_on_display
    
        species_keys_available = [species for species in self.species_keys if species in 
                                   self.cores[self.profile_on_display].keys()]
        
        profile_keys_available = [profile for profile in self.profile_keys if 
                                     self.species_on_display in self.cores[profile].keys()]   
            
    
        if event.key == '+': 
            current_state = self.minmaxscaling_BooleanVar.get()
            self.minmaxscaling_BooleanVar.set(not(current_state))
            
        # we want to define special key bindings for species often used
        if event.key == 'w':
            if 'MSA' in species_keys_available:
                self.species_on_display_StringVar.set('MSA')
        
        if event.key =='s':
            # two different ways to write sulfate
            if 'Sulfate' in species_keys_available:
                self.species_on_display_StringVar.set('Sulfate')
            elif 'SO4' in species_keys_available:
                self.species_on_display_StringVar.set('SO4')

        
        if event.key == 'up' or event.key == 'down':
            n = species_keys_available.index(current_species)
            if event.key == 'down' and  n<len(species_keys_available)-1:
                species = species_keys_available[n+1]
                self.species_on_display_StringVar.set(species)

            if event.key == 'up' and n>0:
                species = species_keys_available[n-1]
                self.species_on_display_StringVar.set(species)
            
        # change profile_key
    
        if event.key == 'right' or event.key == 'left':
            n = profile_keys_available.index(current_profile)
            if event.key =='right' and n<len(profile_keys_available)-1:
                profile_key = profile_keys_available[n+1]
                self.profile_on_display_StringVar.set(profile_key)

            if event.key == 'left' and n>0: 
                profile_key = profile_keys_available[n-1]
                self.profile_on_display_StringVar.set(profile_key)
            
        # callbacks will take care of updating all plots
    
        
    def offset_callback(self,*args):
        
        # callback that catches any change to the offsetmode dropdown menu
        # and call to redraws the graph
            
        if self.offset_mode_StringVar.get() != 'manual':
            self.manual_offset_value_button.config(state='disabled')
        else:
            self.manual_offset_value_button.config(state='normal')
     
        #self.updateUI()

        self.updateXYlims()
        
        self.updateLinks()
        
        #self.updateTiepoints()

       
        self.canvas.draw()
        
    def relim_callback(self,ax):
        
        # callback function that catches any change to the ax(2) limits
        # to draw the rectangle of current view
        # in the bottom preview
    
        xlim2 = ax.get_xlim()
        ylim2 = ax.get_ylim()
    
        xrange2 = xlim2[1]-xlim2[0]
        yrange2 = ylim2[1]-ylim2[0]
    
        self.rect.set_xy((xlim2[0],ylim2[0]))
        self.rect.set_width(xrange2)
        self.rect.set_height(yrange2)
    
    #print("New axis y-limits are", axes.get_ylim())
    
    def updateUI(self):
        
        # function called upon change of species and change of profile
        # to gray out options in the drop down menu depending on what data are available.
        
        # only enable available species in species menu.
        menu = self.species_menu["menu"]
        nentries = menu.index("end")
        for index in range(nentries+1):
            species = menu.entrycget(index, "label")
            if species in self.cores[self.profile_on_display].keys():
                menu.entryconfigure(species, state = 'normal')
            else:
                menu.entryconfigure(species, state = 'disabled')
                
        # only enable available profile in profile menu.
        menu = self.profile_menu["menu"]
        nentries = menu.index("end")
        for index in range(nentries+1):
            profile = menu.entrycget(index, "label")
            if self.species_on_display in self.cores[profile].keys():
                menu.entryconfigure(profile, state = 'normal')
            else:
                menu.entryconfigure(profile, state = 'disabled')
                
        menu = self.offset_mode_menu["menu"]
        #check that both profiles have a date available
        if ((self.profile_on_display in self.metadata.keys() and 'date' in self.metadata[self.profile_on_display].keys())
        and ('REF' in self.metadata.keys() and 'date' in self.metadata['REF'].keys())):
            menu.entryconfigure('time shift',state='normal')
        else:
            menu.entryconfigure('time shift',state='disabled')

            
                
        
    def Var_callback(self,*args):
    
        self.profile_on_display = str(self.profile_on_display_StringVar.get())
        
        self.species_on_display = str(self.species_on_display_StringVar.get())
        
        self.updateUI()

        self.updateLines()
        
        #self.relim_x()
        self.relim_y()


        self.updateTiepoints()
        
        self.updateLinks()
                        
        self.canvas.draw()
        
        
    def offset_input(self):
        
        inputvalue = tkinter.simpledialog.askstring(title='test',prompt="Enter manual offset value")
        self.manual_offset_value_button.configure(text=inputvalue)
        self.manualoffsetvalue = float(inputvalue)
        
        self.relim_x()
        self.updateLinks()
        #self.updateTiepoints()
        self.canvas.draw()
            
    def _quit(self):
        
        print('goodbye')
        self.parent.quit()     # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent
        
        
########################3
## NEXT: what happens when we open a file
        
    def loadData(self):
        #run only once at the opening of the file
        
        new_dic = load_dic_file(self.filename)        
        
        # load tiepoints and cores data in separate dictionaries
        self.tiepoints = new_dic['tiepoints']
        self.cores = new_dic['cores']
        self.metadata = new_dic['metadata']
        
        # NEW save previous state of tiepoints for restore
        # en chantier
        #self.tiepoints_history = []
        #self.tiepoints_history_position = 0
        #self.tiepoints_history.append(self.tiepoints.copy())

        # we also define lists of core and species name for the interface to navigate into
        self.profile_keys = [ bob for bob in list(self.cores.keys()) if bob != 'REF']
        
        #only need consider species which are available on the reference profile
        self.species_keys = list(self.cores['REF'].keys())
        
        
        # VARIABLES USED BY THE INTERFACE TO MANAGE DISPLAY
        
        # initialize with a random profile and species, or something else..
        self.profile_on_display = self.profile_keys[0]
        
        if 'SO4' in self.species_keys:
            #SO4 is a popular species used for alignment
            self.species_on_display = 'SO4'
        elif 'Sulfate' in self.species_keys:
            self.species_on_display = 'Sulfate'
        else:
            self.species_on_display = self.species_keys[0]
            
        # initialize offset_mode
        self.offset_mode = 'match tops'
        
       
    def updateLines(self):
        
        # function to asign x and y data to the lines ploted
        # should be called only upon change of species or change of profile to display       
    
        depth1,signal1,depth2,signal2 = self.get_linedata()

    
        # Function to call when switching species or profile;
        # update lines data and redraw plot
        
        # triggered upon changing profile only

    
        # UPDATE DATA
        
        self.line1.set_xdata(depth1)
        self.line1.set_ydata(signal1)
                
        self.line2.set_xdata(depth2)
        self.line2.set_ydata(signal2)
        
        self.line4.set_xdata(depth2) # redundent
        self.line4.set_ydata(signal2)
    
        #self.text_date.set_text(date1.date())
    
        self.text_profile.set_text(self.profile_on_display) 
    
        self.text_species.set_text(self.species_on_display)
        
        
        
    def get_anchors(self):
    
        offset_mode_str = self.offset_mode_StringVar.get()
        
        depth1 = self.cores[self.profile_on_display][self.species_on_display]['depth']
        depth2 = self.cores['REF'][self.species_on_display]['depth']
    
        ########################
        # to implement: different accumulation values for different sites and compute the expected
        # depth shift
    
        accu = 7.83 # mean accumulation rate based on era5 w.e. precip and density of 320kg/m3
    
        # anchor lines will be at the same position visualy
        # anchor mode by depth: anchor1 = depth1[0] anchor2 = depth2[0]-depth1[0]
        # anchor mode by time shift: anchor1 = depth1, anchor2 = depth2+time_delta*accu
        # anchor mode manual: anchor1 = depth1[0], anchor2 = depth2[0]+manual shift
            
        if offset_mode_str == 'time shift':
            
            # not in use, still need to implement in data structure
    
            anchor1 = depth1[0]
        
            date1 = self.metadata[self.profile_on_display]['date']
            date2 = self.metadata['REF']['date']
    
            time_delta = (date2-date1).days/365.25
    
            anchor2 = depth2[0]+time_delta*accu
    
        if offset_mode_str == 'common depth':
            
            anchor1 = depth1[0]
            anchor2 = depth1[0]
        
        if offset_mode_str == 'manual':
            
            anchor1 = depth1[0]
            anchor2 = depth2[0]+self.manualoffsetvalue
            
        if offset_mode_str == 'match tops':
            
            anchor1 = depth1[0]
            anchor2 = depth2[0]
        
        return anchor1,anchor2
    
    def updateLinks(self):
        
        # Since we draw links on ax2 based on tiepoints on ax1
        # the links depend on the limits of the axes 
        # this is why we need to keep them separate from the tiepoints
        # and to update them upon change of axis (while tiepoints naturally follow the axes)
        
        depth1,signal1,depth2,signal2 = self.get_linedata()
        
        xp1,xp2 = self.get_tiepoints()
        
        yp1 = np.interp(xp1,depth1,signal1)
        yp2 = np.interp(xp2,depth2,signal2)
        
        xp_links,yp_links = get_links(self.ax,xp1,xp2,yp1,yp2)
        self.links.set_data(xp_links,yp_links)  

                
    def updateTiepoints(self):
        
        # A function to be called each time we manipulate tiepoints:
        # redraws the preview in the bottom graph
        # redraws the tiepoints and
        # redraws the links
        
        # defining shortnames for readability
        
        
        depth1,signal1,depth2,signal2 = self.get_linedata()
        
        xp1,xp2 = self.get_tiepoints()
        
        yp1 = np.interp(xp1,depth1,signal1)
        yp2 = np.interp(xp2,depth2,signal2)
        
        #xp_links,yp_links = get_links(self.ax,xp1,xp2,yp1,yp2)
        
        # update tiepoints
        
        self.points1.set_offsets(np.c_[xp1,yp1])
        self.points2.set_offsets(np.c_[xp2,yp2])
        #self.links.set_data(xp_links,yp_links)  
    
        self.updateLinks()
        
        # update preview
    
        depth_new = depth_sqz_str(depth1,xp1,xp2)
        
        signal_new = np.interp(depth2,depth_new,signal1,left=np.nan,right=np.nan)    
        
        self.line3.set_xdata(depth2) # redundent
        self.line3.set_ydata(signal_new)
        
        
        # Set highlight
    
        if self.xp1selection is None:
            
            self.line1.set_linewidth(3)
            self.line2.set_linewidth(1.5)

        else:
            self.line1.set_linewidth(1.5)
            self.line2.set_linewidth(3)
            
        
    def updateXYlims(self):
    
        self.relim_x()
        self.relim_y()
        self.canvas.draw()
        
    def relim_x(self):
        
        #dates as still used in the get_anchor functions
        #can use this again in the future but we want to add if statements in case 
        #no metadata is specified
    
        #date1 = self.cores[self.profile_on_display]['time']
        #date2 = self.cores['REF']['time']
        
        depth1,signal1,depth2,signal2 = self.get_linedata()
    
        rangex1 = np.nanmax(depth1)-np.nanmin(depth1)
        rangex2 = np.nanmax(depth2)-np.nanmin(depth2)

        xlim1 = (np.nanmin(depth1)-rangex1/20,np.nanmax(depth1)+rangex1/20)
        xlim2 = (np.nanmin(depth2)-rangex2/20,np.nanmax(depth2)+rangex2/20)
        
        # OFFSET
    
        self.anchor1,self.anchor2 = self.get_anchors()
            
        # these are just graphical hints to ensure we have set the alignment right
        # between the two graphs
        # (shows the two values on the graph where they are supposed to be aligned)
        
        self.vline1.set_xdata(self.anchor1)
        self.vline2.set_xdata(self.anchor2)

        anchor1 = self.anchor1
        anchor2 = self.anchor2
    
        if np.isfinite(xlim1[0]):
        
            self.ax[0].set_xlim(anchor1-max(anchor1-xlim1[0],anchor2-xlim2[0]),anchor1+max(xlim1[1]-anchor1,xlim2[1]-anchor2))
            self.ax[1].set_xlim(anchor2-max(anchor1-xlim1[0],anchor2-xlim2[0]),anchor2+max(xlim1[1]-anchor1,xlim2[1]-anchor2))
            self.ax[2].set_xlim(depth2[0],depth2[-1])
            
    def relim_y(self):
        
        # TO IMPLEMENT:
        # USE THE MAX OF THE CURRENT VIEW, NOT THE MAX OF THE ENTIRE PROFILE!!!
        
        #date1 = self.cores[self.profile_on_display]['time']
        #date2 = self.cores['REF']['time']
        
        depth1,signal1,depth2,signal2 = self.get_linedata()
    
        rangey1 = np.nanmax(signal1)-np.nanmin(signal1)
        rangey2 = np.nanmax(signal2)-np.nanmin(signal2)
    
        ylim1 = [np.nanmin(signal1)-rangey1/20,np.nanmax(signal1)+rangey1/20]
        ylim2 = [np.nanmin(signal2)-rangey2/20,np.nanmax(signal2)+rangey2/20]
    
        ylim = [np.nanmin(np.array([ylim1[0],ylim2[0]])),
                          np.nanmax(np.array([ylim1[1],ylim2[1]]))]
    
        if np.isfinite(ylim[0]):
            if self.minmaxscaling_BooleanVar.get() is True:
                self.ax[0].set_ylim(ylim1)
                self.ax[1].set_ylim(ylim2)
            else:
                self.ax[0].set_ylim(ylim[0],ylim[1])
                self.ax[1].set_ylim(ylim[0],ylim[1])
                
            self.ax[2].set_ylim(ylim[0],ylim[1])
    
    def update_hl(self,xs,ys):
    
        #pos = sc.get_offsets()[ind["ind"][0]]
        #print(ind)
        self.pointshl.set_offsets(np.c_[xs,ys])
        
    def update_tagsshow(self,x,y,tag):
        
        self.tagsshow.set_text(tag)
        self.tagsshow.set_x(x)
        self.tagsshow.set_y(y)

            
    ## FILE DIALOG WINDOW
    
    def init_option_menu(self):
        # code from the internet
        # we will need to update the option menus upon loading a new file
        menu = self.profile_menu["menu"]
        menu.delete(0, "end")
        for string in self.profile_keys:
            menu.add_command(label=string, 
                             command=lambda value=string: self.profile_on_display_StringVar.set(value))
            
        menu = self.species_menu["menu"]
        menu.delete(0, "end")
        for string in self.species_keys:
            menu.add_command(label=string, 
                             command=lambda value=string: self.species_on_display_StringVar.set(value))
        
    
    def enableUI(self):
        
        default_offset_mode = 'match tops'
        
        self.resetview_button.configure(state="normal")
        self.offset_mode_menu.configure(state="normal")
        self.offset_mode_StringVar.set(default_offset_mode)
        
        self.species_menu.configure(state="normal")
        self.species_on_display_StringVar.set(str(self.species_on_display))
        self.profile_menu.configure(state="normal")
        self.profile_on_display_StringVar.set(str(self.profile_on_display))
        
        self.init_option_menu()
        
        # only now attribute callbacks
        self.offset_mode_StringVar.trace("w", self.offset_callback)
        self.profile_on_display_StringVar.trace("w", self.Var_callback)
        self.species_on_display_StringVar.trace("w", self.Var_callback)
        self.minmaxscaling_BooleanVar.trace("w",self.Var_callback)

        # and attribute mpl connections
        # select tie points
        self.fig.canvas.mpl_connect('button_press_event', self.on_pick)

        #switch between species and profiles with up/down and left/right arrows
        self.fig.canvas.mpl_connect('key_press_event', self.on_press);
        
        #highlight marked points when hovering
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        
        
        self.fileMenu.entryconfig("Save as", state="normal")
        self.fileMenu.entryconfig("Export aligned data to csv",state="normal")


        
        #test
        #fig.canvas.mpl_connect("motion_notify_event", hover)
        
        
            

        
    def onOpenAlig(self):

        ftypes = [('Pickle files', '*.pkl'), ('All files', '*')]
        dlg = tkinter.filedialog.Open(self, filetypes = ftypes)
        fl = dlg.show()

        if fl != '':
            
            
            self.filename = fl
                        
            self.StartApp()
            
            
    def StartApp(self):
        
        self.loadData()
            
        self.enableUI()
            
        self.updateUI()
            
        self.updateLines()
        
        self.updateXYlims()
        
        self.updateTiepoints()
        
        self.updateLinks()
                        
        self.canvas.draw()
        
        
        
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
        
        
        self.opendataButton = tkinter.Button(master=top, text= "Select data files", command= self.onOpenData)
        self.opendataButton.pack(side=tkinter.TOP)
        
        self.selected_datafiles = () # initialize with empty tuple
        
        self.selected_datafiles_Label = tkinter.Label(top, text= "", font=('Mistral 10 bold'))
        self.selected_datafiles_Label.pack(side=tkinter.TOP)
        
        self.opendataButton = tkinter.Button(master=top, text= "Select metadata files", command= self.onOpenMeta)
        self.opendataButton.pack(side=tkinter.TOP)
        
        self.selected_metadatafiles = () # initialize with empty tuple
        
        self.selected_metadatafiles_Label = tkinter.Label(top, text= "", font=('Mistral 10 bold'))
        self.selected_metadatafiles_Label.pack(side=tkinter.TOP)
        
        self.reference_selected_StringVar = tkinter.StringVar(self.parent)
        self.reference_selected_StringVar.set('select ref')
        self.reference_selected_StringVar.trace("w", self.reference_selected_StringVar_callback)
    
        default_list = ['']
        
        self.reference_menu = tkinter.OptionMenu(top, self.reference_selected_StringVar, *default_list)
        self.reference_menu.configure(state="disabled")
        self.reference_menu.pack(side=tkinter.TOP)
        
        tkinter.Label(top,text='min depth: ').pack(side=tkinter.LEFT)
        self.mindepth = tkinter.Entry(top, width = 6,state="disabled")
        #self.mindepth.insert(0, "-infty") 
        self.mindepth.pack(side=tkinter.LEFT)
        
        txt = tkinter.Label(top,text='max depth: ')
        txt.pack(side=tkinter.LEFT)
        self.maxdepth= tkinter.Entry(top,width = 6,state="disabled")
        #self.maxdepth.insert(0, "+infty") 
        self.maxdepth.pack(side=tkinter.LEFT)
        
        self.create_alignmentButton = tkinter.Button(master=top, text= "Generate new file", command= self.createAlignmentFile)
        self.create_alignmentButton.configure(state="disabled")
        self.create_alignmentButton.pack(side=tkinter.BOTTOM)
        
        
    def createAlignmentFile(self):
        
        #collect all the parameters
        datafiles = self.selected_datafiles
        metadatafiles = self.selected_metadatafiles
        ref_lab = self.reference_selected_StringVar.get()
        min_depth = self.mindepth.get()
        max_depth = self.maxdepth.get()

        
        # We will have to make this work for datetimes too
        if min_depth == '':
            min_depth = -np.infty
        else:
            min_depth = int(min_depth)
        if max_depth == '':
            max_depth = np.infty
        else:
            max_depth = int(max_depth)
        
        
        #print(datafiles,metadatafiles,ref_lab,min_depth,max_depth)

        #create the dictionary
        #this is a mess, rewrite later to only use one dictionary state
        new_dic = initAlignmentFile(datafiles,metadatafiles,ref_lab,min_depth,max_depth)
        
        #save the new state to a new file
        self.tiepoints = new_dic['tiepoints']
        self.cores = new_dic['cores']
        self.metadata = new_dic['metadata']
        
        self.saveStateas()
        
        if hasattr(self, 'filename'):
            self.StartApp()
            self.top.destroy()


            
    def reference_selected_StringVar_callback(self,*args):
        if not self.reference_selected_StringVar.get() =='select ref':
            self.create_alignmentButton.configure(state="normal")
        
    def onOpenMeta(self):
        
        workdir = os.getcwd()

        
        ftypes = [('Excel files', '*.xlsx'), ('All files', '*')]
        filez = tkinter.filedialog.askopenfilenames(initialdir = workdir,filetypes = ftypes)
        self.selected_metadatafiles = filez
        
        #now just a couple lines to display them nicely without the full path
        filez_for_label = [file.removeprefix(workdir) for file in filez]
        string_for_label = " ".join([file+" \n " for file in filez_for_label])
        self.selected_metadatafiles_Label.configure(text=string_for_label)
            
        
    def onOpenData(self):
        
        workdir = os.getcwd()

        
        ftypes = [('Excel files', '*.xlsx'), ('All files', '*')]
        filez = tkinter.filedialog.askopenfilenames(initialdir=workdir,filetypes = ftypes)
        self.selected_datafiles = filez
        
        #now just a couple lines to display them nicely without the full path
        filez_for_label = [file.removeprefix(workdir) for file in filez]
        string_for_label = " ".join([file+" \n " for file in filez_for_label])
        self.selected_datafiles_Label.configure(text=string_for_label)
        
        temp = []
        
        for datafile in filez:
            xls = pd.ExcelFile(datafile)
            core_names = xls.sheet_names[:]
            temp+=core_names
            
        references_available = list(set(temp))
        
        self.reference_menu.configure(state="normal")
        self.maxdepth.configure(state="normal")
        self.mindepth.configure(state="normal")
        # not here
        #self.create_alignmentButton.configure(state="normal")

        menu = self.reference_menu["menu"]
        menu.delete(0, "end")
        for string in references_available:
            menu.add_command(label=string, 
                             command=lambda value=string: self.reference_selected_StringVar.set(value))
            
####################################################################
####################################################################
####################################################################


def main():

    root = tkinter.Tk()
    
    ex = ALICE(root)
    #root.geometry("300x250+300+300")
    
    #defining title and icon for the app
    root.title("ALICE - alignment interface for ice cores")
        
    # Broken, haven't figured out how to set up a custom icon so far...
    #photo = tkinter.PhotoImage(file = "/home/aooms/THESE/code_align_devel/lapin.png")
    #print(photo)
    #root.iconphoto(False, photo)
        
        
    root.mainloop()  


if __name__ == '__main__':
    main()  


# In[ ]:





# In[ ]:




