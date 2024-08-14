#!/usr/bin/env python3

import tkinter
import os.path

from lscealice.ALICE import ALICE


def main():
    root = tkinter.Tk()

    ALICE(root)

    root.mainloop()


def launch():
    main()


def quicklaunch():
    root = tkinter.Tk()

    assert os.path.isfile("test.pkl")

    ALICE(root, filename="test.pkl")

    root.mainloop()


if __name__ == "__main__":
    main()
