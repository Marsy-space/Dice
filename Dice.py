
import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игральные кости с карточками игроков")

NUM_PLAYERS = 2  

BEIGE = (255, 235, 205)         
DARK_BEIGE = (222, 184, 135)   
DARK_BLUE = (255, 235, 205)        
WHITE = (160, 82, 45)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

try:
    background = pygame.image.load("background1.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except FileNotFoundError:
    print("Ошибка: файл background.jpg не найден! Используется серый фон.")
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((50, 50, 50))


try:
    dice_images = [
        pygame.image.load(f"dice_{i}.jpg").convert_alpha() for i in range(1, 7)
    ]
    dice_size = 100
    dice_images = [pygame.transform.scale(img, (dice_size, dice_size)) for img in dice_images]
except FileNotFoundError:
    print("Ошибка: файлы с изображениями костей не найдены!")
    dice_images = []
    for i in range(6):
        surf = pygame.Surface((dice_size, dice_size), pygame.SRCALPHA)
        pygame.draw.rect(surf, WHITE, (0, 0, dice_size, dice_size))
        pygame.draw.rect(surf, BLACK, (0, 0, dice_size, dice_size), 2)
        dots = [
            [(1,1)], [(0,0), (2,2)], [(0,0), (1,1), (2,2)],
            [(0,0), (0,2), (2,0), (2,2)], [(0,0), (0,2), (1,1), (2,0), (2,2)],
            [(0,0), (0,1), (0,2), (2,0), (2,1), (2,2)]
        ][i]
        for x, y in dots:
            pygame.draw.circle(surf, BLACK, 
                            (int((x+0.5)*dice_size//3), int((y+0.5)*dice_size//3)), 
                            dice_size//10)
        dice_images.append(surf)

dice_positions = [
    (WIDTH // 2 - 120, 100), 
    (WIDTH // 2 + 20, 100)    
]
text_position = (WIDTH // 2, 50)  

current_dice = [1, 1]

font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)
player_font = pygame.font.SysFont('Arial', 22, bold=True)  

def create_player_cards(num_players):
    cards = []
    max_cards_per_row = 2  
    margin = 20  
    
    if num_players <= 2:
        card_width = (WIDTH - (num_players + 1) * margin) // num_players
    else:
        card_width = (WIDTH - (max_cards_per_row + 1) * margin) // max_cards_per_row
    
    card_height = 120 
    
    rows = (num_players + max_cards_per_row - 1) // max_cards_per_row
    total_height = rows * card_height + (rows - 1) * margin
    start_y = (HEIGHT - total_height) // 2 + 50  
    for player in range(num_players):
        row = player // max_cards_per_row
        col = player % max_cards_per_row
        
        
        if num_players <= 2:
            x = margin + col * (card_width + margin)
        else:
            x = (WIDTH - (max_cards_per_row * card_width + (max_cards_per_row - 1) * margin)) // 2
            x += col * (card_width + margin)
        
        y = start_y + row * (card_height + margin)
        
        
        numbers = list(range(1, 13))
        
        cells = []
        for i in range(12):
            row_num = i // 6
            col_num = i % 6
            rect = pygame.Rect(
                x + col_num * (card_width // 6),
                y + row_num * (card_height // 2),
                card_width // 6 - 2,
                card_height // 2 - 2
            )
            cells.append({
                'rect': rect,
                'number': numbers[i],
                'marked': False
            })
        
        cards.append({
            'position': (x, y),
            'size': (card_width, card_height),
            'cells': cells,
            'player_num': player + 1
        })
    
    return cards

player_cards = create_player_cards(NUM_PLAYERS)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_dice = [random.randint(1, 6), random.randint(1, 6)]
            elif event.key == pygame.K_1:
                NUM_PLAYERS = 1
                player_cards = create_player_cards(NUM_PLAYERS)
            elif event.key == pygame.K_2:
                NUM_PLAYERS = 2
                player_cards = create_player_cards(NUM_PLAYERS)
            elif event.key == pygame.K_3:
                NUM_PLAYERS = 3
                player_cards = create_player_cards(NUM_PLAYERS)
            elif event.key == pygame.K_4:
                NUM_PLAYERS = 4
                player_cards = create_player_cards(NUM_PLAYERS)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            
            mouse_pos = pygame.mouse.get_pos()
            clicked_on_cell = False
            
            for card in player_cards:
                for cell in card['cells']:
                    if cell['rect'].collidepoint(mouse_pos):
                        cell['marked'] = not cell['marked']
                        clicked_on_cell = True
            
            
            if not clicked_on_cell:
                current_dice = [random.randint(1, 6), random.randint(1, 6)]

    
    screen.blit(background, (0, 0))
    
    
    text = font.render("Нажмите SPACE или кликните вне карточек для броска костей", True, WHITE)
    text_rect = text.get_rect(center=text_position)
    pygame.draw.rect(screen, (*DARK_BLUE, 200), 
                       (text_rect.x - 10, text_rect.y - 5,
                        text_rect.width + 20, text_rect.height + 10))
    screen.blit(text, text_rect)

    for i in range(2):
        screen.blit(dice_images[current_dice[i]-1], dice_positions[i])

    
    for card in player_cards:
        
        pygame.draw.rect(screen, GRAY, (*card['position'], *card['size']), 2)
        pygame.draw.rect(screen, BEIGE, (*card['position'], *card['size']))
        
        
        player_text = player_font.render(f"Игрок {card['player_num']}", True, BLACK)
        player_rect = player_text.get_rect(
            center=(card['position'][0] + card['size'][0] // 2, 
                    card['position'][1] + 15)
        )
        screen.blit(player_text, player_rect)
        
        
        for cell in card['cells']:
            color = DARK_BEIGE if cell['marked'] else BEIGE
            pygame.draw.rect(screen, color, cell['rect'])
            pygame.draw.rect(screen, GRAY, cell['rect'], 1)
            
           
            num_text = small_font.render(str(cell['number']), True, BLACK)
            num_rect = num_text.get_rect(center=cell['rect'].center)
            screen.blit(num_text, num_rect)

    
    players_text = small_font.render(f"Игроков: {NUM_PLAYERS} (1-4 для изменения)", True, WHITE)
    screen.blit(players_text, (20, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()