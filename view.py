import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        self._center_window(600, 400)
        self.resizable(False,False)
        self._replace_default_icon()

        self._make_main_frame()
        self._make_image_frame()
        self._make_labels()
        self._make_entries()
        self._make_button()
        self._make_status_bar()

    def main(self) -> None:
        self.mainloop()

    def show_thumbnail(self):
        img = Image.open(self.controller.model.thumbnail_filename)
        img = img.resize((393,193))
        self.img = ImageTk.PhotoImage(img)
        self.label_with_img.configure(image=self.img)

    def show_messagebox(self, type, message):
        if type == "Error":
            messagebox.showerror("Error", message, parent=self)
        elif type == "Warning":
            messagebox.showwarning("Warning", message, parent=self)
        else:
            messagebox.showinfo("Info", message, parent=self)

    def _center_window(self, width, height):

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)

        self.geometry('%dx%d+%d+%d' % (width, height, x, y)) 

    def _make_main_frame(self):
        self.main_frm = ttk.Frame(self)
        self.main_frm.grid()

    def _make_image_frame(self):
        self.main_frm.grid_rowconfigure(2, minsize=20)
        self.img_frm = ttk.Frame(self.main_frm, padding=2,  width=400, height=200, relief="ridge")
        self.img_frm.grid(column=0, row=3,  columnspan=3)
        # Keep constant size (won't change size if bigger label is placed in it)
        self.img_frm.grid_propagate(0)

    def _make_labels(self):
        ttk.Label(self.main_frm, text="YouTube video link:", padding=10).grid(column=0, row=0)
        ttk.Label(self.main_frm, text="Moment from thumbnail:", padding=5).grid(column=0, row=1)
        self.label_with_img = ttk.Label(self.img_frm, text="Thumbnail will be displayed here.")
        self.label_with_img.grid(column=0, row=0)
        
    def _make_entries(self):
        input_url_ent = ttk.Entry(self.main_frm, textvariable=self.input_url, width=40)
        input_url_ent.grid(column=1, row=0)

        # Bind entry with functions to show hint in the status bar
        input_url_ent.bind("<Enter>", self.on_lbl_enter)
        input_url_ent.bind("<Leave>", self.on_lbl_leave)

        output_url_ent = ttk.Entry(self.main_frm, textvariable=self.output_url, width=40)
        output_url_ent.grid(column=1, row=1, padx=10, pady=5)

    def _make_button(self):
        self.process_video_btn = ttk.Button(self.main_frm, text="Find moment form thumbnail", command=self.controller.button_on_click)
        self.process_video_btn.grid(column=2, row=0)

    def _replace_default_icon(self):
        ico = Image.open('icon.jpg')
        photo = ImageTk.PhotoImage(ico)
        self.wm_iconphoto(False, photo)

    def _make_status_bar(self):
        # In order to place status bar at the bottom of the window, 
        # offset is needed
        self.offset=ttk.Frame(self.main_frm, width=500, height=90,  padding=2)
        self.offset.grid(row=4, column=0, rowspan=2, columnspan=3, sticky="W")

        # Frame holding actual label
        self.status_bar_frm=ttk.Frame(self.main_frm, width=500, height=20)
        self.status_bar_frm.grid(row=8, column=0, columnspan=3, sticky="W")

        # Status bar label
        self.status_bar_lbl = tk.Label(self.status_bar_frm)
        self.status_bar_lbl.grid(row = 0, column = 0)

    def on_lbl_enter(self, event):
        if not self.controller.processing_video:
            self.status_bar_lbl.configure(background="white")
            self.set_status_bar_msg("Paste YouTube video link, then click the button.")

    def on_lbl_leave(self, enter):
        if not self.controller.processing_video:
            self.status_bar_lbl.configure(background="grey94")
            self.set_status_bar_msg("")

    def set_status_bar_msg(self, msg):
        if msg == "":
            self.status_bar_lbl.configure(background="grey94")
        else:
            self.status_bar_lbl.configure(background="white")
        self.status_bar_lbl.configure(text=msg)


    

    