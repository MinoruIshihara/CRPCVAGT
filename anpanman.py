import tkinter as tk
import tkinter.ttk as ttk

import time
import serial
import micropyGPS
import threading
import sys
import can
import math
import smbus2

coor = [[0,0],[0,0],[0,0],[0,0]] #[緯度1,経度1],[緯度2,経度2]...の形式で入力してください

data={"NE":0, "PMTPB":0, "SGMTAUO":0, "TA2AT":0, "ENGTRQ":0, "ENGTHW":0, "VREQTRQ":0, "ATOTMP":0, "ABSSP1":0, "METSP1":0, "AP":0,"OILTEMP":0}

rtime = 0
runtime = 0
starttime = 0
goaltime = 0
speed = 0
pointn = 3
point = 0
flag = 0
ss = 0
f=True
sbutton=False
t=True
x=0
lat=0.0
lon=0.0
laptime = 0.0
laptime1 = 0.0
laptime2 = 0.0
laptime3 = 0.0
laptime4 = 0.0
p = 0

gps=micropyGPS.MicropyGPS(9,'dd')

def rungps():
     s=serial.Serial('/dev/serial0',9600,timeout=10)#address
     s.readline()
     while True:
          sentence=s.readline().decode('utf-8')
          if(sentence==""):
              continue
          if (sentence[0]!='$'):
              continue
          for x in sentence:
              gps.update(x)
gpsthread1=threading.Thread(target=rungps,args=())
gpsthread1.daemon=True
gpsthread1.start()



def datalog():
    file = open('./datalog.txt', 'a')
    file.write(str(gps.latitude[0]) + ' ' + str(gps.longitude[0])+ ' ' + time.strftime("%y/%m/%d %H:%M:%S")+"\n")
    file.close()
    root.after(1000,datalog)

def laplog():
    global laptime
    file = open('./laplog.txt','a')
    file.write('地点 %d : %f \n' % (point+1, laptime))
    file.close()

def nextstep(event):
    global t
    t==False

def nextpoint(event):
    global pointn
    pointn=pointn+1
    if(point>pointn):
        t==False


#setting = tk.Tk()
#setting.title("setting")
#setting.geometry("400x400")
#static1 = tk.Label(text="区間数")
#static1.place(x=0, y=0)
#Entry1=tk.Entry(setting,width=100)
#Entry1.insert(tk.END,"0")
#Entry1.place(x=50,y=0)
#Button1=tk.Button(text='次へ')
#Button1.bind("<Button-1>",nextstep, sys.exit)
#Button1.place(x=100, y=200)


#while(t==True):
#    pointn = int(Entry1.get()) - 1


#t=True
#setting = tk.Tk()
#setting.title("setting")
#setting.geometry("400x400")

#while(t==True):
#    static1 = tk.Label(text="緯度")
#    static1.place(x=0, y=0)
#    static2 = tk.Label(text="経度")
#    static2.place(x=200, y=0)
#    Entry1=tk.Entry(setting,wieght=100)
#    Entry1.insert(tk.END,"0")
#    Entry1.place(x=50,y=0)
#    Entry2=tk.Entry(setting,wieght=100)
#    Entry2.place(x=200,y=200)
#    coor[point][0] = float(Entry1.get())
#    coor[point][1] = float(Entry2.get())
#    Button1=tk.Button(text='次へ')
#    Button1.bind("<Button-1>",nextpoint, command=sys.exit)
#    Button1.place(x=100, y=300)

root = tk.Tk()
root.title("V2")
root.geometry("800x420")
nb = ttk.Notebook(master = root)
tab1 = tk.Frame(nb)
tab2 = tk.Frame(nb)
nb.add(tab1,text = 'GPS')
nb.add(tab2,text = "CanView")
nb.pack()


#static2=tk.Label(text="{0:.2f}".format(rtime))

bus=can.interface.Bus('can0',bustype='socketcan',bitrate=500000,canfilters=None)
#Getting data
class CallBackFunction(can.Listener):
    def on_message_received(self,msg):
        if msg.arbitration_id == 0x040:
            data['NE'] = (msg.data[0] * 0x100 + msg.data[1]) * 12800 / 64 / 256
            data['PMTPB'] = (msg.data[3] * 0x100 + msg.data[4]) * 500 / 256 / 256
            data['SGMTAUO'] = (msg.data[5] * 0x100 + msg.data[6]) / 32
            data['XVTHDEF'] = (msg.data[2] & 0x40) / 0x40
            data['XFATHR'] = (msd.data[2] & 0x20) / 0x20
            data['XPMDEF'] = (msd.data[2] & 0x10) / 0x10
            data['XFAPM'] = (msd.data[2] & 0x08) / 0x08
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

var_water=tk.StringVar()
var_engine=tk.StringVar()

def Oil_temp():
    Temp = 0.0
    bus_oil=smbus2.SMBus(1)
    data_oil=bus_oil.read_i2c_block_data(0x68,0x00,2)
    bus_oil.write_i2c_block_data(0x68,0b10001000,[0x00])
    
    raw=data_oil[0]<<8 | data_oil[1]

    if raw >32767:
        raw-=65535
 
    vol=2.048/32767
    v=raw*vol

    Rf=(v/(4.13-v))*10000.0
    lnRf=Rf/10000
    Temp=3380/(math.log(lnRf)+3380/298.16)-273.16
    return ('{:<.1f}'.format(Temp))


def water_temp():
    var_water.set('{:<.1f}'.format(data['ENGTHW']))
    root.after(500,water_temp)

def engine():
    x = Oil_temp()
    var_engine.set(x)
    root.after(1000,engine)

call_back_function=CallBackFunction()
can.Notifier(bus,[call_back_function, ])

def window():
    global s,rtime,starttime,sbutton,speed,static2,point,lon,lat,x
    static1=tk.Label(root, textvariable=var_realtime, font=("",20))
    static1.place(x=0, y=320)
    #static2.destroy()
    static2=tk.Label(root, textvariable=var_stopwatch, text="{0:.2f}".format(rtime), font=("",100),justify="center")
    static2.place(x=0,y=-30)
    static7=tk.Label(root, textvariable=var_laptime, font=("",80))
    static7.place(x=450, y=100)
    static8=tk.Label(root, textvariable=var_titen, font=("",30))
    static8.place(x=200, y=150)
    #static3=tk.Label(text = starttime)
    #static3.place(x=0, y=300)
    #static4=tk.Label(text=gps.latitude[0])
    #static4.place(x=100,y=200)
    #static5=tk.Label(text=gps.longitude[0])
    #static5.place(x=100,y=220)
    #static6=tk.Label(text=coor[point][0] + coor[point][1])
    #static6.place(x=100,y=300)

    #Entry1=tk.Entry(root,wieght=100)
    #Entry1.place(x=100,y=350)
    #lat = float(Entry1.get())
    #Entry2=tk.Entry(root,wieght=100)
    #Entry2.place(x=200,y=350)
    #lon = float(Entry2.get())

    Button1=tk.Button(text='スタート',font=("",20))
    Button1.bind("<Button-1>",start)
    Button1.place(x=0, y=200)
    Button2=tk.Button(text='進む',font=("",20))
    Button2.bind("<Button-1>",next)
    Button2.place(x=0, y=151)
    Button3=tk.Button(text='戻る',font=("",20))
    Button3.bind("<Button-1>",back)
    Button3.place(x=100, y=151)
    Button4=tk.Button(text='前のラップ',font=("",20))
    Button4.bind("<Button-1>",back_lap)
    Button4.place(x=420, y=0)
    Button5=tk.Button(text='次のラップ',font=("",20))
    Button5.bind("<Button-1>",next_lap)
    Button5.place(x=550, y=0)
    #Button4=tk.Button(text='緯度')
    #utton4.bind("<Button-1>",relat)
    #Button4.place(x=150, y=300)
    #Button5=tk.Button(text='経度')
    #Button5.bind("<Button-1>",relon)
    #Button5.place(x=100, y=300)

    #var_water=tk.StringVar()
    #var_engine=tk.StringVar()

    call_back_function=CallBackFunction()
    can.Notifier(bus,[call_back_function, ])



    label_water = tk.Label(root, textvariable=var_water, font=("",80) , fg="blue")
    label_water.place(x=520, y=240)
    label_engine = tk.Label(root, textvariable=var_engine,font=("",80) , fg="red")
    label_engine.place(x=230, y=240)
    TxtWater = tk.Label(root,text='WaterTmp')
    TxtEngine = tk.Label(root,text='OilTmp')
    TxtWater.place(x=600,y=260)
    TxtEngine.place(x=300,y=260)
    #rtime=stopwatch(lat,lon)
    #root.after(500, window)

def eienloop():
    global lat,lon
    lat=coor[point][0]
    lon=coor[point][1]
    root.after(100,eienloop)

#root.after(500,water_temp)
#root.after(1000,engine)

def start(event):
    print('OK')
    global sbutton
    sbutton=True

def next(event):
    global point
    if (point<pointn):
        point=point+1

def back(event):
    global point
    if (point>0):
        point=point-1

def relat(event):
    global coor 
    Entry1.delete(0,tkinter.END)

def relon(event):
    global coor 
    Entry2.delete(0,tkinter.END)

def stopwatch(goallatitude,goallongitude):
    global f,runtime, starttime,goaltime,sbutton,point,laptime
    goallatitude += 0.00002
    goallongitude += 0.00002
    if sbutton:
        if data['METSP1'] > 15:
            starttime=time.time()
            print(starttime)
            f=False
            sbutton=False
    if not f:
        runtime=time.time() - starttime
        if (goallatitude-0.00005<= gps.latitude[0]):
            if (gps.latitude[0] <= goallatitude+0.00005):
                if (goallongitude-0.00005 <= gps.longitude[0]):
                    if (gps.longitude[0] <= goallongitude+0.00005):
                        goaltime=time.time()
                        print(goaltime)
                        f=True
                        runtime = goaltime - starttime
                        laptime = runtime
                        p = 0
                        if ss == 0:
                            laptime1 = laptime
                        elif ss == 1:
                            laptime2 = laptime
                        elif ss == 2:
                            laptime3 = laptime
                        elif ss == 3:
                            laptime4 = laptime
                        ss += 1
                        flag = ss
                        laplog()
                        point=point+1

    #root.after(100, stopwatch)
    return runtime

var_stopwatch=tk.StringVar()
var_realtime=tk.StringVar()
var_titen=tk.StringVar()
var_laptime=tk.StringVar()

def realtime():
    ss = time.strftime("%m/%d %H:%M:%S")
    return ss

def titen():
    global point
    tt = point + 1
    return tt

def laptimes():
    global laptime
    lp = "{:.2f}".format(float(laptime))
    return lp

def back_lap():
    global laptime, p
    p = 1
    if flag == 0 or flag == 1:
        lp = "{:.2f}".format(float(laptime))
        return lp
    elif flag == 2:
        flag = 1
        lp = "{:.2f}".format(float(laptime1))
        return lp
    elif flag == 3:
        flag = 2
        lp = "{:.2f}".format(float(laptime2))
        return lp
    elif flag == 4:
        flag = 3
        lp = "{:.2f}".format(float(laptime3))
        return lp

def next_lap():
    global laptime, p
    p = 2
    if flag == 4:
        lp = "{:.2f}".format(float(laptime4))
        return lp
    elif flag == 3:
        if ss > flag:
            flag = 4
            lp = "{:.2f}".format(float(laptime4))
            return lp
        else :
            lp = "{:.2f}".format(float(laptime))
            return lp
    elif flag == 2:
        if ss > flag:
            flag = 3
            lp = "{:.2f}".format(float(laptime3))
            return lp
        else :
            lp = "{:.2f}".format(float(laptime))
            return lp
    elif flag == 1:
        if ss > flag:
            flag = 2
            lp = "{:.2f}".format(float(laptime2))
            return lp
        else :
            lp = "{:.2f}".format(float(laptime))
            return lp
    
def reflesh():
    global lat, lon
    sw = '{:05.2f}'.format(stopwatch(lat,lon))
    if float(sw)/60.0 >= 1:
        sw=str('{:02}'.format(int(float(sw)/60)))+':'+str('{:05.2f}'.format(float(sw)%60))
    var_stopwatch.set(sw)
    x=realtime()
    var_realtime.set(x)
    y=titen()
    var_titen.set(y)
    if p == 0:
        z=laptimes()
        var_laptime.set(z)
    elif p == 1:
        z=back_lap()
        var_laptime.set(z)
    elif p == 2:
        z=next_lap()
        var_laptime.set(z)    
    root.after(10,reflesh)

#window()

bus_oil=smbus2.SMBus(1)
bus_oil.write_i2c_block_data(0x68,0b10001000,[0x00])

root.after(10,window)

root.after(100,eienloop)

root.after(2000,water_temp)
root.after(2000,engine)
root.after(10,reflesh)
root.after(1000,datalog)

root.mainloop()
