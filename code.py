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
import math

# START
macropad = MacroPad()

TONES = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]
GAMEOVER_MELODY = [262, 196, 196, 220, 196, 0, 247, 262]
# taken from https://github.com/robsoncouto/arduino-songs/blob/master/takeonme/takeonme.ino
WIN_MELODY = [
    0,8, 659,8, 0,8, 659,8, 831,8, 831,8, 880,8, 988,8,
    880,8, 880,8, 880,8, 659,8, 0,8, 587,8, 0,8, 740,8, 
    0,8, 740,8, 0,8, 740,8, 659,8, 659,8, 740,8, 659,8,
    740,8, 740,8,587,8, 494,8, 0,8, 494,8, 0,8, 659,8, 

    0,8, 659,8, 0,8, 659,8, 831,8, 831,8, 880,8, 988,8,
    880,8, 880,8, 880,8, 659,8, 0,8, 587,8, 0,8, 740,8, 
    0,8, 740,8, 0,8, 740,8, 659,8, 659,8, 740,8, 659,8,
    740,8, 740,8,587,8, 494,8, 0,8, 494,8, 0,8, 659,8, 
    0,8, 659,8, 0,8, 659,8, 831,8, 831,8, 880,8, 988,8,

    880,8, 880,8, 880,8, 659,8, 0,8, 587,8, 0,8, 740,8, 
    0,8, 740,8, 0,8, 740,8, 659,8, 659,8, 740,8, 659,8,
]


PLUS = "+"
MINUS= "-"
MULTIPLY = "x"
DIVIDE = "/"

DEFAULT_LIVES = 5
OPS = [PLUS,MINUS,MULTIPLY,DIVIDE]
DEFAULT_POINT = 1
END_SCORE = 50

text_lines = macropad.display_text(title="BrainMAX")
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
tim = 0

def show_text(l1, l2, l3):
    text_lines[0].text = l1 if l1 is not None else text_lines[0].text
    text_lines[1].text = l2 if l2 is not None else text_lines[1].text
    text_lines[2].text = l3 if l3 is not None else text_lines[2].text
    text_lines.show()

def play_correct():
    macropad.play_tone(196, 0.2)
    macropad.play_tone(246, 0.2)
    macropad.play_tone(446, 0.2)
    macropad.stop_tone()

def play_incorrect():
    macropad.play_tone(546, 0.2)
    macropad.play_tone(196, 0.2)
    macropad.stop_tone()

def play_melody(melody):
    for i in melody:
        macropad.play_tone(i, 0.2)
    macropad.stop_tone()

def play_a_melody(melody):
    for i in range(len(melody)):
        macropad.play_tone(melody[2 * i], melody[2 * i + 1] * 0.02)
    macropad.stop_tone()

def next():
    global operator, left, right, score, level
    if score > 30:
        level = 3
    elif score > 20:
        level = 2
    else:
        level = 1

    operator = OPS[random.randint(0,level)]
    difficulty = int((score / 10) * 5)
    if operator == PLUS or operator == MINUS:
        left = random.randint(0, 9 + difficulty)
        right = random.randint(0, 9 + difficulty)
    elif operator == MULTIPLY:
        left = random.randint(0,9 + difficulty)
        right = random.randint(0,9)
    elif operator == DIVIDE:
        right = random.randint(1,9)
        left = right * random.randint(1,9)

    # no negative result
    if operator == MINUS and right > left:
        temp = left
        left = right
        right = temp
    show_text("Solve: {} {} {} = ?".format(left, operator, right), "", "")

def check(answer):
    global left ,right, operator
    if operator == PLUS:
        return answer == (left + right)
    elif operator == MINUS:
        return answer == (left - right)
    elif operator == MULTIPLY:
        return answer == (left * right)
    elif operator == DIVIDE:
        return answer == (left / right)

def title():
    global screen
    screen = "title"
    show_text("Welcome Challenger!", "", "Press ENTER To Start.")

def start():
    global lives, screen, tim, score
    score = 0
    lives = DEFAULT_LIVES
    tim = time.time()
    screen = "stage"
    next()
 
def format_elapsed_time(startime):
    elapsed = time.time() - startime
    hours = elapsed / 3600
    minutes = (elapsed - (hours * 3600)) / 60
    seconds = elapsed % 60
    return "{}{}{}".format(
        "{}h".format(math.floor(hours)) if hours >= 1 else "",
        "{}m".format(math.floor(minutes)) if minutes >= 1 else "",
        "{}s".format(seconds) if seconds >= 1 else "")

def success():
    global score, input, tim, screen
    score += DEFAULT_POINT
    input = ""
    # win condition
    if score >= END_SCORE:
        screen = "gameover"
        show_text("CONGRATULATIONS!","Score: {} Time: {}".format(score, format_elapsed_time(tim)), "Restart?")
        play_a_melody(WIN_MELODY)
    else:
        show_text(None, "AWESOME!", "Score: {}".format(score))
        play_correct()
        next()

def fail():
    global lives, screen, input
    input = ""
    lives -= 1
    if lives == 0:
        screen = "gameover"
        show_text("SCORE: {}".format(score), "GAME OVER...", "Restart?")
        play_melody(GAMEOVER_MELODY)
    else:
        show_text(None, "UH.. TRY AGAIN", "Lives: {}".format(lives))
        play_incorrect()
        

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
    show_text(None, "", input)

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
