import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

root = tk.Tk()
root.geometry("300x300")
root.title("RasterLab")
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)


def import_image():
    extensions = [('formats', ['.jpg', '.png', 'bmp'])]
    file_path = filedialog.askopenfilename(filetypes=extensions)
    new_img = ImageTk.PhotoImage(Image.open(file_path))
    # label = tk.Label(root, text=file_path)
    # label.pack()

    new_window = tk.Toplevel(root)
    new_window.iconphoto(False, icon)
    new_window.title(file_path)

    new_window.geometry("300x300")

    image = tk.Label(new_window, image=new_img)
    image.image = new_img
    image.pack()


import_button = tk.Button(root,
                          text="import image",
                          pady=50,
                          padx=50, command=import_image
                          )
import_button.pack()

# img = tk.PhotoImage(file='icon.png')
# tk.Label(
#     root,
#     image=img
# ).pack()

root.mainloop()
