import sys
from model import Model
from view import View

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
        self.view.main()

    def button_on_click(self):       
        self.model.input_url = self.view.input_url.get()       
        output_url = self.model.process_video()
        self.view.output_url.set(output_url)
        self.view.show_thumbnail()

if __name__ == "__main__":

    controller = Controller()
    controller.main()