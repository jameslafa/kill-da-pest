## Kill Da Pest

This is a 3 days project that we realized with Filippo Galli at Hackmind.

### Idea

The global idea is to build a robot capable of detecting pests on a plant and then kill the pest directly on the plan instead of throwing tons of pesticide on the field as it's usually done.

With the constraint of a 3 days projects, the idea became:
  1. Using **Tensor Flow** detect a bird on a picture taken from a Raspberry Pi and find it's location. _We used a bird because we already had a Tensor Flow trained model._
  2. Using **Computer Vision**, detect and locate a laser pointer which will be used to aim the bird. We used *OpenCV*.
  3. Using the **Raspberry Pi GPIOs**, move 2 servo motors to aim the laser at the bird
  
### Implementation
 
#### Bird Detection
 
We used **Tensor Flow** and **Deep Learning** to locate the bird using the PiCamera. Compiling and installing Tensor Flow on a Raspberry Pi takes a lot of time so we decided at the end to run Tensor Flow on 
's laptop. The communication between the Raspberry Pi and Filippo's laptop was done using a small HTTP server/client made in Python.

The Raspberry Pi took a picture using the PiCamera, sent it to Filippo's laptop via HTTP POST and if a bird was found, the HTTP response would contain the coordinates of the bird on the picture.

```
2018-02-09 11:43:10,717 - Start locating the pest
2018-02-09 11:43:11,506 - Request Tensor Flow web server
2018-02-09 11:43:11,522 - Starting new HTTP connection (1): pjk.local
2018-02-09 11:43:13,795 - http://pjk.local:5000 "POST /find_pest HTTP/1.1" 200 7
2018-02-09 11:43:13,800 - Tensor Flow web server responded with : [154,342]
2018-02-09 11:43:13,824 - Pest located at position (154,342)
```

The code is available in [pest_finder.py](https://github.com/jameslafa/kill-da-pest/blob/master/pest_finder.py).

#### Laser Tracking

To get instant feedback of the laser position and keep adjusting its position in the direction of the bird we decided to use **Computer Vision** and **OpenCV**. It was the occasion to learn about it.

It took me a full day to figure out how to do it because I encountered many problems on the way:
  1. First I wanted to filter red objects on the picture to detect the laser. Unfortunately, because of the poor quality of the camera, the very bright laser pointer was seen as white by the camera instead of red. The accuracy was really low so this option was eliminated.
  2. Then I decided to extract the laser based on its round shape. Unfortunately, the laser is really small and represented two to three pixels on the picture and it was not really possible to detect any shape out of it.
  3. Finally, because the laser would be the only object in movement, I decided to use a background extractor to figure out which object was in movement. Even if the laser was quite small, the accuracy was actually quite good and usuable.

However, after having finally found a way to track the laser with a good accuracy, we haven't been able to use it in the Demo Day because it takes a significant amount of resources out of the Raspberry Pi and it couldn't send the pulse required to move the servo motors with accuracy when being under heavy load. The servo motors were going in every direction and were very unstable.

The code is available in [laser_tracker.py](https://github.com/jameslafa/kill-da-pest/blob/master/laser_tracker.py)

#### Laser Commander

To move the laser we assembled 2 servo motors on top of each other and attached a laser pointer on the upper one. Everything was taped together and ready to fall apart at any time, but luckily it held until Demo Time.

As explained above, we haven't been available to use the laser tracking with Computer Vision and moving the servo motors using PMW GPIOs at the same time. We would have had to build the laser commander with an Arduino but it wasn't possible in the remaining time.

We decided to fall back on something less scientific but efficient but using calibration. 

We looked for the values we have to give each servo motor to go to each corner of the frame and then we move the servo motors proportionnally.

This were the values we used for example:

```
LEFT = 9.4
RIGHT = 5.6
TOP = 5.9
BOTTOM = 8.5
```

To go to the coordinate (0,0) we would send to the horizontal servo motor the value `9.4` and the vertical servo motor `5.9`.

To go to the center of the frame we would send to the horizontal servo motor the value `(9.4-5.6)/2` and the vertical servo motor `(8.5-5.9)/2`.

You get the idea...

The code is available in [laser_commander.py](https://github.com/jameslafa/kill-da-pest/blob/master/laser_commander.py)

#### Run the whole thing

The whole program was run by [main.py](https://github.com/jameslafa/kill-da-pest/blob/master/main.py).


### How does it look like

Well to summarize, it looks like crap but well with 3 days, shitty motors and tape, what could we expect ;-)

![Installation](https://github.com/jameslafa/kill-da-pest/blob/master/pics/pic_1.jpg)

![Laser](https://github.com/jameslafa/kill-da-pest/blob/master/pics/pic_2.jpg)
  
  
  
