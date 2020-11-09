# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.ttk as ttk
import time
import serial
import threading
import sys
import can
import math
import smbus2

data={"oilTemp" : 0, "NE" : 0, "PMTPB" : 0, "SGMTAUO" : 0, "TA2AT" : 0, "ENGTRQ" : 0, "ENGTHW" : 0, "UREQTRQ" : 0, "ATOTMP" : 0, "ABSSP1" : 0, "METSP1" : 0, "AP" : 0, "OILTEMP" : 0, "XPMDEF" : 0, "XTHWHIAT" : 0, "XTHWNG" : 0, "XFAPM" : 0, "XFATHR" : 0, "XVTHDEFAT" : 0, "XVTHDEF" : 1, "TRQLMTBK" : 0,"VSCTRQR" : 0, "XEGSTOPFREQ" : 0}
dataName = ["oilTemp", "NE", "PMTPB", "SGMTAUO", "TA2AT","ENGTRQ", "ENGTHW", "UREQTRQ", "ABSSP1", "TRQLMTBK", "METSP1"]
flagName={"XVTHDEF":"スロットルセンサーフェイルセーフ中","XFATHR":"スロットルセンサーフェイル","XPMDEF":"PMセンサーフェイルセーフ中","XFAPM":"PMセンサーフェイル","XTHWHIAT":"高水温","XVTHDEFAT":"スロットルセンサーフェイルセーフ中 AT","XTHWNG":"エンジン水温異常","VSCTRQR":"トルクダウン要求","XEGSTOPFREQ":"エンジン始動中止要求"}
dataNameJP = {"oilTemp" : "油温", "NE":"エンジン回転数","PMTPB":"仮想吸気管圧力","SGMTAUO":"燃料噴射量","TA2AT":"スロットル開度","ENGTRQ":"エンジントルク","ENGTHW":"エンジン水温","UREQTRQ":"ユーザー要求トルク","ABSSP1":"ABS(VSC)車速","TRQLMTBK":"VSC要求トルク","METSP1":"メーター車速"}
canBus = can.interface.Bus('can0', bustype = 'socketcan', bitrate = 500000, canfilters = None)

root = tk.Tk()
root.title("Developer's tool")
root.attributes('-fullscreen', True)
root.configure(bg = '#ffffff')
root.bind('<Escape>', lambda e: root.quit())

titleLabel = dict()
valueLabel = dict()
valueString = dict()
numofElement = 0
topFrame = tk.Frame(root, bg = 'black')
topFrame.pack(fill = tk.BOTH)
menuFrame = tk.Frame(topFrame)
menuFrame.pack()
variableFrame = tk.Frame(topFrame, bg = '#080805')
variableFrame.pack(fill = tk.X, anchor = tk.CENTER)
flagFrame = tk.Frame(topFrame, bg = '#080805')
flagFrame.pack(fill = tk.X)
exitButton = tk.Button(menuFrame, text = '終了', font = ('', 20), width = 1080, bg = '#080805', fg = 'white')
exitButton.pack()
exitButton.bind("<Button-1>",exit)

print(data["VSCTRQR"])
dataName.sort()
print(data["VSCTRQR"])
for enName in dataName:
	titleLabel[enName] = tk.Label(variableFrame,text = dataNameJP[enName], font = ("", 20), bg = '#080805', fg = 'white')
	titleLabel[enName].grid(row = numofElement // 3 * 2,column = numofElement % 3, padx = 15)
	valueString[enName] = tk.DoubleVar()
	valueLabel[enName] = tk.Label(variableFrame,textvariable = valueString[enName], font = ("", 20), bg = '#080805', fg = 'white')
	valueLabel[enName].grid(row = numofElement // 3 * 2 + 1,column = numofElement % 3)
	numofElement += 1

flagLabel = dict()
flagString = dict()
flagName = sorted(flagName.items())
for n, enName in enumerate(flagName):
	flagString[enName[0]] = tk.StringVar()
	flagLabel[enName[0]] = tk.Label(flagFrame,textvariable = flagString[enName[0]], font = ('', 12), bg = "#080805", fg = "orange")
	flagLabel[enName[0]].grid(row = n % 3, column = int(n / 3))
class CallBackFunction(can.Listener):
    def on_message_received(self, msg):
#        print('call_back id = ', msg.arbitration_id)
        if msg.arbitration_id == 0x040:
            data['NE'] = (msg.data[0] * 0x100 + msg.data[1]) * 12800 / 64 / 256
            data['PMTPB'] = (msg.data[3] * 0x100 + msg.data[4]) * 500 / 256 / 256
            data['SGMTAUO'] = (msg.data[5] * 0x100 + msg.data[6]) / 32
            data['XVTHDEF'] = (msg.data[2] & 0x40) / 0x40
            data['XFATHR'] = (msg.data[2] & 0x20) / 0x20
            data['XPMDEF'] = (msg.data[2] & 0x10) / 0x10
            data['XFAPM'] = (msg.data[2] & 0x08) / 0x08
            #print('msg:', data['NE'])
        if msg.arbitration_id == 0x042:
            data['TA2AT'] = (msg.data[0] * 0x100 + msg.data[1]) * 125 / 64 / 256
            data['ENGTRQ'] = (msg.data[2] * 0x100 + msg.data[3]) / 64
            data['XTHWHIAT'] = (msg.data[4] & 0x02) / 0x02
            data['XVTHDEFAT'] = (msg.data[5] & 0x20) / 0x20
            data['XTHWNG'] = (msg.data[6] & 0x80) / 0x80
        if msg.arbitration_id == 0x3D1:
            data['THO'] = (msg.data[0] * 0x04 + (msg.data[1] & 0x0C) / 0x40) * 0.1 - 30
        if msg.arbitration_id == 0x044:
            print('id = 68')
            data['ENGTHW'] = (msg.data[1] * 0x100 + msg.data[2]) * 0.01
            data['UREQTRQ'] = (msg.data[3] * 0x100 + msg.data[4]) / 64
        if msg.arbitration_id == 0x05A:
            data['ATOTMP'] = (msg.data[3] * 0x100 + msg.data[4]) * 0.01
        if msg.arbitration_id == 0x021:
            data['ABSSP1'] = (msg.data[1] * 0x100 + msg.data[2]) * 0.01
            data['VSCTRQR'] = (msg.data[0] * 0x80) / 0x80
            data['TRQLMTBK'] = (msg.data[1] * 0x100 + msg.data[2]) / 64
            data['XEGSTOPFREQ'] = (msg.data[5] & 0x02) / 0x02
            #print('APSSP1', data['ABSSP1'])
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

def getCurrentTime():
    return time.strftime("%m/%d %H:%M:%S")

def updateWindow():
	for enName in dataName :
		if enName == "oilTemp":
			valueString[enName].set(getOilTemp())
			print(enName, ':', getOilTemp())
		else :
			valueString[enName].set('{:.1f}'.format(data[enName]))
			print(enName, ':', data[enName])
	for n, enName in enumerate(flagName):
		flagLabel[enName[0]].grid_forget()
		flagString[enName[0]].set(enName[1])
		if data[enName[0]] != 0 :
			flagLabel[enName[0]] = tk.Label(flagFrame,textvariable = flagString[enName[0]], font = ('', 12), bg = "#080805", fg = "orange")
			flagLabel[enName[0]].grid(row = n % 3, column = int(n / 3), padx = 12)
		#flagLabel[enName].pack()
		else :
			flagLabel[enName[0]] = tk.Label(flagFrame,textvariable = flagString[enName[0]], font = ('', 12), bg = "#080805", fg = "blue2")
			flagLabel[enName[0]].grid(row = n % 3, column = int(n / 3), padx = 12)
	root.after(1000,updateWindow)

busOil = smbus2.SMBus(1)
busOil.write_i2c_block_data(0x68, 0b10001000, [0x00])

call_back_function = CallBackFunction()
can.Notifier(canBus, [call_back_function, ])



root.after(100, updateWindow)
root.mainloop()
