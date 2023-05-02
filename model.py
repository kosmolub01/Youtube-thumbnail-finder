import sys
import requests
import shutil
import cv2
import numpy as np
from multiprocessing import Process, Manager
from pytube import YouTube
from pytube.extract import video_id
from pytube.exceptions import VideoUnavailable
from urllib.error import URLError
from math import floor
from exceptions import *
import time

"""
TODO
Fix imports
Wait after KeyError: 'streamingData' occurs, then repeat
"""

class Model:
    """
    Model class of "Youtube thumbnail finder" app.

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
        self.input_url = ""
        self.thumbnail_filename = "thumbnail.jpg"
        self.video_filename = "yt_video.mp4"
        # Number of processes to use while processing video.
        self.num_processes = 8

    def process_video(self):
        """
        Processes video - compares video's frames with video's thumbnail.

        Returns:
            url -- URL of a particular moment in the video 
            (moment in which frame most similar to the thumbnail is shown).

        """
        # YouTube object with URL of desired video.
        try:
            yt = YouTube(self.input_url)
        except:
            raise(InvalidVideoUrlException)

        # To be able to determine how long getting stream take
        start = time.time()

        # Get filtered stream for the video.
        while True:
            try:
                stream = yt.streams.filter(adaptive = True, mime_type="video/mp4").first()
                break
            except URLError:
                raise(InternetConnectionException)
            except VideoUnavailable:
                raise(InvalidVideoUrlException)
            except KeyError:
                interval = time.time() - start

                # If trying to get the stream took longer than 30 seconds, 
                # then raise an exception
                if interval > 30:
                    raise(PytubeStreamException)

        # Download video.
        stream.download(filename = self.video_filename)

        # Request thumbnail image.
        thumbnail_url = yt.thumbnail_url

        self.request_and_save_thumbnail_img(thumbnail_url)

        # Compare thumbnail and video frames.
        cap = cv2.VideoCapture(self.video_filename)

        # Max float possible value is init value for min_error.
        min_error = sys.float_info.max

        most_similar_frame_process_index = 0 

        self.remove_horizontal_black_bars_from_img()

        # Get the total number of frames in the video.
        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculate the number of frames per process.
        frames_per_process = num_frames // self.num_processes

        manager = Manager()

        # Processes return values - minimal errors.
        minimal_errors = manager.dict()

        # Processes return values - timestamps.
        timestamps = manager.dict()

        # Divide the video frames into segments.
        segment_indexes = [[0 for x in range(2)] for y in range(self.num_processes)] 

        for i in range(self.num_processes):
            start_frame = i * frames_per_process
            end_frame = start_frame + frames_per_process
            if i == self.num_processes - 1:
                end_frame = num_frames

            segment_indexes[i] = start_frame, end_frame

        # Process each video segment in a separate process.
        processes = []
        for i in range(self.num_processes):
            process = Process(
                target=self.process_video_segment, 
                args=(segment_indexes[i], i, 
                      minimal_errors, timestamps))
                        
            processes.append(process)
            process.start()

        # Wait for all processes to finish.
        for process in processes:
            process.join()

        # Distinguish which process returned minimal error. 
        # Assign timestamp and most_similar_frame_process_index respectively.
        for i in range(self.num_processes):
            if min_error >= minimal_errors[i]:
                min_error = minimal_errors[i]
                timestamp = timestamps[i]
                most_similar_frame_process_index = i

        # Create timestamp URL 
        # (even if user provided not exact URL eg. with typos). 
        id = video_id(self.input_url)
        timestamp = "https://youtube.com/watch?v=" + id + "&t=" + str(timestamp)

        # Save most similar frame.
        index=str(most_similar_frame_process_index)
        most_similar_frame_filename = "most_similar_frame{i}.jpg".format(i=index)

        most_similar_frame = cv2.imread(most_similar_frame_filename)

        cv2.imwrite("most_similar_frame.jpg", most_similar_frame)

        cap.release()

        return timestamp

    def error_between_two_images(self, img1, img2):
        """
        Computes the error between two images. Second image is resized to 
        the size of the first image.

        Args:
            img1 -- first image.
            img2 -- second image.

        Returns:
            err (float) -- error between two images 
            (mean of differences between corresponding pixels).

        """
        h, w, x = img1.shape

        img2 = cv2.resize(img2, (w, h))

        diff = cv2.absdiff(img1, img2)

        err = np.mean(diff)

        cv2.waitKey(0)

        return err

    def miliseconds_to_minutes(miliseconds):
        """
        Converts miliseconds to minutes.

        Args:
            miliseconds -- time in miliseconds to convert.

        Returns:
            minutes -- miliseconds converted to minutes 
            (YouTube's video time format - e.g. 4.23).

        """
        # Less than 1 minute.
        if(miliseconds / 60000 < 1):
            minutes = "0." + str(round(miliseconds / 1000))

        else:   # More or equal 1 minute.
            minutes = str(floor(miliseconds / 60000)) + ".{msec}"
            minutes.format(msec=str(miliseconds / 1000 % 60))

        return minutes 
    
    def request_and_save_thumbnail_img(self, thumbnail_url):
        """
        Downloads and saves YouTube's video thumbnail.

        Args:
        thumbnail_url -- URL of a thumbnail.

        """
        thumbnail_url = thumbnail_url.replace('sddefault', 'maxresdefault')

        response = requests.get(thumbnail_url, stream=True)

        if response.status_code == 200:
            with open(self.thumbnail_filename, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
        else:

            thumbnail_url = thumbnail_url.replace('maxresdefault', 'sddefault')

            response = requests.get(thumbnail_url, stream=True)

            if response.status_code == 200:
                with open(self.thumbnail_filename, "wb") as out_file:
                    shutil.copyfileobj(response.raw, out_file)

        del response

    def remove_horizontal_black_bars_from_img(self):
        """
        Removes horizontal black bars from the image. Processed image is saved.

        """
            
        img = cv2.imread(self.thumbnail_filename)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Threshold the image.
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

        # Find contours.
        contours, hierarchy = cv2.findContours(
                                thresh, cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE)

        # Find largest contour.
        largest_contour = max(contours, key=cv2.contourArea)

        # Find bounding box of largest contour.
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Crop image to bounding box.
        img_cropped = img[y:y+h, x:x+w]

        cv2.imwrite(self.thumbnail_filename, img_cropped)

    def process_video_segment(
            self, segment_indexes, 
            process_no, segment_min_error, 
            timestamp):
        """
        Processes video segment - every frame of a video is compared 
        with provided image. Timestamp of most similar frame 
        and it's similarity error is saved.

        Args:
        segment_indexes -- indexes pointing what part of video to process.
        process_no -- number of a process.
        segment_min_error -- dict of minimal errors form processes.
        timestamp -- dict of timestamps of frames from processes.

        """

        # Max float possible value is init value for min_error.
        min_error = sys.float_info.max

        cap = cv2.VideoCapture(self.video_filename)

        thumbnail = cv2.imread(self.thumbnail_filename)

        cap.set(cv2.CAP_PROP_POS_FRAMES, segment_indexes[0])
        for i in range(segment_indexes[0], segment_indexes[1]):
            ret, frame = cap.read()
            if ret:
                error = self.error_between_two_images(thumbnail, frame)
                if min_error >= error:
                    min_error = error
                    most_similar_frame = frame
                    msec = cap.get(cv2.CAP_PROP_POS_MSEC)

        most_similar_frame_filename = "most_similar_frame" + str(process_no) + ".jpg"
        cv2.imwrite(most_similar_frame_filename, most_similar_frame)

        cap.release()

        segment_min_error[process_no] = min_error
        timestamp[process_no] = int(msec // 1000)


    