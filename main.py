from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from tkinter import filedialog


class RasterLab(App):
    def build(self):
        self.window = GridLayout()
        self.icon = "icon.png"
        self.window.cols = 1
        # self.window.size_hint = (0.2, 0.7)
        # self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        # add widgets to window
        self.button_interface = GridLayout(
            # spacing=10,
            # padding=(10, 10, 40, 40),
            size_hint=(0.2, 0.2),
            cols=8,
            col_default_width=0.2,
        )
        self.window.add_widget(self.button_interface)

        self.import_button = Button(
            width=55,
            text="Import image",
            size_hint=(0.2, 0.3),
            bold=True,
            background_color='#00FFCE',
        )
        self.import_button.bind(on_press=self.import_image)  # type: ignore
        self.hist_button = Button(
            width=55,
            text="Histogram",
            size_hint=(0.2, 0.3),
            bold=True,
            background_color='#00FFCE',
        )
        self.button_interface.add_widget(self.import_button)
        self.button_interface.add_widget(self.hist_button)

        self.chosen_image = Image(
            source=""
        )
        self.window.add_widget(self.chosen_image)
        # self.greeting = Label(
        #     text="greeting",
        #     font_size=20,
        #     color='#00FFCE'
        # )
        # self.window.add_widget(self.greeting)

        # self.user = TextInput(
        #     multiline=False,
        #     padding_y=(20, 20),
        #     padding_x=(40, 40),
        #     size_hint=(1, 0.5),
        #     font_size=20
        # )
        # self.window.add_widget(self.user)

        return self.window

    def import_image(self, event):
        global img
    # allowed file extensions
        extensions = [('formats', ['.jpg', '.png', 'bmp'])]
        file_name = filedialog.askopenfilename(filetypes=extensions)
        print(file_name)
        self.chosen_image.source = file_name


if __name__ == "__main__":
    RasterLab().run()
