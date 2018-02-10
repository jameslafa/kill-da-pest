import logging
import time

import laser_commander
from pest_finder import locate_pest


def main():
    """
    This is the main program running the whole execution:
        1. set some configuration about the environment + initialize servo motors
        2. run an infinite loop doing the following:
            2.1. take a picture with the raspberry pi
            2.2. send the picture to the Tensor Flow engine via HTTP and get the coordinates of the detected pest
            2.3. when the best is located, move the laser to the pest coordinates
    :return:
    """
    # Basic configuration
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

    camera_resolution = (640, 480)
    tensor_flow_server_url = "http://pjk.local:5000/find_pest"

    # Setup GPIO and move the laser on the TOP LEFT corner
    laser_commander.setup_gpio(camera_resolution)
    laser_commander.move_to(0, 0)

    # Keep track of the position of the last pest.
    last_x = -9999
    last_y = -9999

    # Beginning of the infinite loop
    while True:
        # check if there is a pest and get its coordinates
        logging.info("Start locating the pest")
        x, y = locate_pest(camera_resolution, tensor_flow_server_url)

        # check if the new coordinates are far enough from the previous one to consider it has really moved.
        if (abs(last_x - x) > 10) and (abs(last_y - y) > 10):
            # we have new pest coordinates
            logging.info("Pest located at position ({x},{y})".format(x=x, y=y))

            # move the laser to the bird
            laser_commander.move_to(x, y)

            # update coordinates of the last bird targeted
            last_x = x
            last_y = y

            # wait 5 seconds before looking again for another bird
            time.sleep(5)


if __name__ == '__main__':
    main()
