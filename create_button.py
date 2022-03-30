import tkinter as tk


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
