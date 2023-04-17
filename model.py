import sys
import requests
import shutil
import cv2
import numpy as np
import threading
from pytube import YouTube
from math import floor

# Define the number of threads to use.
num_threads = 8

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

    def process_video(self):
        """
        Processes video - compares video's frames with video's thumbnail.

        Returns:
            url -- URL of a particular moment in the video 
            (moment in which frame most similar to the thumbnail is shown).

        """
        # YouTube object with URL of desired video.
        yt = YouTube(self.input_url)

        # Get filtered stream for the video.
        stream = yt.streams.filter(adaptive = True, mime_type="video/mp4").first()

        # Download video.
        stream.download(filename = "yt_video.mp4")

        # Request thumbnail image.
        thumbnail_url = yt.thumbnail_url

        self.request_and_save_thumbnail_img(thumbnail_url, "thumbnail.jpg")

        # Compare thumbnail and video frames.
        cap = cv2.VideoCapture("yt_video.mp4")

        # Max float possible value is init value for min_error.
        min_error = sys.float_info.max

        most_similar_frame_thread_index = 0 

        self.remove_horizontal_black_bars_from_img('thumbnail.jpg')

        # Get the total number of frames in the video.
        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculate the number of frames per thread.
        frames_per_thread = num_frames // num_threads

        # Threads return values - minimal errors.
        minimal_errors = [None] * num_threads

        # Threads return values - timestamps.
        timestamps = [None] * num_threads

        # Divide the video frames into segments.
        segment_indexes = [[0 for x in range(2)] for y in range(num_threads)] 

        for i in range(num_threads):
            start_frame = i * frames_per_thread
            end_frame = start_frame + frames_per_thread
            if i == num_threads - 1:
                end_frame = num_frames

            segment_indexes[i] = start_frame, end_frame

        # Process each video segment in a separate thread.
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(
                        target=self.process_video_segment, 
                        args=("yt_video.mp4", segment_indexes[i], 
                            "thumbnail.jpg", i, minimal_errors, 
                            timestamps))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish.
        for thread in threads:
            thread.join()

        print("Threads joined")

        # Distinguish which thread returned minimal error. 
        # Assign timestamp and most_similar frame thread_index respectively.
        for i in range(num_threads):
            if min_error >= minimal_errors[i]:
                min_error = minimal_errors[i]
                timestamp = timestamps[i]
                most_similar_frame_thread_index = i

        print("Min. error: " + str( min_error))

        # Print timestamp URL.
        timestamp = self.input_url + "&t=" + str(timestamp)

        # Save most similar frame.
        index=str(most_similar_frame_thread_index)
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
            err -- error between two images 
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
    
    def request_and_save_thumbnail_img(self, thumbnail_url, filename):
        """
        Downloads and saves YouTube's video thumbnail.

        Args:
        thumbnail_url -- URL of a thumbnail.
        filename -- name of a file to save (in cwd) downloaded thumbnail.

    """
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

    def remove_horizontal_black_bars_from_img(self, img_filename):
        """
        Removes horizontal black bars from the image. Processed image is saved.

        Args:
        img_filename -- name of a file to process.

        """
            
        img = cv2.imread(img_filename)

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

        cv2.imwrite(img_filename, img_cropped)

    def process_video_segment(
            self, video_filename, 
            segment_indexes, thumbnail_filename, 
            thread_no, segment_min_error, 
            timestamp):
        """
        Processes video segment - every frame of a video is compared 
        with provided image. Timestamp of most similar frame 
        and it's similarity error is saved.

        Args:
        video_filename -- name of a file to process.
        segment_indexes -- indexes pointing what part of video to process.
        thumbnail_filename -- name of a file with thumbnail.
        thread_no -- number of a thread.
        segment_min_error -- list of minimal errors form threads.
        timestamp -- list of timestamps of frames from threads.

        """

        # Max float possible value is init value for min_error.
        min_error = sys.float_info.max

        cap = cv2.VideoCapture(video_filename)

        thumbnail = cv2.imread(thumbnail_filename)

        print("Thread", thread_no, ":", segment_indexes[0], "-", segment_indexes[1])

        cap.set(cv2.CAP_PROP_POS_FRAMES, segment_indexes[0])
        for i in range(segment_indexes[0], segment_indexes[1]):
            ret, frame = cap.read()
            if ret:
                error = self.error_between_two_images(thumbnail, frame)
                if min_error >= error:
                    min_error = error
                    most_similar_frame = frame
                    msec = cap.get(cv2.CAP_PROP_POS_MSEC)

        most_similar_frame_filename = "most_similar_frame" + str(thread_no) + ".jpg"
        cv2.imwrite(most_similar_frame_filename, most_similar_frame)

        cap.release()

        segment_min_error[thread_no] = min_error
        timestamp[thread_no] = int(msec // 1000)


    