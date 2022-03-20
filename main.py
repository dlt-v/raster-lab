from tkinter import *
from tkinter import ttk

from pip import main

root = Tk()
root.title("RasterLab")
# root.minsize(600, 300)
root.geometry('600x300')
root.resizable(FALSE, FALSE)
# root.maxsize(1200, 600)


def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(str(int(0.3048 * value * 10000.0 + 0.5)/10000.0))
    except ValueError:
        pass


mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  # type: ignore
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

feet = StringVar()
feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(W, E))  # type: ignore

meters = StringVar()
ttk.Label(mainframe, textvariable=meters).grid(
    column=2, row=2, sticky=(W, E))  # type: ignore

ttk.Button(mainframe, text="Calculate", command=calculate).grid(
    column=3, row=3, sticky=W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
feet_entry.focus()
root.bind("<Return>", calculate)

root.mainloop()
