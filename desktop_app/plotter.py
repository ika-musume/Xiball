import numpy as np
import matplotlib.pyplot as plt

#value recorder
MAX_RECORDING_LENGTH = 600
addrCntr = 0
xPosBuf = np.zeros(shape=(MAX_RECORDING_LENGTH), dtype=int)
yPosBuf = np.zeros(shape=(MAX_RECORDING_LENGTH), dtype=int)

#plotter
fileNum = 0


def flushBuffer():
    global addrCntr, xPosBuf, yPosBuf

    addrCntr = 0
    xPosBuf = np.zeros(MAX_RECORDING_LENGTH)
    yPosBuf = np.zeros(MAX_RECORDING_LENGTH)

    plt.clf()

def recordValue(xPos, yPos):
    global addrCntr, xPosBuf, yPosBuf

    if(addrCntr < MAX_RECORDING_LENGTH):
        xPosBuf[addrCntr] = xPos - 240
        yPosBuf[addrCntr] = 240 - yPos
        addrCntr = addrCntr + 1
        
    elif(addrCntr == MAX_RECORDING_LENGTH):
        plotBuffer()
        addrCntr = addrCntr + 1

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
    
    fileNum = fileNum + 1


"""
xPosBuf[0] = 240 - 240
xPosBuf[1] = 360 - 240
xPosBuf[2] = 297 - 240
xPosBuf[3] = 120 - 240
xPosBuf[4] = 400 - 240
xPosBuf[5] = 98 - 240

yPosBuf[0] = 340 - 240
yPosBuf[1] = 410 - 240
yPosBuf[2] = 397 - 240
yPosBuf[3] = 20 - 240
yPosBuf[4] = 300 - 240
yPosBuf[5] = 198 - 240

plotBuffer()
"""

