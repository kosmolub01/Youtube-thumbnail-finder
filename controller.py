from email import message
from multiprocessing import process
import sys
from model import Model
from view import View
from exceptions import *
import http.client as httplib
import threading

class Controller:
    """
    Controller class of "Youtube thumbnail finder" app.

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

    def __init__(self) -> None:
        self.model = Model()
        self.view = View(self)
        self.processing_video = False

    def main(self):
        # Check internet_connectivity. 
        # Show error message in case there is no internet.
        if self._check_internet_connectivity() == False:
            message = "No internet connection available. "\
                "To use application, connect computer to the internet."
            self.view.set_status_bar_msg("Error.")
            self.view.show_messagebox("Error", message)
            self.view.set_status_bar_msg("")

        self.view.main()

    def button_on_click(self):
        if self.processing_video:
            return

        self.view.process_video_btn.state(["disabled"]) # Disable the button.
        self.processing_video = True   
        t = threading.Thread(target=self._start_processing_video) 
        t.start()
        self.view.set_status_bar_msg("Processing the video...")

    # Function to be run in separate thread
    def _start_processing_video(self):
        self.model.input_url = self.view.input_url.get()       
        try:   
            output_url = self.model.process_video()
            self.view.output_url.set(output_url)
            self.view.show_thumbnail()
            self.view.set_status_bar_msg("Program has finished.")
             
        except(InternetConnectionException) as e:
            self.view.set_status_bar_msg("Error.")
            self.view.show_messagebox("Error", e)
            self.view.set_status_bar_msg("")
        except(InvalidVideoUrlException) as e:
            self.view.set_status_bar_msg("Error.")
            self.view.show_messagebox("Info", e)
            self.view.set_status_bar_msg("")
        except(PytubeStreamException) as e:
            self.view.set_status_bar_msg("Error.")
            self.view.show_messagebox("Error", e)
            self.view.set_status_bar_msg("")
        finally:
            self.processing_video = False 
            self.view.process_video_btn.state(["!disabled"]) # Enable the button.

    def _check_internet_connectivity(self) -> bool:
        conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
        try:
            conn.request("HEAD", "/")
            return True
        except Exception:
            return False
        finally:
            conn.close()

if __name__ == "__main__":

    controller = Controller()
    controller.main()