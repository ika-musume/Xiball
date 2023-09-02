#import libraries
import cv2
import tkinter as tk
from PIL import Image, ImageTk

#import user sources
import imgproc
import calc
import pid


#Webcam settings, APC940
cam = cv2.VideoCapture(cv2.CAP_DSHOW+1)
cam.set(cv2.CAP_PROP_FPS, 60)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
if not cam.isOpened():
    print("Could not open an webcam")
    #exit()

#set main window's properties
controlInterface = tk.Tk()
controlInterface.title("Xiball")
controlInterface.geometry("960x480+100+100")
controlInterface.resizable(0, 0)

#make camera vision labels
camVision = tk.Label(controlInterface)
camVision.place(x=0, y=0)
fpsIndicator = tk.Label(controlInterface)
fpsIndicator.place(x=500, y=15)

#color picker
paletteInfo = tk.Label(controlInterface)
paletteInfo.place(x=770, y=15)
paletteColor = tk.Label(controlInterface)
paletteColor.place(x=920, y=14)

#mouse input handler
isMousePressed = 0
pointerX, pointerY = 0, 0
refX, refY = 240, 240
def mousePressed(event):
    global isMousePressed, pointerX, pointerY
    isMousePressed = 1
    pointerX, pointerY = event.x, event.y
def mouseReleased(event):
    global isMousePressed
    isMousePressed = 0
def keyPPressed(event):
    global isMousePressed, pointerX, pointerY
    if(isMousePressed):
        imgproc.getPixelFromPointer(pointerX, pointerY)
def keyRPressed(event):
    global isMousePressed, pointerX, pointerY
    global refX, refY
    if(isMousePressed):
        if(pointerX < 480 and pointerY < 480):
            refX = pointerX
            refY = pointerY
controlInterface.bind("<Button-3>", mousePressed)
controlInterface.bind("<ButtonRelease-3>", mouseReleased) 
controlInterface.bind("<p>", keyPPressed)
controlInterface.bind("<r>", keyRPressed)

#mode selector
modeRadioButton = tk.BooleanVar()
mode = 0
def setModeHSV():
    global mode
    mode = 0
def setModeRGB():
    global mode
    mode = 1

modeMessage = tk.Label(controlInterface, text = "Mode: ")
modeRGB = tk.Radiobutton(controlInterface, text = "RGB", variable = modeRadioButton, value = 1, command = setModeRGB)
modeHSV = tk.Radiobutton(controlInterface, text = "HSV", variable = modeRadioButton, value = 0, command = setModeHSV)
modeMessage.place(x=620, y=15)
modeRGB.place(x=710, y=14)
modeHSV.place(x=660, y=14)

#sensitivity sliders
sens0, sens1, sens2 = 0, 0, 0
sliderSens0Var, sliderSens1Var, sliderSens2Var = tk.IntVar(), tk.IntVar(), tk.IntVar()
def getSlider0(data):
    global sens0
    sens0 = int(data)
def getSlider1(data):
    global sens1 
    sens1 = int(data)
def getSlider2(data):
    global sens2
    sens2 = int(data)

sliderSens0 = tk.Scale(controlInterface, variable = sliderSens0Var, command = getSlider0, orient="horizontal", showvalue=True, to=64, length=300)
sliderSens1 = tk.Scale(controlInterface, variable = sliderSens1Var, command = getSlider1, orient="horizontal", showvalue=True, to=96, length=300)
sliderSens2 = tk.Scale(controlInterface, variable = sliderSens2Var, command = getSlider2, orient="horizontal", showvalue=True, to=96, length=300)
sliderSens0.place(x=610, y=50)
sliderSens1.place(x=610, y=90)
sliderSens2.place(x=610, y=130)

sliderH_R = tk.Label(controlInterface, text = "H sensitivity")
sliderS_G = tk.Label(controlInterface, text = "S sensitivity")
sliderV_B = tk.Label(controlInterface, text = "V sensitivity")
sliderH_R.place(x=520, y=68)
sliderS_G.place(x=520, y=108)
sliderV_B.place(x=520, y=148)

#mask enable button
showMask = 0
showMaskButtonVar = tk.BooleanVar()
def isMaskEnabled():
    global showMask
    showMask = showMaskButtonVar.get()
showMaskButton = tk.Checkbutton(controlInterface, text = "Show mask", variable = showMaskButtonVar, command = isMaskEnabled)
showMaskButton.place(x=850, y=175)

#PID coefficient sliders
pCoeff, iCoeff, dCoeff = 0, 0, 0
sliderPVar, sliderIVar, sliderDVar = tk.IntVar(), tk.IntVar(), tk.IntVar()
def getSliderP(data):
    global sens0, pCoeff
    pCoeff = int(data)
def getSliderI(data):
    global sens1, iCoeff
    iCoeff = int(data)
def getSliderD(data):
    global sens2, dCoeff
    dCoeff = int(data)

sliderSens0 = tk.Scale(controlInterface, variable = sliderPVar, command = getSliderP, orient="horizontal", showvalue=True, to=100, length=300, resolution=1)
sliderSens1 = tk.Scale(controlInterface, variable = sliderIVar, command = getSliderI, orient="horizontal", showvalue=True, to=100, length=300, resolution=1)
sliderSens2 = tk.Scale(controlInterface, variable = sliderDVar, command = getSliderD, orient="horizontal", showvalue=True, to=100, length=300, resolution=1)
sliderSens0.place(x=610, y=200)
sliderSens1.place(x=610, y=240)
sliderSens2.place(x=610, y=280)

sliderP = tk.Label(controlInterface, text = "P coefficient")
sliderI = tk.Label(controlInterface, text = "I coefficient")
sliderD = tk.Label(controlInterface, text = "D coefficient")
sliderP.place(x=520, y=218)
sliderI.place(x=520, y=258)
sliderD.place(x=520, y=298)



def updatePalette(palette, mode, h_r, s_g, v_b):
    palette = cv2.cvtColor(palette, cv2.COLOR_BGR2RGB)
    palette = Image.fromarray(palette)
    palettelabel = ImageTk.PhotoImage(image = palette)
    paletteColor.palettelabel = palettelabel
    paletteColor.configure(image = palettelabel)

    h_r = str(h_r)
    s_g = str(s_g)
    v_b = str(v_b)
    paletteMessage = ""
    if(mode == 0):
        paletteMessage = paletteMessage + "(H, S, V) = " + h_r + ", " + s_g + ", " + v_b

        sliderH_R.config(text = "H sensitivity")
        sliderS_G.config(text = "S sensitivity")
        sliderV_B.config(text = "V sensitivity")
    else:
        paletteMessage = paletteMessage + "(R, G, B) = " + h_r + ", " + s_g + ", " + v_b

        sliderH_R.config(text = "R sensitivity")
        sliderS_G.config(text = "G sensitivity")
        sliderV_B.config(text = "B sensitivity")

    paletteInfo.config(text = paletteMessage)

def updateCamVision(img):
    #update camera vision
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imglabel = ImageTk.PhotoImage(image = img)
    camVision.imglabel = imglabel
    camVision.configure(image = imglabel)
    camVision.after(1, main)

    #update frame indicator
    fps = imgproc.getFPS()
    fpsIndicator.config(text = "Current fps: " + fps)


def main():
    global refX, refY
    global pCoeff, iCoeff, dCoeff

    _, rawimg = cam.read() #get camera image
    img, palette, color0, color1, color2, mask, isBallPresent, ballX, ballY = imgproc.imgproc(rawimg, mode, sens0, sens1, sens2, refX, refY) #image processing

    #Update GUI elements
    updatePalette(palette, mode, color0, color1, color2) #update palette information
    if(showMask):
        updateCamVision(mask) #update tk labels
    else:
        updateCamVision(img) #update tk labels

    azimuth, tilt = pid.pidControlXY(pCoeff, iCoeff, dCoeff, pCoeff, iCoeff, dCoeff, ballX, ballY, refX, refY, 180, 1)
    

calc.loadConversionTable() #execute once
main()
camVision.mainloop()