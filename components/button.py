import pygame
from config import *

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 30)
        self.is_clicked = False
        self.is_hovered = False

    def draw(self, screen):
        """Draw button and center text"""
        # check hover and set color
        current_color = self.color
        if self.is_hovered:
            if self.color == BLUE:
                current_color = DARKER_BLUE
            else:
                current_color = DARK_GREEN
        pygame.draw.rect(screen, current_color, self.rect, border_radius=5)

        text = self.font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def handle_click(self, event):
        """Check mouse for clicks on the button surface"""
        # check hover state
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        # enter key or space key to start, pause, or play again
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.is_clicked = True
                return True
        # mouse click button to start, pause, or play again
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_clicked = True
                return True
        return False
