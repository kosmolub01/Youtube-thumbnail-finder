class InternetConnectionException(Exception):
   def __init__(self):
      pass

   def __str__(self):
      message = "No internet connection available. "\
                "To use application, connect computer to the internet."
      return message
   
class InvalidVideoUrlException(Exception):
   def __init__(self):
      pass

   def __str__(self):
      return "Provide valid YouTube video URL."
   
class PytubeStreamException(Exception):
   def __init__(self):
      pass

   def __str__(self):
      return "Unexpected error occurred. Program was unable to download the video. Please, try again."