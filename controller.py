import sys
from model import Model

class Controller:
    def __init__(self) -> None:
        # Save program parameter
        video_url = sys.argv[1]
        self.model = Model(video_url)

    def main(self):
        self.model.process_video()

if __name__ == "__main__":

    controller = Controller()
    controller.main()