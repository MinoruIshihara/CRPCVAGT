import tkinter as tk
import tkinter.ttk as ttk
import time
import serial
import threading
import sys
import can
import math
import smbus2

data = {"NE":0, "PMTPB":0, "SGMTAUO":0, "TA2AT":0, "ENGTRQ":0, "ENGTHW":0, "UREQTRQ":0, "ATOTMP":0, "ABSSP1":0, "METSP1":0, "AP":0,"OILTEMP":0}
dataName = {"NE","PMTPB","SGMTAUO","TA2AT","ENGTRQ","ENGTHW","UREQTRQ","ABSSP1","TRQLMTBK","METSP1"}
flagNameJP = {"XVTHDEF":"�X���b�g���Z���T�[�t�F�C���Z�[�t��","XFATHR":"�X���b�g���Z���T�[�t�F�C��","XPMDEF":"PM�Z���T�[�t�F�C���Z�[�t��","XFAPM":"PM�Z���T�[�t�F�C��","XTHWHIAT":"������","XVTHDEFAT":"�X���b�g���Z���T�[�t�F�C���Z�[�t��","XTHWNG":"�G���W�������ُ�","VSCTRQR":"�g���N�_�E���v��","XEGSTOPFREQ":"�G���W���n�����~�v��"
dataNameJP = {"NE":"�G���W����]��","PMTPB":"���z�z�C�ǈ���","SGMATAUO":"�R�����˗�","TA2AT":"�X���b�g���J�x","ENGTRQ":"�G���W���g���N","ENGTHW":"�G���W������","UREQTRQ":"���[�U�[�v���g���N","ABSSP1":"ABS(VSC)�ԑ�","TRQLMTBK":"VSC�v���g���N","METSP1":"���[�^�[�ԑ�"}
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
	variableFrame = tk.Frame(root)
	variableFrame.grid(row = 0,column = 0)
	flagFrame = tk.Frame(root)
	flagFrame.grid(row = 1.column = 0)
	
	titleLabel = dict()
	valueLabel = dict()
	numofElement = 0
	for enName in dataName
		titleLabel[enName] = tk.Label(variableFrame,text = dataNameJP[enName])
		titleLabel[enName].grid(row = numofElement // 3 * 2,column = numofElement % 3)
		valueLabel[enName] = tk.Label(variableFrame,textvariable = data[enName])
		valueLabel[enName].grid(row = numofElement // 3 * 2 + 1,column = numofElement % 3)
		numofElement += 1
	
	flagLabel = dict()
	for enName in flagName.keys()
		if data[enName] != 0 :
			dictLabel[enName] = tk.Label(flagFrame,text = flagName[enName])
			ditcLabel[enName].pack()
	root.after(10,updateWindow)


busOil = smbus2.SMBus(1)
busOil.write_i2c_block_data(0x68, 0b10001000, [0x00])

call_back_function = CallBackFunction()
can.Notifier(bus, [call_back_function, ])

root = tk.Tk()
root.title("Developer's tool")
root.attributes('-fullscreen', True)
root.configure(bg = 'gray9')

root.mainloop()