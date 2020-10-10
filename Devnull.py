import tkinter as tk
import tkinter.ttk as ttk
import time
import serial
import threading
import sys
import can
import math
import smbus2

data = {"NE":0, "PMTPB":0, "SGMTAUO":0, "TA2AT":0, "ENGTRQ":0, "ENGTHW":0, "VREQTRQ":0, "ATOTMP":0, "ABSSP1":0, "METSP1":0, "AP":0,"OILTEMP":0}
canBus = can.interface.Bus('can0', bustype = 'socketcan', bitrate = 500000, canfilters = None)

class CallBackFunction(can.Listener):
    def on_message_received(self, msg):
        if msg.arbitration_id == 0x040:
            data['NE'] = (msg.data[0] * 0x100 + msg.data[1]) * 12800 / 64 / 256
            data['PMTPB'] = (msg.data[3] * 0x100 + msg.data[4]) * 500 / 256 / 256
            data['SGMTAUO'] = (msg.data[5] * 0x100 + msg.data[6]) / 32
            data['XVTHDEF'] = (msg.data[2] & 0x40) / 0x40
            data['XFATHR'] = (msg.data[2] & 0x20) / 0x20
            data['XPMDEF'] = (msg.data[2] & 0x10) / 0x10
            data['XFAPM'] = (msg.data[2] & 0x08) / 0x08
        if msg.arbitration_id == 0x042:
            data['TA2AT'] = (msg.data[0] * 0x100 + msg.data[1]) * 125 / 64 / 256
            data['ENGTRQ'] = (msg.data[2] * 0x100 + msg.data[3]) / 64
            data['XTHWHIAT'] = (msg.data[4] & 0x02) / 0x02
            data['XVTHDEFAT'] = (msg.data[5] & 0x20) / 0x20
            data['XTHWNG'] = (msg.data[6] & 0x80) / 0x80
        if msg.arbitration_id == 0x3D1:
            data['THO'] = (msg.data[0] * 0x04 + (msg.data[1] & 0x0C) / 0x40) * 0.1 - 30
        if msg.arbitration_id == 0x044:
            data['ENGTHW'] = (msg.data[1] * 0x100 + msg.data[2]) * 0.01
            data['UREQTRQ'] = (msg.data[3] * 0x100 + msg.data[4]) / 64
        if msg.arbitration_id == 0x05A:
            data['ATOTMP'] = (msg.data[3] * 0x100 + msg.data[4]) * 0.01
        if msg.arbitration_id == 0x021:
            data['ABSSP1'] = (msg.data[1] * 0x100 + msg.data[2]) * 0.01
            data['VSCTRQR'] = (msg.data[0] * 0x80) / 0x80
            data['TRQLMTBK'] = (msg.data[1] * 0x100 + msg.data[2]) / 64
            data['XEGSTOPFREQ'] = (msg.data[5] & 0x02) / 0x02
        if msg.arbitration_id == 0x080:
            data['METSP1'] = (msg.data[0] * 0x100 + msg.data[1]) * 0.01

def getOilTemp():
    Temp = 0.0
    busOil = smbus2.SMBus(1)
    dataOil = busOil.read_i2c_block_data(0x68, 0x00, 2)
    busOil.write_i2c_block_data(0x68, 0b10001000, [0x00])
    
    rawOilTempData = dataOil[0]<<8 | dataOil[1]

    if rawOilTempData >32767:
        rawOilTempData -= 65535
 
    volume = 2.048/32767
    v = rawOilTempData*volume

    Rf = (v / (4.13 - v)) * 10000.0
    lnRf = Rf / 10000
    Temp = 3380 / (math.log(lnRf) + 3380 / 298.16) - 273.16
    return ('{:<.1f}'.format(Temp))
    return 'Oil'

def getWaterTemp():
    return ('{:<.1f}'.format(data['ENGTHW']))
    return 'Water'

def getCurrentTime():
    return time.strftime("%m/%d %H:%M:%S")

def updateWindow():
    waterTemp=tk.StringVar()
    waterTemp.set(getWaterTemp())
    engineRPM=tk.StringVar()
    engineRPM.set('ENGINERPM')
    oilTemp = tk.StringVar()
    oilTemp.set(getOilTemp())

    oilTitleLabel = tk.Label(root, text = 'OilTmep', fg = 'red', bg = 'gray12')
    oilTitleLabel.place(x=300,y=220)
    waterTitleLabel = tk.Label(root, text='WaterTmep', fg = "blue", bg = 'gray12')
    waterTitleLabel.place(x=570,y=220)
        
    oilTempLabel = tk.Label(root, textvariable = oilTemp, font = ("", 80), fg = "red", bg = 'gray12')
    oilTempLabel.place(x = 230, y = 235)
    waterTempLabel = tk.Label(root, textvariable = waterTemp, font = ("", 80), fg = "blue", bg = 'gray12')
    waterTempLabel.place(x = 520, y = 235)


busOil = smbus2.SMBus(1)
busOil.write_i2c_block_data(0x68, 0b10001000, [0x00])

call_back_function = CallBackFunction()
can.Notifier(bus, [call_back_function, ])

root = tk.Tk()
root.title("Developer's tool")
root.attributes('-fullscreen', True)
root.configure(bg = 'gray9')

root.after(10,updateWindow)

root.mainloop()