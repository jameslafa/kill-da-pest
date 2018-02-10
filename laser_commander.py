import logging
import time
from typing import Tuple

import RPi.GPIO as GPIO

# CONFIGURATION

# values representing the values for our servo motor borders. Requires calibration
LEFT = 9.4
RIGHT = 5.6
TOP = 5.9
BOTTOM = 8.5

# link to both initialized GPIO pin with PWM
servo_h = None
servo_v = None

# size of the plan the servo needs to move on
width = 0
height = 0


def setup_gpio(plan_size: Tuple[int, int]) -> None:
    """
    Must be called once before trying to move the laser.
    It initialize the GPIO.
    :param plan_size: tuple representing the plan size. Ex: (640, 480)
    :return: None
    """
    global width, height, servo_v, servo_h
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(24, GPIO.OUT)

    # set pin to pwm
    servo_v = GPIO.PWM(18, 50)
    servo_h = GPIO.PWM(24, 50)

    # set plan size
    width = plan_size[0]
    height = plan_size[1]


def center() -> None:
    """
    Center the laser in the middle of the plan
    :return: None
    """
    move_to(width / 2, height / 2)


def move_to(x: float, y: float, sleep_after_move: int = 1) -> None:
    """
    Move the laser to a precise coordinate on the plan
    :param x: the horizontal coordinate
    :param y: the vertical coordinate
    :param sleep_after_move: how long should the program sleep after the move, in seconds. Default: 1
    :return: None
    """

    # get the values required by the servo motors to move to the desired coordinates
    # we round the value to 1 digit to avoid the servo motor to get crazy
    h_value = round(__get_h_value(x), 1)
    v_value = round(__get_v_value(y), 1)

    # move the motors in the desired directions
    logging.debug("Move laser to ({x},{y}) -> ({h_value},{v_value})".format(x=x, y=y, h_value=h_value, v_value=v_value))
    servo_h.start(h_value)
    servo_v.start(v_value)

    # sleep to let the motors rest a little bit
    time.sleep(sleep_after_move)


def cleanup() -> None:
    """
    Clean up the GPIO. Should be called at the end of the program.
    :return: None
    """
    GPIO.cleanup()


def __get_h_value(x: float) -> float:
    """
    Calculate the value for the horizontal servo motor base the the desired horizontal coordinate
    :param x: the horizontal coordinate
    :return: the value to pass to the PWM servo motor
    """
    x_perc = x / width
    return LEFT - (x_perc * (LEFT - RIGHT))


def __get_v_value(y: float) -> float:
    """
    Calculate the value for the vertical servo motor base the the desired vertical coordinate
    :param y: the vertical coordinate
    :return: the value to pass to the PWM servo motor
    """
    y_perc = y / height
    return TOP - (y_perc * (TOP - BOTTOM))
