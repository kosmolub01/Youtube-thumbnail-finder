import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class View (tk.Tk):
    """
    View class of "Youtube thumbnail finder" app.

    TBD:
    Attributes
    ----------
    name : str
        first name of the person

    Methods
    -------
    info(additional=""):
        Prints the person's name and age.
    """
    def __init__(self, controller) -> None:
        super().__init__()

        self.controller = controller

        self.input_url = tk.StringVar()
        self.output_url = tk.StringVar()
        self.label_with_img = ""
        self.img = ""

        self.title("YouTube thumbnail finder")
        self.geometry('600x400')
        self.resizable(False,False)

        self._make_main_frame()
        self._make_labels()
        self._make_entries()
        self._make_button()

    def main(self) -> None:
        self.mainloop()

    def show_thumbnail(self):
        img = Image.open(self.controller.model.thumbnail_filename)
        img.thumbnail((200,130), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.label_with_img.configure(image=self.img)

    def _make_main_frame(self):
        self.frm = ttk.Frame(self, padding=10)
        self.frm.grid()

    def _make_labels(self):
        ttk.Label(self.frm, text="YouTube video link:").grid(column=0, row=0)
        ttk.Label(self.frm, text="Moment from thumbnail:").grid(column=0, row=1)
        self.label_with_img = ttk.Label(self.frm, text="Thumbnail will be displayed here")
        self.label_with_img.grid(column=1, row=2)
        

    def _make_entries(self):
        input_url_ent = ttk.Entry(self.frm, textvariable=self.input_url, width=40)
        input_url_ent.grid(column=1, row=0)

        output_url_ent = ttk.Entry(self.frm, textvariable=self.output_url, width=40)
        output_url_ent.grid(column=1, row=1)

    def _make_button(self):
        ttk.Button(self.frm, text="Find moment form thumbnail", command=self.controller.button_on_click).grid(column=2, row=0)

    
