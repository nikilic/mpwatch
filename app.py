import RPi.GPIO as GPIO
import os
import time
from threading import Timer,Thread,Event
from config import *

global state, written, hourstart, minutestart, menuselect, strchange, blackhour, blackminute, blacksecond, whitehour, whiteminute, whitesecond

state = 0
written = 0

clear = lambda: os.system('clear')

GPIO.setmode(GPIO.BCM)

GPIO.setup(LEFT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # black/left
GPIO.setup(DOWN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # down
GPIO.setup(UP_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # up
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
    global blackhour, blackminute, blacksecond, whitehour, whiteminute, whitesecond, state, strchange
    if state == STATE_BLACK_MOVE:
        blacksecond -= 1
        if blacksecond < 0:
            blacksecond = 59
            blackminute -= 1
            if blackminute < 0:
                blackminute = 59
                blackhour -= 1
                if blackhour < 0:
                    state = STATE_WHITE_WIN
                    strchange = True

    if state == STATE_WHITE_MOVE:
        whitesecond -= 1
        if whitesecond < 0:
            whitesecond = 59
            whiteminute -= 1
            if whiteminute < 0:
                whiteminute = 59
                whitehour -= 1
                if whitehour < 0:
                    state = STATE_BLACK_WIN
                    strchange = True


def Start():
    global state, menuselect, hourstart, minutestart, strchange
    clear()
    print("WELCOME TO PUPIN CLOCK PROJECT")
    time.sleep(2.0)
    menuselect = 0
    hourstart = 1
    minutestart = 0
    strchange = True
    state = STATE_SELECT


def Select():
    global hourstart, minutestart, menuselect, strchange, state
    if strchange:
        strToPrint = hourstart+":"+minutestart+":0     | "
        if menuselect == 0:
            strToPrint += ">>CH. HOUR<< | CH. MINUTE | CH. MODE | START"
        elif menuselect == 1:
            strToPrint += "CH. HOUR | >>CH. MINUTE<< | CH. MODE | START"
        elif menuselect == 2:
            strToPrint += "CH. HOUR | CH. MINUTE | >>CH. MODE<< | START"
        elif menuselect == 3:
            strToPrint += "CH. HOUR | CH. MINUTE | CH. MODE | >>START<<"
        clear()
        print(strToPrint)
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
        strToPrint = "Hours of play: " + hourstart
        clear()
        print(strToPrint)
        strchange = False

    up_state = GPIO.input(UP_GPIO)
    down_state = GPIO.input(DOWN_GPIO)
    enter_state = GPIO.input(ENTER_GPIO)

    if not up_state:
        if hourstart < 10:
            hourstart += 1
        time.sleep(0.2)
        strchange = True

    if not down_state:
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
        strToPrint = "Minutes of play: " + minutestart
        clear()
        print(strToPrint)
        strchange = False

    up_state = GPIO.input(UP_GPIO)
    down_state = GPIO.input(DOWN_GPIO)
    enter_state = GPIO.input(ENTER_GPIO)

    if not up_state:
        minutestart += 1
        if minutestart == 60:
            if hourstart < 10:
                minutestart = 0
                hourstart += 1
            else:
                minutestart = 59
        time.sleep(0.2)
        strchange = True

    if not down_state:
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
    global strchange, state
    if strchange:
        clear()
        print("Only one mode available. Return")
        strchange = False

    enter_state = GPIO.input(ENTER_GPIO)

    if not enter_state:
        state = STATE_SELECT
        strchange = True
        time.sleep(0.2)


def Begin():
    global strchange, state, blackhour, blackminute, blacksecond, whitehour, whiteminute, whitesecond
    if strchange:
        clear()
        print("GAME READY TO BEGIN. TIME: " + hourstart + ":" + minutestart + ":0 | Press white to begin...")
        strchange = False

    blackhour = hourstart
    blackminute = minutestart
    blacksecond = 0

    whitehour = hourstart
    whiteminute = minutestart
    whitesecond = 0

    white_state = GPIO.input(RIGHT_GPIO)

    if not white_state:
        state = STATE_BLACK_MOVE
        strchange = True


def Black():
    global strchange, state, blackhour, blackminute, blacksecond, whitehour, whiteminute, whitesecond
    if strchange:
        clear()
        print("Black to play.")
        print("Black time: " + blackhour + ":" + blackminute + ":" + blacksecond)
        print("White time: " + whitehour + ":" + whiteminute + ":" + whitesecond)
        strchange = False

    black_state = GPIO.input(LEFT_GPIO)

    if not black_state:
        state = STATE_BLACK_MOVE
        strchange = True


def White():
    global strchange, state, blackhour, blackminute, blacksecond, whitehour, whiteminute, whitesecond
    if strchange:
        clear()
        print("White to play.")
        print("Black time: " + blackhour + ":" + blackminute + ":" + blacksecond)
        print("White time: " + whitehour + ":" + whiteminute + ":" + whitesecond)
        strchange = False

    white_state = GPIO.input(RIGHT_GPIO)

    if not white_state:
        state = STATE_BLACK_MOVE
        strchange = True


def BlackWin():
    global strchange, state
    if strchange:
        clear()
        print("BLACK WON. PRESS ENTER TO RESTART")
        strchange = False

    enter_state = GPIO.input(ENTER_GPIO)

    if not enter_state:
        state = STATE_START
        strchange = True


def WhiteWin():
    global strchange, state
    if strchange:
        clear()
        print("WHITE WON. PRESS ENTER TO RESTART")
        strchange = False

    enter_state = GPIO.input(ENTER_GPIO)

    if not enter_state:
        state = STATE_START
        strchange = True


t = PerpetualTimer(1, second)
t.start()

try:
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
except:
    GPIO.cleanup()
