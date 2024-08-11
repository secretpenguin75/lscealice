#!/usr/bin/env python3

import tkinter

from .ALICE import ALICE


def main():
    root = tkinter.Tk()

    ALICE(root)
    # root.geometry("300x250+300+300")

    # defining title and icon for the app
    root.title("ALICE - alignment interface for ice cores")

    # Broken, haven't figured out how to set up a custom icon so far...
    # photo = tkinter.PhotoImage(file = "/home/aooms/THESE/code_align_devel/lapin.png")
    # print(photo)
    # root.iconphoto(False, photo)

    root.mainloop()


def launch():
    main()


if __name__ == "__main__":
    main()
