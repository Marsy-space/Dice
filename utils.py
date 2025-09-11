import pygame
import json
import os
import time
from scripts.theme import theme_manager

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

def create_player_cards(num_players, width, height):
    cards = []
    max_cards_per_row = 2  
    margin = 20  
    card_width = (width - (max_cards_per_row + 1) * margin) // max_cards_per_row if num_players > 2 else (width - (num_players + 1) * margin) // num_players
    card_height = 120
    
    rows = (num_players + max_cards_per_row - 1) // max_cards_per_row
    total_height = rows * card_height + (rows - 1) * margin
    start_y = (height - total_height) // 2 + 50
    
    for player in range(num_players):
        row = player // max_cards_per_row
        col = player % max_cards_per_row
        x = margin + col * (card_width + margin) if num_players <= 2 else (width - (max_cards_per_row * card_width + (max_cards_per_row - 1) * margin)) // 2 + col * (card_width + margin)
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

def check_winner(player_cards):
    for card in player_cards:
        if all(cell['marked'] for cell in card['cells']):
            return card['player_num']
    return 0

def get_available_moves(card, has_rolled, current_dice, dice_sum):
    available = []
    if not has_rolled:
        return available

    available_numbers = [cell['number'] for cell in card['cells'] if not cell['marked']]
    
    if dice_sum in available_numbers:
        available.append(dice_sum)
    
    if all(num in available_numbers for num in current_dice):
        available.extend(current_dice)
    
    return available

def mark_numbers(card, numbers_to_mark):
    marked_any = False
    for cell in card['cells']:
        if not cell['marked'] and cell['number'] in numbers_to_mark:
            cell['marked'] = True
            marked_any = True
    return marked_any

def load_background(width, height):
    try:
        background_path = theme_manager.get_background_path()
        if os.path.exists(background_path):
            background = pygame.image.load(background_path).convert()
            return pygame.transform.scale(background, (width, height))
        else:
            print(f"Файл не найден: {background_path}")
            return None
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None