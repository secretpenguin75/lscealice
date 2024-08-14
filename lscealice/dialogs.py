import os
from tkinter.filedialog import asksaveasfilename

import pandas as pd

from .ALICE import ALICE

from .export import load_alig_array
from .dic import Dic, load_dic_file, write_dic_file


def tkinter_export_to_csv(out: pd.DataFrame):
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


def export_to_csv(filename: str, species_on_display: str):
    out = load_alig_array(filename, species_on_display)
    tkinter_export_to_csv(out)


def tkinter_saveStateAs(out: Dic):
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


def saveStateAs(alice: ALICE):
    def dialog():
        new_dic = Dic(
            tiepoints=alice.tiepoints.copy(),
            cores=alice.cores.copy(),
            metadata=alice.metadata.copy(),
        )

        newfilename = tkinter_saveStateAs(new_dic)
        if newfilename is not None:
            alice.filename = newfilename

    return dialog


def saveState(alice: ALICE):
    def writer():
        new_dic = load_dic_file(alice.filename)

        new_dic["tiepoints"] = alice.tiepoints.copy()

        write_dic_file(new_dic, alice.filename)

    return writer
