import pygame
from data.scripts.utils import create_player_cards

class Player:
    def __init__(self, num_players, width, height):
        self.NUM_PLAYERS = num_players
        self.WIDTH = width
        self.HEIGHT = height
        self.current_player = 1
        self.player_cards = create_player_cards(self.NUM_PLAYERS, self.WIDTH, self.HEIGHT)
        
        # Цвета
        self.BEIGE = (255, 235, 205)         
        self.DARK_BEIGE = (222, 184, 135)   
        self.WHITE = (160, 82, 45)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.HIGHLIGHT = (205, 133, 63)
        self.PLAYER_COLORS = [(205, 133, 63), (210, 105, 30), (139, 69, 19), (160, 82, 45)]
        
        # Шрифты
        self.small_font = pygame.font.SysFont('Comic Sans MS', 18)
        self.player_font = pygame.font.SysFont('Comic Sans MS', 22, bold=True)
        
    def next_turn(self):
        self.current_player = self.current_player % self.NUM_PLAYERS + 1
        
    def render(self, screen, dice):
        for card in self.player_cards:
            if card['player_num'] == self.current_player:
                card_color = self.BEIGE
                border_color = self.HIGHLIGHT
            else:
                card_color = (180, 180, 180)
                border_color = (100, 100, 100)
            
            pygame.draw.rect(screen, card_color, (*card['position'], *card['size']))
            pygame.draw.rect(screen, border_color, (*card['position'], *card['size']), 2)
            
            player_text_y = card['position'][1] - 20 if self.NUM_PLAYERS <= 2 else card['position'][1] - 10
            player_text_color = self.BLACK if card['player_num'] == self.current_player else (100, 100, 100)
            player_text = self.player_font.render(f"Игрок {card['player_num']}", True, player_text_color)
            screen.blit(player_text, player_text.get_rect(center=(card['position'][0] + card['size'][0] // 2, player_text_y)))
            
            current_card = card['player_num'] == self.current_player
            from data.scripts.utils import get_available_moves
            available_moves = get_available_moves(card, dice.has_rolled, dice.current_dice, dice.dice_sum) if current_card else []
            
            separate_numbers = [num for num in available_moves if num in dice.current_dice]
            sum_number = dice.dice_sum if dice.dice_sum in available_moves else None
            
            for cell in card['cells']:
                if current_card:
                    if not cell['marked']:
                        if cell['number'] in separate_numbers:
                            cell_color = (144, 238, 144)
                        elif cell['number'] == sum_number:
                            cell_color = (135, 206, 250)
                        else:
                            cell_color = self.BEIGE
                    else:
                        cell_color = self.DARK_BEIGE
                else:
                    if cell['marked']:
                        cell_color = (150, 150, 150)
                    else:
                        cell_color = (200, 200, 200)
                
                pygame.draw.rect(screen, cell_color, cell['rect'])
                pygame.draw.rect(screen, border_color, cell['rect'], 1)
                
                if not cell['marked']:
                    text_color = self.BLACK
                    num_text = self.small_font.render(str(cell['number']), True, text_color)
                    screen.blit(num_text, num_text.get_rect(center=cell['rect'].center))
                    
    def render_turn_indicator(self, screen):
        indicator_rect = pygame.Rect(self.WIDTH - 170, 20, 150, 50)
        pygame.draw.rect(screen, self.PLAYER_COLORS[self.current_player-1], indicator_rect)
        pygame.draw.rect(screen, self.BLACK, indicator_rect, 2)
        turn_text = self.player_font.render(f"Ход игрока {self.current_player}", True, self.BLACK)
        screen.blit(turn_text, turn_text.get_rect(center=indicator_rect.center))