"""
================================================================================
Filename: get_thumbnail.py
Description:
Script finds the thumbnail of a given YouTube's video and saves it in a given 
location.
Input parameters:
    - YouTube's video url 
    - path to location to save the thumbnail
================================================================================
"""
import sys
import requests
import shutil
import cv2
import numpy as np

# To compare two images
def mse(img1, img2):
   h, w = img1.shape
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse

if __name__ == "__main__":

    # Create thumbnail url
    video_url = sys.argv[1]
    video_id = video_url[video_url.index("=") + 1: ]
    thumbnail_url = "https://img.youtube.com/vi/{}/0.jpg"
    thumbnail_url = thumbnail_url.format(video_id)

    # Request and save image in given location
    response = requests.get(thumbnail_url, stream=True)
    with open(sys.argv[2], "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response