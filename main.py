import tkinter as tk
from tkinter import filedialog
from typing import Any, Dict
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib as mtl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def terminate_all():
    plt.close('all')
    root.destroy()


root = tk.Tk()
# root.geometry("220x50")
root.title("RasterLab")
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", terminate_all)

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


def plot_histogram(data: Dict[str, int], label: str = "", color: str = "gray") -> None:
    """
        Displays histogram for one segment of data.
    """
    # data doesn't have to be passed sorted so we have to sort it
    sorted_data: Dict[str, int] = {}
    for i in range(256):
        key = str(i)
        if key in data.keys():
            sorted_data[key] = data[key]
        else:
            sorted_data[key] = 0

    plt.bar(list(sorted_data.keys()),
            list(sorted_data.values()), color=color, width=1)
    # hide tick information on the sides - prevents excessive during resize
    plt.xticks([])
    plt.yticks([])
    plt.title(label)


def compose_histogram():
    if focused_file == "":
        return
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
            plot_histogram(color_values, 'luma')
            plt.show()

        case 'RGB':
            print("This image is RGB.")
            r_values = {}
            g_values = {}
            b_values = {}
            i = 0
            while i < len(pixel_list):
                red_v = str(pixel_list[i][0])
                blu_v = str(pixel_list[i][1])
                grn_v = str(pixel_list[i][2])
                if red_v in r_values.keys():
                    r_values[red_v] += 1
                else:
                    r_values[red_v] = 1

                if blu_v in g_values.keys():
                    g_values[blu_v] += 1
                else:
                    g_values[blu_v] = 1

                if grn_v in b_values.keys():
                    b_values[grn_v] += 1
                else:
                    b_values[grn_v] = 1
                i += 1
            # hide control buttons on figures
            mtl.rcParams['toolbar'] = 'None'

            plot_histogram(r_values, 'red channel', 'r')

            plt.figure()
            plot_histogram(g_values, 'green channel', 'g')

            plt.figure()
            plot_histogram(b_values, 'blue channel', 'b')

            plt.show()


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
