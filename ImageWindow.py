import tkinter as tk
from PIL import Image, ImageTk


class ImageWindow():
    def __init__(self, root, file_path: str):
        opened_image = Image.open(file_path)
        new_img = ImageTk.PhotoImage(opened_image)
        new_window = tk.Toplevel(
            root,
            width=opened_image.width,
            height=opened_image.height
        )
        new_window.title(f"RasterLab: {file_path}")
        new_window.resizable(False, False)
