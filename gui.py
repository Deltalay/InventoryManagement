
# This file was generated by the Tkinter Designer by Parth Jadhav
# https://github.com/ParthJadhav/Tkinter-Designer


from ctypes import windll
from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"D:\school\Tkinter-Designer\build\assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


windll.shcore.SetProcessDpiAwareness(1)
window = Tk()

window.geometry("900x600")
window.configure(bg = "#FFFFFF")


canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 600,
    width = 900,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
canvas.create_rectangle(
    446.0,
    2.0,
    900.0,
    602.0,
    fill="#FFFFFF",
    outline="")

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    242.0,
    302.0,
    image=image_image_1
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    657.5,
    295.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=446.0,
    y=269.0,
    width=423.0,
    height=51.0
)

canvas.create_text(
    446.0,
    252.0,
    anchor="nw",
    text="Password:",
    fill="#000000",
    font=("Inter Medium", 16 * -1)
)

canvas.create_text(
    602.0,
    52.0,
    anchor="nw",
    text="LOGIN",
    fill="#000000",
    font=("Inter Bold", 36 * -1)
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    657.5,
    203.5,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_2.place(
    x=446.0,
    y=177.0,
    width=423.0,
    height=51.0
)

canvas.create_text(
    446.0,
    158.0,
    anchor="nw",
    text="Username:",
    fill="#000000",
    font=("Inter Medium", 17 * -1)
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat"
)
button_1.place(
    x=468.0,
    y=407.0,
    width=379.0,
    height=51.0
)
window.resizable(False, False)
window.mainloop()
