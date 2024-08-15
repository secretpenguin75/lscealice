import tkinter
from typing import Any, Callable


def insert_tiepoint_dialog(top: tkinter.Toplevel, on_confirm: Callable[[float, float], None]):
        top.geometry("250x150")
        top.title("Insert new tiepoint manually")

        tkinter.Label(top, text="profile depth: ").pack(side=tkinter.TOP)

        profile_depth_sv = tkinter.StringVar()
        e = tkinter.Entry(top, width=6, textvariable=profile_depth_sv)
        e.pack(side=tkinter.TOP)

        tkinter.Label(top, text="reference depth: ").pack(side=tkinter.TOP)

        ref_depth_sv = tkinter.StringVar()
        e2 = tkinter.Entry(top, width=6, textvariable=ref_depth_sv)
        e2.pack(side=tkinter.TOP)

        def validate_inputs(*_: Any):
            try:
                float(ref_depth_sv.get())
                float(profile_depth_sv.get())
                create_tiepoint_button.configure(state="normal")
            except ValueError:
                create_tiepoint_button.configure(state="disabled")

        ref_depth_sv.trace_add("write", validate_inputs)
        profile_depth_sv.trace_add("write", validate_inputs)

        def on_create(*_: Any):
            on_confirm(
                float(profile_depth_sv.get()),
                float(ref_depth_sv.get()),
            )
            top.destroy()

        create_tiepoint_button = tkinter.Button(
            master=top, text="Create tiepoint", command=on_create
        )
        create_tiepoint_button.configure(state="disabled")
        create_tiepoint_button.pack(side=tkinter.BOTTOM)
