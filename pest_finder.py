import logging
import time
from io import BytesIO
from typing import Tuple

import requests
from picamera import PiCamera


def locate_pest(camera_resolution: Tuple[int, int], tensor_flow_server_url: str) -> Tuple[int, int]:
    """
    Capture an image using the PiCamera and send it to the web server running TensorFlow to find
    if a pest is found and get his coordinates
    :param camera_resolution: a tuple with the camera resolution used
    :param tensor_flow_server_url: the url of the Tensor Flow web server
    :return: a Tuple with the coordinates of the pest
    """

    # Initialize the PiCamera
    camera = PiCamera()
    camera.resolution = camera_resolution

    # We loop until a pest is found and we have his coordinates
    while True:
        # The picture is captured in a stream of BytesIO in jpeg format
        picture_stream = BytesIO()
        camera.capture(picture_stream, 'jpeg')

        # Post the picture to Tensor Flow webserver
        # If a pest is found , the response will be a string with the coordinates in the following format "XXX,YYY"
        # If no pest is found, the response will be an empty string
        logging.debug("Request Tensor Flow web server")
        response = requests.post(tensor_flow_server_url, files={"file": ('pest.jpg', picture_stream.getvalue())})
        coordinates = response.text
        logging.debug("Tensor Flow web server responded with : [{coordinates}]".format(coordinates=coordinates))
        if coordinates:
            # If coordinates has been found, we convert them to int and return them
            x, y = coordinates.split(",")
            x = int(x)
            y = int(y)
            camera.close()
            return x, y
        else:
            # If no coordinate is returned, then we wait 5 seconds, take a new picture an submit it again to the
            # Tensor Flow web server
            time.sleep(5)
