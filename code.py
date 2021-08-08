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
from adafruit_macropad import MacroPad
from game import Game

# START
macropad = MacroPad()
game = Game(macropad)

while True:
    game.run()
