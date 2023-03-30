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
- fix comparison algo - right now it has random accuracy
- change min_error init value
- input validation
- exception handling (no suitable stream for video)
- remove saving thumbnail functionality

"""
import sys
import requests
import shutil
import cv2
import numpy as np
from pytube import YouTube

# Computes the Mean Squared Error between two images
def mse(img1, img2):
   h, w, x = img1.shape
   img2 = cv2.resize(img2, (w, h))
   #print(img1.shape)
   #print(img2.shape)
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse

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

    min_error = 100.0
    
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


    


