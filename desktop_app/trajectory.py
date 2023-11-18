from math import *

MAX_DISTANCE = 120

angle = 0
distance = MAX_DISTANCE

def increaseOrbitRadius():
    global angle, distance

    refX = 240 + int(cos(radians(angle))*distance)
    refY = 240 + int(sin(radians(angle))*distance)

    angle = angle + 0.4
    if(angle > 359):
        angle = angle - 360

    return refX, refY
