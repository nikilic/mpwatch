import RPi.GPIO as GPIO
import os
import time
import thread
import Adafruit_CharLCD as LCD
from threading import Timer,Thread,Event
from config import *
from flask import Flask, request
app = Flask(__name__)

global state, written, hourstart, minutestart, menuselect, strchange, blackhour, blackminute, blacksecond, blackperiod, blacktime, blackflag
global whitehour, whiteminute, whitesecond, whiteperiod, whitetime, whiteflag, modeselect, byoperiod, byotime, count

blackhour = 0
blackminute = 0
blacksecond = 0
whitehour = 0
whiteminute = 0
whitesecond = 0
blackflag = False
whiteflag = False
blackperiod = 0
whiteperiod = 0
blacktime = 0
whitetime = 0
count = 0


state = 0
written = 0

# Raspberry Pi pin setup
lcd_rs = 26
lcd_en = 16
lcd_d4 = 23
lcd_d5 = 13
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 2

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

clear = lambda: os.system('clear')

GPIO.setmode(GPIO.BCM)

GPIO.setup(LEFT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # black/left
GPIO.setup(RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # white/right
GPIO.setup(ENTER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # enter
GPIO.setup(LED_GPIO, GPIO.OUT)  # LED


class PerpetualTimer:

    def __init__(self, t, hFunction):
        self.t=t
        self.hFunction = hFunction
        self.thread = Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


def second():
    global blackhour, blackminute, blacksecond, blackperiod, blacktime, blackflag, whitehour, whiteminute, whitesecond, whiteperiod, whitetime, whiteflag, state, strchange
    while True:
        if state == STATE_BLACK_MOVE:
            if not blackflag:
                blacksecond -= 1
                if blacksecond < 0:
                    blacksecond = 59
                    blackminute -= 1
                    if blackminute < 0:
                        blackminute = 59
                        blackhour -= 1
                        if blackhour < 0:
                            blackflag = True
            else:
                blacktime -= 1
                if blacktime < 0:
                    blackperiod -= 1
                    blacktime = byotime
                    if blackperiod < 0:
                        state = STATE_WHITE_WIN
            strchange = True

        if state == STATE_WHITE_MOVE:
            if not whiteflag:
                whitesecond -= 1
                if whitesecond < 0:
                    whitesecond = 59
                    whiteminute -= 1
                    if whiteminute < 0:
                        whiteminute = 59
                        whitehour -= 1
                        if whitehour < 0:
                            whiteflag = True
            else:
                whitetime -= 1
                if whitetime < 0:
                    whiteperiod -= 1
                    whitetime = byotime
                    if whiteperiod < 0:
                        state = STATE_BLACK_WIN
            strchange = True
        time.sleep(1.0)


def Start():
    global state, menuselect, hourstart, minutestart, strchange, byoperiod, byotime
    lcd.clear()
    lcd.message("WELCOME TO\nPUPIN CLOCK")
    time.sleep(2.0)
    menuselect = 0
    hourstart = 1
    minutestart = 0
    byoperiod = 6
    byotime = 30
    strchange = True
    state = STATE_SELECT


def Select():
    global hourstart, minutestart, byoperiod, byotime, menuselect, strchange, state, modeselect
    modeselect = 0
    if strchange:
        strToPrint = str(hourstart)+":"+str(minutestart)+":0-"+str(byoperiod)+"/"+str(byotime)
        if menuselect == 0:
            strToPrint += "\n>H<-M-MOD-START"
        elif menuselect == 1:
            strToPrint += "\nH->M<-MOD-START"
        elif menuselect == 2:
            strToPrint += "\nH-M->MOD<-START"
        elif menuselect == 3:
            strToPrint += "\nH-M-MOD->START<"
        lcd.clear()
        lcd.message(strToPrint)
        strchange = False

    left_state = GPIO.input(LEFT_GPIO)
    right_state = GPIO.input(RIGHT_GPIO)
    enter_state = GPIO.input(ENTER_GPIO)

    if not left_state:
        menuselect -= 1
        strchange = True
        if menuselect == -1:
            menuselect = 3
        time.sleep(0.2)

    if not right_state:
        menuselect += 1
        strchange = True
        if menuselect == 4:
            menuselect = 0
        time.sleep(0.2)

    if not enter_state:
        if menuselect == 0:
            state = STATE_CH_HOUR
        elif menuselect == 1:
            state = STATE_CH_MINUTE
        elif menuselect == 2:
            state = STATE_CH_MODE
        elif menuselect == 3:
            state = STATE_BEGIN
        strchange = True
        time.sleep(0.2)


def ChangeHour():
    global strchange, hourstart, state
    if strchange:
        strToPrint = "Hours of play:\n" + str(hourstart)
        lcd.clear()
        lcd.message(strToPrint)
        strchange = False

    right_state = GPIO.input(RIGHT_GPIO)
    left_state = GPIO.input(LEFT_GPIO)
    enter_state = GPIO.input(ENTER_GPIO)

    if not right_state:
        if hourstart < 10:
            hourstart += 1
        time.sleep(0.2)
        strchange = True

    if not left_state:
        if hourstart > 0:
            hourstart -= 1
        time.sleep(0.2)
        strchange = True

    if not enter_state:
        state = STATE_SELECT
        strchange = True
        time.sleep(0.2)


def ChangeMinute():
    global strchange, hourstart, minutestart, state
    if strchange:
        strToPrint = "Min of play:\n" + str(minutestart)
        lcd.clear()
        lcd.message(strToPrint)
        strchange = False

    right_state = GPIO.input(RIGHT_GPIO)
    left_state = GPIO.input(LEFT_GPIO)
    enter_state = GPIO.input(ENTER_GPIO)

    if not right_state:
        minutestart += 1
        if minutestart == 60:
            if hourstart < 10:
                minutestart = 0
                hourstart += 1
            else:
                minutestart = 59
        time.sleep(0.2)
        strchange = True

    if not left_state:
        minutestart -= 1
        if minutestart == -1:
            if hourstart > 1:
                minutestart = 59
                hourstart -= 1
            else:
                minutestart = 0
        time.sleep(0.2)
        strchange = True

    if not enter_state:
        state = STATE_SELECT
        strchange = True
        time.sleep(0.2)


def ChangeMode():
    global strchange, state, modeselect, byoperiod, byotime
    if strchange:
        lcd.clear()
        if modeselect == 0:
            lcd.message(str(byoperiod) + "/" + str(byotime) + "\n>PER<-TIME-BACK")
        elif modeselect == 1:
            lcd.message(str(byoperiod) + "/" + str(byotime) + "\nPER->TIME<-BACK")
        elif modeselect == 2:
            lcd.message(str(byoperiod) + "/" + str(byotime) + "\nPER-TIME->BACK<")
        strchange = False

    enter_state = GPIO.input(ENTER_GPIO)
    right_state = GPIO.input(RIGHT_GPIO)
    left_state = GPIO.input(LEFT_GPIO)

    if not left_state:
        modeselect -= 1
        strchange = True
        if modeselect == -1:
            modeselect = 2
        time.sleep(0.2)

    if not right_state:
        modeselect += 1
        strchange = True
        if modeselect == 3:
            modeselect = 0
        time.sleep(0.2)
    
    if not enter_state:
        if modeselect == 0:
            state = STATE_CH_MODE_PERIOD
        elif modeselect == 1:
            state = STATE_CH_MODE_TIME
        elif modeselect == 2:
            state = STATE_SELECT
        strchange = True
        time.sleep(0.2)


def ChangeModePeriod():
    global strchange, byoperiod, state
    if strchange:
        strToPrint = "Byo-yomi period:\n" + str(byoperiod)
        lcd.clear()
        lcd.message(strToPrint)
        strchange = False

    right_state = GPIO.input(RIGHT_GPIO)
    left_state = GPIO.input(LEFT_GPIO)
    enter_state = GPIO.input(ENTER_GPIO)

    if not right_state:
        if byoperiod < 99:
            byoperiod += 1
        time.sleep(0.2)
        strchange = True

    if not left_state:
        if byoperiod > 0:
            byoperiod -= 1
        time.sleep(0.2)
        strchange = True

    if not enter_state:
        state = STATE_CH_MODE
        strchange = True
        time.sleep(0.2)


def ChangeModeTime():
    global strchange, byotime, state
    if strchange:
        strToPrint = "Byo-yomi time:\n" + str(byotime)
        lcd.clear()
        lcd.message(strToPrint)
        strchange = False

    right_state = GPIO.input(RIGHT_GPIO)
    left_state = GPIO.input(LEFT_GPIO)
    enter_state = GPIO.input(ENTER_GPIO)

    if not right_state:
        if byotime < 999:
            byotime += 1
        time.sleep(0.2)
        strchange = True

    if not left_state:
        if byotime > 0:
            byotime -= 1
        time.sleep(0.2)
        strchange = True

    if not enter_state:
        state = STATE_CH_MODE
        strchange = True
        time.sleep(0.2)


def Begin():
    global strchange, state, blackhour, blackminute, blacksecond, blackperiod, blacktime, blackflag, whitehour, whiteminute, whitesecond, whiteperiod, whitetime, whiteflag, count
    if strchange:
        lcd.clear()
        lcd.message("READY TO BEGIN.\nTIME: " + str(hourstart) + ":" + str(minutestart) + ":0")
        strchange = False

    blackhour = hourstart
    blackminute = minutestart
    blacksecond = 0
    blackperiod = byoperiod
    blacktime = byotime
    blackflag = False
    count = 0

    whitehour = hourstart
    whiteminute = minutestart
    whitesecond = 0
    whiteperiod = byoperiod
    whitetime = byotime
    whiteflag = False

    white_state = GPIO.input(RIGHT_GPIO)

    if not white_state:
        state = STATE_BLACK_MOVE
        strchange = True


def Black():
    global strchange, state, blackhour, blackminute, blacksecond, blackperiod, blacktime, blackflag, whitehour, whiteminute, whitesecond, whiteperiod, whitetime, whiteflag, count
    if strchange:
        lcd.clear()
        if not blackflag and not whiteflag:
            lcd.message("Black: " + str(blackhour) + ":" + str(blackminute) + ":" + str(blacksecond) + " " + str(count) + "\nWhite: " + str(whitehour) + ":" + str(whiteminute) + ":" + str(whitesecond))
        elif not blackflag and whiteflag:
            lcd.message("Black: " + str(blackhour) + ":" + str(blackminute) + ":" + str(blacksecond) + " " + str(count) "\nWhite: " + str(whiteperiod) + "/" + str(whitetime))
        elif blackflag and not whiteflag:
            lcd.message("Black: " + str(blackperiod) + "/" + str(blacktime) + " " + str(count) "\nWhite: " + str(whitehour) + ":" + str(whiteminute) + ":" + str(whitesecond))
        elif blackflag and whiteflag:
            lcd.message("Black: " + str(blackperiod) + "/" + str(blacktime) + " " + str(count) "\nWhite: " + str(whiteperiod) + "/" + str(whitetime))
        strchange = False

    black_state = GPIO.input(LEFT_GPIO)

    if not black_state:
        if blackflag:
            blacktime = byotime
        count += 1
        state = STATE_WHITE_MOVE
        strchange = True


def White():
    global strchange, state, blackhour, blackminute, blacksecond, blackperiod, blacktime, blackflag, whitehour, whiteminute, whitesecond, whiteperiod, whitetime, whiteflag, count
    if strchange:
        lcd.clear()
        if not blackflag and not whiteflag:
            lcd.message("Black: " + str(blackhour) + ":" + str(blackminute) + ":" + str(blacksecond) + "\nWhite: " + str(whitehour) + ":" + str(whiteminute) + ":" + str(whitesecond) + " " + str(count))
        elif not blackflag and whiteflag:
            lcd.message("Black: " + str(blackhour) + ":" + str(blackminute) + ":" + str(blacksecond) + "\nWhite: " + str(whiteperiod) + "/" + str(whitetime) + " " + str(count))
        elif blackflag and not whiteflag:
            lcd.message("Black: " + str(blackperiod) + "/" + str(blacktime) + "\nWhite: " + str(whitehour) + ":" + str(whiteminute) + ":" + str(whitesecond) + " " + str(count))
        elif blackflag and whiteflag:
            lcd.message("Black: " + str(blackperiod) + "/" + str(blacktime) + "\nWhite: " + str(whiteperiod) + "/" + str(whitetime) + " " + str(count))
        strchange = False

    white_state = GPIO.input(RIGHT_GPIO)

    if not white_state:
        if whiteflag:
            whitetime = byotime
        count += 1
        state = STATE_BLACK_MOVE
        strchange = True


def BlackWin():
    global strchange, state
    if strchange:
        lcd.clear()
        lcd.message("BLACK WON\nENTER TO RESTART")
        strchange = False

    enter_state = GPIO.input(ENTER_GPIO)

    if not enter_state:
        state = STATE_START
        strchange = True


def WhiteWin():
    global strchange, state
    if strchange:
        lcd.clear()
        lcd.message("WHITE WON\nENTER TO RESTART")
        strchange = False

    enter_state = GPIO.input(ENTER_GPIO)

    if not enter_state:
        state = STATE_START
        strchange = True

def Main():
    while True:
        GPIO.output(LED_GPIO, True)
        if state == STATE_START:
            Start()
        elif state == STATE_SELECT:
            Select()
        elif state == STATE_CH_HOUR:
            ChangeHour()
        elif state == STATE_CH_MINUTE:
            ChangeMinute()
        elif state == STATE_CH_MODE:
            ChangeMode()
        elif state == STATE_CH_MODE_PERIOD:
            ChangeModePeriod()
        elif state == STATE_CH_MODE_TIME:
            ChangeModeTime()
        elif state == STATE_BEGIN:
            Begin()
        elif state == STATE_BLACK_MOVE:
            Black()
        elif state == STATE_WHITE_MOVE:
            White()
        elif state == STATE_BLACK_WIN:
            BlackWin()
        elif state == STATE_WHITE_WIN:
            WhiteWin()
        time.sleep(0.1)
    
thread.start_new_thread(second, ())
thread.start_new_thread(Main, ())
    
# FLASK
# KOD

@app.route("/status")
def status():
    output = "State: " + str(state) + "\n Black hour: " + str(blackhour) + "\n Black minute: " + str(blackminute) + "\n Black second: " + str(blacksecond) + "\n White hour: " + str(whitehour) + "\n White minute: " + str(whiteminute) + "\n White second: " + str(whitesecond)
    return output

@app.route("/settime", methods = ['POST'])
def settime():
    global state, hourstart, minutestart, strchange
    if state == STATE_SELECT:
        hourstart = int(request.form["hour"])
        minutestart = int(request.form["minute"])
        state = STATE_BEGIN
        strchange = True
        return "OK"
    return "State: " + str(state)

@app.route("/starttime", methods = ['POST'])
def starttime():
    global state, strchange
    if state == STATE_BEGIN:
        state = STATE_BLACK_MOVE
        strchange = True
        return "OK"
    elif state == STATE_BLACK_WIN or state == STATE_WHITE_WIN:
        state = STATE_SELECT
        strchange = True
        return "OK"
    return "State: " + str(state)
   
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

# FLASK
# KOD
