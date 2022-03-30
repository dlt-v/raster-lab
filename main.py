import tkinter as tk
from tkinter import filedialog
from typing import Dict, List
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy.ndimage


def terminate_all():
    """
    When you close the root element, destroy all the matplotlib figures as well and close the program.
    """
    plt.close('all')
    root.destroy()


mpl.rcParams['toolbar'] = 'None'
focused_file: Dict[str, str] = {
    "path": "",
    "mode": ""
}
plot_profile_data: Dict[str, List[int]] = {
    "start": [-1, -1],
    "end": [-1, -1]
}


def import_image():
    """
    Asks for the image in file explorer and then imports it to the program, creating a dedicated widget for it.
    """
    extensions = [('formats', ['.jpg', '.png', '.bmp', '.jpeg'])]
    file_path = filedialog.askopenfilename(filetypes=extensions)
    if not file_path:
        return
    opened_image = Image.open(file_path)
    new_img = ImageTk.PhotoImage(opened_image)

    new_window = tk.Toplevel(
        root, width=opened_image.width, height=opened_image.height)
    # new_window.iconphoto(False, icon)
    new_window.title(f"RasterLab: {file_path}")
    new_window.resizable(False, False)

    def on_focus(event):
        """
        Switches the focused_file data to the current image in order for other functions to operate on them. Resets the plot profile data since it's another image.
        """
        global focused_file
        global plot_profile_data

        # reset plot profile data for new image
        plot_profile_data["start"] = [-1, -1]
        plot_profile_data["end"] = [-1, -1]
        plot_profile_button["state"] = "disabled"

        focused_file["path"] = file_path
        focused_file["mode"] = opened_image.mode
        # print(f"Focused file changed to: {focused_file['path']}...")
        # enable buttons
        if focused_file["mode"] == 'L':
            histogram_array_button["state"] = "normal"
        else:
            plot_profile_button["state"] = "disabled"
            histogram_array_button["state"] = "disabled"
        histogram_button["state"] = "normal"

    def on_scroll(event):
        """
        Depending on the scroll direction it resizes the image up and down, scaling the entire widget/frame with it.
        """
        # get current widget height and width, account for borders (-4)
        cur_height = new_window.winfo_height() - 4
        cur_width = new_window.winfo_width() - 4
        if event.delta == 120:
            new_width = int(cur_width * 1.05)
            new_height = int(cur_height * 1.05)
        elif event.delta == -120:
            new_width = int(cur_width * 0.95)
            new_height = int(cur_height * 0.95)
        else:
            return
        # destroy the current image
        for widget in new_window.winfo_children():
            widget.destroy()
        # resize the actual image
        resized_image = Image.open(file_path).resize((new_width, new_height))
        new_img = ImageTk.PhotoImage(resized_image)
        new_window["height"] = new_height
        new_window["width"] = new_width
        # render image in the frame of the widget
        image = tk.Label(new_window, image=new_img)
        # create a reference for the file
        image.image = new_img  # type: ignore
        image.pack()

    def on_click(event) -> None:
        """
            Store plot profile endpoints in global variable.
        """
        global plot_profile_data
        global focused_file
        if focused_file["mode"] != "L":
            return

        if plot_profile_data["start"] == [-1, -1]:
            plot_profile_data["start"] = [event.x, event.y]

        elif plot_profile_data["end"] == [-1, -1]:
            plot_profile_data["end"] = [event.x, event.y]

            plot_profile_button["state"] = "normal"
        else:
            plot_profile_data["start"] = [-1, -1]
            plot_profile_data["end"] = [-1, -1]
            plot_profile_button["state"] = "disabled"

    # bind certain events to specific functions
    new_window.bind("<FocusIn>", on_focus)
    new_window.bind("<MouseWheel>", on_scroll)
    new_window.bind("<Button-1>", on_click)

    image = tk.Label(new_window, image=new_img)
    # it has to be a reference, otherwise the image doesn't load!
    image.image = new_img  # type: ignore
    image.pack()


def sort_histogram_data(data: Dict[str, int]) -> Dict[str, int]:
    """
    Given the probably not full, unsorted dictionary of values, return a sorted dictionary with "blank" zeroes if value doesn't appear.
    """
    sorted_data: Dict[str, int] = {}
    for i in range(256):
        key = str(i)
        if key in data.keys():
            sorted_data[key] = data[key]
        else:
            sorted_data[key] = 0
    return sorted_data


def plot_histogram(data: Dict[str, int], label: str = "", color: str = "gray") -> None:
    """
        Displays histogram for one segment of data.
    """
    # data doesn't have to be passed sorted so we have to sort it
    sorted_data = sort_histogram_data(data)
    plt.bar(list(sorted_data.keys()),
            list(sorted_data.values()), color=color, width=1)
    # hide tick information on the sides - prevents excessive during resize
    plt.xticks([])
    plt.yticks([])
    plt.title(label)


def generate_histogram_table(data: Dict[str, int]) -> None:
    """
    Creates a new widget with histogram data in form of a copyable text.
    """
    sorted_data = sort_histogram_data(data)
    new_window = tk.Toplevel(root)
    # new_window.iconphoto(False, icon)
    new_window.resizable(False, False)
    # sheet = tksheet.Sheet(new_window)
    # sheet.grid()
    # sheet.set_sheet_data([f"{cj}" for cj in sorted_data.values()])
    t = tk.Text(new_window, height=256, width=10)
    for i in sorted_data.keys():
        t.insert(tk.END, f"{i}: {sorted_data[i]}\n")
    t.pack()


def compose_histogram(mode: str):
    """
    Collects data about the image to render later in a histogram. Some aspects of the program are available depending of the image mode (greyscale, RGB, RGBA.)
    """
    if focused_file == "":
        return
    new_image = Image.open(focused_file["path"])
    pixel_list = list(new_image.getdata())
    match (new_image.mode):
        # L for greyscale images, RGB for color images (duh)
        case 'L':
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

            if mode == 'plot':
                plot_histogram(color_values, 'luma')
                plt.show()
            elif mode == 'array':
                generate_histogram_table(color_values)

        case 'RGB' | 'RGBA':
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

            if mode == 'plot':
                plot_histogram(r_values, 'red channel', 'r')

                plt.figure()
                plot_histogram(g_values, 'green channel', 'g')

                plt.figure()
                plot_histogram(b_values, 'blue channel', 'b')

                plt.show()


def plot_profile() -> None:

    global plot_profile_data, focused_file
    x0, y0 = plot_profile_data["start"][0], plot_profile_data["start"][1]
    x1, y1 = plot_profile_data["end"][0], plot_profile_data["end"][1]
    x = np.linspace(
        x0, x1, 100)
    y = np.linspace(
        y0, y1, 100)
    z = Image.open(focused_file["path"])
    zi = scipy.ndimage.map_coordinates(z, (y, x))

    fig, axes = plt.subplots(nrows=2)
    axes[0].imshow(z)  # type: ignore
    axes[0].plot([x0, x1], [y0, y1], 'ro-')  # type: ignore
    axes[0].axis('image')  # type: ignore

    axes[1].plot(zi)  # type: ignore

    plt.show()


# define main menu
root = tk.Tk()
# root.geometry("220x50")
root.title("RasterLab")
# icon = tk.PhotoImage(file='icon.png')
# root.iconphoto(False, icon)
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", terminate_all)


def show_file_menu():
    """
    Render FILE menu with buttons to import and save an image.
    """
    new_window = tk.Toplevel(root)
    new_window.title(f"FILE")
    new_window.resizable(False, False)

    import_button = tk.Button(new_window,
                              text="import image",
                              pady=5,
                              padx=10, command=import_image,
                              font=("consolas", 12)
                              )
    import_button.grid(column=1, row=1, padx=5, pady=5)

    save_button = tk.Button(new_window,
                            text="save image",
                            pady=5,
                            padx=10, command=lambda: print('save'),
                            font=("consolas", 12)
                            )
    save_button.grid(column=2, row=1, padx=5, pady=5)


def show_analyze_menu():
    """
    Render ANALYZE menu with buttons for plotting profile and creating histograms.
    """
    pass


file_button = tk.Button(root,
                        text="FILE",
                        pady=5,
                        padx=10, command=show_file_menu,
                        font=("consolas", 12)
                        )
file_button.grid(column=1, row=1, padx=5, pady=5)

analysis_button = tk.Button(root,
                            text="ANALYZE",
                            pady=5,
                            padx=10, command=show_analyze_menu,
                            font=("consolas", 12)
                            )
analysis_button.grid(column=2, row=1, padx=5, pady=5)

histogram_button = tk.Button(root,
                             text="hist plot",
                             pady=5,
                             padx=10, command=lambda: compose_histogram('plot'),
                             font=("consolas", 12)

                             )
histogram_button.grid(column=2, row=1, padx=5, pady=5)
histogram_array_button = tk.Button(root,
                                   text="hist array",
                                   pady=5,
                                   padx=10, command=lambda: compose_histogram('array'),
                                   font=("consolas", 12)

                                   )
histogram_array_button.grid(column=3, row=1, padx=5, pady=5)
plot_profile_button = tk.Button(root,
                                text="plot profile",
                                pady=5,
                                padx=10, command=plot_profile,
                                font=("consolas", 12)

                                )
plot_profile_button.grid(column=4, row=1, padx=5, pady=5)
# variable = tk.StringVar(root)
# variable.set("one")

# w = tk.OptionMenu(root, variable, "one", "two", "three")
# w.grid(column=4, row=2, padx=5, pady=5)

# disable buttons at the start since there's no data to operate on
histogram_array_button["state"] = "disabled"
histogram_button["state"] = "disabled"
plot_profile_button["state"] = "disabled"


root.mainloop()
