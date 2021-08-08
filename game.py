from rainbowio import colorwheel
import random
import time
import math

PLUS = "+"
MINUS= "-"
MULTIPLY = "x"
DIVIDE = "/"

ENTER_KEY = 11
BACK_KEY = 9

DEFAULT_LIVES = 5
OPS = [PLUS,MINUS,MULTIPLY,DIVIDE]
DEFAULT_POINT = 1
END_SCORE = 50

TONES = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]
GAMEOVER_MELODY = [262, 196, 196, 220, 196, 0, 247, 262]
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
    0,8, 740,8, 0,8, 740,8, 659,8, 659,8, 740,8, 659,8
]

class Game:
    def __init__(self, macropad):
        self.macropad = macropad
        self.text_lines = macropad.display_text(title="BrainMAX")
        self.text_lines.show()
        self.left = 0
        self.operator = ""
        self.right = 0

        self.input = ""
        self.score = 0
        self.level = 1
        self.start_time = 0
        self.title()

    def title(self):
        self.screen = "title"
        self.show_text("Welcome Challenger!", "", "Press ENTER To Start.")
    
    def start(self):
        self.score = 0
        self.lives = DEFAULT_LIVES
        self.start_time = time.time()
        self.screen = "stage"
        self.next()

    def run(self):
        key_event = self.macropad.keys.events.get()

        if key_event:
            if self.screen == "title":
                if key_event.pressed:
                    if key_event.key_number == ENTER_KEY:
                        self.display_color(key_event.key_number)
                        self.start() 
            elif self.screen == "stage":
                if key_event.pressed:
                    self.display_color(key_event.key_number)
                    if key_event.key_number == ENTER_KEY and len(self.input) > 0:
                        self.success() if self.check(int(self.input)) else self.fail()
                    else:
                        self.process_input(key_event.key_number)
            elif self.screen == "gameover":
                if key_event.pressed:
                    if key_event.key_number == ENTER_KEY:
                        self.display_color(key_event.key_number)
                        self.title()
        else:
            self.macropad.pixels.fill((0, 0, 0))
            self.macropad.stop_tone()

    def next(self):
        if self.score > 30:
            self.level = 3
        elif self.score > 20:
            self.level = 2
        else:
            self.level = 1

        self.operator = OPS[random.randint(0,self.level)]
        difficulty = int((self.score / 10) * 5)
        if self.operator == PLUS or self.operator == MINUS:
            self.left = random.randint(0, 9 + difficulty)
            self.right = random.randint(0, 9 + difficulty)
        elif self.operator == MULTIPLY:
            self.left = random.randint(0,9 + difficulty)
            self.right = random.randint(0,9)
        elif self.operator == DIVIDE:
            self.right = random.randint(1,9)
            self.left = self.right * random.randint(1,9)

        # no negative result
        if self.operator == MINUS and self.right > self.left:
            temp = self.left
            self.left = self.right
            self.right = temp
        self.show_text("Solve: {} {} {} = ?".format(self.left, self.operator, self.right), "", "")

    def process_input(self, keyed):
        self.macropad.start_tone(TONES[keyed])
        # numpad
        if keyed < BACK_KEY:
            self.input += "{}".format(keyed + 1)
        elif keyed == 10:
            self.input += "0"
        elif keyed == BACK_KEY:
            self.input = self.input[:-1]
        self.show_text(None, "", self.input)


    def check(self, answer):
        print("{} {} {}".format(self.left, self.operator, self.right))
        if self.operator == PLUS:
            return answer == (self.left + self.right)
        elif self.operator == MINUS:
            return answer == (self.left - self.right)
        elif self.operator == MULTIPLY:
            return answer == (self.left * self.right)
        elif self.operator == DIVIDE:
            return answer == (self.left / self.right)

    def success(self):
        self.score += DEFAULT_POINT
        self.input = ""
    
        # win condition
        if self.score >= END_SCORE:
            self.screen = "gameover"
            self.show_text("CONGRATULATIONS!","Score: {} Time: {}".format(self.score, self.format_elapsed_time(self.start_time)), "Restart?")
            self.play_a_melody(WIN_MELODY)
        else:
            self.show_text(None, "AWESOME!", "Score: {}".format(self.score))
            self.play_correct()
            self.next()

    def fail(self):
        self.input = ""
        self.lives -= 1
        if self.lives == 0:
            self.screen = "gameover"
            self.show_text("SCORE: {}".format(self.score), "GAME OVER...", "Restart?")
            self.play_melody(GAMEOVER_MELODY)
        else:
            self.show_text(None, "UH.. TRY AGAIN", "Lives: {}".format(self.lives))
            self.play_incorrect()

    def show_text(self, l1, l2, l3):
        self.text_lines[0].text = l1 if l1 is not None else self.text_lines[0].text
        self.text_lines[1].text = l2 if l2 is not None else self.text_lines[1].text
        self.text_lines[2].text = l3 if l3 is not None else self.text_lines[2].text
        self.text_lines.show()

    def play_correct(self):
        self.macropad.play_tone(196, 0.2)
        self.macropad.play_tone(246, 0.2)
        self.macropad.play_tone(446, 0.2)
        self.macropad.stop_tone()

    def play_incorrect(self):
        self.macropad.play_tone(546, 0.2)
        self.macropad.play_tone(196, 0.2)
        self.macropad.stop_tone()

    def play_melody(self, melody):
        for i in melody:
            self.macropad.play_tone(i, 0.2)
        self.macropad.stop_tone()

    def play_a_melody(self, melody):
        for i in range(len(melody)):
            self.macropad.play_tone(melody[2 * i], melody[2 * i + 1] * 0.02)
        self.macropad.stop_tone()

    def format_elapsed_time(self, startime):
        elapsed = time.time() - startime
        hours = elapsed / 3600
        minutes = (elapsed - (hours * 3600)) / 60
        seconds = elapsed % 60
        return "{}{}{}".format(
            "{}h".format(math.floor(hours)) if hours >= 1 else "",
            "{}m".format(math.floor(minutes)) if minutes >= 1 else "",
            "{}s".format(seconds) if seconds >= 1 else "")

    def display_color(self, keyed):
        self.macropad.pixels[keyed] = colorwheel(
            int(255 / 12) * keyed
        )
