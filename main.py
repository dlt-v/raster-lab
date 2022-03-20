import tkinter as tk
from tkinter import ttk

from pip import main

root = tk.Tk()
root.title("RasterLab")
# root.minsize(600, 300)
root.geometry('600x300')
root.resizable(tk.FALSE, tk.FALSE)
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)
# root.maxsize(1200, 600)


def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(str(int(0.3048 * value * 10000.0 + 0.5)/10000.0))
    except ValueError:
        pass


mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(
    tk.N, tk.W, tk.E, tk.S))  # type: ignore
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

feet = tk.StringVar()
feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(tk.W, tk.E))  # type: ignore

meters = tk.StringVar()
ttk.Label(mainframe, textvariable=meters).grid(
    column=2, row=2, sticky=(tk.W, tk.E))  # type: ignore

ttk.Button(mainframe, text="Calculate", command=calculate).grid(
    column=3, row=3, sticky=tk.W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=tk.W)
ttk.Label(mainframe, text="is equivalent to").grid(
    column=1, row=2, sticky=tk.E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=tk.W)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
feet_entry.focus()
root.bind("<Return>", calculate)

root.mainloop()
