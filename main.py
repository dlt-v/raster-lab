from tkinter import Button, Label, Tk, filedialog
from PIL import Image, ImageTk

root = Tk()


def import_image():
    extensions = [('formats', ['.jpg', '.png', 'bmp'])]
    file_path = filedialog.askopenfilename(filetypes=extensions)
    label = Label(root, text=file_path)
    label.pack()


import_button = Button(root,
                       text="import",
                       pady=50,
                       padx=50, command=import_image
                       )
import_button.pack()

root.mainloop()
