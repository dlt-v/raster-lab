import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

root = tk.Tk()
# root.geometry("220x50")
root.title("RasterLab")
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)
root.resizable(False, False)

focused_file: str = ""


def import_image():
    extensions = [('formats', ['.jpg', '.png', '.bmp', '.jpeg'])]
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


def compose_histogram():
    new_image = Image.open(focused_file)
    pixel_list = list(new_image.getdata())
    match (new_image.mode):
        # L for greyscale images, RGB for color images (duh)
        case 'L':
            print("This image is greyscale.")
            color_values = {}
            i = 0
            while i < len(pixel_list):
                # if the value is already in the dictionary
                if f"{pixel_list[i]}" in color_values.keys():
                    color_values[f"{pixel_list[i]}"] += 1
                # if the value is not yet in dictionary
                else:
                    color_values[f"{pixel_list[i]}"] = 1
                i += 1
            print(color_values.keys())

        case 'RGB':
            print("This image is RGB.")


import_button = tk.Button(root,
                          text="import image",
                          pady=5,
                          padx=10, command=import_image,
                          font=("consolas", 12)
                          )
import_button.grid(column=1, row=1, padx=5, pady=5)

histogram_button = tk.Button(root,
                             text="make a histogram",
                             pady=5,
                             padx=10, command=compose_histogram,
                             font=("consolas", 12)

                             )
histogram_button.grid(column=2, row=1, padx=5, pady=5)

root.mainloop()
