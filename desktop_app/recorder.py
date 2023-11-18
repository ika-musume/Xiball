import numpy as np
import matplotlib.pyplot as plt

#value recorder
MAX_RECORDING_LENGTH = 2400
addrCntr = 0

refPointLog = np.zeros(shape=(MAX_RECORDING_LENGTH, 2), dtype=int)
currPosLog = np.zeros(shape=(MAX_RECORDING_LENGTH, 2), dtype=int)
controlLog = np.zeros(shape=(MAX_RECORDING_LENGTH, 2))
motorAngleLog = np.zeros(shape=(MAX_RECORDING_LENGTH, 3))


#plotter
fileNum = 0


def flushBuffer():
    global addrCntr, refPointLog, currPosLog, controlLog, motorAngleLog

    addrCntr = 0
    refPointLog = np.zeros(shape=(MAX_RECORDING_LENGTH, 2), dtype=int)
    currPosLog = np.zeros(shape=(MAX_RECORDING_LENGTH, 2), dtype=int)
    controlLog = np.zeros(shape=(MAX_RECORDING_LENGTH, 2))
    motorAngleLog = np.zeros(shape=(MAX_RECORDING_LENGTH, 3))

def recordValue(xRef, yRef, xPos, yPos, tilt, azimuth, servoA, servoB, servoC):
    global addrCntr, refPointLog, currPosLog, controlLog, motorAngleLog

    if(addrCntr < MAX_RECORDING_LENGTH):
        refPointLog[addrCntr] = (xRef, yRef)
        currPosLog[addrCntr] = (xPos - 240, 240 - yPos)
        controlLog[addrCntr] = (tilt, azimuth)
        motorAngleLog[addrCntr] = (servoA, servoB, servoC)

        addrCntr = addrCntr + 1
        
    elif(addrCntr == MAX_RECORDING_LENGTH):
        #plotBuffer()
        saveCSV()
        addrCntr = addrCntr + 1

    #plt.clf()

"""
def plotBuffer():
    global xPosBuf, yPosBuf, fileNum

    x = np.linspace(0, MAX_RECORDING_LENGTH - 1, MAX_RECORDING_LENGTH)
    plt.plot(x, xPosBuf, 'b-', x, yPosBuf, 'r-')
    plt.xlabel("samples")
    plt.ylabel("pos(pixel)")
    plt.xlim([0, MAX_RECORDING_LENGTH])
    plt.ylim([-240, 240])
    #plt.show()
    plt.savefig("GRAPH" + str(fileNum))
    print("GRAPH" + str(fileNum) + " SAVED")
    plt.clf()

    fileNum = fileNum + 1
"""

def saveCSV():
    global fileNum

    merged = np.concatenate((refPointLog, currPosLog, controlLog, motorAngleLog), axis=1)
    np.savetxt("LOG" + str(fileNum) + ".csv", merged, delimiter=",", fmt="%.2f")
    print("LOG" + str(fileNum) + " SAVED")

    fileNum = fileNum + 1

    