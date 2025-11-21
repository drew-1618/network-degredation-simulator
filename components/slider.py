import pygame
from config import *

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.bar_rect = pygame.Rect(x, y + height // 2 - 2, width, 4)
        self.slider_min_x = x
        self.slider_max_x = x + width

        self.value = min_val
        self.min_val = min_val
        self.max_val = max_val
        self.label = label

        self.thumb_radius = 8
        self.thumb_x = self.slider_min_x

        self.dragging = False
        self.font = pygame.font.Font(None, 24)

    def handle_event(self, event):
        """Handle events that move the slider thumb"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                # move thumb immediately to click position
                self._update_value_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # update position while dragging
                self._update_value_from_pos(event.pos[0])

    def _update_value_from_pos(self, mouse_x):
        """Calculate new slider value based on mouse position"""
        # keep within slider bounds
        mouse_x = max(self.slider_min_x, min(self.slider_max_x, mouse_x))
        self.thumb_x = mouse_x

        # calculate ratio 0 - 1
        range_width = self.slider_max_x - self.slider_min_x
        ratio = (mouse_x - self.slider_min_x) / range_width

        # calculate actual value
        value_range = self.max_val - self.min_val
        self.value = round(self.min_val + value_range * ratio, 2)

    def get_value(self):
        return self.value

    def set_value(self, value):
        """Set the value and update thumb position"""
        self.value = max(self.min_val, min(self.max_val, value))

        # calculate visual position
        range_width = self.slider_max_x - self.slider_min_x
        value_range = self.max_val - self.min_val

        if value_range == 0:
            return
        
        ratio = (self.value - self.min_val) / value_range
        self.thumb_x = self.slider_min_x + (range_width * ratio)

    def draw(self, screen):
        """Draw slider bar, thumb, and label"""
        # draw slider bar
        pygame.draw.rect(screen, WHITE, self.bar_rect, border_radius=2)
        # draw thumb
        current_color = BLUE
        if self.dragging:
            current_color = DARKER_BLUE
        pygame.draw.circle(screen, current_color, (self.thumb_x, self.bar_rect.centery), self.thumb_radius)
        # draw label
        text = self.font.render(f"{self.label}: {self.value}", True, WHITE)
        screen.blit(text, (self.rect.x, self.rect.y))
