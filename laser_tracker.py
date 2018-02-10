import logging
import time
from typing import Dict, Tuple

import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray


def track_laser(camera_resolution: Tuple[int, int], position: Dict):
    """
    Track the laser position using the PiCamera video stream
    :param camera_resolution: the resolution used to capture from the camera
    :param position: dict to update with the new laser position [x, y]
    :return: None
    """

    # track the progress
    frame_idx = 0

    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = camera_resolution
    camera.framerate = 12
    rawCapture = PiRGBArray(camera, size=camera_resolution)

    # allow the camera to warmup
    time.sleep(0.1)

    # initialize the background extractor
    bg_extractor = cv2.bgsegm.createBackgroundSubtractorMOG()

    logging.info('Camera + background extractor initialized, start processing video frames to locate laser')

    # loop on video frames
    for rawframe in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame_idx += 1
        frame = rawframe.array
        logging.debug("[{frame_idx}] : Processing frame".format(**locals()))

        # blur the frame to remove some noise before background detection
        blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)

        # generate a mask representing objects in motion
        # (white in motion from previous frame, black stay constant (background)
        motion_mask = bg_extractor.apply(blurred_frame)

        # extract contours out of the mask. Multiple contours may be found
        # Hint: we haven't used any cv2.threshold, but it's worth to investigate
        _, contours, _ = cv2.findContours(motion_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        logging.debug(
            "[{frame_idx}] : found {contour_nb} contours".format(frame_idx=frame_idx, contour_nb=len(contours)))

        # in our specific case, we expect only the laser to be moving and only one contour to be found.
        # If more are found it's probably noise and we should ignore it.
        if len(contours) == 1:
            contour = contours[0]
            # extract coordinates and radius of the contour
            (x, y), radius = cv2.minEnclosingCircle(contour)
            x = int(x)
            y = int(y)
            radius = int(radius)
            logging.debug("[{frame_idx}] : contour center : ({x}, {y} - radius: {radius})".format(**locals()))

            # the laser is very thin, if we find a shape which has a big radius, it's probably not the laser and should
            # be ignored
            if radius < 15:
                logging.debug("[{frame_idx}] : laser position updated: ({x}, {y})".format(**locals()))
                position["x"] = x
                position["y"] = y

        key = cv2.waitKey(1) & 0xff

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
