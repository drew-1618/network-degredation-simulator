import pygame
import random
from config import *

class Ball(pygame.Rect):
    def __init__(self, x, y, speed):
        # init parent class 'pygame.Rect'
        super().__init__(x, y, BALL_SIZE, BALL_SIZE)
        self.speed = speed

        # init velocity
        # start unpredictable
        self.velocity_x = random.choice([speed, -speed])
        self.velocity_y = random.choice([speed, -speed])

    def move(self):
        """Update balls position based on velocity"""
        self.x += self.velocity_x
        self.y += self.velocity_y

    def reset(self):
        """Reset ball to center of screen & reverse horizontal direction"""
        self.center = (WIDTH // 2, (HEIGHT // 2) + CONTROL_PANEL_HEIGHT)
        # reverse horizontal direction to alternate serves
        self.velocity_x *= -1
        # give new random vertical angle (when combined with horizontal component)
        self.velocity_y = random.choice([self.speed, -self.speed])
