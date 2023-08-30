from scipy.optimize import fsolve
from math import *
import time
import json

#constants
jd = 18  #the distance between two ball joints
pd = 10.4  #the distance between the center of the upper plate and a ball joint
m  = 7.5 #the distance between the center of the base plate and a servo axis
l1 = 6   #the length of the first part of an arm
l2 = 8.5 #the length of the second of an arm

#theta = azimuth angle(radian), start from +X axis, ccw
#phi = tilting angle(radian), 90deg - altitude
theta, phi = 0, 0

#conversion table
tablepath = './angle2motor.json'
angle2motor = dict() #declare empty dictionary


def equationLengthBetweenJoints(weights, *side):
    global theta, phi
    p, q, r = weights #unpack args
    s = side[0]

    #squared distance between the joint A and the joint B
    slAB = (-(sqrt(3)/2)*q * cos(theta))**2 + (((1/2)*q * cos(theta)) + (p * cos(theta)))**2 + ((-(1/2)*q * sin(theta)*sin(phi)) + ((sqrt(3)/2)*q * sin(theta)*cos(phi)) - (p * sin(theta)*sin(phi)))**2 - s**2
    
    #squared distance between the joint B and the joint C
    slBC = (((sqrt(3)/2)*r * cos(theta)) + ((sqrt(3)/2)*q * cos(theta)))**2 + (((1/2)*r * cos(theta)) - ((1/2)*q * cos(theta)))**2 + ((-(1/2)*r * sin(theta)*sin(phi)) - ((sqrt(3)/2)*r * sin(theta)*cos(phi)) + ((1/2)*q * sin(theta)*sin(phi)) - ((sqrt(3)/2)*q * sin(theta)*cos(phi)))**2 - s**2
    
    #squared distance between the joint C and the joint A
    slCA = (-(sqrt(3)/2)*r * cos(theta))**2+ ((-p * cos(theta)) - ((1/2)*r * cos(theta)))**2 + ((p * sin(theta)*sin(phi)) + ((1/2)*r * sin(theta)*sin(phi)) + ((sqrt(3)/2)*r * sin(theta)*cos(phi)))**2 - s**2

    return slAB, slBC, slCA


def equationServoJointpos(alpha, *pos):
    global m, l1, l2
    x, y, z = pos #unpack args

    #servo rotation angle
    return (sqrt(x**2 + y**2) - (m - l1*cos(alpha)))**2 + (z - l1*sin(alpha))**2 - (l2)**2


def calcServoAngle(azimuth_deg, tilt_deg):
    global theta, phi, jd, pd

    #deg to rad
    theta = radians(tilt_deg)
    phi = radians(azimuth_deg)

    #solve equations
    p, q, r = fsolve(equationLengthBetweenJoints, (1, 1, 1), args = 1) #unit triangle, 0.5~1.5
    p, q, r = p*jd, q*jd, r*jd #multiply

    #calculate positions
    xA, yA, zA = 0, p*cos(theta), -p * sin(theta)*sin(phi) + pd
    xB, yB, zB = (sqrt(3)/2)*q * cos(theta), -(1/2)*q * cos(theta), (1/2)*q * sin(theta)*sin(phi) - (sqrt(3)/2)*q * sin(theta)*cos(phi) + pd
    xC, yC, zC = -(sqrt(3)/2)*r * cos(theta), -(1/2)*r * cos(theta), (1/2)*r * sin(theta)*sin(phi) + (sqrt(3)/2)*r * sin(theta)*cos(phi) + pd

    angleA = round(degrees(fsolve(equationServoJointpos, pi/4, args = (xA, yA, zA))), 1) #start from 45 degrees
    angleB = round(degrees(fsolve(equationServoJointpos, pi/4, args = (xB, yB, zB))), 1)
    angleC = round(degrees(fsolve(equationServoJointpos, pi/4, args = (xC, yC, zC))), 1)

    return angleA, angleB, angleC


def makeConversionTable():
    global angle2motor

    azimuth, tilt = 0, 0
    angleA, angleB, angleC = 0, 0, 0

    for azimuth in range(0, 3600, 2):
        for tilt in range(0, 360, 2):
            angleA, angleB, angleC = calcServoAngle(azimuth/10, tilt/10) #get angle
            angleA, angleB, angleC = int(angleA*10), int(angleB*10), int(angleC*10) #formatting(for the STM32)
            print("azimuth = ", azimuth/10, ", tilt = ", tilt/10, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)

            dictKey = azimuth*1000 + tilt
            angle2motor[dictKey] = angleA, angleB, angleC

    with open(tablepath, 'w', encoding='utf-8') as outfile:
        json.dump(angle2motor, outfile)


def loadConversionTable():
    global angle2motor

    with open(tablepath, 'r', encoding='utf-8') as infile:
        angle2motor = json.load(infile)


def lookupServoAngle(azimuth_deg, tilt_deg):
    global angle2motor

    dictKey = int(azimuth_deg*10*1000 + tilt_deg*10)
    angleA, angleB, angleC = angle2motor[str(dictKey)]

    return angleA, angleB, angleC


loadConversionTable()
lookupServoAngle(359.8, 35.6)

"""
from servodrv import moveServoWithAngle

azimuth = 45
c = 0
for c in range(0, 360, 1):
    tilt = 15
    angleA, angleB, angleC = calcServoAngle(c, tilt)
    angleA, angleB, angleC = int(angleA*10), int(angleB*10), int(angleC*10)
    moveServoWithAngle(angleA, angleB, angleC)
    print("azimuth = ", c, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)
    time.sleep(0.003)

for c in range(0, 360, 1):
    tilt = 15
    angleA, angleB, angleC = calcServoAngle(c, tilt)
    angleA, angleB, angleC = int(angleA*10), int(angleB*10), int(angleC*10)
    moveServoWithAngle(angleA, angleB, angleC)
    print("azimuth = ", c, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)
    time.sleep(0.003)

for c in range(0, 360, 1):
    tilt = 15
    angleA, angleB, angleC = calcServoAngle(c, tilt)
    angleA, angleB, angleC = int(angleA*10), int(angleB*10), int(angleC*10)
    moveServoWithAngle(angleA, angleB, angleC)
    print("azimuth = ", c, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)
    time.sleep(0.003)

for c in range(0, 360, 1):
    tilt = 15
    angleA, angleB, angleC = calcServoAngle(c, tilt)
    angleA, angleB, angleC = int(angleA*10), int(angleB*10), int(angleC*10)
    moveServoWithAngle(angleA, angleB, angleC)
    print("azimuth = ", c, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)
    time.sleep(0.003)

for c in range(0, 360, 1):
    tilt = 15
    angleA, angleB, angleC = calcServoAngle(c, tilt)
    angleA, angleB, angleC = int(angleA*10), int(angleB*10), int(angleC*10)
    moveServoWithAngle(angleA, angleB, angleC)
    print("azimuth = ", c, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)
    time.sleep(0.003)

for c in range(0, 360, 1):
    tilt = 15
    angleA, angleB, angleC = calcServoAngle(c, tilt)
    angleA, angleB, angleC = int(angleA*10), int(angleB*10), int(angleC*10)
    moveServoWithAngle(angleA, angleB, angleC)
    print("azimuth = ", c, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)
    time.sleep(0.003)

time.sleep(0.003)
tilt = 0
azimuth = 90
angleA, angleB, angleC = calcServoAngle(tilt, azimuth)
angleA, angleB, angleC = int(angleA*10), int(angleB*10), int(angleC*10)
moveServoWithAngle(angleA, angleB, angleC)
print("azimuth = ", c, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)
"""