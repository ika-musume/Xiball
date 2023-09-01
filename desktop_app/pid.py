from math import *

#PID controller
#video width = 480, video height 480, maximum error is 480 pixels
#max(reference - actual position)

#reference: 240, 240
#ball pos: 360, 260
#xerr = 120, yerr = 20
#weightedX = p*120 + i*3600 + d*(20/0.016667 = 1200) = 1200 + 3600 + 3600 = 8400

errorX_z, errorY_z = 240, 240 #previous errors
errorAccX, errorAccY = 0, 0 #error accumulator

partialAccumulationPeriod = 60
errorListAddrCntr = 0 #error list address counter
partialErrorListX, partialErrorListY = [0]*partialAccumulationPeriod, [0]*partialAccumulationPeriod #holds errors from past one second
partialErrorAccX, partialErrorAccY = 0, 0 #partial error accumulator that sums the errors from past one second

plateVector = 10000

def pidControlXY(p, i, d, ballPosX, ballPosY, refPosX, refPosY, partialErrorThreshold):
    global errorX_z, errorY_z, errorAccX, errorAccY
    global partialErrorListX, partialErrorListY, partialErrorAccX, partialErrorAccY
    global errorListAddrCntr

    #calc new error value
    errorX = refPosX - ballPosX
    errorY = refPosY - ballPosY

    #accumulate partial errors, subtract the previous values and add the new values
    partialErrorAccX = partialErrorAccX - partialErrorListX[errorListAddrCntr] + errorX 
    partialErrorAccY = partialErrorAccY - partialErrorListY[errorListAddrCntr] + errorY 

    #store the new error values
    partialErrorListX[errorListAddrCntr] = errorX
    partialErrorListY[errorListAddrCntr] = errorY

    #wrap-around counter
    if(errorListAddrCntr < partialAccumulationPeriod - 1):
        errorListAddrCntr = errorListAddrCntr + 1
    else:
        errorListAddrCntr = 0

    #accumulate errors
    errorAccX = errorAccX + errorX
    errorAccY = errorAccY + errorY

    #I control on/off
    if(partialErrorAccX < partialErrorThreshold):
        errorAccX = 0 #clear accumulator
        weightedX = p*(errorX) + d*((errorX - errorX_z)/0.016667) #average 60fps
    else:
        weightedX = p*(errorX) + i*errorAccX + d*((errorX - errorX_z)/0.016667) #average 60fps
    if(partialErrorAccY < partialErrorThreshold):
        errorAccY = 0 #clear accumulator
        weightedY = p*(errorY) + d*((errorY - errorY_z)/0.016667)
    else:
        weightedY = p*(errorY) + i*errorAccY + d*((errorY - errorY_z)/0.016667)

    #shift prev error value
    errorX_z = errorX
    errorY_z = errorY


    magnitudeXY = round(sqrt(weightedX**2 + weightedY**2))

    if(magnitudeXY == 0):
        tilt = 0.0
        azimuth = 0.0
        
    elif(magnitudeXY < 10000):
        tilt = round(degrees(asin(magnitudeXY / 10000)), 1)
        azimuth = 0.0

    else:
        tilt = 28.0
        azimuth = 0.0 

    print(azimuth, tilt, errorAccX, partialErrorAccX, partialErrorAccY  )

    return azimuth, tilt


def pidControlDist(p, i, d, ballPosX, ballPosY, refPosX, refPosY, partialErrorThreshold):
    #calc error value
    errorX = refPosX - ballPosX
    errorY = refPosY - ballPosY
    errorDist = sqrt(errorX**2 + errorY**2)