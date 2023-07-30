from scipy.optimize import fsolve
from math import *
import time

#constants
jd = 17  #the distance between two ball joints
pd = 11  #the distance between the center of the upper plate and a ball joint
m  = 7.5 #the distance between the center of the base plate and a servo axis
l1 = 6   #the length of the first part of an arm
l2 = 8.5 #the length of the second of an arm

#theta = azimuth angle(radian), start from +X axis, ccw
#phi = tilting angle(radian), 90deg - altitude
theta, phi = 0, 0


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


def getServoAngle(theta_deg, phi_deg):
    global theta, phi, jd, pd

    #deg to rad
    theta = radians(theta_deg)
    phi = radians(phi_deg)

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

azimuth = 80
tilt = 17


angleA, angleB, angleC = getServoAngle(tilt, azimuth)
print("azimuth = ", azimuth, ", tilt = ", tilt, " | ", "A = ", angleA, ", B = ", angleB, ", C = ", angleC)