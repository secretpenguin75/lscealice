import os
from tkinter.filedialog import askopenfilenames, asksaveasfilename, Open
from tkinter.simpledialog import askstring

from .export import load_alig_array
from .dic import Dic, Tiepoint, initAlignmentFile, load_dic_file, write_dic_file

def tkinter_export_to_csv(out):
        workdir = os.getcwd()

        ftypes = [("CSV files", "*.csv"), ("All files", "*")]

        csvfilename = asksaveasfilename(
            initialdir=workdir,
            initialfile="Untitled.csv",
            defaultextension=".csv",
            filetypes=ftypes,
        )

        if csvfilename:
            out.to_csv(csvfilename, index=True)

def export_to_csv(filename,species_on_display):
    out = load_alig_array(filename, species_on_display)
    tkinter_export_to_csv(out)

def tkinter_saveStateAs(out):
    workdir = os.getcwd()

    ftypes = [("Pickle files", "*.pkl"), ("All files", "*")]

    pklfilename = asksaveasfilename(
        initialdir=workdir,
        initialfile="Untitled.pkl",
        defaultextension=".pkl",
        filetypes=ftypes,
    )

    if pklfilename is None:  # type: ignore
        # asksaveasfile return `None` if dialog closed with "cancel".
        return
    
    write_dic_file(out, pklfilename)

    return pklfilename


def saveStateAs(ALICE):
    def dialog():
        new_dic = Dic(
            tiepoints=ALICE.tiepoints.copy(),
            cores=ALICE.cores.copy(),
            metadata=ALICE.metadata.copy(),
        )

        newfilename = tkinter_saveStateAs(new_dic)

        ALICE.filename = newfilename

    return dialog



def saveState(ALICE):

    def writer():

        new_dic = load_dic_file(ALICE.filename)

        new_dic["tiepoints"] = ALICE.tiepoints.copy()

        write_dic_file(new_dic, ALICE.filename)

    return writer

