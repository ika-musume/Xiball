import serial
from time import sleep
import time

servoA_PW, servoB_PW, servoC_PW = 0, 0, 0
ser = serial.Serial(port = 'COM5', baudrate=19200, parity='N', stopbits=1, bytesize=8, timeout=8)

"""
DEPRECATED

#A Python prototype of the equivalent STM32 C function
def getPulseWidth(angle, pw0d, pw10d, pw20d, pw30d, pw40d, pw50d, pw60d, pw70d, pw80d, pw90d):
    if(angle < 20):
        return pw20d
    elif(angle < 30):
        return round(pw20d - ((pw20d-pw30d)/100)*((angle-20)*10))
    elif(angle < 40):
        return round(pw30d - ((pw30d-pw40d)/100)*((angle-30)*10))
    elif(angle < 50):
        return round(pw40d - ((pw40d-pw50d)/100)*((angle-40)*10))
    elif(angle < 60):
        return round(pw50d - ((pw50d-pw60d)/100)*((angle-50)*10))
    elif(angle < 70):
        return round(pw60d - ((pw60d-pw70d)/100)*((angle-60)*10))
    elif(angle < 80):
        return round(pw70d - ((pw70d-pw80d)/100)*((angle-70)*10))
    elif(angle < 90):
        return round(pw80d - ((pw80d-pw90d)/100)*((angle-80)*10))
    else:
        return pw90d

#A Python prototype of the equivalent STM32 C function
def moveServoWithPulse(angleA, angleB, angleC):
    global servoA_PW, servoB_PW, servoC_PW

    servoA_PW = getPulseWidth(angleA, 2400, 2310, 2228, 2130, 2025, 1935, 1840, 1740, 1640, 1535)
    servoB_PW = getPulseWidth(angleB, 2410, 2330, 2234, 2150, 2052, 1978, 1865, 1770, 1650, 1565)
    servoC_PW = getPulseWidth(angleC, 2410, 2320, 2220, 2140, 2040, 1960, 1860, 1755, 1640, 1515)

    ser.write(bytes('a' + str(servoA_PW) + str(servoB_PW) + str(servoC_PW), encoding='ascii'))
"""

def moveServoWithAngle(angleA, angleB, angleC):
    angleAstr = str(angleA)
    angleBstr = str(angleB)
    angleCstr = str(angleC)

    if(len(angleAstr) < 4): angleAstr = '0' + str(angleA)
    if(len(angleBstr) < 4): angleBstr = '0' + str(angleB)
    if(len(angleCstr) < 4): angleCstr = '0' + str(angleC)

    ser.write(bytes('f' + angleAstr + angleBstr + angleCstr, encoding='ascii'))

    #if(wasSent == 0): ser.write(bytes('i' + angleAstr + angleBstr + angleCstr, encoding='ascii'))
    #wasSent = wasSent ^ 1


#Towerpro Servo
#Servo A        Servo B         Servo C
#2400 = 0deg    2410 = 0deg     2410 = 0deg
#2310 = 10deg   2330 = 10deg    2320 = 10deg
#2228 = 20deg   2245 = 20deg    2220 = 20deg
#2130 = 30deg   2150 = 30deg    2140 = 30deg
#2025 = 40deg   2052 = 40deg    2040 = 40deg
#1935 = 50deg   1978 = 50deg    1960 = 50deg
#1840 = 60deg   1865 = 60deg    1860 = 60deg
#1740 = 70deg   1770 = 70deg    1755 = 70deg
#1640 = 80deg   1650 = 80deg    1640 = 80deg
#1535 = 90deg   1565 = 90deg    1515 = 90deg

#Hitec Servo
#Servo A        Servo B         Servo C
#0650 = 0deg    0665 = 0deg     0645 = 0deg
#0760 = 10deg   0765 = 10deg    0745 = 10deg
#0860 = 20deg   0865 = 20deg    0845 = 20deg
#0960 = 30deg   0965 = 30deg    0945 = 30deg
#1055 = 40deg   1060 = 40deg    1040 = 40deg
#1150 = 50deg   1150 = 50deg    1130 = 50deg
#1240 = 60deg   1245 = 60deg    1225 = 60deg
#1330 = 70deg   1340 = 70deg    1315 = 70deg
#1420 = 80deg   1430 = 80deg    1410 = 80deg
#1510 = 90deg   1525 = 90deg    1500 = 90deg

ser.write(bytes('f600045004500', encoding='ascii'))

#moveServoWithAngle(200, 25, 25)
#ser.write(bytes('i000000000', encoding='ascii'))




"""
DEPRECATED

from pyftdi.i2c import I2cController, I2cGpioPort
from pyftdi.eeprom import FtdiEeprom
from pyftdi.misc import hexdump

# Note that pyftdi uses libusbK driver that can be installed by Zadig.
# Change the USB driver to the FTDI official driver in Windows Device Manager 
# when the EEPROM needs to be modified.

def readEEPROM(device_id):
    eeprom = FtdiEeprom()
    eeprom.open(device_id) #default: ftdi://ftdi:232h:XIBALL/1
    #Ftdi().open_from_url('ftdi:///?')
    eeprom.dump_config()
    print(hexdump(eeprom.data))

def gpioI2C(device_id):
    i2c = I2cController()
    i2c.configure(device_id)
    i2c.set_gpio_direction(0x10, 0x10) #(mask, direction)

    gpio = I2cGpioPort(i2c) #declare gpio

    pins = 0
    gpio.write(pins)

    pins = gpio.read()

i2c = I2cController()
i2c.configure('ftdi://ftdi:232h:XIBALL/1')

slave = i2c.get_port(0x40)
slave.write_to(0x06, b'\xFF')
slave.write_to(0x07, b'\x07')
"""