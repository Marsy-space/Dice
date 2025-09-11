import pygame
from scripts.button import Button
from scripts.utils import load_background
from scripts.theme import theme_manager

class Menu:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        
        # Кнопки меню
        self.play_button = Button(pygame.Rect(self.WIDTH // 2 - 150, 200, 300, 60), "Играть")
        self.players_button = Button(pygame.Rect(self.WIDTH // 2 - 150, 280, 300, 60), f"Игроков: 2")
        self.theme_button = Button(pygame.Rect(self.WIDTH // 2 - 150, 360, 300, 60), f"Тема: {theme_manager.get_theme()['name']}")
        self.rules_button = Button(pygame.Rect(self.WIDTH // 2 - 150, 440, 300, 60), "Правила")
        self.records_button = Button(pygame.Rect(self.WIDTH // 2 - 150, 520, 300, 60), "Рекорды")
            
        # Шрифты
        self.title_font = pygame.font.SysFont('Comic Sans MS', 64, bold=True)
        
    def update_players_button(self, num_players):
        self.players_button.text = f"Игроков: {num_players}"
        
    def update_theme_button(self):
        # Обновляем текст кнопки с текущей темой
        self.theme_button.text = f"Тема: {theme_manager.get_theme()['name']}"
        
    def render(self, screen):
        background = load_background(self.WIDTH, self.HEIGHT)
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((50, 50, 50))
        
        title = self.title_font.render("Игра в кости", True, (255, 255, 255))
        screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 80))
        
        mouse_pos = pygame.mouse.get_pos()
        self.play_button.render(screen, mouse_pos)
        self.players_button.render(screen, mouse_pos)
        self.theme_button.render(screen, mouse_pos)
        self.rules_button.render(screen, mouse_pos)
        self.records_button.render(screen, mouse_pos)

    def handle_click(self, mouse_pos):
        if self.play_button.is_hovered(mouse_pos):
            return "PLAY"
        elif self.players_button.is_hovered(mouse_pos):
            return "PLAYERS"
        elif self.theme_button.is_hovered(mouse_pos):
            return "THEME"
        elif self.rules_button.is_hovered(mouse_pos):
            return "RULES"
        elif self.records_button.is_hovered(mouse_pos):
            return "RECORDS"
        return None