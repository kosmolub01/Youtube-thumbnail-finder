"""
================================================================================
Filename: get_thumbnail.py
Description:
Script finds the thumbnail of a given YouTube's video and saves it in current 
working directory. Video is also downloaded. Frame most similar to the 
thumbnail is shown.
Input parameters:
    - YouTube's video url 
================================================================================
TODO:
- compare thumbnail and video frames 
- input validation
- exception handling (no suitable stream for video)
"""
import sys
import requests
import shutil
import cv2
import numpy as np
from pytube import YouTube

# Computes the error between two images. Second image is resized 
# to the size of the first image 
def error_between_two_images(img1, img2):
   h, w, x = img1.shape

   img2 = cv2.resize(img2, (w, h))

   diff = cv2.absdiff(img1, img2)

   err = np.mean(diff)

   cv2.waitKey(0)

   return err

def miliseconds_to_minute(miliseconds):
    # Less than 1 minute
    if(miliseconds / 60000 < 1):
        return "0." + str(round(miliseconds / 1000))
    else:   # More or equal 1 minute
        return str(floor(miliseconds / 60000)) + "." + str(miliseconds / 1000 % 60)

if __name__ == "__main__":

    # Save program parameter
    video_url = sys.argv[1]

    # YouTube object with URL of desired video
    yt = YouTube(video_url)

    # Get filtered stream for the video
    stream = yt.streams.filter(adaptive = True, mime_type="video/mp4").first()

    # Download video
    stream.download(filename = "yt_video.mp4")

    # Request thumbnail image

    thumbnail_url = yt.thumbnail_url

    response = requests.get(thumbnail_url, stream=True)
    with open("thumbnail.png", "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    # Compare thumbnail and video frames

    # Max float possible value is init value for min_error
    min_error = sys.float_info.max
    
    thumbnail = cv2.imread("thumbnail.png")

    cap = cv2.VideoCapture("yt_video.mp4")

    while not cap.isOpened():
        cap = cv2.VideoCapture("yt_video.mp4")
        cv2.waitKey(1000)
        print("Wait for the header")

        pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    while True:
        flag, frame = cap.read()
        if flag:
            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

            print(str(pos_frame) + " frames")

            error = mse(thumbnail, frame)

            if min_error >= error:
                min_error = error
                most_similar_frame = frame

            print("Error: " + str(error))
        else:
            # The next frame is not ready, try to read it again
            cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
            print("Frame is not ready")

        if cv2.waitKey(10) == 27:
            break

        if cap.get(cv2.CAP_PROP_POS_FRAMES)==cap.get(cv2.CAP_PROP_FRAME_COUNT):
            # If the number of captured frames is equal to the total number 
            # of frames, then stop
            break
    
    print("Min. error: " + str( min_error))

    cv2.imshow("most_similar_frame", most_similar_frame)

    cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()