import tkinter as tk
from PIL import Image, ImageTk


class ImageWindow():
    def __init__(self, root, file_path: str, ):
        # load image from
        self.file_path = file_path
        opened_image = Image.open(file_path)
        new_img = ImageTk.PhotoImage(opened_image)
        self.window = tk.Toplevel(
            root, width=opened_image.width,
            height=opened_image.height
        )
        self.window.title(f"RasterLab: {file_path}")
        self.window.resizable(False, False)

        # bind events to window
        # self.window.bind("<FocusIn>", on_focus)
        self.window.bind("<MouseWheel>", self.on_scroll)
        self.window.bind("<Button-1>", on_click)

    def on_scroll(self, event):
        """
        Depending on the scroll direction it resizes the image up and down, scaling the entire widget/frame with it.
        """
        # get current widget height and width, account for borders (-4)
        cur_height = self.window.winfo_height() - 4
        cur_width = self.window.winfo_width() - 4
        if event.delta == 120:
            new_width = int(cur_width * 1.05)
            new_height = int(cur_height * 1.05)
        elif event.delta == -120:
            new_width = int(cur_width * 0.95)
            new_height = int(cur_height * 0.95)
        else:
            return
        # destroy the current image
        for widget in self.window.winfo_children():
            widget.destroy()
        # resize the actual image
        resized_image = Image.open(self.file_path).resize(
            (new_width, new_height))
        new_img = ImageTk.PhotoImage(resized_image)
        self.window["height"] = new_height
        self.window["width"] = new_width
        # render image in the frame of the widget
        image = tk.Label(self.window, image=new_img)
        # create a reference for the file
        image.image = new_img  # type: ignore
        image.pack()

    # def on_focus(self, event):
    #     """
    #     Switches the focused_file data to the current image in order for other functions to operate on them. Resets the plot profile data since it's another image.
    #     """
    #     global focused_file, plot_profile_data
    #     focused_file["path"] = file_path
    #     focused_file["mode"] = opened_image.mode
    #     # reset plot profile data for new image
    #     try:
    #         plot_profile_data["start"] = [-1, -1]
    #         plot_profile_data["end"] = [-1, -1]
    #         plot_profile_button["state"] = "disabled"

    #         # print(f"Focused file changed to: {focused_file['path']}...")
    #         # enable buttons
    #         if focused_file["mode"] == 'L':
    #             histogram_array_button["state"] = "normal"
    #         else:
    #             plot_profile_button["state"] = "disabled"
    #             histogram_array_button["state"] = "disabled"
    #         histogram_button["state"] = "normal"
    #     except:
    #         print("Couldn't change state of some buttons.")
