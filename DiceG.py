import pygame
import sys
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игральные кости с карточками игроков")

# Состояния игры
MENU = 0
GAME = 1
game_state = MENU  # Начинаем с меню

NUM_PLAYERS = 2  
current_player = 1  # Текущий игрок (начинает первый)
has_rolled = False  # Флаг, что игрок уже бросал кости в этот ход
rolling = False     # Флаг, что кости сейчас вращаются
last_roll_time = 0  # Время последнего броска
game_over = False   # Флаг окончания игры
winner = 0          # Номер победителя
show_exit_confirmation = False  # Флаг для подтверждения выхода

BEIGE = (255, 235, 205)         
DARK_BEIGE = (222, 184, 135)   
DARK_BLUE = (255, 235, 205)        
WHITE = (160, 82, 45)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HIGHLIGHT = (205, 133, 63)  # Цвет подсветки доступных чисел
PLAYER_COLORS = [(205, 133, 63), (210, 105, 30), (139, 69, 19), (160, 82, 45)]  # Цвета для индикатора игроков
BUTTON_COLOR = (222, 184, 135)
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
available_numbers = set(current_dice + [dice_sum])  # Доступные для закрытия чисел

font = pygame.font.SysFont('Comic Sans MS', 24)
small_font = pygame.font.SysFont('Comic Sans MS', 18)
player_font = pygame.font.SysFont('Comic Sans MS', 22, bold=True)  
large_font = pygame.font.SysFont('Comic Sans MS', 48, bold=True)  # Для сообщения о победе
title_font = pygame.font.SysFont('Comic Sans MS', 64, bold=True)  # Для заголовка меню

# Кнопки игры
roll_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 120, 40)
stop_button = pygame.Rect(WIDTH // 2 + 30, HEIGHT - 100, 120, 40)
close_button = pygame.Rect(10, 10, 30, 30)  # Кнопка закрытия

# Кнопки меню
play_button = pygame.Rect(WIDTH // 2 - 150, 200, 300, 60)
players_button = pygame.Rect(WIDTH // 2 - 150, 280, 300, 60)
theme_button = pygame.Rect(WIDTH // 2 - 150, 360, 300, 60)
settings_button = pygame.Rect(WIDTH // 2 - 150, 440, 300, 60)

# Кнопка возврата в меню
menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)

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
    if not has_rolled:  # Если игрок еще не бросал кости, нет доступных ходов
        return available
    
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

def check_winner():
    """Проверяет, есть ли победитель (все клетки закрыты)"""
    for card in player_cards:
        if all(cell['marked'] for cell in card['cells']):
            return card['player_num']
    return 0

def draw_winner_screen():
    """Рисует экран с победителем"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Полупрозрачный черный фон
    screen.blit(overlay, (0, 0))
    
    winner_text = large_font.render(f"Игрок {winner} победил!", True, WHITE)
    restart_text = font.render("Нажмите R для новой игры", True, WHITE)
    
    screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
    
    # Кнопка "В меню"
    menu_color = BUTTON_HOVER if menu_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, menu_color, menu_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, menu_button, 2, border_radius=5)
    menu_text = font.render("В меню", True, WHITE)
    screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2, 
                          menu_button.centery - menu_text.get_height() // 2))

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

def draw_menu():
    screen.blit(background, (0, 0))
    
    # Заголовок
    title = title_font.render("Игра в кости", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    
    # Кнопка "Играть"
    play_color = BUTTON_HOVER if play_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, play_color, play_button, border_radius=10)
    pygame.draw.rect(screen, BLACK, play_button, 2, border_radius=10)
    play_text = font.render("Играть", True, WHITE)
    screen.blit(play_text, (play_button.centerx - play_text.get_width() // 2, 
                           play_button.centery - play_text.get_height() // 2))
    
    # Кнопка "Количество игроков"
    players_color = BUTTON_HOVER if players_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, players_color, players_button, border_radius=10)
    pygame.draw.rect(screen, BLACK, players_button, 2, border_radius=10)
    players_text = font.render(f"Игроков: {NUM_PLAYERS}", True, WHITE)
    screen.blit(players_text, (players_button.centerx - players_text.get_width() // 2, 
                             players_button.centery - players_text.get_height() // 2))
    
    # Кнопка "Оформление"
    theme_color = BUTTON_HOVER if theme_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, theme_color, theme_button, border_radius=10)
    pygame.draw.rect(screen, BLACK, theme_button, 2, border_radius=10)
    theme_text = font.render("Оформление", True, WHITE)
    screen.blit(theme_text, (theme_button.centerx - theme_text.get_width() // 2, 
                           theme_button.centery - theme_text.get_height() // 2))
    
    # Кнопка "Настройки"
    settings_color = BUTTON_HOVER if settings_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, settings_color, settings_button, border_radius=10)
    pygame.draw.rect(screen, BLACK, settings_button, 2, border_radius=10)
    settings_text = font.render("Настройки", True, WHITE)
    screen.blit(settings_text, (settings_button.centerx - settings_text.get_width() // 2, 
                              settings_button.centery - settings_text.get_height() // 2))

def draw_exit_confirmation():
    """Рисует окно подтверждения выхода"""
    # Затемнение фона
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Окно подтверждения
    confirm_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
    pygame.draw.rect(screen, BEIGE, confirm_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, confirm_rect, 2, border_radius=10)
    
    # Текст
    warning_text = font.render("Прогресс игры не сохранится!", True, BLACK)
    question_text = font.render("Вы точно хотите выйти?", True, BLACK)
    
    screen.blit(warning_text, (confirm_rect.centerx - warning_text.get_width()//2, 
                             confirm_rect.y + 40))
    screen.blit(question_text, (confirm_rect.centerx - question_text.get_width()//2, 
                              confirm_rect.y + 80))
    
    # Кнопки Да/Нет
    yes_button = pygame.Rect(confirm_rect.x + 50, confirm_rect.y + 120, 100, 50)
    no_button = pygame.Rect(confirm_rect.x + 250, confirm_rect.y + 120, 100, 50)
    
    pygame.draw.rect(screen, (255, 99, 71), yes_button, border_radius=5)
    pygame.draw.rect(screen, (144, 238, 144), no_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, yes_button, 2, border_radius=5)
    pygame.draw.rect(screen, BLACK, no_button, 2, border_radius=5)
    
    yes_text = font.render("Да", True, BLACK)
    no_text = font.render("Нет", True, BLACK)
    
    screen.blit(yes_text, (yes_button.centerx - yes_text.get_width()//2, 
                         yes_button.centery - yes_text.get_height()//2))
    screen.blit(no_text, (no_button.centerx - no_text.get_width()//2, 
                        no_button.centery - no_text.get_height()//2))
    
    return yes_button, no_button

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
            if event.key == pygame.K_ESCAPE and game_state == GAME:
                game_state = MENU  # Возврат в меню по ESC
            elif event.key == pygame.K_SPACE and not has_rolled and not rolling and not game_over and game_state == GAME:
                rolling = True
                last_roll_time = current_time
            elif event.key == pygame.K_r and game_over and game_state == GAME:
                # Перезапуск игры
                game_over = False
                winner = 0
                current_player = 1
                player_cards = create_player_cards(NUM_PLAYERS)
                has_rolled = False
                rolling = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if game_state == MENU:
                # Обработка кликов в меню
                if play_button.collidepoint(mouse_pos):
                    game_state = GAME
                    # Сброс игры при начале новой
                    game_over = False
                    winner = 0
                    current_player = 1
                    player_cards = create_player_cards(NUM_PLAYERS)
                    has_rolled = False
                    rolling = False
                    show_exit_confirmation = False
                elif players_button.collidepoint(mouse_pos):
                    # Циклическое изменение количества игроков
                    NUM_PLAYERS = NUM_PLAYERS % 4 + 1
            elif game_state == GAME:
                if game_over:
                    # Обработка кликов на экране окончания игры
                    if menu_button.collidepoint(mouse_pos):
                        game_state = MENU
                elif not game_over:
                    if show_exit_confirmation:
                        yes_button, no_button = draw_exit_confirmation()
                        if yes_button.collidepoint(mouse_pos):
                            #running = False
                            game_state = MENU
                        elif no_button.collidepoint(mouse_pos):
                            show_exit_confirmation = False
                    else:
                        # Обработка клика на кнопку закрытия
                        if close_button.collidepoint(mouse_pos):
                            show_exit_confirmation = True
                            
                        # Обработка кликов в игре
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
                                available_numbers = set()  # Очищаем доступные числа
                        
                        # Обработка кликов по карточкам
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
                                                # Проверяем, не победил ли игрок
                                                winner = check_winner()
                                                if winner > 0:
                                                    game_over = True
                                                else:
                                                    current_player = current_player % NUM_PLAYERS + 1
                                                    has_rolled = False
                                                    available_numbers = set()  # Очищаем доступные числа
                                                break
                                if clicked_on_cell:
                                    break

    if game_state == MENU:
        draw_menu()
    elif game_state == GAME:
        screen.blit(background, (0, 0))

        if not game_over:
            # Рисуем кнопку закрытия
            pygame.draw.rect(screen, (255, 0, 0), close_button, border_radius=15)
            close_text = font.render("×", True, WHITE)
            screen.blit(close_text, (close_button.centerx - close_text.get_width()//2, 
                                   close_button.centery - close_text.get_height()//2))
            
            if show_exit_confirmation:
                draw_exit_confirmation()
            else:
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
                        
                        # Рисуем число только если клетка не помечена
                        if not cell['marked']:
                            num_text = small_font.render(str(cell['number']), True, BLACK)
                            num_rect = num_text.get_rect(center=cell['rect'].center)
                            screen.blit(num_text, num_rect)

                # Отображаем информацию о доступных числах
                if has_rolled and not rolling:
                    current_card = next(card for card in player_cards if card['player_num'] == current_player)
                    available_moves = get_available_moves(current_card)
                    if available_moves:
                        info_text = font.render(f"Закройте: {', '.join(map(str, sorted(available_moves)))}", True, WHITE)
                        screen.blit(info_text, (WIDTH // 2 - 90, 50))
                    else:
                        info_text = font.render("Нет доступных ходов - пропуск хода", True, WHITE)
                        screen.blit(info_text, (WIDTH // 2 - 150, 220))

                # Инструкция
                if rolling:
                    instruction = font.render("Кости вращаются... нажмите СТОП", True, WHITE)
                elif not has_rolled:
                    instruction = font.render("Нажмите БРОСИТЬ или ПРОБЕЛ для броска костей", True, WHITE)
                else:
                    instruction = font.render("Выберите число для закрытия", True, WHITE)
                screen.blit(instruction, (WIDTH // 2 - 250, HEIGHT - 60))

                players_text = small_font.render(f"Игроков: {NUM_PLAYERS}", True, WHITE)
                screen.blit(players_text, (20, HEIGHT - 30))
                
                # Рисуем индикатор текущего игрока
                draw_turn_indicator()
                
                # Рисуем кнопки
                draw_buttons()
        else:
            draw_winner_screen()

    pygame.display.flip()

pygame.quit()
sys.exit()