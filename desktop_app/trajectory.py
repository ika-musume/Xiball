from math import *

MAX_DISTANCE = 60

angle = 0
distance = 0

def increaseOrbitRadius():
    global angle, distance

    refX = 240 + int(cos(radians(angle))*distance)
    refY = 240 + int(sin(radians(angle))*distance)

    angle = angle + 4
    if(angle > 359):
        angle = angle - 360
        if(distance < MAX_DISTANCE):
            distance = distance + 2

    return refX, refY
