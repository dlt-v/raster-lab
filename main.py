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
            text="Import image",
            size_hint=(0.2, 0.3),
            bold=True,
            background_color='#00FFCE',
        )
        self.import_button.bind(on_press=self.import_image)  # type: ignore
        self.hist_button = Button(
            text="Histogram",
            size_hint=(0.2, 0.3),
            bold=True,
            background_color='#00FFCE',
        )
        self.button_interface.add_widget(self.import_button)
        self.button_interface.add_widget(self.hist_button)

        self.window.add_widget(Image(source="logo.png"))
        self.greeting = Label(
            text="greeting",
            font_size=20,
            color='#00FFCE'
        )
        self.window.add_widget(self.greeting)

        self.user = TextInput(
            multiline=False,
            padding_y=(20, 20),
            padding_x=(40, 40),
            size_hint=(1, 0.5),
            font_size=20
        )
        self.window.add_widget(self.user)
        self.button.bind(on_press=self.callback)  # type: ignore

        return self.window

    def import_image(self, event):

        self.greeting.text = "Hello " + self.user.text + "!"


if __name__ == "__main__":
    RasterLab().run()
