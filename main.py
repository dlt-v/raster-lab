from ast import Pass
from email.policy import default
import tkinter as tk
from tkinter import filedialog
from typing import Any, Dict, List, Tuple
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy.ndimage
import cv2 as cv

from create_button import create_button


def terminate_all():
    """
    When you close the root element, destroy all the matplotlib figures as well and close the program.
    """
    plt.close('all')
    root.destroy()


mpl.rcParams['toolbar'] = 'None'
focused_file: Dict[str, Any] = {
    "path": "",
    "mode": "",
    "image": ""
}
plot_profile_data: Dict[str, List[int]] = {
    "start": [-1, -1],
    "end": [-1, -1]
}


def add_event_listeners(window, image):

    def on_focus(event):
        global focused_file, plot_profile_data
        focused_file["path"] = ''
        focused_file["mode"] = image.mode
        focused_file["image"] = image

    window.bind("<FocusIn>", on_focus)


def import_image(root_window: tk.Toplevel):
    """
    Asks for the image in file explorer and then imports it to the program, creating a dedicated widget for it.
    """
    root_window.destroy()
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
        global focused_file, plot_profile_data, save_button
        focused_file["path"] = file_path
        focused_file["mode"] = opened_image.mode
        focused_file["image"] = opened_image
        # reset plot profile data for new image
        try:
            plot_profile_data["start"] = [-1, -1]
            plot_profile_data["end"] = [-1, -1]
            plot_profile_button["state"] = "disabled"

            # print(f"Focused file changed to: {focused_file['path']}...")
            # enable buttons
            if focused_file["mode"] == 'L':
                histogram_array_button["state"] = "normal"
            else:
                plot_profile_button["state"] = "disabled"
                histogram_array_button["state"] = "disabled"
            histogram_button["state"] = "normal"
        except:
            print("Couldn't change state of some buttons.")

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
        global plot_profile_button
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
    if focused_file["image"]:
        new_image = focused_file["image"]
    elif focused_file["path"]:

        new_image = Image.open(focused_file["path"])
    elif focused_file == "":
        return
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


def negate_image(window_to_close: tk.Toplevel) -> None:
    window_to_close.destroy()
    if focused_file["image"]:
        new_image = focused_file["image"]
    elif focused_file["path"]:

        new_image = Image.open(focused_file["path"])
    elif focused_file == "":
        return
    negated_image = ''

    if new_image.mode == 'L':

        pixel_list: List[int] = list(new_image.getdata())
        negated_pixel_list: List[int] = []

        for pixel in pixel_list:
            negated_pixel_list.append(abs(pixel - 255))

        negated_image = Image.new(new_image.mode, new_image.size)
        negated_image.putdata(negated_pixel_list)
    elif new_image.mode == 'RGB' or new_image.mode == 'RGBA':

        pixel_rgb_list: List[List[int]] = list(new_image.getdata())
        negated_pixel_rgb_list: List[Tuple[int, int, int]] = []

        for pixel in pixel_rgb_list:
            new_pixel = (abs(pixel[0] - 255),
                         abs(pixel[1] - 255), abs(pixel[2] - 255))
            negated_pixel_rgb_list.append(new_pixel)

        negated_image = Image.new(new_image.mode, new_image.size)
        negated_image.putdata(negated_pixel_rgb_list)  # type: ignore

    new_image = negated_image

    negated_image = ImageTk.PhotoImage(negated_image)

    new_window = tk.Toplevel(
        root, width=new_image.width, height=new_image.height)
    # new_window.iconphoto(False, icon)
    new_window.title(f"RasterLab: {focused_file['path']}")
    new_window.resizable(False, False)
    image = tk.Label(new_window, image=negated_image)
    image.image = negated_image  # type: ignore

    add_event_listeners(new_window, new_image)
    image.pack()


def threshold_image(window_to_close: tk.Toplevel, value: str, isSimple: bool) -> None:
    window_to_close.destroy()
    if not value:
        value = 2
    try:
        value = int(value)
    except:
        return

    if focused_file["image"]:
        new_image = focused_file["image"]
    elif focused_file["path"]:

        new_image = Image.open(focused_file["path"])
    elif focused_file == "":
        return

    processed_image = ''

    if new_image.mode != 'L':
        return

    pixel_list = list(new_image.getdata())
    processed_pixel_list: List[int] = []

    goal_table: List[int] = []

    for i in range(value):
        for j in range(int(255/value)):
            goal_table.append(int(255/value * (i)))

    for pixel in pixel_list:
        if isSimple:
            if pixel < (value):
                processed_pixel_list.append(0)
            else:
                processed_pixel_list.append(255)
        else:
            processed_pixel_list.append(goal_table[pixel])

    print(goal_table)

    processed_image = Image.new(new_image.mode, new_image.size)
    processed_image.putdata(processed_pixel_list)
    new_image = processed_image
    processed_image = ImageTk.PhotoImage(processed_image)

    new_window = tk.Toplevel(
        root, width=new_image.width, height=new_image.height)
    new_window.title(f"RasterLab: {focused_file['path']}")
    new_window.resizable(False, False)
    image = tk.Label(new_window, image=processed_image)
    image.image = processed_image  # type: ignore
    add_event_listeners(new_window, new_image)
    image.pack()


def posterize_image(window_to_close: tk.Toplevel, value: str) -> None:
    window_to_close.destroy()
    try:
        value = int(value)
    except:
        return

    if focused_file["image"]:
        new_image = focused_file["image"]
    elif focused_file["path"]:

        new_image = Image.open(focused_file["path"])
    elif focused_file == "":
        return

    processed_image = ''

    goal_table: List[int] = []
    for i in range(value):
        for j in range(int(256/value)):
            goal_table.append(int(256/value * (i)))

    if new_image.mode == 'RGB' or new_image.mode == 'RGBA':

        pixel_rgb_list: List[List[int]] = list(new_image.getdata())
        negated_pixel_rgb_list: List[Tuple[int, int, int]] = []

        for pixel in pixel_rgb_list:
            new_pixel = (goal_table[pixel[0]],
                         goal_table[pixel[1]],
                         goal_table[pixel[2]]
                         )
            negated_pixel_rgb_list.append(new_pixel)

        negated_image = Image.new(new_image.mode, new_image.size)
        negated_image.putdata(negated_pixel_rgb_list)  # type: ignore

        new_image = negated_image
        negated_image = ImageTk.PhotoImage(negated_image)
    new_window = tk.Toplevel(
        root, width=new_image.width, height=new_image.height)
    # new_window.iconphoto(False, icon)
    new_window.title(f"RasterLab: {focused_file['path']}")
    new_window.resizable(False, False)
    image = tk.Label(new_window, image=negated_image)
    image.image = negated_image  # type: ignore
    add_event_listeners(new_window, new_image)

    image.pack()

    return


def generate_lut(pixel_list: List[int]):
    lut = {}
    for pixel in pixel_list:
        if pixel in lut:
            lut[pixel] += 1
        else:
            lut[pixel] = 0
    for i in range(256):
        if i not in lut:
            lut[i] = 0
    return lut


def stretch_histogram(window_to_close: tk.Toplevel, p1, p2, q3, q4) -> None:
    window_to_close.destroy()
    if focused_file["image"]:
        new_image = focused_file["image"]
    elif focused_file["path"]:

        new_image = Image.open(focused_file["path"])
    elif focused_file == "":
        return
    processed_image = ''

    if new_image.mode != 'L':
        return

    pixel_list = list(new_image.getdata())
    processed_pixel_list: List[int] = []

    lut_table = generate_lut(pixel_list)
    end: int = 0
    start: int = 0

    if p1 and p2 and q3 and q4:
        start = int(p1)
        end = int(p2)
        q3 = int(q3)
        q4 = int(q4)
    else:
        q3 = 0
        q4 = 255
        for i in range(255):
            if lut_table[i] != 0:
                end = i

        for i in range(255, 0, -1):
            try:
                if lut_table[i] != 0:
                    start = i
            except:
                print('elo')
    for pixel in pixel_list:

        if pixel < q3:
            processed_pixel_list.append(q3)
        elif pixel > q4:
            processed_pixel_list.append(q4)
        else:
            processed_pixel_list.append(
                int(((pixel - start) * q4) / (end - start))
            )
        # print(pixel, ':', int(((pixel - start) * 255) / (end - start)))
    print(len(processed_pixel_list))
    print(max(processed_pixel_list), min(processed_pixel_list))
    processed_image = Image.new(new_image.mode, new_image.size)
    processed_image.putdata(processed_pixel_list)
    new_image = processed_image
    processed_image = ImageTk.PhotoImage(processed_image)

    new_window = tk.Toplevel(
        root, width=new_image.width, height=new_image.height)
    new_window.title(f"RasterLab: {focused_file['path']}")
    new_window.resizable(False, False)
    image = tk.Label(new_window, image=processed_image)
    image.image = processed_image  # type: ignore
    add_event_listeners(new_window, new_image)
    image.pack()


def save_image(window_to_close: tk.Toplevel, new_file_name: str) -> None:
    window_to_close.destroy()
    focused_file["image"].save(new_file_name)


# define main menu
root = tk.Tk()
# root.geometry("220x50")
root.title("RasterLab")
# icon = tk.PhotoImage(file='icon.png')
# root.iconphoto(False, icon)
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", terminate_all)

save_button = ''


def show_file_menu():
    """
    Render FILE menu with buttons to import and save an image.
    """
    global save_button
    new_window = tk.Toplevel(root)
    new_window.title(f"FILE")
    new_window.resizable(False, False)

    import_button = create_button(
        new_window, "import image", lambda: import_image(new_window))
    save_button = create_button(
        new_window, "save image", lambda: save_image_menu(new_window))
    import_button.grid(column=1, row=1, padx=5, pady=5)
    save_button.grid(column=2, row=1, padx=5, pady=5)


def save_image_menu(window_to_destroy: tk.Toplevel):
    window_to_destroy.destroy()

    new_window = tk.Toplevel(root)
    new_window.title(f"SAVE FILE")
    new_window.resizable(False, False)
    tk.Label(new_window, text="Name: ", font=("Arial", 12)).grid(
        column=1, row=1, padx=10, pady=10)
    e1 = tk.Entry(new_window, font=("Arial", 12))
    e1.grid(
        column=2, row=1, padx=10, pady=10)

    create_button(
        new_window, "save", lambda: save_image(new_window, e1.get())).grid(column=2, row=2, padx=5, pady=5)


def show_analyze_menu():
    """
    Render ANALYZE menu with buttons for plotting profile and creating histograms.
    """
    new_window = tk.Toplevel(root)
    new_window.title(f"FILE")
    new_window.resizable(False, False)
    global histogram_button
    histogram_button = create_button(
        new_window, "hist plot", lambda: compose_histogram('plot'))
    global histogram_array_button
    histogram_array_button = create_button(
        new_window, "hist array", lambda: compose_histogram('array'))
    global plot_profile_button
    plot_profile_button = create_button(
        new_window, "plot profile", plot_profile)
    histogram_button.grid(column=2, row=1, padx=5, pady=5)
    histogram_array_button.grid(column=3, row=1, padx=5, pady=5)
    plot_profile_button.grid(column=4, row=1, padx=5, pady=5)

    # disable buttons at the start since there's no data to operate on
    histogram_array_button["state"] = "disabled"
    histogram_button["state"] = "disabled"
    plot_profile_button["state"] = "disabled"


def show_process_menu():
    new_window = tk.Toplevel(root)
    new_window.title(f"PROCESS")
    new_window.resizable(False, False)

    negation_button = create_button(
        new_window, "negation", lambda: negate_image(new_window))
    treshhold_button = create_button(
        new_window, "threshold", lambda: show_threshold_menu(new_window))
    posterize_button = create_button(
        new_window, "posterize", lambda: show_posterize_menu(new_window))
    stretch_button = create_button(
        new_window, "stretch", lambda: show_stretch_menu(new_window))
    negation_button.grid(column=1, row=1, padx=5, pady=5)
    treshhold_button.grid(column=1, row=2, padx=5, pady=5)
    posterize_button.grid(column=1, row=3, padx=5, pady=5)
    stretch_button.grid(column=1, row=4, padx=5, pady=5)


def show_threshold_menu(window_to_destroy):
    window_to_destroy.destroy()
    new_window = tk.Toplevel(root)
    new_window.title(f"THRESHOLD")
    new_window.resizable(False, False)

    tk.Label(new_window, text="Value: ", font=("Arial", 12)).grid(
        column=1, row=1, padx=10, pady=10)
    e1 = tk.Entry(new_window, font=("Arial", 12))
    e1.grid(
        column=2, row=1, padx=10, pady=10)

    create_button(
        new_window, "multilevel", lambda: threshold_image(new_window, e1.get(), False)).grid(column=2, row=2, padx=5, pady=5)
    create_button(
        new_window, "simple", lambda: threshold_image(new_window, e1.get(), True)).grid(column=1, row=2, padx=5, pady=5)


def show_stretch_menu(window_to_destroy):
    window_to_destroy.destroy()
    new_window = tk.Toplevel(root)
    new_window.title(f"STRETCH")
    new_window.resizable(False, False)

    tk.Label(new_window, text="p1: ", font=("Arial", 12)).grid(
        column=1, row=1, padx=10, pady=10)
    p1 = tk.Entry(new_window, font=("Arial", 12))
    p1.grid(
        column=2, row=1, padx=10, pady=10)
    tk.Label(new_window, text="p2: ", font=("Arial", 12)).grid(
        column=1, row=2, padx=10, pady=10)
    p2 = tk.Entry(new_window, font=("Arial", 12))
    p2.grid(
        column=2, row=2, padx=10, pady=10)

    tk.Label(new_window, text="q3: ", font=("Arial", 12)).grid(
        column=1, row=3, padx=10, pady=10)
    q3 = tk.Entry(new_window, font=("Arial", 12))
    q3.grid(
        column=2, row=3, padx=10, pady=10)
    tk.Label(new_window, text="q4: ", font=("Arial", 12)).grid(
        column=1, row=4, padx=10, pady=10)
    q4 = tk.Entry(new_window, font=("Arial", 12))
    q4.grid(
        column=2, row=4, padx=10, pady=10)

    create_button(
        new_window, "stretch", lambda: stretch_histogram(new_window, p1.get(), p2.get(), q3.get(), q4.get())).grid(column=2, row=5, padx=5, pady=5)


def show_posterize_menu(window_to_destroy):
    window_to_destroy.destroy()
    new_window = tk.Toplevel(root)
    new_window.title(f"POSTERIZE")
    new_window.resizable(False, False)

    tk.Label(new_window, text="Bins: ", font=("Arial", 12)).grid(
        column=1, row=1, padx=10, pady=10)
    e1 = tk.Entry(new_window, font=("Arial", 12))
    e1.grid(
        column=2, row=1, padx=10, pady=10)

    create_button(
        new_window, "process", lambda: posterize_image(new_window, e1.get())).grid(column=2, row=2, padx=5, pady=5)


def filter_image(filter_option: int, edge_option: int, a=0, b=0, c=0) -> None:
    if not focused_file['path']:
        return
    img = cv.imread(focused_file['path'])
    title: str = ""
    match edge_option:
        case 0:  # isolated
            img = cv.copyMakeBorder(
                img, 10, 10, 10, 10,
                cv.BORDER_ISOLATED, None, value=0
            )
        case 1:  # reflect
            img = cv.copyMakeBorder(
                img, 10, 10, 10, 10,
                cv.BORDER_REFLECT, None, value=0
            )
        case 2:  # replicate
            img = cv.copyMakeBorder(
                img, 10, 10, 10, 10,
                cv.BORDER_REPLICATE, None, value=0
            )

    match filter_option:
        case 0:
            blur = cv.GaussianBlur(img, (5, 5), 0)
            title = 'Gaussian'
        case 1:
            blur = cv.blur(img, (5, 5))
            title = 'Blur'
        case 2:
            blur = cv.Sobel(img, cv.CV_64F, a, b, c)
            title = 'edge_sobel'
        case 3:
            blur = cv.Laplacian(img, a)
            title = 'edge_laplacian'
        case 4:
            blur = cv.Canny(img, a, b)
            title = 'edge_canny'
        case 5:
            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ])
            blur = cv.filter2D(img, -1, kernel)
            title = 'sharpen_a'
        case 6:
            kernel = np.array([
                [-1, -1, -1],
                [-1, 9, -1],
                [-1, -1, -1]
            ])
            blur = cv.filter2D(img, -1, kernel)
            title = 'sharpen_b'
        case 7:
            kernel = np.array([
                [1, -2, 1],
                [-2, 5, -2],
                [1, -2, 1]
            ])
            blur = cv.filter2D(img, -1, kernel)
            title = 'sharpen_c'
        case 8:
            match a:
                case 0:
                    kernel = np.array([
                        [1, 1, 1],
                        [1, -2, 1],
                        [-1, -1, -1]
                    ])
                case 1:
                    kernel = np.array([
                        [1, 1, -1],
                        [1, -2, -1],
                        [1, 1, -1]
                    ])
                case 2:
                    kernel = np.array([
                        [-1, 1, 1],
                        [-1, -2, 1],
                        [-1, 1, 1]
                    ])
                case 3:
                    kernel = np.array([
                        [-1, -1, -1],
                        [1, -2, 1],
                        [1, 1, 1]
                    ])
                case 4:
                    kernel = np.array([
                        [1, 1, 1],
                        [-1, -2, 1],
                        [-1, -1, 1]
                    ])
                case 5:
                    kernel = np.array([
                        [1, 1, 1],
                        [1, -2, -1],
                        [1, -1, -1]
                    ])
                case 6:
                    kernel = np.array([
                        [1, -1, -1],
                        [1, -2, -1],
                        [1, 1, 1]
                    ])
                case 7:
                    kernel = np.array([
                        [-1, -1, 1],
                        [-1, -2, 1],
                        [1, 1, 1]
                    ])
            title = 'Prewitt'
            blur = cv.filter2D(img,  -1, kernel)
        case 9:
            kernel = a
            title = 'Custom'
            blur = cv.filter2D(img,  -1, kernel)
        case 10:
            title = f'Median {a}x{a}'
            blur = cv.medianBlur(img, a)

    plt.imshow(blur), plt.title(title)
    plt.xticks([]), plt.yticks([])
    plt.show()


def show_filter_menu():
    new_window = tk.Toplevel(root)
    new_window.title(f"FILTER")
    new_window.resizable(False, False)

    button1 = create_button(
        new_window,
        "blur",
        lambda: show_blur_submenu(new_window)
    )
    button2 = create_button(
        new_window,
        "edge detection",
        lambda: show_edge_submenu(new_window)
    )
    button3 = create_button(
        new_window,
        "sharpen",
        lambda: show_sharpen_submenu(new_window)
    )
    button4 = create_button(
        new_window,
        "custom_kernel",
        lambda: show_custom_kernel_submenu(new_window)
    )
    button5 = create_button(
        new_window,
        "median_filter",
        lambda: show_median_submenu(new_window)
    )

    button1.grid(column=1, row=1, padx=5, pady=5)
    button2.grid(column=1, row=2, padx=5, pady=5)
    button3.grid(column=1, row=3, padx=5, pady=5)
    button4.grid(column=1, row=4, padx=5, pady=5)
    button5.grid(column=1, row=5, padx=5, pady=5)

    def show_edge_mode_submenu(window, option: int, a=0, b=0, c=0):
        if option != 9:
            a = int(a)
            b = int(b)
            c = int(c)
        window.destroy()
        new_window = tk.Toplevel(root)
        new_window.title(f"Edge Mode")
        new_window.resizable(False, False)

        button1 = create_button(
            new_window,
            "Isolated",
            lambda: filter_image(option, 0, a, b, c)
        )
        button2 = create_button(
            new_window,
            "Reflect",
            lambda: filter_image(option, 1, a, b, c)
        )
        button3 = create_button(
            new_window,
            "Replicate",
            lambda: filter_image(option, 2, a, b, c)
        )

        button1.grid(column=1, row=2, padx=5, pady=5)
        button2.grid(column=1, row=3, padx=5, pady=5)
        button3.grid(column=1, row=4, padx=5, pady=5)

    def show_blur_submenu(to_destroy):
        to_destroy.destroy()
        new_window = tk.Toplevel(root)
        new_window.title(f"Blur")
        new_window.resizable(False, False)

        button1 = create_button(
            new_window,
            "blur",
            lambda: show_edge_mode_submenu(new_window, 0)
        )
        button2 = create_button(
            new_window,
            "gaussian",
            lambda: show_edge_mode_submenu(new_window, 1)
        )

        button1.grid(column=1, row=1, padx=5, pady=5)
        button2.grid(column=1, row=2, padx=5, pady=5)

    def show_edge_submenu(to_destroy):
        to_destroy.destroy()
        new_window = tk.Toplevel(root)
        new_window.title(f"Edge detection")
        new_window.resizable(False, False)
        a = tk.Entry(new_window, font=("Arial", 12))
        b = tk.Entry(new_window, font=("Arial", 12))
        c = tk.Entry(new_window, font=("Arial", 12))
        a.grid(
            column=1, row=1, padx=10, pady=10)
        b.grid(
            column=2, row=1, padx=10, pady=10)
        c.grid(
            column=3, row=1, padx=10, pady=10)

        tk.Label(new_window, text="Prewitt\n0-N\n1-W\n2-E\n3-S\n4-NE\n5-NW\n6-SW\n7-SE", font=("Arial", 12)).grid(
            column=2, row=2, padx=10, pady=10)

        button1 = create_button(
            new_window,
            "Sobel (a, b, c)",
            lambda: show_edge_mode_submenu(new_window,
                                           2, a.get(), b.get(), c.get())
        )
        button2 = create_button(
            new_window,
            "Laplacian (a)",
            lambda: show_edge_mode_submenu(new_window, 3, a.get())
        )
        button3 = create_button(
            new_window,
            "Canny (a, b)",
            lambda: show_edge_mode_submenu(new_window, 4, a.get(), b.get())
        )
        button4 = create_button(
            new_window,
            "Prewitt (a - kierunek)",
            lambda: show_edge_mode_submenu(new_window, 8, a.get())
        )

        button1.grid(column=1, row=2, padx=5, pady=5)
        button2.grid(column=1, row=3, padx=5, pady=5)
        button3.grid(column=1, row=4, padx=5, pady=5)
        button4.grid(column=1, row=5, padx=5, pady=5)

    def show_sharpen_submenu(to_destroy):
        to_destroy.destroy()
        new_window = tk.Toplevel(root)
        new_window.title(f"Sharpen")
        new_window.resizable(False, False)

        button1 = create_button(
            new_window,
            "Option A",
            lambda: show_edge_mode_submenu(new_window, 5)
        )
        button2 = create_button(
            new_window,
            "Option B",
            lambda: show_edge_mode_submenu(new_window, 6)
        )
        button3 = create_button(
            new_window,
            "Option C",
            lambda: show_edge_mode_submenu(new_window, 7)
        )

        button1.grid(column=1, row=2, padx=5, pady=5)
        button2.grid(column=1, row=3, padx=5, pady=5)
        button3.grid(column=1, row=4, padx=5, pady=5)

    def show_custom_kernel_submenu(to_destroy):
        to_destroy.destroy()
        new_window = tk.Toplevel(root)
        new_window.title(f"Edge detection")
        new_window.resizable(False, False)
        a = tk.Entry(new_window, font=("Arial", 12))
        b = tk.Entry(new_window, font=("Arial", 12))
        c = tk.Entry(new_window, font=("Arial", 12))
        a.grid(
            column=1, row=1, padx=10, pady=10)
        b.grid(
            column=2, row=1, padx=10, pady=10)
        c.grid(
            column=3, row=1, padx=10, pady=10)

        d = tk.Entry(new_window, font=("Arial", 12))
        e = tk.Entry(new_window, font=("Arial", 12))
        f = tk.Entry(new_window, font=("Arial", 12))
        d.grid(
            column=1, row=2, padx=10, pady=10)
        e.grid(
            column=2, row=2, padx=10, pady=10)
        f.grid(
            column=3, row=2, padx=10, pady=10)

        g = tk.Entry(new_window, font=("Arial", 12))
        h = tk.Entry(new_window, font=("Arial", 12))
        i = tk.Entry(new_window, font=("Arial", 12))
        g.grid(
            column=1, row=3, padx=10, pady=10)
        h.grid(
            column=2, row=3, padx=10, pady=10)
        i.grid(
            column=3, row=3, padx=10, pady=10)

        def submit_kernel():
            kernel_sum = int(a.get()) + int(b.get()) + int(c.get()) + int(d.get()) + int(
                e.get()) + int(f.get()) + int(g.get()) + int(h.get()) + int(i.get())
            kernel = np.array(
                [
                    [int(a.get()), int(b.get()), int(c.get())],
                    [int(d.get()), int(e.get()), int(f.get())],
                    [int(g.get()), int(h.get()), int(i.get())]
                ]
            ) / kernel_sum
            show_edge_mode_submenu(new_window, 9, kernel)

        button1 = create_button(
            new_window,
            "Submit",
            lambda: submit_kernel()
        )

        button1.grid(column=1, row=4, padx=5, pady=5)

    def show_median_submenu(to_destroy):
        to_destroy.destroy()
        new_window = tk.Toplevel(root)
        new_window.title(f"Median")
        new_window.resizable(False, False)

        button1 = create_button(
            new_window,
            "3x3",
            lambda: show_edge_mode_submenu(new_window, 10, 3)
        )
        button2 = create_button(
            new_window,
            "5x5",
            lambda: show_edge_mode_submenu(new_window, 10, 5)
        )
        button3 = create_button(
            new_window,
            "7x7",
            lambda: show_edge_mode_submenu(new_window, 10, 7)
        )

        button1.grid(column=1, row=2, padx=5, pady=5)
        button2.grid(column=1, row=3, padx=5, pady=5)
        button3.grid(column=1, row=4, padx=5, pady=5)


file_button = create_button(root, "FILE", show_file_menu)
analysis_button = create_button(root, "ANALYZE", show_analyze_menu)
process_button = create_button(root, "PROCESS", show_process_menu)
filter_button = create_button(root, "FILTER", show_filter_menu)
file_button.grid(column=1, row=1, padx=5, pady=5)
analysis_button.grid(column=2, row=1, padx=5, pady=5)
process_button.grid(column=3, row=1, padx=5, pady=5)
filter_button.grid(column=4, row=1, padx=5, pady=5)


root.mainloop()
