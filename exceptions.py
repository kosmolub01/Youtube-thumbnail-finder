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