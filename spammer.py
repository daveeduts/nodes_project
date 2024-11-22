import pyautogui as pt
import time


msj = "SINGURU BOT DE AICI E SPADES!"
n = 15

def spam(mesaj, n):
    
    time.sleep(3)
    for m in range(n):
        
        pt.typewrite(mesaj)
        pt.press("enter")
        time.sleep(0.1)

spam(msj,n)