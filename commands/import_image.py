
from tkinter import filedialog, PhotoImage
from PIL import Image, ImageTk


def import_image() -> str:
    """Returns an absolute path to chosen image."""
    global img
    # allowed file extensions
    extensions = [('formats', ['.jpg', '.png', 'bmp'])]
    file_name = filedialog.askopenfilename(filetypes=extensions)
    print(file_name)
    return file_name
