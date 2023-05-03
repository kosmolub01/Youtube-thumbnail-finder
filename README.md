# Youtube Thumbnail Finder
Find moment from thumbnail in a YouTube video. Program presentation: https://www.youtube.com/watch?v=YvoJ_e35pSs 


## Table of Contents
* [General Info](#general-information)
* [Technologies Used To Implement Core Features](#technologies-used-to-implement-core-features)
* [Features](#features)
* [Screenshots](#screenshots)
* [How it works](#how-it-works)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)


## General Information
The program finds moment from thumbnail in a YouTube video. The user provides a link to the video, the program outputs a link to the video with a timestamp (a moment in which action form thumbnail takes place). Altought YouTube provides 'Most Replayed' feature that helps to find a moment from thumbnail manually, it may be not enough. Sometimes the most replayed segment of a video is not the one that is shown in a thumbnail, sometimes the feature is disabled. The app has serious limitation - it works only if thumbnail is exact frame from the video. I created this program because I wanted to create GUI app with MVC in Python.


## Technologies Used To Implement Core Features
- Python
- pytube
- OpenCV 
- Tkinter


## Features
- Finding moment from thumbnail for YouTube videos
- GUI
- Exceptions handling (no Internet connection, invalid video link, pytube error)


## Screenshots
![image](https://user-images.githubusercontent.com/72302279/235911935-7bf6422a-a6a2-44fd-a614-637b638beff3.png)
![image](https://user-images.githubusercontent.com/72302279/235929076-18c782d2-8628-4bec-9bfe-8c357ca32839.png)


## How it works
1. Program downloads the video and the thumbnail.
2. Every frame of the video is compared with the thumbnail - mean of the differences between corresponding pixels is calculated.
3. Timestamp of the frame with the lowest mean is retrieved.

## Setup
1. Install Python and Git, if you don’t have it already installed.
2. Clone the repo ```git clone https://github.com/kosmolub01/Youtube-thumbnail-finder.git```.
3. Install required packages ```python -m pip install -r requirements.txt``` (run this command in project folder).


## Usage
Run ```python controller.py```.


## Project Status
Project is: _in progress_.


## Room for Improvement
Room for improvement:
- Determine better way of comparing thumbnail and each frame of a video, so the program will be more universal and work for other types of thumbnails (not only for those that are exact frames from the video)
- Don't overload the CPU that much
- App heavily relies on pytube, which is not perfect. Sometimes it has problems with accessing available videos. Consider changing the library.

To do:
- Add comments
