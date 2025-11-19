import pygame
from config import HEIGHT
from config import *

class Paddle(pygame.Rect):
    def __init__(self, x, y, speed):
        # init parent class 'pygame.Rect'
        super().__init__(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = speed
    
    def move(self, direction):
        """
        Moves paddle up (direction=-1) or down (direction=1)
        and ensures it stays within boundaries (vertical only)
        """
        # update position
        self.y += direction * self.speed

        # check boundaries
        # top & bottom: inherited from pygame.Rect
        if self.top < CONTROL_PANEL_HEIGHT:
            self.top = CONTROL_PANEL_HEIGHT
        if self.bottom > TOTAL_HEIGHT:
            self.bottom = TOTAL_HEIGHT
