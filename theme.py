import pygame
import os

class ThemeManager:
    def __init__(self):
        self.themes = [
            {
                'name': 'Классическая',
                'background': os.path.join("data", "img", "background", "background1.jpg"),
                'colors': {
                    'BEIGE': (255, 235, 205),
                    'DARK_BEIGE': (222, 184, 135),
                    'WHITE': (160, 82, 45),
                    'BLACK': (0, 0, 0),
                    'GRAY': (200, 200, 200),
                    'HIGHLIGHT': (205, 133, 63),
                    'PLAYER_COLORS': [(205, 133, 63), (210, 105, 30), (139, 69, 19), (160, 82, 45)],
                    'BUTTON_COLOR': (222, 184, 135),
                    'BUTTON_HOVER': (150, 150, 150),
                    'BUTTON_TEXT': (160, 82, 45),
                    'DICE_BG': (222, 184, 135),
                    'DICE_DOT': (0, 0, 0),
                    'AVAILABLE_SINGLE': (144, 238, 144),
                    'AVAILABLE_SUM': (135, 206, 250),
                    'TEXT_COLOR': (0, 0, 0)
                }
            },
            {
                'name': 'Синяя',
                'background': os.path.join("data", "img", "background", "background2.jpg"),
                'colors': {
                    'BEIGE': (200, 225, 255),
                    'DARK_BEIGE': (150, 200, 255),
                    'WHITE': (100, 150, 255),
                    'BLACK': (0, 0, 50),
                    'GRAY': (180, 200, 220),
                    'HIGHLIGHT': (100, 150, 255),
                    'PLAYER_COLORS': [(100, 150, 255), (80, 130, 235), (60, 110, 215), (40, 90, 195)],
                    'BUTTON_COLOR': (150, 200, 255),
                    'BUTTON_HOVER': (120, 170, 220),
                    'BUTTON_TEXT': (0, 0, 80),
                    'DICE_BG': (100, 150, 255),
                    'DICE_DOT': (255, 255, 255),
                    'AVAILABLE_SINGLE': (120, 220, 120),
                    'AVAILABLE_SUM': (80, 180, 255),
                    'TEXT_COLOR': (10, 103,200)
                }
            }
        ]
        
        self.current_theme_index = 0
        self.current_theme = self.themes[self.current_theme_index]
    
    def next_theme(self):
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        self.current_theme = self.themes[self.current_theme_index]
        return self.current_theme
    
    def get_theme(self):
        return self.current_theme
    
    def get_background_path(self):
        return self.current_theme['background']
    
    def get_color(self, color_name):
        return self.current_theme['colors'].get(color_name, (255, 255, 255))
    
    def get_player_colors(self):
        return self.current_theme['colors']['PLAYER_COLORS']

theme_manager = ThemeManager()