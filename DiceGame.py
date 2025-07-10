
import pygame
import sys
import random
import time
import json
import os

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игральные кости с карточками игроков")

# Состояния игры
MENU = 0
GAME = 1
RULES = 2
RECORDS = 3
INPUT_NAME = 4
game_state = MENU

NUM_PLAYERS = 2  
current_player = 1
has_rolled = False
rolling = False
last_roll_time = 0
game_over = False
winner = 0
show_exit_confirmation = False
input_active = False
input_text = ""
input_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 40)

# Цвета
BEIGE = (255, 235, 205)         
DARK_BEIGE = (222, 184, 135)   
WHITE = (160, 82, 45)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HIGHLIGHT = (205, 133, 63)
PLAYER_COLORS = [(205, 133, 63), (210, 105, 30), (139, 69, 19), (160, 82, 45)]
BUTTON_COLOR = (222, 184, 135)
BUTTON_HOVER = (150, 150, 150)

# Загрузка фона
try:
    background = pygame.image.load("background1.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except FileNotFoundError:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((50, 50, 50))

# Создание костей
dice_size = 100
dice_images = []
for i in range(6):
    try:
        img = pygame.image.load(f"ice_{i+1}.png").convert_alpha()
        img = pygame.transform.scale(img, (dice_size, dice_size))
        dice_images.append(img)
    except FileNotFoundError:
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

dice_positions = [(WIDTH // 2 - 120, 100), (WIDTH // 2 + 20, 100)]
current_dice = [1, 1]
dice_sum = sum(current_dice)
available_numbers = set(current_dice + [dice_sum])

# Шрифты
font = pygame.font.SysFont('Comic Sans MS', 24)
small_font = pygame.font.SysFont('Comic Sans MS', 18)
player_font = pygame.font.SysFont('Comic Sans MS', 22, bold=True)
large_font = pygame.font.SysFont('Comic Sans MS', 48, bold=True)
title_font = pygame.font.SysFont('Comic Sans MS', 64, bold=True)

# Кнопки
roll_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 120, 40)
stop_button = pygame.Rect(WIDTH // 2 + 30, HEIGHT - 100, 120, 40)
close_button = pygame.Rect(10, 10, 30, 30)
play_button = pygame.Rect(WIDTH // 2 - 150, 200, 300, 60)
players_button = pygame.Rect(WIDTH // 2 - 150, 280, 300, 60)
theme_button = pygame.Rect(WIDTH // 2 - 150, 360, 300, 60)
rules_button = pygame.Rect(WIDTH // 2 - 150, 440, 300, 60)
records_button = pygame.Rect(WIDTH // 2 - 150, 520, 300, 60)
menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)

def create_player_cards(num_players):
    cards = []
    max_cards_per_row = 2  
    margin = 20  
    card_width = (WIDTH - (max_cards_per_row + 1) * margin) // max_cards_per_row if num_players > 2 else (WIDTH - (num_players + 1) * margin) // num_players
    card_height = 120
    
    rows = (num_players + max_cards_per_row - 1) // max_cards_per_row
    total_height = rows * card_height + (rows - 1) * margin
    start_y = (HEIGHT - total_height) // 2 + 50
    
    for player in range(num_players):
        row = player // max_cards_per_row
        col = player % max_cards_per_row
        x = margin + col * (card_width + margin) if num_players <= 2 else (WIDTH - (max_cards_per_row * card_width + (max_cards_per_row - 1) * margin)) // 2 + col * (card_width + margin)
        y = start_y + row * (card_height + margin)
        
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
            cells.append({'rect': rect, 'number': i+1, 'marked': False})
        
        cards.append({'position': (x, y), 'size': (card_width, card_height), 'cells': cells, 'player_num': player + 1})
    
    return cards

player_cards = create_player_cards(NUM_PLAYERS)

def load_records():
    if os.path.exists('records.json'):
        with open('records.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_records(records):
    with open('records.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def add_record(player_name, player_num):
    records = load_records()
    records.append({
        'name': player_name,
        'player_num': player_num,
        'date': time.strftime("%Y-%m-%d %H:%M:%S")
    })
    save_records(records[-10:])  # Сохраняем только последние 10 записей

def draw_turn_indicator():
    indicator_rect = pygame.Rect(WIDTH - 170, 20, 150, 50)
    pygame.draw.rect(screen, PLAYER_COLORS[current_player-1], indicator_rect)
    pygame.draw.rect(screen, BLACK, indicator_rect, 2)
    turn_text = player_font.render(f"Ход игрока {current_player}", True, BLACK)
    screen.blit(turn_text, turn_text.get_rect(center=indicator_rect.center))

def draw_buttons():
    # Кнопка "Бросить кости"
    roll_color = BUTTON_HOVER if roll_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, roll_color, roll_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, roll_button, 2, border_radius=5)
    roll_text = font.render("Бросить", True, WHITE)
    screen.blit(roll_text, (roll_button.centerx - roll_text.get_width() // 2, roll_button.centery - roll_text.get_height() // 2))
    
    # Кнопка "Стоп"
    stop_color = BUTTON_HOVER if stop_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, stop_color, stop_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, stop_button, 2, border_radius=5)
    stop_text = font.render("Стоп", True, WHITE)
    screen.blit(stop_text, (stop_button.centerx - stop_text.get_width() // 2, stop_button.centery - stop_text.get_height() // 2))

def mark_numbers(card, numbers_to_mark):
    marked_any = False
    for cell in card['cells']:
        if not cell['marked'] and cell['number'] in numbers_to_mark:
            cell['marked'] = True
            marked_any = True
    return marked_any

def get_available_moves(card):
    available = []
    if not has_rolled:
        return available
    
    if dice_sum in [cell['number'] for cell in card['cells'] if not cell['marked']]:
        available.append(dice_sum)
    
    if all(num in [cell['number'] for cell in card['cells'] if not cell['marked']] for num in current_dice):
        available.extend(current_dice)
    
    return available

def check_winner():
    for card in player_cards:
        if all(cell['marked'] for cell in card['cells']):
            return card['player_num']
    return 0

def draw_exit_confirmation():
    """Рисует окно подтверждения выхода"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    confirm_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
    pygame.draw.rect(screen, BEIGE, confirm_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, confirm_rect, 2, border_radius=10)
    
    warning_text = font.render("Прогресс игры не сохранится!", True, BLACK)
    question_text = font.render("Вы точно хотите выйти?", True, BLACK)
    
    screen.blit(warning_text, (confirm_rect.centerx - warning_text.get_width()//2, confirm_rect.y + 40))
    screen.blit(question_text, (confirm_rect.centerx - question_text.get_width()//2, confirm_rect.y + 80))
    
    yes_button = pygame.Rect(confirm_rect.x + 50, confirm_rect.y + 120, 100, 50)
    no_button = pygame.Rect(confirm_rect.x + 250, confirm_rect.y + 120, 100, 50)
    
    pygame.draw.rect(screen, (255, 99, 71), yes_button, border_radius=5)
    pygame.draw.rect(screen, (144, 238, 144), no_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, yes_button, 2, border_radius=5)
    pygame.draw.rect(screen, BLACK, no_button, 2, border_radius=5)
    
    yes_text = font.render("Да", True, BLACK)
    no_text = font.render("Нет", True, BLACK)
    
    screen.blit(yes_text, (yes_button.centerx - yes_text.get_width()//2, yes_button.centery - yes_text.get_height()//2))
    screen.blit(no_text, (no_button.centerx - no_text.get_width()//2, no_button.centery - no_text.get_height()//2))
    
    return yes_button, no_button

def draw_winner_screen():
    global input_active, input_text
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    winner_text = large_font.render(f"Игрок {winner} победил!", True, WHITE)
    screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 100))
    
    if game_state == INPUT_NAME:
        name_text = font.render("Введите ваше имя:", True, WHITE)
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2 - 30))
        
        pygame.draw.rect(screen, WHITE, input_rect, 2)
        pygame.draw.rect(screen, BEIGE, input_rect)
        text_surface = font.render(input_text, True, BLACK)
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        
        if input_active:
            pygame.draw.rect(screen, BLACK, input_rect, 2)
    else:
        restart_text = font.render("Нажмите R для новой игры", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
    
    menu_color = BUTTON_HOVER if menu_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, menu_color, menu_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, menu_button, 2, border_radius=5)
    menu_text = font.render("В меню", True, WHITE)
    screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2, menu_button.centery - menu_text.get_height() // 2))

def draw_records_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    records_rect = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 300, 700, 600)
    pygame.draw.rect(screen, BEIGE, records_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, records_rect, 2, border_radius=10)
    
    title = title_font.render("Таблица рекордов", True, BLACK)
    screen.blit(title, (records_rect.centerx - title.get_width()//2, records_rect.y + 1))
    
    records = load_records()
    if not records:
        no_records = font.render("Пока нет сохраненных рекордов", True, BLACK)
        screen.blit(no_records, (records_rect.centerx - no_records.get_width()//2, records_rect.centery - no_records.get_height()//2))
    else:
        headers = ["Имя", "Игрок", "Дата"]
        header_y = records_rect.y + 90
        for i, header in enumerate(headers):
            text = player_font.render(header, True, BLACK)
            screen.blit(text, (records_rect.x + 50 + i * 200, header_y))
        
        for i, record in enumerate(reversed(records)):
            y = header_y + 40 + i * 40
            if y > records_rect.y + records_rect.height - 50:
                break
            
            name_text = font.render(record['name'], True, BLACK)
            screen.blit(name_text, (records_rect.x + 50, y))
            
            player_text = font.render(f"Игрок {record['player_num']}", True, BLACK)
            screen.blit(player_text, (records_rect.x + 250, y))
            
            date_text = font.render(record['date'], True, BLACK)
            screen.blit(date_text, (records_rect.x + 450, y))
    
    back_button = pygame.Rect(records_rect.centerx - 100, records_rect.y + records_rect.height - 70, 200, 50)
    back_color = BUTTON_HOVER if back_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, back_color, back_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, back_button, 2, border_radius=5)
    back_text = font.render("Назад", True, BLACK)
    screen.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))
    
    return back_button

def draw_rules_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    rules_rect = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 300, 800, 600)
    pygame.draw.rect(screen, BEIGE, rules_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rules_rect, 2, border_radius=10)
    
    title = title_font.render("Правила игры", True, BLACK)
    screen.blit(title, (rules_rect.centerx - title.get_width()//2, rules_rect.y + 5))
    
    rules = [
        "Суть игры:",
        "- Каждый игрок получает карточку с числами от 1 до 12.",
        "- По очереди игроки бросают две шестигранные кости.",
        "- После броска можно закрыть на своей карточке:",
        "  - одно из выпавших чисел (например, если выпало 2 и 4,",
        "    можно закрыть 2 или 4),",
        "  - либо их сумму (2 + 4 = 6 → можно закрыть 6).",
        "- Если подходящих чисел нет — ход пропускается.",
        "- Побеждает тот, кто первым закроет все числа",
        "  на своей карточке!"
    ]
    
    for i, line in enumerate(rules):
        text = font.render(line, True, BLACK)
        screen.blit(text, (rules_rect.x + 30, rules_rect.y + 100 + i * 30))
    
    back_button = pygame.Rect(rules_rect.centerx - 100, rules_rect.y + 450, 200, 50)
    back_color = BUTTON_HOVER if back_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, back_color, back_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, back_button, 2, border_radius=5)
    back_text = font.render("Назад", True, BLACK)
    screen.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))
    
    return back_button

def draw_menu():
    screen.blit(background, (0, 0))
    
    title = title_font.render("Игра в кости", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    
    buttons = [
        (play_button, "Играть"),
        (players_button, f"Игроков: {NUM_PLAYERS}"),
        (theme_button, "Оформление"),
        (rules_button, "Правила"),
        (records_button, "Рекорды")
    ]
    
    for button, text in buttons:
        color = BUTTON_HOVER if button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(screen, color, button, border_radius=10)
        pygame.draw.rect(screen, BLACK, button, 2, border_radius=10)
        btn_text = font.render(text, True, WHITE)
        screen.blit(btn_text, (button.centerx - btn_text.get_width() // 2, button.centery - btn_text.get_height() // 2))

def draw_game():
    screen.blit(background, (0, 0))
    
    if not game_over:
        pygame.draw.rect(screen, (200, 0, 0), close_button, border_radius=15)
        close_text = font.render("×", True, BLACK)
        screen.blit(close_text, (close_button.centerx - close_text.get_width()//2, close_button.centery - close_text.get_height()//2))
        
        if show_exit_confirmation:
            yes_button, no_button = draw_exit_confirmation()
        else:
            for i in range(2):
                screen.blit(dice_images[current_dice[i]-1], dice_positions[i])
            
            for card in player_cards:
                pygame.draw.rect(screen, BEIGE, (*card['position'], *card['size']))
                pygame.draw.rect(screen, GRAY, (*card['position'], *card['size']), 2)
                
                player_text_y = card['position'][1] - 20 if NUM_PLAYERS <= 2 else card['position'][1] - 10
                player_text = player_font.render(f"Игрок {card['player_num']}", True, BLACK)
                screen.blit(player_text, player_text.get_rect(center=(card['position'][0] + card['size'][0] // 2, player_text_y)))
                
                current_card = card['player_num'] == current_player
                available_moves = get_available_moves(card) if current_card else []
                
                for cell in card['cells']:
                    color = HIGHLIGHT if current_card and not cell['marked'] and cell['number'] in available_moves else DARK_BEIGE if cell['marked'] else BEIGE
                    pygame.draw.rect(screen, color, cell['rect'])
                    pygame.draw.rect(screen, GRAY, cell['rect'], 1)
                    
                    if not cell['marked']:
                        num_text = small_font.render(str(cell['number']), True, BLACK)
                        screen.blit(num_text, num_text.get_rect(center=cell['rect'].center))
            
            if has_rolled and not rolling:
                current_card = next(card for card in player_cards if card['player_num'] == current_player)
                available_moves = get_available_moves(current_card)
                if available_moves:
                    info_text = font.render(f"Закройте: {', '.join(map(str, sorted(available_moves)))}", True, WHITE)
                    screen.blit(info_text, (WIDTH // 2 - 90, 50))
                else:
                    info_text = font.render("Нет доступных ходов - пропуск хода", True, WHITE)
                    screen.blit(info_text, (WIDTH // 2 - 150, 220))
            
            instruction = font.render(
                "Кости вращаются... нажмите СТОП" if rolling else 
                "Нажмите БРОСИТЬ или ПРОБЕЛ для броска костей" if not has_rolled else 
                "Выберите число для закрытия", 
                True, WHITE)
            screen.blit(instruction, (WIDTH // 2 - 250, HEIGHT - 60))
            
            players_text = small_font.render(f"Игроков: {NUM_PLAYERS}", True, WHITE)
            screen.blit(players_text, (20, HEIGHT - 30))
            
            draw_turn_indicator()
            draw_buttons()
    else:
        draw_winner_screen()

running = True
while running:
    current_time = time.time()
    
    if rolling and current_time - last_roll_time > 0.1:
        current_dice = [random.randint(1, 6), random.randint(1, 6)]
        last_roll_time = current_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state in [RULES, RECORDS]:
                    game_state = MENU
                elif game_state == GAME:
                    game_state = MENU
            elif game_state == INPUT_NAME:
                if event.key == pygame.K_RETURN:
                    if input_text.strip():
                        add_record(input_text.strip(), winner)
                        game_state = GAME
                        input_active = False
                        input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
            elif event.key == pygame.K_SPACE and not has_rolled and not rolling and not game_over and game_state == GAME:
                rolling = True
                last_roll_time = current_time
            elif event.key == pygame.K_r and game_over and game_state == GAME:
                game_over = False
                winner = 0
                current_player = 1
                player_cards = create_player_cards(NUM_PLAYERS)
                has_rolled = False
                rolling = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if game_state == MENU:
                if play_button.collidepoint(mouse_pos):
                    game_state = GAME
                    game_over = False
                    winner = 0
                    current_player = 1
                    player_cards = create_player_cards(NUM_PLAYERS)
                    has_rolled = False
                    rolling = False
                    show_exit_confirmation = False
                elif players_button.collidepoint(mouse_pos):
                    NUM_PLAYERS = NUM_PLAYERS % 4 + 1
                elif rules_button.collidepoint(mouse_pos):
                    game_state = RULES
                elif records_button.collidepoint(mouse_pos):
                    game_state = RECORDS
            elif game_state == RULES:
                back_button = draw_rules_screen()
                if back_button.collidepoint(mouse_pos):
                    game_state = MENU
            elif game_state == RECORDS:
                back_button = draw_records_screen()
                if back_button.collidepoint(mouse_pos):
                    game_state = MENU
            elif game_state == GAME:
                if game_over:
                    if menu_button.collidepoint(mouse_pos):
                        game_state = MENU
                elif not game_over:
                    if show_exit_confirmation:
                        yes_button, no_button = draw_exit_confirmation()
                        if yes_button.collidepoint(mouse_pos):
                            game_state = MENU
                        elif no_button.collidepoint(mouse_pos):
                            show_exit_confirmation = False
                    else:
                        if close_button.collidepoint(mouse_pos):
                            show_exit_confirmation = True
                            
                        if roll_button.collidepoint(mouse_pos) and not has_rolled and not rolling:
                            rolling = True
                            last_roll_time = current_time
                        elif stop_button.collidepoint(mouse_pos) and rolling:
                            rolling = False
                            dice_sum = sum(current_dice)
                            available_numbers = set(current_dice + [dice_sum])
                            has_rolled = True
                            
                            current_card = next(card for card in player_cards if card['player_num'] == current_player)
                            if not get_available_moves(current_card):
                                current_player = current_player % NUM_PLAYERS + 1
                                has_rolled = False
                                available_numbers = set()
                        
                        clicked_on_cell = False
                        for card in player_cards:
                            if card['player_num'] == current_player and has_rolled and not rolling:
                                for cell in card['cells']:
                                    if cell['rect'].collidepoint(mouse_pos) and not cell['marked'] and cell['number'] in available_numbers:
                                        if cell['number'] == dice_sum:
                                            cell['marked'] = True
                                            clicked_on_cell = True
                                        elif cell['number'] in current_dice:
                                            other_num = dice_sum - cell['number'] if dice_sum - cell['number'] in current_dice else None
                                            if other_num is not None:
                                                can_mark_both = all(num in [c['number'] for c in card['cells'] if not c['marked']] for num in current_dice)
                                                if can_mark_both and mark_numbers(card, current_dice):
                                                    clicked_on_cell = True
                                            else:
                                                cell['marked'] = True
                                                clicked_on_cell = True
                                        
                                        if clicked_on_cell:
                                            winner = check_winner()
                                            if winner > 0:
                                                game_over = True
                                                game_state = INPUT_NAME
                                                input_active = True
                                            else:
                                                current_player = current_player % NUM_PLAYERS + 1
                                                has_rolled = False
                                                available_numbers = set()
                                            break
                                if clicked_on_cell:
                                    break

    if game_state == MENU:
        draw_menu()
    elif game_state == RULES:
        draw_rules_screen()
    elif game_state == RECORDS:
        draw_records_screen()
    elif game_state == GAME:
        draw_game()
    elif game_state == INPUT_NAME:
        draw_winner_screen()

    pygame.display.flip()

pygame.quit()
sys.exit()