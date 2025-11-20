import pygame
from config import *

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 30)
        self.is_clicked = False

    def draw(self, screen):
        """Draw button and center text"""
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)

        text = self.font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def handle_click(self, event):
        """Check mouse for clicks on the button surface"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_clicked = True
                return True
        return False
