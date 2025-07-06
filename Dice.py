import pygame
import sys
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игральные кости с карточками игроков")

NUM_PLAYERS = 2  
current_player = 1  # Текущий игрок (начинает первый)
has_rolled = False  # Флаг, что игрок уже бросал кости в этот ход
rolling = False     # Флаг, что кости сейчас вращаются
last_roll_time = 0  # Время последнего броска

BEIGE = (255, 235, 205)         
DARK_BEIGE = (222, 184, 135)   
DARK_BLUE = (255, 235, 205)        
WHITE = (160, 82, 45)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HIGHLIGHT = (205, 133, 63)  # Цвет подсветки доступных чисел
PLAYER_COLORS = [(205, 133, 63), (210, 105, 30), (139, 69, 19), (160, 82, 45)]  # Цвета для индикатора игроков
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER = (150, 150, 150)

try:
    background = pygame.image.load("background1.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except FileNotFoundError:
    print("Ошибка: файл background.jpg не найден! Используется серый фон.")
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((50, 50, 50))

dice_size = 100
dice_images = []
for i in range(6):
    try:
        img = pygame.image.load(f"ice_{i+1}.png").convert_alpha()
        img = pygame.transform.scale(img, (dice_size, dice_size))
        dice_images.append(img)
    except FileNotFoundError:
        print(f"Ошибка: файл Dice_{i+1}.png не найден! Создаю стандартную кость.")
        surf = pygame.Surface((dice_size, dice_size), pygame.SRCALPHA)
        pygame.draw.rect(surf, (222, 184, 135), (0, 0, dice_size, dice_size))
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
dice_sum = sum(current_dice)
available_numbers = set(current_dice + [dice_sum])  # Доступные для закрытия числа

font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)
player_font = pygame.font.SysFont('Arial', 22, bold=True)  

# Кнопки
roll_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 120, 40)
stop_button = pygame.Rect(WIDTH // 2 + 30, HEIGHT - 100, 120, 40)


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

def draw_turn_indicator():
    indicator_size = 150
    indicator_rect = pygame.Rect(WIDTH - indicator_size - 20, 20, indicator_size, 50)
    pygame.draw.rect(screen, PLAYER_COLORS[current_player-1], indicator_rect)
    pygame.draw.rect(screen, BLACK, indicator_rect, 2)
    
    turn_text = player_font.render(f"Ход игрока {current_player}", True, BLACK)
    text_rect = turn_text.get_rect(center=indicator_rect.center)
    screen.blit(turn_text, text_rect)

def mark_numbers(card, numbers_to_mark):
    """Помечает указанные числа на карточке игрока"""
    marked_any = False
    for cell in card['cells']:
        if not cell['marked'] and cell['number'] in numbers_to_mark:
            cell['marked'] = True
            marked_any = True
    return marked_any

def get_available_moves(card):
    """Возвращает доступные для закрытия числа с учетом уже закрытых"""
    available = []
    # Проверяем сумму
    if dice_sum in [cell['number'] for cell in card['cells'] if not cell['marked']]:
        available.append(dice_sum)
    
    # Проверяем возможность закрыть оба числа
    both_available = True
    for num in current_dice:
        if num not in [cell['number'] for cell in card['cells'] if not cell['marked']]:
            both_available = False
            break
    
    if both_available:
        available.extend(current_dice)
    
    return available

def draw_buttons():
    # Кнопка "Бросить кости"
    roll_color = BUTTON_HOVER if roll_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, roll_color, roll_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, roll_button, 2, border_radius=5)
    roll_text = font.render("Бросить", True, WHITE)
    screen.blit(roll_text, (roll_button.centerx - roll_text.get_width() // 2, 
                           roll_button.centery - roll_text.get_height() // 2))
    
    # Кнопка "Стоп"
    stop_color = BUTTON_HOVER if stop_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, stop_color, stop_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, stop_button, 2, border_radius=5)
    stop_text = font.render("Стоп", True, WHITE)
    screen.blit(stop_text, (stop_button.centerx - stop_text.get_width() // 2, 
                          stop_button.centery - stop_text.get_height() // 2))
    

running = True
while running:
    current_time = time.time()
    
    # Если кости вращаются и прошло достаточно времени с последнего броска
    if rolling and current_time - last_roll_time > 0.1:  # 100 мс
        current_dice = [random.randint(1, 6), random.randint(1, 6)]
        last_roll_time = current_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not has_rolled and not rolling:
                rolling = True
                last_roll_time = current_time
            elif event.key == pygame.K_1:
                NUM_PLAYERS = 1
                current_player = 1
                player_cards = create_player_cards(NUM_PLAYERS)
                has_rolled = False
                rolling = False
            elif event.key == pygame.K_2:
                NUM_PLAYERS = 2
                current_player = 1
                player_cards = create_player_cards(NUM_PLAYERS)
                has_rolled = False
                rolling = False
            elif event.key == pygame.K_3:
                NUM_PLAYERS = 3
                current_player = 1
                player_cards = create_player_cards(NUM_PLAYERS)
                has_rolled = False
                rolling = False
            elif event.key == pygame.K_4:
                NUM_PLAYERS = 4
                current_player = 1
                player_cards = create_player_cards(NUM_PLAYERS)
                has_rolled = False
                rolling = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Обработка нажатия на кнопки
            if roll_button.collidepoint(mouse_pos) and not has_rolled and not rolling:
                rolling = True
                last_roll_time = current_time
            elif stop_button.collidepoint(mouse_pos) and rolling:
                rolling = False
                dice_sum = sum(current_dice)
                available_numbers = set(current_dice + [dice_sum])
                has_rolled = True
                
                # Проверяем, есть ли доступные ходы
                current_card = next(card for card in player_cards if card['player_num'] == current_player)
                available_moves = get_available_moves(current_card)
                if not available_moves:
                    # Нет доступных ходов - пропускаем ход
                    current_player = current_player % NUM_PLAYERS + 1
                    has_rolled = False
            
            # Обработка кликов по карточкам (как в оригинальном коде)
            clicked_on_cell = False
            for card in player_cards:
                if card['player_num'] == current_player and has_rolled and not rolling:
                    for cell in card['cells']:
                        if cell['rect'].collidepoint(mouse_pos) and not cell['marked']:
                            if cell['number'] in available_numbers:
                                if cell['number'] == dice_sum:
                                    cell['marked'] = True
                                    clicked_on_cell = True
                                elif cell['number'] in current_dice:
                                    other_num = dice_sum - cell['number'] if dice_sum - cell['number'] in current_dice else None
                                    if other_num is not None:
                                        can_mark_both = True
                                        for num in current_dice:
                                            if num not in [c['number'] for c in card['cells'] if not c['marked']]:
                                                can_mark_both = False
                                                break
                                        
                                        if can_mark_both:
                                            marked_both = mark_numbers(card, current_dice)
                                            
                                            if marked_both:
                                                clicked_on_cell = True
                                    else:
                                        cell['marked'] = True
                                        clicked_on_cell = True
                                
                                if clicked_on_cell:
                                    current_player = current_player % NUM_PLAYERS + 1
                                    has_rolled = False
                                    break
                    if clicked_on_cell:
                        break

    screen.blit(background, (0, 0))

    for i in range(2):
        screen.blit(dice_images[current_dice[i]-1], dice_positions[i])

    for card in player_cards:
        pygame.draw.rect(screen, BEIGE, (*card['position'], *card['size']))
        pygame.draw.rect(screen, GRAY, (*card['position'], *card['size']), 2)
        
        if NUM_PLAYERS <= 2:
            player_text_y = card['position'][1] - 20
        else:
            player_text_y = card['position'][1] - 10
            
        player_text = player_font.render(f"Игрок {card['player_num']}", True, BLACK)
        player_rect = player_text.get_rect(
            center=(card['position'][0] + card['size'][0] // 2, 
                    player_text_y))
        screen.blit(player_text, player_rect)
        
        current_card = card['player_num'] == current_player
        available_moves = get_available_moves(card) if current_card else []
        
        for cell in card['cells']:
            if current_card and not cell['marked'] and cell['number'] in available_moves:
                color = HIGHLIGHT
            else:
                color = DARK_BEIGE if cell['marked'] else BEIGE
                
            pygame.draw.rect(screen, color, cell['rect'])
            pygame.draw.rect(screen, GRAY, cell['rect'], 1)
            
            num_text = small_font.render(str(cell['number']), True, BLACK)
            num_rect = num_text.get_rect(center=cell['rect'].center)
            screen.blit(num_text, num_rect)

    # Отображаем информацию о доступных числах
    if has_rolled and not rolling:
        current_card = next(card for card in player_cards if card['player_num'] == current_player)
        available_moves = get_available_moves(current_card)
        if available_moves:
            info_text = font.render(f"Закройте: {', '.join(map(str, sorted(available_moves)))}", True, WHITE)
            screen.blit(info_text, (WIDTH // 2 - 100, 220))
        else:
            info_text = font.render("Нет доступных ходов - пропуск хода", True, WHITE)
            screen.blit(info_text, (WIDTH // 2 - 150, 220))

    # Инструкция
    if rolling:
        instruction = font.render("Кости вращаются... нажмите СТОП", True, WHITE)
    elif not has_rolled:
        instruction = font.render("Нажмите БРОСИТЬ для броска костей", True, WHITE)
    else:
        instruction = font.render("Выберите число для закрытия", True, WHITE)
    screen.blit(instruction, (WIDTH // 2 - 150, HEIGHT - 60))

    players_text = small_font.render(f"Игроков: {NUM_PLAYERS} (1-4 для изменения)", True, WHITE)
    screen.blit(players_text, (20, HEIGHT - 30))
    
    # Рисуем индикатор текущего игрока
    draw_turn_indicator()
    
    # Рисуем кнопки
    draw_buttons()

    pygame.display.flip()

pygame.quit()
sys.exit()


