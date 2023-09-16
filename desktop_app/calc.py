from scipy.optimize import fsolve
from math import *
import time
import json

#constants
jd = 18  #the distance between two ball joints
pd = 9.5  #the distance between the center of the base plate and the upper plate
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

    angleA = round(degrees(fsolve(equationServoJointpos, pi/4, args = (xA, yA, zA))), 2) #start from 45 degrees
    angleB = round(degrees(fsolve(equationServoJointpos, pi/4, args = (xB, yB, zB))), 2)
    angleC = round(degrees(fsolve(equationServoJointpos, pi/4, args = (xC, yC, zC))), 2)

    return int(angleA*100), int(angleB*100), int(angleC*100)


def makeConversionTable():
    global angle2motor

    azimuth, tilt = 0, 0
    angleA, angleB, angleC = 0, 0, 0

    for azimuth in range(0, 3600, 1):
        for tilt in range(0, 281, 1):
            angleA, angleB, angleC = calcServoAngle(azimuth/10, tilt/10) #get angle
            print("azimuth = ", azimuth/10, ", tilt = ", tilt/10, " | ", "A = ", angleA/100, ", B = ", angleB/100, ", C = ", angleC/100)

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

    azimuth = int(round(azimuth_deg, 1) * 10)
    tilt = int(round(tilt_deg, 1) * 10)

    dictKey = int(azimuth*1000 + tilt)
    angleA, angleB, angleC = angle2motor[str(dictKey)]

    return angleA, angleB, angleC


#makeConversionTable()
"""
from servodrv import moveServoWithAngle
loadConversionTable()
#tilt = 28
#azimuth = 90
#angleA, angleB, angleC = lookupServoAngle(azimuth, tilt)
#moveServoWithAngle(angleA, angleB, angleC)
#print("azimuth = ", azimuth, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)

tilt = 0
for i in range(0, 12, 1):
    for azimuth in range(0, 3600, 1):
        tilt = tilt + 0.00648
        tilt2 = round(tilt)
        if(tilt2 > 280): tilt2 = 280
        
        angleA, angleB, angleC = lookupServoAngle(azimuth/10, tilt2/10)
        moveServoWithAngle(angleA, angleB, angleC)
        print("azimuth = ", azimuth/10, "tilt = ", tilt2/10, " | ", "A = ", angleA/100, ", B = ", angleB/100, ", C = ", angleC/100)
        time.sleep(0.0001)

for i in range(0, 12, 1):
    for azimuth in range(0, 3600, 1):
        tilt = tilt - 0.00648
        tilt2 = round(tilt)
        if(tilt2 > 280): tilt2 = 280
        
        angleA, angleB, angleC = lookupServoAngle(azimuth/10, tilt2/10)
        moveServoWithAngle(angleA, angleB, angleC)
        print("azimuth = ", azimuth/10, "tilt = ", tilt2/10, " | ", "A = ", angleA/100, ", B = ", angleB/100, ", C = ", angleC/100)
        time.sleep(0.0001)
"""