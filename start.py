import tkinter as Tkinter
import os

def startDevTool():
	os.system('python3 devTool.py')

def startAssistanceMonitor():
	os.system('python3 AssistanceMonitor.py')

rootPanel = Tkinter.Tk()
rootPanel.title(u"CAN Selector")
rootPanel.geometry("1280x860")
buttonDriver = Tkinter.Button(text = u"ドライバー",width=100,height=10,command=startDevTool)
buttonDriver.place(x=0,y=0)
buttonDeveloper = Tkinter.Button(text = u"開発者",width=100,height=10,command=startAssistanceMonitor)
buttonDeveloper.place(x=0,y=200)

rootPanel.mainloop()
def __main__():
	pass
