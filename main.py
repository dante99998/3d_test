#!/usr/bin/env python

import numpy as np
import math

from game import Game
from settings import *

def main():
    game = Game()

    while game.is_running:
        game.render()
        game.update()
        game.event_handler()

    game.quit()
    print("GAME OVER")

if __name__ == '__main__':
    main()