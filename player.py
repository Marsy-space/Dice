import pygame
from scripts.utils import create_player_cards
from scripts.theme import theme_manager

class Player:
    def __init__(self, num_players, width, height):
        self.NUM_PLAYERS = num_players
        self.WIDTH = width
        self.HEIGHT = height
        self.current_player = 1
        self.player_cards = create_player_cards(self.NUM_PLAYERS, self.WIDTH, self.HEIGHT)
        
        # Шрифты
        self.small_font = pygame.font.SysFont('Comic Sans MS', 18)
        self.player_font = pygame.font.SysFont('Comic Sans MS', 22, bold=True)
        
    def next_turn(self):
        self.current_player = self.current_player % self.NUM_PLAYERS + 1
        
    def render(self, screen, dice):
        for card in self.player_cards:
            if card['player_num'] == self.current_player:
                card_color = theme_manager.get_color('BEIGE')
                border_color = theme_manager.get_color('HIGHLIGHT')
            else:
                card_color = (180, 180, 180)
                border_color = (100, 100, 100)
            
            pygame.draw.rect(screen, card_color, (*card['position'], *card['size']))
            pygame.draw.rect(screen, border_color, (*card['position'], *card['size']), 2)
            
            player_text_y = card['position'][1] - 20 if self.NUM_PLAYERS <= 2 else card['position'][1] - 10
            player_text_color = theme_manager.get_color('TEXT_COLOR') if card['player_num'] == self.current_player else (100, 100, 100)
            player_text = self.player_font.render(f"Игрок {card['player_num']}", True, player_text_color)
            screen.blit(player_text, player_text.get_rect(center=(card['position'][0] + card['size'][0] // 2, player_text_y)))
            
            current_card = card['player_num'] == self.current_player
            from scripts.utils import get_available_moves
            available_moves = get_available_moves(card, dice.has_rolled, dice.current_dice, dice.dice_sum) if current_card else []
            
            separate_numbers = [num for num in available_moves if num in dice.current_dice]
            sum_number = dice.dice_sum if dice.dice_sum in available_moves else None
            
            for cell in card['cells']:
                if current_card:
                    if not cell['marked']:
                        if cell['number'] in separate_numbers:
                            cell_color = theme_manager.get_color('AVAILABLE_SINGLE')
                        elif cell['number'] == sum_number:
                            cell_color = theme_manager.get_color('AVAILABLE_SUM')
                        else:
                            cell_color = theme_manager.get_color('BEIGE')
                    else:
                        cell_color = theme_manager.get_color('DARK_BEIGE')
                else:
                    if cell['marked']:
                        cell_color = (150, 150, 150)
                    else:
                        cell_color = (200, 200, 200)
                
                pygame.draw.rect(screen, cell_color, cell['rect'])
                pygame.draw.rect(screen, border_color, cell['rect'], 1)
                
                if not cell['marked']:
                    text_color = theme_manager.get_color('TEXT_COLOR')
                    num_text = self.small_font.render(str(cell['number']), True, text_color)
                    screen.blit(num_text, num_text.get_rect(center=cell['rect'].center))
                    
    def render_turn_indicator(self, screen):
        indicator_rect = pygame.Rect(self.WIDTH - 170, 20, 150, 50)
        player_colors = theme_manager.get_player_colors()
        pygame.draw.rect(screen, player_colors[self.current_player-1], indicator_rect)
        pygame.draw.rect(screen, theme_manager.get_color('BLACK'), indicator_rect, 2)
        turn_text = self.player_font.render(f"Ход игрока {self.current_player}", True, theme_manager.get_color('TEXT_COLOR'))
        screen.blit(turn_text, turn_text.get_rect(center=indicator_rect.center))