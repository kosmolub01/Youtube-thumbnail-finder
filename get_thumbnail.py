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

if __name__ == "__main__":

    url = sys.argv[1]
    response = requests.get(url, stream=True)
    with open(sys.argv[2], "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

