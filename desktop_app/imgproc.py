import cv2
import numpy as np
import time

#global variables
prevTimestamp, currentTimestamp = 0, 0
pointerX, pointerY = 0, 0
isMousePressed = 0
palette = np.zeros((20, 20, 3), dtype=np.uint8)
H, S, V, R, G, B = 0, 0, 0, 0, 0, 0

procStart, procEnd = 0, 0

def getFPS():
    global prevTimestamp
    global currentTimestamp

    currentTimestamp = time.time()
    if(currentTimestamp != prevTimestamp):
        fps = 1/(currentTimestamp - prevTimestamp)
        prevTimestamp = currentTimestamp
        fps = int(fps)
        fps = str(fps) + "fps"
        #cv2.putText(img, fps, (25,70), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 255, 0), 3, cv2.LINE_AA)
    else:
        fps = "60fps"

    return fps

#mouse click event
def getPixelFromPointer(pointerPosition):
    global pointerX, pointerY
    global isMousePressed

    pointerX, pointerY = pointerPosition.x, pointerPosition.y

    if(pointerX < 480 and pointerY < 480):
        isMousePressed = 1
    

def imgproc(rawimg, mode, sens0, sens1, sens2):
    global pointerX, pointerY
    global isMousePressed
    global palette
    global H, S, V, R, G, B

    global procStart, procEnd
    procStart = time.time()

    imgBGR = rawimg[0:, 80:560] #crop, BGR image
    
    #apply circle imgGray
    circleimgGray = np.zeros((480, 480, 3), dtype=np.uint8)
    cv2.circle(circleimgGray, (240, 240), 240, (255, 255, 255), -1, cv2.LINE_8, 0)
    imgBGR = imgBGR & circleimgGray

    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)

    if(isMousePressed):
        isMousePressed = 0

        #get pixel values
        if(mode == 0):
            pixelData = np.uint8(imgHSV[pointerY, pointerX])
            palette[:, :, :] = imgBGR[pointerY, pointerX]
            H = pixelData[0]
            S = pixelData[1]
            V = pixelData[2]

            
        else:
            pixelData = imgBGR[pointerY, pointerX]
            palette[:, :, :] = pixelData
            B = pixelData[0]
            G = pixelData[1]
            R = pixelData[2]

    #define uppder/lower boundary of color range
    if(mode == 0):
        #calculate boundary
        upperBoundary = np.array([H + sens0, S + sens1, V + sens2])
        lowerBoundary = np.array([H - sens0, S - sens1, V - sens2])

        #saturation
        upperBoundary = np.where(upperBoundary < 0, 0, upperBoundary)
        lowerBoundary = np.where(lowerBoundary < 0, 0, lowerBoundary)
        upperBoundary = np.where(upperBoundary > 255, 255, upperBoundary)
        lowerBoundary = np.where(lowerBoundary > 255, 255, lowerBoundary)

        #make a imgGray
        imgGray = cv2.inRange(imgHSV, lowerBoundary, upperBoundary)
    else:
        #calculate boundary
        upperBoundary = np.array([B + sens0, G + sens1, R + sens2])
        lowerBoundary = np.array([B - sens0, G - sens1, R - sens2])

        #saturation
        upperBoundary = np.where(upperBoundary < 0, 0, upperBoundary)
        lowerBoundary = np.where(lowerBoundary < 0, 0, lowerBoundary)
        upperBoundary = np.where(upperBoundary > 255, 255, upperBoundary)
        lowerBoundary = np.where(lowerBoundary > 255, 255, lowerBoundary)

        #make a imgGray
        imgGray = cv2.inRange(imgBGR, lowerBoundary, upperBoundary)
    
    #image preprocessing
    imgGray = cv2.blur(imgGray,(5,5))
    imgGray = cv2.erode(imgGray, None, iterations=4)
    imgGray = cv2.dilate(imgGray, None, iterations=3)
    
    #copy image since the function alters the original
    contours, _ = cv2.findContours(imgGray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #find longest contours
    if(len(contours) > 0):
        contourMaxLength = max(contours, key = cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(contourMaxLength)

        cv2.putText(imgBGR, "R=" + str(int(radius)), (400, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2) #print radius
        cv2.putText(imgBGR, "(" + str(int(x)) + ", " + str(int(y)) + ")", (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2) #print pos

        if (radius > 10 and radius < 80):
            cv2.circle(imgBGR, (int(x), int(y)), int(radius),(0, 255, 0), 2)


    imgGray = cv2.cvtColor(imgGray, cv2.COLOR_GRAY2BGR)

    #procEnd = time.time()
    #print(procEnd - procStart)

    if(mode == 0):
        return imgBGR, palette, H, S, V, imgGray
    else:
        return imgBGR, palette, R, G, B, imgGray