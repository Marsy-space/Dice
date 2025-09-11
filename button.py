import pygame
from scripts.theme import theme_manager

class Button:
    def __init__(self, rect, text, color=None, hover_color=None, text_color=None):
        self.rect = rect
        self.text = text
        self.color = color if color else theme_manager.get_color('BUTTON_COLOR')
        self.hover_color = hover_color if hover_color else theme_manager.get_color('BUTTON_HOVER')
        self.text_color = text_color if text_color else theme_manager.get_color('BUTTON_TEXT')
        self.font = pygame.font.SysFont('Comic Sans MS', 24)
        
    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
        
    def render(self, screen, mouse_pos=None):
        color = theme_manager.get_color('BUTTON_HOVER') if mouse_pos and self.is_hovered(mouse_pos) else theme_manager.get_color('BUTTON_COLOR')
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, theme_manager.get_color('BLACK'), self.rect, 2, border_radius=5)
        text_surface = self.font.render(self.text, True, theme_manager.get_color('BUTTON_TEXT'))
        screen.blit(text_surface, (self.rect.centerx - text_surface.get_width() // 2, self.rect.centery - text_surface.get_height() // 2))