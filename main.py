from tkinter import Button, Label, PhotoImage, Tk, filedialog
from PIL import Image, ImageTk

root = Tk()
root.geometry("300x50")
root.title("RasterLab")
icon = PhotoImage(file='icon.png')
root.iconphoto(False, icon)


def import_image():
    extensions = [('formats', ['.jpg', '.png', 'bmp'])]
    file_path = filedialog.askopenfilename(filetypes=extensions)
    label = Label(root, text=file_path)
    label.pack()


import_button = Button(root,
                       text="import image",
                       pady=50,
                       padx=50, command=import_image
                       )
import_button.pack()

root.mainloop()
