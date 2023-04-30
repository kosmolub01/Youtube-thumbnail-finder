from email import message
import sys
from model import Model
from view import View
from exceptions import *
import http.client as httplib

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

    def main(self):
        # Check internet_connectivity. 
        # Show error message in case there is no internet.
        if self._check_internet_connectivity() == False:
            message = "No internet connection available. "\
                "To use application, connect computer to the internet."
            self.view.show_messagebox("Error", message)

        self.view.main()

    def button_on_click(self):       
        self.model.input_url = self.view.input_url.get()       
        try:   
            output_url = self.model.process_video()
            self.view.output_url.set(output_url)
            self.view.show_thumbnail()
        except(InternetConnectionException) as e:
            self.view.show_messagebox("Error", e)
        except(InvalidVideoUrlException) as e:
            self.view.show_messagebox("Info", e)
        except(PytubeStreamException) as e:
            self.view.show_messagebox("Error", e)

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