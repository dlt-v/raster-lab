import tkinter as tk
from tkinter import filedialog
from typing import Any
from PIL import Image, ImageTk

root = tk.Tk()
# root.geometry("220x50")
root.title("RasterLab")
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)
root.resizable(False, False)

focused_file: str = ""


def import_image():
    extensions = [('formats', ['.jpg', '.png', 'bmp'])]
    file_path = filedialog.askopenfilename(filetypes=extensions)
    if not file_path:
        return
    new_img = ImageTk.PhotoImage(Image.open(file_path))
    # label = tk.Label(root, text=file_path)
    # label.pack()

    new_window = tk.Toplevel(root)
    new_window.iconphoto(False, icon)
    new_window.title(f"RasterLab: {file_path}")
    geo_img = Image.open(file_path)
    geometry = f"{geo_img.height}x{geo_img.width}"
    new_window.resizable(False, False)
    new_window.geometry(geometry)

    def on_focus(event):
        global focused_file
        print(f"Focused file changed from: {focused_file} to {file_path}")
        focused_file = file_path

    new_window.bind("<FocusIn>", on_focus)

    image = tk.Label(new_window, image=new_img)
    # it has to be a reference, otherwise the image doesn't load!
    image.image = new_img  # type: ignore
    image.pack()


import_button = tk.Button(root,
                          text="import image",
                          pady=10,
                          padx=20, command=import_image
                          )
import_button.grid(column=1, row=1, padx=5, pady=5)

histogram_button = tk.Button(root,
                             text="make a histogram",
                             pady=10,
                             padx=20, command=import_image
                             )
histogram_button.grid(column=2, row=1, padx=5, pady=5)

root.mainloop()
