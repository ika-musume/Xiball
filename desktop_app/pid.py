from math import *

#constants
plateVector = 10000
partialAccumulationPeriod = 60

#PID controller
#video width = 480, video height 480, maximum error is 480 pixels
#max(reference - actual position)

#reference: 240, 240
#ball pos: 360, 260
#xerr = 120, yerr = 20
#weightedErrorX = Kp*120 + Ki*3600 + Kd*(20/0.016667 = 1200) = 1200 + 3600 + 3600 = 8400

tilt_z, azimuth_z = 0, 0
errorListAddrCntr = 0 #error list address counter

#variables for pidConctolXY function
errorX_z, errorY_z = 0, 0 #previous errors
errorAccX, errorAccY = 0, 0 #error accumulator
partialErrorListX, partialErrorListY = [0]*partialAccumulationPeriod, [0]*partialAccumulationPeriod #holds errors from past one second
partialErrorAccX, partialErrorAccY = 0, 0 #partial error accumulator that sums the errors from past one second

def pidControlXY(isBallPresent, KpX, KiX, KdX, KpY, KiY, KdY, ballPosX, ballPosY, refPosX, refPosY, partialErrorThreshold, filterAzimuth, filterTilt):
    global partialAccumulationPeriod
    global errorX_z, errorY_z, errorAccX, errorAccY
    global partialErrorListX, partialErrorListY, partialErrorAccX, partialErrorAccY
    global errorListAddrCntr
    global tilt_z, azimuth_z

    # +X = +err   -X = -err

    if(not isBallPresent):
        errorX_z = 0; errorY_z = 0; errorAccX = 0; errorAccY = 0
        partialErrorAccX = 0; partialErrorAccY = 0
        errorListAddrCntr = 0

        for i in range(0, partialAccumulationPeriod, 1):
            partialErrorListX[i] = 0
            partialErrorListY[i] = 0
        
        return azimuth_z, tilt_z #keep the final values

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
        weightedErrorX = KpX*(errorX) + KdX*((errorX - errorX_z)/0.016667) #average 60fps
    else:
        weightedErrorX = KpX*(errorX) + KiX*errorAccX + KdX*((errorX - errorX_z)/0.016667) #average 60fps
    if(partialErrorAccY < partialErrorThreshold):
        errorAccY = 0 #clear accumulator
        weightedErrorY = KpY*(errorY) + KdY*((errorY - errorY_z)/0.016667)
    else:
        weightedErrorY = KpY*(errorY) + KiY*errorAccY + KdY*((errorY - errorY_z)/0.016667)

    #shift current error value
    errorX_z = errorX
    errorY_z = errorY

    #calc the magnitude of the X+Y vector
    magnitudeXY = round(sqrt(weightedErrorX**2 + weightedErrorY**2))

    #zero magnitude
    if(magnitudeXY == 0):
        azimuth = 0.0
        tilt = 0.0
    
    #if the angle between X+Y vector and the normal vector of the plate(10000) < 90deg
    elif(magnitudeXY < 10000):
        #atan2 negative(3rd and 4th quadrant)
        if(weightedErrorY < 0):
            azimuth = degrees(2*pi + atan2(weightedErrorY, weightedErrorX))

        #atns2 positive(1st and 2nd quadrant)
        else:
            azimuth = degrees(atan2(weightedErrorY, weightedErrorX))

        tilt = degrees(asin(magnitudeXY / 10000))

    #max angle
    else:
        #atan2 negative(3rd and 4th quadrant)
        if(weightedErrorY < 0):
            azimuth = degrees(2*pi + atan2(weightedErrorY, weightedErrorX))

        #atns2 positive(1st and 2nd quadrant)
        else:
            azimuth = degrees(atan2(weightedErrorY, weightedErrorX))

        tilt = 28.0 #clipping

    #tilting angle clipping
    if(tilt > 28.0): tilt = 28.0

    #azimuth is wrap-around value
    if(azimuth < 0.0): azimuth = 360.0 + azimuth
    elif(azimuth >= 360.0): azimuth = 360.0 - azimuth

    #filter
    azimuth = round(azimuth_z*(1 - filterAzimuth) + azimuth*filterAzimuth, 1)
    tilt = round(tilt_z*(1 - filterTilt) + tilt*filterTilt, 1)

    #shift current value
    azimuth_z = azimuth
    tilt_z = tilt

    #debug
    print(azimuth, tilt, errorAccX, partialErrorAccX, partialErrorAccY)

    return azimuth, tilt


#variables for pidConctolDist function
error_z = 0 #prev error
errorAcc = 0 #error accumulator
partialErrorList = [0]*partialAccumulationPeriod #holds errors from past one second
partialErrorAcc = 0 #partial error accumulator that sums the errors from past one second

def pidControlDist(isBallPresent, Kp, Ki, Kd, ballPosX, ballPosY, refPosX, refPosY, partialErrorThreshold, filterAzimuth, filterTilt):
    global partialAccumulationPeriod
    global error_z, errorAcc
    global partialErrorList, partialErrorAcc
    global errorListAddrCntr
    global tilt_z, azimuth_z

    # +X = +err   -X = -err

    if(not isBallPresent):
        error_z = 0; errorAcc = 0
        partialErrorAcc = 0
        errorListAddrCntr = 0

        for i in range(0, partialAccumulationPeriod, 1):
            partialErrorList[i] = 0
        
        return azimuth_z, tilt_z #keep the final values

    #calc new error value
    errorX = ballPosX - refPosX
    errorY = ballPosY - refPosY
    error = sqrt(errorX**2 + errorY**2)

    #accumulate errors, subtract the previous values and add the new values
    partialErrorAcc = partialErrorAcc - partialErrorList[errorListAddrCntr] + error

    #store the new error values
    partialErrorList[errorListAddrCntr] = error

    #wrap-around counter
    if(errorListAddrCntr < partialAccumulationPeriod - 1):
        errorListAddrCntr = errorListAddrCntr + 1
    else:
        errorListAddrCntr = 0

    #accumulate errors
    errorAcc = errorAcc + error

    #I control on/off
    if(partialErrorAcc < partialErrorThreshold):
        errorAcc = 0 #clear accumulator
        weightedError = Kp*(error) + Kd*((error - error_z)/0.016667) #average 60fps
    else:
        weightedError = Kp*(error) + Ki*errorAcc + Kd*((error - error_z)/0.016667) #average 60fps

    #shift current error value
    error_z = error

    #zero magnitude
    if(error == 0):
        azimuth = 0.0
        tilt = 0.0
    
    #if the angle between X+Y vector and the normal vector of the plate(10000) < 90deg
    elif(weightedError < 10000):
        azimuth = degrees(atan2(errorY, errorX) + pi)
        tilt = degrees(asin(weightedError / 10000))

    #max angle
    else:
        azimuth = degrees(atan2(errorY, errorX) + pi)
        tilt = 28.0 #clipping

    #tilting angle clipping
    if(tilt > 28.0): tilt = 28.0

    #azimuth is wrap-around value
    if(azimuth < 0.0): azimuth = 360.0 + azimuth
    elif(azimuth >= 360.0): azimuth = 360.0 - azimuth

    #filter
    azimuth = round(azimuth_z*(1 - filterAzimuth) + azimuth*filterAzimuth, 1)
    tilt = round(tilt_z*(1 - filterTilt) + tilt*filterTilt, 1)

    #shift current value
    azimuth_z = azimuth
    tilt_z = tilt

    #debug
    print(azimuth, tilt, errorAcc, partialErrorAcc)

    return azimuth, tilt