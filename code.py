"""
MacroPad Math Game

Key Layout
1 2 3
4 5 6
7 8 9
< 0 >

Title: Press > to start new game
Game: Enter answer, then press > to submit
Gameover: Press > to go back to title screen

"""
from rainbowio import colorwheel
from adafruit_macropad import MacroPad
import random
import time

macropad = MacroPad()

TONES = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]
MELODY = [262, 196, 196, 220, 196, 0, 247, 262]

DEFAULT_LIVES = 5
OPS = ["+","-"]
DEFAULT_POINT = 100

text_lines = macropad.display_text(title="BrainMAX ")
text_lines.show()

screen = "title"
lives = DEFAULT_LIVES

# variables
left = 2
operator = "+"
right = 7
expected = 9
input = ""
result = ""
score = 0
level = 1

def next():
    global operator, left, right
    operator = OPS[random.randint(0,1)]
    left = random.randint(0,9)
    right = random.randint(0,9)

    # no negative result
    if operator == "-" and right > left:
        temp = left
        left = right
        right = temp
    text_lines[0].text = "Solve: {} {} {} = ?".format(left, operator, right)
    text_lines[1].text = ""
    text_lines[2].text = ""

def check(answer):
    global left ,right, operator
    print("Checking {} {} {} {}".format(left, operator, right, answer))
    if operator == "+":
        return answer == (left + right)
    elif operator == "-":
        return answer == (left - right)

def title():
    global screen
    screen = "title"
    text_lines[0].text = "Welcome Challenger!"
    text_lines[1].text = "" 
    text_lines[2].text = "Press ENTER To Start."
    text_lines.show()

def start():
    global lives, screen
    lives = DEFAULT_LIVES
    screen = "stage"
    next()
 
def success():
    text_lines[1].text = "AWESOME!"
    text_lines[2].text = ""
    text_lines.show()
    global score, input
    macropad.play_tone(196, 0.2)
    macropad.play_tone(246, 0.2)
    macropad.play_tone(446, 0.2)
    macropad.stop_tone()
    score += DEFAULT_POINT
    input = ""
    next()

def fail():
    global lives, screen, input
    input = ""
    lives -= 1
    print("Lives left: {}".format(lives))
    if lives == 0:
        screen = "gameover"
        text_lines[0].text = "SCORE: {}".format(score)
        text_lines[1].text = "GAME OVER..."
        text_lines[2].text = "Restart?"
        text_lines.show()
        for i in MELODY:
            macropad.play_tone(i, 0.2)
        macropad.stop_tone()
    else:
        text_lines[1].text = "UH.. TRY AGAIN"
        text_lines[2].text = ""
        text_lines.show()
        macropad.play_tone(546, 0.2)
        macropad.play_tone(196, 0.2)
        macropad.stop_tone()

def display_color(keyed):
    macropad.pixels[keyed] = colorwheel(
        int(255 / 12) * keyed
    )

def process_input(keyed):
    global input
    macropad.start_tone(TONES[keyed])
    # numpad
    if keyed < 9:
        input += "{}".format(keyed + 1)
    elif keyed == 10:
        input += "0"
    elif keyed == 9:
        input = input[:-1]
    text_lines[1].text = ""
    text_lines[2].text = input
    text_lines.show()

title()

while True:
    key_event = macropad.keys.events.get()

    if key_event:
        if screen == "title":
            if key_event:
                if key_event.pressed:
                    if key_event.key_number == 11:
                        display_color(key_event.key_number)
                        start() 
        elif screen == "stage":
            if key_event:
                if key_event.pressed:
                    display_color(key_event.key_number)
                    if key_event.key_number == 11 and len(input) > 0:
                        success() if check(int(input)) else fail()
                    else:
                        process_input(key_event.key_number)
        elif screen == "gameover":
            if key_event:
                if key_event.pressed:
                    if key_event.key_number == 11:
                        display_color(key_event.key_number)
                        title()
    else:
        macropad.pixels.fill((0, 0, 0))
        macropad.stop_tone()

            
                    



