"""
================================================================================
Filename: get_thumbnail.py
Description:
Script finds the thumbnail of a given YouTube's video and saves it in current 
working directory. Video is also downloaded. Frame most similar to the 
thumbnail is saved.
Input parameters:
    - YouTube's video URL
Output:
    - Thumbnail timestamp in a video (URL)
================================================================================
TODO:
- result should be thumbnail timestamp 
(moment of thumbnail occurrence in a video), as a URL
- add GUI
- input validation
- exception handling (no suitable stream for video)
"""
import sys
import requests
import shutil
import cv2
import numpy as np
import threading
import tkinter as tk
from pytube import YouTube
from math import floor

# Define the number of threads to use
num_threads = 8

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
    
def request_and_save_thumbnail_img(thumbnail_url, filename):

    thumbnail_url = thumbnail_url.replace('sddefault', 'maxresdefault')

    response = requests.get(thumbnail_url, stream=True)

    if response.status_code == 200:
        with open(filename, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
    else:
        print("Max resolution thumbnail is not available")

        thumbnail_url = thumbnail_url.replace('maxresdefault', 'sddefault')

        response = requests.get(thumbnail_url, stream=True)

        if response.status_code == 200:
            with open(filename, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
        else:
            print("Thumbnail is not available")
    
    print("Thumbnail URL:", thumbnail_url)

    del response

# Removes horizontal black bars from image
def remove_horizontal_black_bars_from_img(img_filename):
    img = cv2.imread(img_filename)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold the image
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Find bounding box of largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Crop image to bounding box
    img_cropped = img[y:y+h, x:x+w]

    cv2.imwrite(img_filename, img_cropped)

# Define the function to process a video segment
def process_video_segment(video_filename, segment_indexes, thumbnail_filename, thread_no, segment_min_error, timestamp):

    # Max float possible value is init value for min_error
    min_error = sys.float_info.max

    cap = cv2.VideoCapture(video_filename)

    thumbnail = cv2.imread(thumbnail_filename)

    print("Thread ", thread_no, ": ", segment_indexes[0], "-", segment_indexes[1])

    cap.set(cv2.CAP_PROP_POS_FRAMES, segment_indexes[0])
    for i in range(segment_indexes[0], segment_indexes[1]):
        ret, frame = cap.read()
        if ret:
            error = error_between_two_images(thumbnail, frame)
            if min_error >= error:
                min_error = error
                most_similar_frame = frame
                msec = cap.get(cv2.CAP_PROP_POS_MSEC)

    most_similar_frame_filename = "most_similar_frame" + str(thread_no) + ".jpg"
    cv2.imwrite(most_similar_frame_filename, most_similar_frame)

    cap.release()

    segment_min_error[thread_no] = min_error
    timestamp[thread_no] = int(msec // 1000)

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

    request_and_save_thumbnail_img(thumbnail_url, "thumbnail.jpg")

    # Compare thumbnail and video frames
    cap = cv2.VideoCapture("yt_video.mp4")

    # Max float possible value is init value for min_error
    min_error = sys.float_info.max

    most_similar_frame_thread_index = 0 

    remove_horizontal_black_bars_from_img('thumbnail.jpg')

    # Get the total number of frames in the video
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate the number of frames per thread
    frames_per_thread = num_frames // num_threads

    # Threads return values - minimal errors
    minimal_errors = [None] * num_threads

    # Threads return values - timestamps
    timestamps = [None] * num_threads

    # Divide the video frames into segments
    segment_indexes = [[0 for x in range(2)] for y in range(num_threads)] 

    for i in range(num_threads):
        start_frame = i * frames_per_thread
        end_frame = start_frame + frames_per_thread
        if i == num_threads - 1:
            end_frame = num_frames

        segment_indexes[i] = start_frame, end_frame

    # Process each video segment in a separate thread
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=process_video_segment, args=("yt_video.mp4", segment_indexes[i], "thumbnail.jpg", i, minimal_errors, timestamps))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("Threads joined")

    # Distinguish which thread returned minimal error. 
    # Assign timestamp and most_similar frame thread_index respectively
    for i in range(num_threads):
        if min_error >= minimal_errors[i]:
            min_error = minimal_errors[i]
            timestamp = timestamps[i]
            most_similar_frame_thread_index = i

    print("Min. error: " + str( min_error))

    # Print timestamp URL
    timestamp = video_url + "&t=" + str(timestamp)
    print("Timestamp URL: " + timestamp)

    # Save most similar frame
    most_similar_frame_filename = "most_similar_frame" + str(most_similar_frame_thread_index) + ".jpg"

    cv2.imwrite("most_similar_frame.jpg", cv2.imread(most_similar_frame_filename))

    cap.release()