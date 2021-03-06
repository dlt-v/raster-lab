
import tkinter as tk
from tkinter import filedialog
from typing import Any, Dict, List, Tuple
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy.ndimage
from scipy.signal import convolve2d as conv2
import cv2 as cv
import random
import imutils


def terminate_all():
    """
    Destroy all the matplotlib figures as well and close the program.
    """
    plt.close('all')
    root.destroy()


class RasterImage:
    '''
    Holds information about imported image.
    '''

    def __init__(self, path) -> None:
        self.path = path
        self.object = Image.open(self.path)
        self.tk_object = ImageTk.PhotoImage(self.object)

    def get_mode(self) -> str:
        '''
        Returns the color mode of the image.

        "L" - greyscale

        "RGB" | "RGBa" - color | color transparent
        '''
        return self.object.mode()


def create_button(root: tk.Toplevel | tk.Tk, text: str, command) -> tk.Button:
    """
    Given the root element, text and command, the function returns a ready tkinter Button element.
    """
    return tk.Button(root,
                     text=text,
                     pady=5,
                     padx=10, command=command,
                     font=("consolas", 12)
                     )


opened_images_list: List[RasterImage] = []
# disables the toolbar for rendered images
mpl.rcParams['toolbar'] = 'None'
# stores two last actively used images
focused_file: Dict[str, Any] = {
    "path": "",
    "mode": "",
    "image": ""
}
previous_file: Dict[str, Any] = {
    "path": "",
    "mode": "",
    "image": ""
}
# globally store coordinates for plotting function
plot_profile_data: Dict[str, List[int]] = {
    "start": [-1, -1],
    "end": [-1, -1]
}


def add_event_listeners(window, image):
    '''
    Add focus event listeners to image object.
    '''
    def on_focus(event):
        global focused_file, previous_file, plot_profile_data
        previous_file = focused_file
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
    raster_image = RasterImage(file_path)
    opened_images_list.insert(0, raster_image)
    new_window = tk.Toplevel(
        root, width=opened_image.width, height=opened_image.height)
    new_window.title(f"RasterLab: {file_path}")
    new_window.resizable(False, False)

    def on_focus(event):
        """
        Switches the focused_file data to the current image in order for other functions to operate on them. Resets the plot profile data since it's another image.
        """
        global focused_file, previous_file, plot_profile_data, save_button
        previous_file["path"] = focused_file["path"]
        previous_file["mode"] = focused_file["mode"]
        previous_file["image"] = focused_file["image"]
        focused_file["path"] = file_path
        focused_file["mode"] = opened_image.mode
        focused_file["image"] = opened_image
        print(f"Focused image: {focused_file['path']}")
        print(f"Previous image: {previous_file['path']}")
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
            pass

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
    new_window.resizable(False, False)
    t = tk.Text(new_window, height=256, width=20)
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
    match new_image.mode:
        # L for greyscale images, RGB for color images
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
    """
    Using coordinates of plot_profile_data make a line profile connecting two coordinates and display the graph with image.
    """
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
    '''
    Invert color values on given image. Works on RGB(a) and greyscale objects.
    '''
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

        # Convert pixel values to their opposites.
        for pixel in pixel_list:
            negated_pixel_list.append(abs(pixel - 255))

        negated_image = Image.new(new_image.mode, new_image.size)
        negated_image.putdata(negated_pixel_list)
    elif new_image.mode == 'RGB' or new_image.mode == 'RGBA':

        pixel_rgb_list: List[List[int]] = list(new_image.getdata())
        negated_pixel_rgb_list: List[Tuple[int, int, int]] = []

        for pixel in pixel_rgb_list:
            # Convert pixel values to their opposites.
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
    '''
    Perform a threshold operation on an image object.
    value variable depending on the isSimple boolean flag is interpeted as number of bins or an actual threshold.
    '''
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
    '''
    Perform posterization on an image.
    Works only on RGB(a) images.
    '''
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

    goal_table: List[int] = []
    # Define bin values.
    for i in range(value):
        for j in range(int(256/value)):
            goal_table.append(int(256/value * (i)))

    if new_image.mode == 'RGB' or new_image.mode == 'RGBA':
        # TODO: Reused parts of negate image algoritm, didn't change variable names.
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
    new_window.title(f"RasterLab: {focused_file['path']}")
    new_window.resizable(False, False)
    image = tk.Label(new_window, image=negated_image)
    image.image = negated_image  # type: ignore
    add_event_listeners(new_window, new_image)

    image.pack()


def generate_lut(pixel_list: List[int]):
    '''
    Generates LUT table in form of a dictionary.
    '''
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
    '''
    Performs a histogram value stretch.
    Could be given 4 parameters, if not program will default to maximum stretch.
    '''
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
    '''
    Save image to disk.
    '''
    window_to_close.destroy()
    focused_file["image"].save(f"output\{new_file_name}")


# define main menu
root = tk.Tk()
root.title("RasterLab")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", terminate_all)

save_button = ''


def show_file_menu() -> None:
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


def save_image_menu(window_to_destroy: tk.Toplevel) -> None:
    '''
    Renders save image menu.
    '''
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


def find_and_show_contours(fname) -> None:
    '''
    Algorithm that finds and displays marked contours on a given image object.
    '''
    img = cv.imread(fname, cv.IMREAD_GRAYSCALE)
    ret, thresh = cv.threshold(img, 127, 255, 0)
    contours, hierarchy = cv.findContours(
        thresh, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
    img3 = cv.cvtColor(thresh, cv.COLOR_GRAY2RGB)
    for cnt in contours:
        cv.drawContours(img3, [cnt], 0, (random.randrange(
            50, 200, 25), random.randrange(50, 200, 25), random.randrange(50, 200, 25)), 3)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    im_pil = Image.fromarray(img3)

    new_img = ImageTk.PhotoImage(im_pil)

    new_window = tk.Toplevel(
        root, width=im_pil.width, height=im_pil.height)
    new_window.resizable(False, False)
    image = tk.Label(new_window, image=new_img)
    # it has to be a reference, otherwise the image doesn't load
    image.image = new_img  # type: ignore
    image.pack()


def find_objects(window_to_destroy: tk.Toplevel):
    '''
    Performs series of operations to locate and analyse a list of found objects.
    '''
    window_to_destroy.destroy()
    if not focused_file['path']:
        return
    img = cv.imread(focused_file['path'], cv.IMREAD_GRAYSCALE)
    find_and_show_contours(focused_file['path'])
    title: str = ""
    ret, thresh = cv.threshold(img, 127, 255, 0)
    # Save contour data.
    contours, hierarchy = cv.findContours(
        thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    sorted_data = cv.moments(img)
    new_window = tk.Toplevel(root)
    # Render text file with data about found objects.
    new_window.resizable(False, False)
    t = tk.Text(new_window, height=30, width=40)
    cnt = contours[0]
    t.insert(tk.END, f"Found {len(contours)} elements.\n")
    t.insert(tk.END, f"Area: {cv.contourArea(cnt)}.\n")
    t.insert(tk.END, f"Perimiter: {cv.arcLength(cnt,True)}.\n")
    x, y, w, h = cv.boundingRect(cnt)
    aspect_ratio = float(w)/h

    t.insert(tk.END, f"aspect ratio: {aspect_ratio}.\n")
    area = cv.contourArea(cnt)
    x, y, w, h = cv.boundingRect(cnt)
    rect_area = w*h
    extent = float(area)/rect_area
    t.insert(tk.END, f"extent: {extent}.\n")
    area = cv.contourArea(cnt)
    hull = cv.convexHull(cnt)
    hull_area = cv.contourArea(hull)
    solidity = float(area)/hull_area
    t.insert(tk.END, f"solidity: {solidity}.\n")
    area = cv.contourArea(cnt)
    equi_diameter = np.sqrt(4*area/np.pi)
    t.insert(tk.END, f"equivalentDiameter: {equi_diameter}.\n")

    for i in sorted_data.keys():
        t.insert(tk.END, f"{i}: {sorted_data[i]}\n")
    t.pack()


def show_analyze_menu():
    """
    Render ANALYZE menu with buttons for plotting profile and creating histograms.
    """
    new_window = tk.Toplevel(root)
    new_window.title(f"FILE")
    new_window.resizable(False, False)
    # TODO: refactor button rendering if necessary
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
    find_objects_button = create_button(
        new_window,
        "find objects",
        lambda: find_objects(new_window)
    )
    find_objects_button.grid(column=5, row=1, padx=5, pady=5)

    # disable buttons at the start since there's no data to operate on
    histogram_array_button["state"] = "disabled"
    histogram_button["state"] = "disabled"
    plot_profile_button["state"] = "disabled"


def show_process_menu() -> None:
    '''
    Shows process menu with given options.
    '''
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


def show_threshold_menu(window_to_destroy) -> None:
    '''
    Shows threshold menu with given options.
    '''
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


def show_stretch_menu(window_to_destroy) -> None:
    '''
    Shows stretch menu with given options.
    '''
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


def show_posterize_menu(window_to_destroy) -> None:
    '''
    Shows posterize menu with given options.
    '''
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
    '''
    Performs filter operations on selected image object depending on parameters given.
    '''
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
    im_pil = Image.fromarray(blur)

    new_img = ImageTk.PhotoImage(im_pil)
    new_window = tk.Toplevel(
        root, width=im_pil.width, height=im_pil.height)
    # new_window.iconphoto(False, icon)
    new_window.resizable(False, False)
    image = tk.Label(new_window, image=new_img)
    # it has to be a reference, otherwise the image doesn't load!
    image.image = new_img  # type: ignore
    image.pack()


def show_filter_menu():
    '''
    Shows filter menu with given options.
    '''
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
        '''
        Show edge mode submenu
        '''
        # Convert params into integers.
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
        '''
        Renders blur submenu
        '''
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
        '''
        Renders show_edge submenu
        '''
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
        '''
        Display sharpen submenu
        '''
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
        # new_window.geometry("200x200")
        a = tk.Entry(new_window, font=("Arial", 12), width=3)
        b = tk.Entry(new_window, font=("Arial", 12), width=3)
        c = tk.Entry(new_window, font=("Arial", 12), width=3)
        a.grid(
            column=1, row=1, padx=10, pady=10)
        b.grid(
            column=2, row=1, padx=10, pady=10)
        c.grid(
            column=3, row=1, padx=10, pady=10)

        d = tk.Entry(new_window, font=("Arial", 12), width=3)
        e = tk.Entry(new_window, font=("Arial", 12), width=3)
        f = tk.Entry(new_window, font=("Arial", 12), width=3)
        d.grid(
            column=1, row=2, padx=10, pady=10)
        e.grid(
            column=2, row=2, padx=10, pady=10)
        f.grid(
            column=3, row=2, padx=10, pady=10)

        g = tk.Entry(new_window, font=("Arial", 12), width=3)
        h = tk.Entry(new_window, font=("Arial", 12), width=3)
        i = tk.Entry(new_window, font=("Arial", 12), width=3)
        g.grid(
            column=1, row=3, padx=10, pady=10)
        h.grid(
            column=2, row=3, padx=10, pady=10)
        i.grid(
            column=3, row=3, padx=10, pady=10)

        def submit_kernel():
            # String values from inputs has to be converted to integers.
            kernel_sum = int(a.get()) + int(b.get()) + int(c.get()) + int(d.get()) + int(
                e.get()) + int(f.get()) + int(g.get()) + int(h.get()) + int(i.get())
            # Create ready kernel to send.
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

        button1.grid(column=4, row=1, padx=5, pady=5)

    def show_median_submenu(to_destroy):
        '''
        Renders median submenu.
        '''
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


def two_point_operation(window_to_close, option: int, blend_a: float = 1, blend_b: float = 1):
    '''
    Performs a selected series of two point operations on compatible images depending on given parameters.
    '''
    window_to_close.destroy()
    if not focused_file['path'] and not previous_file['path']:
        return
    if blend_b:
        blend_a = float(blend_a)
        blend_b = float(blend_b)
    img1 = cv.imread(focused_file['path'])
    img2 = cv.imread(previous_file['path'])

    match option:
        case 0:  # add
            result_image = cv.add(img1, img2)
            title = 'addition'
        case 1:  # subtract
            result_image = cv.subtract(img1, img2)
            title = 'subtraction'
        case 2:  # blend
            title = 'blend'
            result_image = cv.addWeighted(img1, blend_a, img2, blend_b, 0)
        case 3:  # and
            title = 'and'
            result_image = cv.bitwise_and(img1, img2)
        case 4:  # or
            title = 'or'
            result_image = cv.bitwise_or(img1, img2)
        case 5:  # not
            title = 'not'
            result_image = cv.bitwise_not(img1, img2)
        case 6:  # xor
            title = 'xor'
            result_image = cv.bitwise_xor(img1, img2)

    plt.imshow(result_image), plt.title(title)
    plt.xticks([]), plt.yticks([])
    plt.show()


def show_two_point_menu():
    '''
    Shows two point menu with given options.
    '''
    new_window = tk.Toplevel(root)
    new_window.title(f"Two Point")
    new_window.resizable(False, False)
    a = tk.Entry(new_window, font=("Arial", 12))
    b = tk.Entry(new_window, font=("Arial", 12))
    a.grid(
        column=2, row=2, padx=5, pady=5)
    b.grid(
        column=3, row=2, padx=5, pady=5)

    button1 = create_button(
        new_window,
        "ADD",
        lambda: two_point_operation(new_window, 0)
    )
    button2 = create_button(
        new_window,
        "SUBTRACT",
        lambda: two_point_operation(new_window, 1)
    )
    button3 = create_button(
        new_window,
        "BLEND",
        lambda: two_point_operation(new_window, 2, a.get(), b.get())
    )
    button4 = create_button(
        new_window,
        "AND",
        lambda: two_point_operation(new_window, 3)
    )
    button5 = create_button(
        new_window,
        "OR",
        lambda: two_point_operation(new_window, 4)
    )
    button6 = create_button(
        new_window,
        "NOT",
        lambda: two_point_operation(new_window, 5)
    )
    button7 = create_button(
        new_window,
        "XOR",
        lambda: two_point_operation(new_window, 6)
    )

    button1.grid(column=1, row=1, padx=5, pady=5)
    button2.grid(column=2, row=1, padx=5, pady=5)
    button3.grid(column=1, row=2, padx=5, pady=5)
    button4.grid(column=3, row=1, padx=5, pady=5)
    button5.grid(column=4, row=1, padx=5, pady=5)
    button6.grid(column=5, row=1, padx=5, pady=5)
    button7.grid(column=6, row=1, padx=5, pady=5)


def morph_image(window_to_close, o1, o2, o3, o4):
    '''
    Performs morph operations.
    '''
    window_to_close.destroy()
    o1, o2, o3, o4 = int(o1), int(o2), int(o3), int(o4)
    if not focused_file['path']:
        return
    img = cv.imread(focused_file['path'])
    title: str = ""
    # edge mode
    match o3:
        case 1:  # constant
            edge_mode = cv.BORDER_CONSTANT
        case 2:  # replicate
            edge_mode = cv.BORDER_REPLICATE
        case 3:  # reflect
            edge_mode = cv.BORDER_REFLECT
        case 4:  # reflect101
            edge_mode = cv.BORDER_REFLECT101
        case 5:  # wrap
            edge_mode = cv.BORDER_WRAP
    # generate kernel
    match o2:
        case 1:  # rombus
            # kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
            r = o4
            kernel = np.uint8(np.add.outer(*[np.r_[:r, r: -1: -1]]*2) >= r)
        case 2:  # square
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (o4, o4))
    # morph option
    match o1:
        case 1:  # Erode
            result = cv.erode(
                img,
                kernel,
                iterations=2,
                borderType=edge_mode
            )
            title = 'erosion'
        case 2:  # Dilate
            result = cv.dilate(
                img,
                kernel,
                iterations=2,
                borderType=edge_mode
            )
            title = 'dilution'
        case 3:  # Open
            result = cv.morphologyEx(
                img,
                cv.MORPH_OPEN,
                kernel,
                iterations=2,
                borderType=edge_mode
            )
            title = 'open'
        case 4:  # Close
            result = cv.morphologyEx(
                img,
                cv.MORPH_CLOSE,
                kernel,
                iterations=2,
                borderType=edge_mode
            )
            title = 'close'

    plt.imshow(result), plt.title(title)
    plt.xticks([]), plt.yticks([])
    plt.show()


def show_morph_menu():
    '''
    Shows morph menu with given options.
    '''
    new_window = tk.Toplevel(root)
    new_window.title(f"Morph")
    new_window.resizable(False, False)
    option1 = tk.IntVar()
    check1 = tk.Checkbutton(
        new_window,
        text='Erosion',
        variable=option1,
        onvalue=1,
        offvalue=0,
        padx=5,
        pady=5
    )
    check2 = tk.Checkbutton(
        new_window,
        text='Dilution',
        variable=option1,
        onvalue=2,
        offvalue=0,
        padx=5,
        pady=5
    )
    check3 = tk.Checkbutton(
        new_window,
        text='Open',
        variable=option1,
        onvalue=3,
        offvalue=0,
        padx=5,
        pady=5
    )
    check4 = tk.Checkbutton(
        new_window,
        text='Close',
        variable=option1,
        onvalue=4,
        offvalue=0,
        padx=5,
        pady=5
    )
    check1.grid(column=1, row=1, padx=5, pady=5)
    check2.grid(column=1, row=2, padx=5, pady=5)
    check3.grid(column=1, row=3, padx=5, pady=5)
    check4.grid(column=1, row=4, padx=5, pady=5)
    option2 = tk.IntVar()
    check5 = tk.Checkbutton(
        new_window,
        text='Rombus',
        variable=option2,
        onvalue=1,
        offvalue=0,
        padx=5,
        pady=5
    )
    check6 = tk.Checkbutton(
        new_window,
        text='Square',
        variable=option2,
        onvalue=2,
        offvalue=0,
        padx=5,
        pady=5
    )
    check5.grid(column=2, row=1, padx=5, pady=5)
    check6.grid(column=2, row=2, padx=5, pady=5)

    option3 = tk.IntVar()

    border1 = tk.Checkbutton(
        new_window,
        text='constant',
        variable=option3,
        onvalue=1,
        offvalue=0,
        padx=5,
        pady=5
    )
    border2 = tk.Checkbutton(
        new_window,
        text='replicate',
        variable=option3,
        onvalue=2,
        offvalue=0,
        padx=5,
        pady=5
    )
    border3 = tk.Checkbutton(
        new_window,
        text='reflect',
        variable=option3,
        onvalue=3,
        offvalue=0,
        padx=5,
        pady=5
    )
    border4 = tk.Checkbutton(
        new_window,
        text='reflect_101',
        variable=option3,
        onvalue=4,
        offvalue=0,
        padx=5,
        pady=5
    )
    border5 = tk.Checkbutton(
        new_window,
        text='wrap',
        variable=option3,
        onvalue=5,
        offvalue=0,
        padx=5,
        pady=5
    )
    border1.grid(column=3, row=1, padx=5, pady=5)
    border2.grid(column=3, row=2, padx=5, pady=5)
    border3.grid(column=3, row=3, padx=5, pady=5)
    border4.grid(column=3, row=4, padx=5, pady=5)
    border5.grid(column=3, row=5, padx=5, pady=5)

    option4 = tk.IntVar()
    kernel_size1 = tk.Checkbutton(
        new_window,
        text='3x3',
        variable=option4,
        onvalue=3,
        offvalue=0,
        padx=5,
        pady=5
    )
    kernel_size2 = tk.Checkbutton(
        new_window,
        text='5x5',
        variable=option4,
        onvalue=5,
        offvalue=0,
        padx=5,
        pady=5
    )
    kernel_size1.grid(column=4, row=1, padx=5, pady=5)
    kernel_size2.grid(column=4, row=2, padx=5, pady=5)

    submit_button = create_button(
        new_window,
        "submit",
        lambda: morph_image(
            new_window,
            option1.get(),
            option2.get(),
            option3.get(),
            option4.get()
        )
    )
    submit_button.grid(column=5, row=1, padx=5, pady=5)


def mask_filter_image(window_to_close, o1, o2, o3):
    '''
    Performs filter operations with a mask on selected image object.
    '''
    window_to_close.destroy()
    o1, o2, o3 = int(o1), int(o2), int(o3)
    if not focused_file['path']:
        return
    img = cv.imread(focused_file['path'])
    title: str = "mask_filter"
    match o3:
        case 1:  # constant
            edge_mode = cv.BORDER_CONSTANT
        case 2:  # replicate
            edge_mode = cv.BORDER_REPLICATE
        case 3:  # reflect
            edge_mode = cv.BORDER_REFLECT
        case 4:  # reflect101
            edge_mode = cv.BORDER_REFLECT101
        case 5:  # wrap
            edge_mode = cv.BORDER_WRAP

    smoothen_mask = np.ones((3, 3))
    sharpen_mask = np.array([
        [1, -2, 1],
        [-2, 4, -2],
        [1, -2, 1]
    ])
    conv_mask = conv2(smoothen_mask, sharpen_mask, mode='full')
    match o2:
        case 1:
            chosen_mask = sharpen_mask
        case 2:
            chosen_mask = smoothen_mask

    match o1:  # stages
        case 1:  # one stage
            result = cv.filter2D(
                img,
                cv.CV_64F,
                chosen_mask,
                borderType=edge_mode
            )
        case 2:  # two stage
            result = cv.filter2D(
                img,
                cv.CV_64F,
                smoothen_mask,
                borderType=edge_mode
            )
            result = cv.filter2D(
                result,
                cv.CV_64F,
                sharpen_mask,
                borderType=edge_mode
            )
    plt.imshow(result), plt.title(title)
    plt.xticks([]), plt.yticks([])
    plt.show()


def show_mask_filter_menu():
    '''
    Shows mask filter menu with given options.
    '''
    new_window = tk.Toplevel(root)
    new_window.title(f"Morph")
    new_window.resizable(False, False)
    option1 = tk.IntVar()
    check1 = tk.Checkbutton(
        new_window,
        text='1 stage',
        variable=option1,
        onvalue=1,
        offvalue=0,
        padx=5,
        pady=5
    )
    check2 = tk.Checkbutton(
        new_window,
        text='2 stage',
        variable=option1,
        onvalue=2,
        offvalue=0,
        padx=5,
        pady=5
    )
    check1.grid(column=1, row=1, padx=5, pady=5)
    check2.grid(column=1, row=2, padx=5, pady=5)
    option2 = tk.IntVar()
    check5 = tk.Checkbutton(
        new_window,
        text='sharpen',
        variable=option2,
        onvalue=1,
        offvalue=0,
        padx=5,
        pady=5
    )
    check6 = tk.Checkbutton(
        new_window,
        text='smoothen',
        variable=option2,
        onvalue=2,
        offvalue=0,
        padx=5,
        pady=5
    )
    check5.grid(column=2, row=1, padx=5, pady=5)
    check6.grid(column=2, row=2, padx=5, pady=5)

    option3 = tk.IntVar()

    border1 = tk.Checkbutton(
        new_window,
        text='isolated',
        variable=option3,
        onvalue=1,
        offvalue=0,
        padx=5,
        pady=5
    )
    border2 = tk.Checkbutton(
        new_window,
        text='replicate',
        variable=option3,
        onvalue=2,
        offvalue=0,
        padx=5,
        pady=5
    )
    border3 = tk.Checkbutton(
        new_window,
        text='reflect',
        variable=option3,
        onvalue=3,
        offvalue=0,
        padx=5,
        pady=5
    )
    border1.grid(column=3, row=1, padx=5, pady=5)
    border2.grid(column=3, row=2, padx=5, pady=5)
    border3.grid(column=3, row=3, padx=5, pady=5)

    submit_button = create_button(
        new_window,
        "submit",
        lambda: mask_filter_image(
            new_window,
            option1.get(),
            option2.get(),
            option3.get(),
        )
    )
    submit_button.grid(column=4, row=1, padx=5, pady=5)


def skeletonize_image(to_destroy, o1):
    '''
    Performs skeletonization operation on selected image object.
    '''
    to_destroy.destroy()
    o1 = int(o1)
    if not focused_file['path']:
        return
    img = cv.imread(focused_file['path'], 0)

    title = "skeletonize"

    def skeletonize(img):
        """ OpenCV function to return a skeletonized version of img, a Mat object"""

        img = img.copy()  # don't clobber original
        skel = img.copy()

        skel[:, :] = 0
        kernel = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))

        while True:
            eroded = cv.morphologyEx(img, cv.MORPH_ERODE, kernel)
            temp = cv.morphologyEx(eroded, cv.MORPH_DILATE, kernel)
            temp = cv.subtract(img, temp)
            skel = cv.bitwise_or(skel, temp)
            img[:, :] = eroded[:, :]
            if cv.countNonZero(img) == 0:
                break

        return skel

    result = skeletonize(img)
    plt.imshow(result), plt.title(title)
    plt.xticks([]), plt.yticks([])
    plt.show()


def show_skeletonize_menu():
    '''
    Shows skeletonize menu with given options.
    '''
    new_window = tk.Toplevel(root)
    new_window.title(f"Skeletonize")
    new_window.resizable(False, False)
    option3 = tk.IntVar()

    border1 = tk.Checkbutton(
        new_window,
        text='isolated',
        variable=option3,
        onvalue=1,
        offvalue=0,
        padx=5,
        pady=5
    )
    border2 = tk.Checkbutton(
        new_window,
        text='replicate',
        variable=option3,
        onvalue=2,
        offvalue=0,
        padx=5,
        pady=5
    )
    border3 = tk.Checkbutton(
        new_window,
        text='reflect',
        variable=option3,
        onvalue=3,
        offvalue=0,
        padx=5,
        pady=5
    )
    border1.grid(column=1, row=1, padx=5, pady=5)
    border2.grid(column=1, row=2, padx=5, pady=5)
    border3.grid(column=1, row=3, padx=5, pady=5)

    submit_button = create_button(
        new_window,
        "submit",
        lambda: skeletonize_image(
            new_window,
            option3.get(),
        )
    )
    submit_button.grid(column=2, row=1, padx=5, pady=5)


def thershold_image(to_destroy, o1=0, o2=0):
    '''
    Performs threshold operations on selected image object.
    '''
    to_destroy.destroy()
    # try converting string values into integers
    try:
        o1, o2 = int(o1), int(o2)
    except:
        o1 = int(o1)
    if not focused_file['path']:
        return
    img = cv.imread(focused_file['path'], cv.IMREAD_GRAYSCALE)
    match o1:
        case 1:
            title = "normal thersholding"
            ret, result = cv.threshold(img, o2, 255, cv.THRESH_BINARY)
        case 2:
            title = "adaptive thersholding"

            result = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C,
                                          cv.THRESH_BINARY, 11, 2)
        case 3:
            title = "otsu thersholding"
            blur = cv.GaussianBlur(img, (5, 5), 0)

            ret3, result = cv.threshold(
                blur, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
        case 4:

            img = cv.imread(focused_file['path'], cv.IMREAD_COLOR)
            title = "watershedding"
            # Convert to greyscale.
            img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            ret2, thresh = cv.threshold(
                img_gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
            kernel = np.ones((3, 3), np.uint8)
            # Reduce the noise pollution.
            opening = cv.morphologyEx(
                thresh, cv.MORPH_OPEN, kernel, iterations=1)
            sure_bg = cv.dilate(opening, kernel, iterations=1)
            dist_transform = cv.distanceTransform(opening, cv.DIST_L2, 5)
            # Find clean objects by distance transforming.
            ret, sure_fg = cv.threshold(
                dist_transform, 0.5*dist_transform.max(), 255, 0)
            sure_fg = np.uint8(sure_fg)
            # Find uncertain objects.
            unknown = cv.subtract(sure_bg, sure_fg)
            # Mark found objects.
            ret, markers = cv.connectedComponents(sure_fg)
            markers = markers+1
            markers[unknown == 255] = 0

            markers2 = cv.watershed(img, markers)
            # Display image with color markers.
            img_gray[markers2 == -1] = 255
            img[markers2 == -1] = [255, 0, 0]
            result = cv.applyColorMap(np.uint8(markers2*10), cv.COLORMAP_JET)

    plt.imshow(result), plt.title(title)
    plt.xticks([]), plt.yticks([])
    plt.show()


def show_segmentation_menu():
    '''
    Shows segmenation menu with given options.
    '''
    new_window = tk.Toplevel(root)
    new_window.title(f"segmentation")
    new_window.resizable(False, False)

    a = tk.Entry(new_window, font=("Arial", 12), width=3)
    a.grid(
        column=2, row=1, padx=5, pady=5)

    btn1 = create_button(
        new_window,
        "normal thresholding",
        lambda: thershold_image(
            new_window,
            1,
            a.get(),
        )
    )
    btn2 = create_button(
        new_window,
        "adaptive thresholding",
        lambda: thershold_image(
            new_window,
            2,
            a.get(),
        )
    )
    btn3 = create_button(
        new_window,
        "otsu thersholding",
        lambda: thershold_image(
            new_window,
            3,
            a.get(),
        )
    )
    btn4 = create_button(
        new_window,
        "watershedding",
        lambda: thershold_image(
            new_window,
            4,
            a.get(),
        )
    )
    btn1.grid(column=1, row=1, padx=5, pady=5)
    btn2.grid(column=1, row=2, padx=5, pady=5)
    btn3.grid(column=1, row=3, padx=5, pady=5)
    btn4.grid(column=1, row=4, padx=5, pady=5)


def render_pil_image(image, title: str) -> Image.Image:
    '''Convert openCV image into PIL image, return and display it.'''
    image_array = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    new_image = Image.fromarray(image_array)
    tk_image = ImageTk.PhotoImage(new_image)

    new_window = tk.Toplevel(
        root,
        width=new_image.width,
        height=new_image.height
    )
    new_window.title(title)
    new_window.resizable(False, False)

    image = tk.Label(new_window, image=tk_image)
    image.image = tk_image  # type: ignore
    add_event_listeners(new_window, new_image)
    image.pack()
    return new_image


def stitch(to_destroy: tk.Toplevel, raw: bool):
    '''Stitch all opened images.'''

    to_destroy.destroy()
    images = []

    for image_object in opened_images_list:
        img = cv.imread(image_object.path)
        images.append(img)

    stitcher = cv.Stitcher_create()

    error, stitched_img = stitcher.stitch(images)

    if not error:
        if not raw:
            # add black padding to the image
            stitched_img = cv.copyMakeBorder(
                stitched_img, 10, 10, 10, 10,
                cv.BORDER_CONSTANT, (0, 0, 0)
            )
            gray = cv.cvtColor(stitched_img, cv.COLOR_BGR2GRAY)
            # isolate contours as black pixels
            thresh_img = cv.threshold(gray, 0, 255, cv.THRESH_BINARY)[1]

            contours = cv.findContours(
                thresh_img.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

            contours = imutils.grab_contours(contours)
            # from found contours locate area of interest
            areaOI = max(contours, key=cv.contourArea)

            mask = np.zeros(thresh_img.shape, dtype="uint8")
            # create area to be cut from the original image
            x, y, w, h = cv.boundingRect(areaOI)
            cv.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

            minRectangle = mask.copy()
            sub = mask.copy()
            # find the minimum area with the image
            while cv.countNonZero(sub) > 0:
                minRectangle = cv.erode(minRectangle, None)
                sub = cv.subtract(minRectangle, thresh_img)

            contours = cv.findContours(
                minRectangle.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

            contours = imutils.grab_contours(contours)
            areaOI = max(contours, key=cv.contourArea)

            x, y, w, h = cv.boundingRect(areaOI)
            # from the original stitched image "cut" only the rectangle
            stitched_img = stitched_img[y:y + h, x:x + w]

        render_pil_image(stitched_img, "Stitch result")

    else:
        new_window = tk.Toplevel(root)
        new_window.title("Error")
        new_window.resizable(False, False)
        tk.Label(new_window, text="Sorry, something went wrong.", font=("Arial", 12)).grid(
            column=0, row=0, padx=10, pady=10)
        btn1 = create_button(
            new_window,
            "OK",
            lambda: new_window.destroy()
        )
        btn1.grid(column=1, row=2, padx=5, pady=5)


def show_stitch_menu():
    '''
    Shows segmenation menu with given options.
    '''

    new_window = tk.Toplevel(root)
    new_window.title(f"stich")
    new_window.resizable(False, False)
    tk.Label(new_window, text=f"Images in memory: {len(opened_images_list)}", font=("Arial", 12)).grid(
        column=1, row=1, padx=10, pady=10)

    btn1 = create_button(
        new_window,
        "raw stitch",
        lambda: stitch(
            new_window,
            True
        )
    )
    btn2 = create_button(
        new_window,
        "cut stitch",
        lambda: stitch(
            new_window,
            False
        )
    )
    btn1.grid(column=1, row=2, padx=5, pady=5)
    btn2.grid(column=2, row=2, padx=5, pady=5)


# Generates and renders the main menu.
file_button = create_button(root, "FILE", show_file_menu)
analysis_button = create_button(root, "ANALYZE", show_analyze_menu)
process_button = create_button(root, "PROCESS", show_process_menu)
filter_button = create_button(root, "FILTER", show_filter_menu)
two_point_button = create_button(root, "TWO POINT", show_two_point_menu)
morph_button = create_button(root, "MORPH", show_morph_menu)
mask_filter_button = create_button(root, "MASK FILTER", show_mask_filter_menu)
skeletonize_button = create_button(
    root, "SKELETONIZE", show_skeletonize_menu)
threshold_button = create_button(
    root, "SEGMENTATION", show_segmentation_menu)
stitch_button = create_button(
    root, "STITCH", show_stitch_menu)
file_button.grid(column=1, row=1, padx=5, pady=5)
analysis_button.grid(column=2, row=1, padx=5, pady=5)
process_button.grid(column=3, row=1, padx=5, pady=5)
filter_button.grid(column=4, row=1, padx=5, pady=5)
two_point_button.grid(column=5, row=1, padx=5, pady=5)
morph_button.grid(column=6, row=1, padx=5, pady=5)
mask_filter_button.grid(column=7, row=1, padx=5, pady=5)
skeletonize_button.grid(column=8, row=1, padx=5, pady=5)
threshold_button.grid(column=9, row=1, padx=5, pady=5)
stitch_button.grid(column=10, row=1, padx=5, pady=5)

# Initialize program.
root.mainloop()
