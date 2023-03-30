"""
================================================================================
Filename: get_thumbnail.py
Description:
Script finds the thumbnail of a given YouTube's video and saves it in current 
working directory. Video is also downloaded.
Input parameters:
    - YouTube's video url 
================================================================================

TODO:
- input validation
- exception handling (no suitable stream for video)
- remove saving thumbnail functionality

"""
import sys
import os
import requests
import shutil
import cv2
import numpy as np
from pytube import YouTube

if __name__ == "__main__":

    # Save program parameter
    video_url = sys.argv[1]

    # YouTube object with URL of desired video
    yt = YouTube(video_url)

    # Get filtered stream for the video
    stream = yt.streams.filter(adaptive = True, mime_type="video/mp4").first()

    # Download video
    stream.download()

    # Request thumbnail image

    thumbnail_url = yt.thumbnail_url

    response = requests.get(thumbnail_url, stream=True)
    with open(os.getcwd() + "\\thumbnail.png", "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


    


