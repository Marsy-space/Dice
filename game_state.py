import pygame
import time
import sys
import os
from data.scripts.dice import Dice
from data.scripts.player import Player
from data.scripts.button import Button
from data.scripts.menu import Menu
from data.scripts.utils import add_record, check_winner, get_available_moves, mark_numbers, create_player_cards, load_background

class GameState:
    def __init__(self, width, height, screen):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen
        
        # Состояния игры
        self.MENU = 0
        self.GAME = 1
        self.RULES = 2
        self.RECORDS = 3
        self.INPUT_NAME = 4
        self.state = self.MENU
        
        # Загрузка звуков
        self.load_sounds()
        
        # Игровые объекты
        self.dice = Dice(self.WIDTH, self.HEIGHT)
        self.player = Player(2, self.WIDTH, self.HEIGHT)
        self.menu = Menu(self.WIDTH, self.HEIGHT)
        
        # Кнопки игры
        self.roll_button = Button(pygame.Rect(self.WIDTH // 2 - 150, self.HEIGHT - 100, 120, 40), "Бросить")
        self.stop_button = Button(pygame.Rect(self.WIDTH // 2 + 30, self.HEIGHT - 100, 120, 40), "Стоп")
        self.close_button = pygame.Rect(10, 10, 30, 30)
        self.menu_button = Button(pygame.Rect(self.WIDTH // 2 - 100, self.HEIGHT // 2 + 160, 200, 50), "В меню")
        
        # Состояние игры
        self.game_over = False
        self.winner = 0
        self.show_exit_confirmation = False
        self.input_active = False
        self.input_text = ""
        self.input_rect = pygame.Rect(self.WIDTH//2 - 100, self.HEIGHT//2 + 20, 200, 40)
        
        # Шрифты
        self.font = pygame.font.SysFont('Comic Sans MS', 24)
        self.large_font = pygame.font.SysFont('Comic Sans MS', 48, bold=True)
        self.title_font = pygame.font.SysFont('Comic Sans MS', 64, bold=True)

        self.yes_button = Button(pygame.Rect(self.WIDTH//2 - 150, self.HEIGHT//2 + 120, 100, 50), "Да", (255, 99, 71))
        self.no_button = Button(pygame.Rect(self.WIDTH//2 + 50, self.HEIGHT//2 + 120, 100, 50), "Нет", (144, 238, 144))

        self.play_music("menu")
    
    def load_sounds(self):
        try:
            music_dir = os.path.join("data", "mixer", "music")
            sfx_dir = os.path.join("data", "mixer", "sfx")
            os.makedirs(music_dir, exist_ok=True)
            
            music_files = {
                "menu_music": "menu_music.mp3",
                "ingame_music": "ingame_music.mp3", 
            }

            sfx_files = {
                "dice_roll": "dice_roll.wav",
                "win": "win.wav"
            }
            
            self.sounds = {}
            
            for sound_name, filename in music_files.items():
                filepath = os.path.join(music_dir, filename)
                if os.path.exists(filepath):
                    try:
                        if filename.endswith('.mp3'):
                            self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                        
                        print(f"Загружен звук: {filename}")
                        
                    except pygame.error as e:
                        print(f"Ошибка загрузки {filename}: {e}")
                        self.sounds[sound_name] = None
                else:
                    print(f"Файл не найден: {filepath}")
                    self.sounds[sound_name] = None

            for sound_name, filename in sfx_files.items():
                filepath = os.path.join(sfx_dir, filename)
                if os.path.exists(filepath):
                    try:
                        if filename.endswith('.wav'):
                            self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                        
                        print(f"Загружен звук: {filename}")
                        
                    except pygame.error as e:
                        print(f"Ошибка загрузки {filename}: {e}")
                        self.sounds[sound_name] = None
                else:
                    print(f"Файл не найден: {filepath}")
                    self.sounds[sound_name] = None
            
            for sound_name in self.sounds:
                if self.sounds[sound_name]:
                    if sound_name in ['menu_music', 'ingame_music']:
                        self.sounds[sound_name].set_volume(0.5)
                    else:
                        self.sounds[sound_name].set_volume(0.7)
                        
        except Exception as e:
            print(f"Ошибка инициализации звуков: {e}")
            self.sounds = {
                "menu_music": None,
                "ingame_music": None,
                "dice_roll": None,
                "win": None
            }

    def play_music(self, music_type):
        pygame.mixer.stop()
        
        if music_type == "menu" and self.sounds["menu_music"]:
            try:
                self.sounds["menu_music"].play(-1)
                print("Запущена музыка меню")
            except Exception as e:
                print(f"Ошибка воспроизведения музыки меню: {e}")
        elif music_type == "ingame" and self.sounds["ingame_music"]:
            try:
                self.sounds["ingame_music"].play(-1)
                print("Запущена игровая музыка")
            except Exception as e:
                print(f"Ошибка воспроизведения игровой музыки: {e}")

    def play_sound_effect(self, sound_type):
        if sound_type in self.sounds and self.sounds[sound_type]:
            try:
                if sound_type == "win":
                    pygame.mixer.stop()
                self.sounds[sound_type].play()
            except:
                pass
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in [self.RULES, self.RECORDS]:
                        self.state = self.MENU
                        self.play_music("menu")
                    elif self.state == self.GAME:
                        self.show_exit_confirmation = True
                elif self.state == self.INPUT_NAME:
                    if event.key == pygame.K_RETURN:
                        if self.input_text.strip():
                            add_record(self.input_text.strip(), self.winner)
                            self.state = self.GAME
                            self.input_active = False
                            self.input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode
                elif event.key == pygame.K_SPACE and not self.dice.has_rolled and not self.dice.rolling and not self.game_over and self.state == self.GAME:
                    self.dice.roll()
                    self.play_sound_effect("dice_roll")
                elif event.key == pygame.K_r and self.game_over and self.state == self.GAME:
                    self.reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.handle_mouse_click(mouse_pos)
    
    def handle_mouse_click(self, mouse_pos):
        if self.state == self.MENU:
            menu_action = self.menu.handle_click(mouse_pos)
            if menu_action == "PLAY":
                self.state = self.GAME
                self.play_music("ingame")
                self.reset_game()
            elif menu_action == "PLAYERS":
                self.player.NUM_PLAYERS = self.player.NUM_PLAYERS % 4 + 1
                self.menu.update_players_button(self.player.NUM_PLAYERS)
                self.player.player_cards = create_player_cards(self.player.NUM_PLAYERS, self.WIDTH, self.HEIGHT)
            elif menu_action == "RULES":
                self.state = self.RULES
            elif menu_action == "RECORDS":
                self.state = self.RECORDS
        elif self.state == self.GAME:
            if self.game_over:
                if self.menu_button.is_hovered(mouse_pos):
                    self.state = self.MENU
                    self.play_music("menu")
            elif not self.game_over:
                if self.show_exit_confirmation:
                    if self.yes_button.is_hovered(mouse_pos):
                        self.state = self.MENU
                        self.play_music("menu")
                        self.show_exit_confirmation = False
                    elif self.no_button.is_hovered(mouse_pos):
                        self.show_exit_confirmation = False
                else:
                    if self.close_button.collidepoint(mouse_pos) and not self.game_over:
                        self.show_exit_confirmation = True
                        
                    if self.roll_button.is_hovered(mouse_pos) and not self.dice.has_rolled and not self.dice.rolling:
                        self.dice.roll()
                        self.play_sound_effect("dice_roll")
                    elif self.stop_button.is_hovered(mouse_pos) and self.dice.rolling:
                        self.dice.stop()
                        
                        current_card = next(card for card in self.player.player_cards if card['player_num'] == self.player.current_player)
                        if not get_available_moves(current_card, self.dice.has_rolled, self.dice.current_dice, self.dice.dice_sum):
                            self.player.next_turn()
                            self.dice.has_rolled = False
                            self.dice.available_numbers = set()
                    
                    clicked_on_cell = False
                    for card in self.player.player_cards:
                        if card['player_num'] == self.player.current_player and self.dice.has_rolled and not self.dice.rolling:
                            for cell in card['cells']:
                                if cell['rect'].collidepoint(mouse_pos) and not cell['marked'] and cell['number'] in self.dice.available_numbers:
                                    
                                    if cell['number'] == self.dice.dice_sum:
                                        cell['marked'] = True
                                        clicked_on_cell = True
                                    elif cell['number'] in self.dice.current_dice:
                                        numbers_to_mark = self.dice.current_dice.copy()
                                        available_numbers = [c['number'] for c in card['cells'] if not c['marked']]
                                        if all(num in available_numbers for num in numbers_to_mark):
                                            for num in numbers_to_mark:
                                                for c in card['cells']:
                                                    if c['number'] == num and not c['marked']:
                                                        c['marked'] = True
                                                        break
                                            clicked_on_cell = True
                                    
                                    if clicked_on_cell:
                                        self.winner = check_winner(self.player.player_cards)
                                        if self.winner > 0:
                                            self.game_over = True
                                            self.state = self.INPUT_NAME
                                            self.input_active = True
                                            self.play_sound_effect("win")
                                        else:
                                            self.player.next_turn()
                                            self.dice.has_rolled = False
                                            self.dice.available_numbers = set()
                                        break
                            if clicked_on_cell:
                                break
        elif self.state in [self.RULES, self.RECORDS]:
            if self.menu_button.is_hovered(mouse_pos):
                self.state = self.MENU
                self.play_music("menu")
        elif self.state == self.INPUT_NAME:
            if self.menu_button.is_hovered(mouse_pos):
                self.state = self.MENU
                self.play_music("menu")
                self.input_active = False
                self.input_text = ""
    
    def update(self):
        if self.state == self.GAME:
            self.dice.update()
            if self.dice.rolling and self.sounds["dice_roll"]:
                current_time = pygame.time.get_ticks()
                if not hasattr(self, 'last_dice_sound_time'):
                    self.last_dice_sound_time = 0
                    
                if current_time - self.last_dice_sound_time > 150:
                    try:
                        self.sounds["dice_roll"].play()
                        self.last_dice_sound_time = current_time
                    except:
                        pass
    
    def render(self):
        if self.state == self.MENU:
            self.menu.render(self.screen)
        elif self.state == self.GAME:
            self.render_game()
        elif self.state == self.RULES:
            self.render_rules()
        elif self.state == self.RECORDS:
            self.render_records()
        elif self.state == self.INPUT_NAME:
            self.render_winner_screen()
    
    def render_game(self):
        background = load_background(self)
        if background:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((50, 50, 50))
        
        if not self.game_over:
            pygame.draw.rect(self.screen, (200, 0, 0), self.close_button, border_radius=15)
            close_text = self.font.render("×", True, (0, 0, 0))
            self.screen.blit(close_text, (self.close_button.centerx - close_text.get_width()//2, self.close_button.centery - close_text.get_height()//2))
            
            if self.show_exit_confirmation:
                self.render_exit_confirmation()
            else:
                self.dice.render(self.screen)
                
                self.player.render(self.screen, self.dice)
                
                if self.dice.has_rolled and not self.dice.rolling:
                    current_card = next(card for card in self.player.player_cards if card['player_num'] == self.player.current_player)
                    available_moves = get_available_moves(current_card, self.dice.has_rolled, self.dice.current_dice, self.dice.dice_sum)
                    if available_moves:
                        dice1, dice2 = self.dice.current_dice
                        if len(available_moves) == 3:
                            sum_text = self.font.render(f"Закройте сумму: {self.dice.dice_sum}", True, (0, 0, 0))
                            self.screen.blit(sum_text, (self.WIDTH // 2 - 90, 40))
                            if dice1 != dice2:
                                separate_text = self.font.render(f"Или числа: {dice1}, {dice2}", True, (0, 0, 0))
                                self.screen.blit(separate_text, (self.WIDTH // 2 - 90, 70))
                            else:
                                separate_text = self.font.render(f"Или число: {dice1}", True, (0, 0, 0))
                                self.screen.blit(separate_text, (self.WIDTH // 2 - 90, 70))
                        elif len(available_moves) == 2:
                            if dice1 != dice2:
                                separate_text = self.font.render(f"Закройте числа: {dice1}, {dice2}", True, (0, 0, 0))
                                self.screen.blit(separate_text, (self.WIDTH // 2 - 90, 70))
                            else:
                                separate_text = self.font.render(f"Закройте число: {dice1}", True, (0, 0, 0))
                                self.screen.blit(separate_text, (self.WIDTH // 2 - 90, 70))
                        elif len(available_moves) == 1:
                            sum_text = self.font.render(f"Закройте число: {self.dice.dice_sum}", True, (0, 0, 0))
                            self.screen.blit(sum_text, (self.WIDTH // 2 - 90, 40))
                    else:
                        info_text = self.font.render("Нет доступных ходов - пропуск хода", True, (0, 0, 0))
                        self.screen.blit(info_text, (self.WIDTH // 2 - 150, 220))
                
                instruction = self.font.render(
                    "Кости вращаются... нажмите СТОП" if self.dice.rolling else 
                    "Нажмите БРОСИТЬ или ПРОБЕЛ для броска костей" if not self.dice.has_rolled else 
                    "Выберите число для закрытия", 
                    True, (255, 255, 255))
                self.screen.blit(instruction, (self.WIDTH // 2 - 250, self.HEIGHT - 60))
                
                players_text = self.font.render(f"Игроков: {self.player.NUM_PLAYERS}", True, (255, 255, 255))
                self.screen.blit(players_text, (20, self.HEIGHT - 30))
                
                self.player.render_turn_indicator(self.screen)
                
                mouse_pos = pygame.mouse.get_pos()
                self.roll_button.render(self.screen, mouse_pos)
                self.stop_button.render(self.screen, mouse_pos)
        else:
            self.render_winner_screen()
    
    def render_exit_confirmation(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        confirm_rect = pygame.Rect(self.WIDTH//2 - 200, self.HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(self.screen, (255, 235, 205), confirm_rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), confirm_rect, 2, border_radius=10)
        
        warning_text = self.font.render("Прогресс игры не сохранится!", True, (0, 0, 0))
        question_text = self.font.render("Вы точно хотите выйти?", True, (0, 0, 0))
        
        self.screen.blit(warning_text, (confirm_rect.centerx - warning_text.get_width()//2, confirm_rect.y + 40))
        self.screen.blit(question_text, (confirm_rect.centerx - question_text.get_width()//2, confirm_rect.y + 80))
        
        mouse_pos = pygame.mouse.get_pos()
        self.yes_button.render(self.screen, mouse_pos)
        self.no_button.render(self.screen, mouse_pos)
    
    def render_winner_screen(self):
        background = load_background(self)
        if background:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((50, 50, 50))
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        winner_text = self.large_font.render(f"Игрок {self.winner} победил!", True, (255, 255, 255))
        self.screen.blit(winner_text, (self.WIDTH // 2 - winner_text.get_width() // 2, self.HEIGHT // 2 - 100))
        
        if self.state == self.INPUT_NAME:
            name_text = self.font.render("Введите ваше имя:", True, (255, 255, 255))
            self.screen.blit(name_text, (self.WIDTH // 2 - name_text.get_width() // 2, self.HEIGHT // 2 - 30))
            
            pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, 2)
            pygame.draw.rect(self.screen, (255, 235, 205), self.input_rect)
            text_surface = self.font.render(self.input_text, True, (0, 0, 0))
            self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
            
            if self.input_active:
                pygame.draw.rect(self.screen, (0, 0, 0), self.input_rect, 2)
        else:
            restart_text = self.font.render("Нажмите R для новой игры", True, (255, 255, 255))
            self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2 + 20))
        
        mouse_pos = pygame.mouse.get_pos()
        self.menu_button.render(self.screen, mouse_pos)
    
    def render_rules(self):
        background = load_background(self)
        if background:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((50, 50, 50))

        title = self.title_font.render("Правила игры", True, (255, 255, 255))
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 50))

        rules = [
            "1. Игроки по очереди бросают два кубика",
            "2. Можно закрыть:",
            "   - Число, равное сумме кубиков",
            "   - Оба числа на кубиках (если доступны)",
            "3. Если нет доступных ходов - ход пропускается",
            "4. Побеждает тот, кто первым закроет все числа!"
        ]
        
        for i, rule in enumerate(rules):
            rule_text = self.font.render(rule, True, (255, 255, 255))
            self.screen.blit(rule_text, (self.WIDTH // 2 - 200, 150 + i * 40))

        mouse_pos = pygame.mouse.get_pos()
        self.menu_button.render(self.screen, mouse_pos)

    def render_records(self):
        background = load_background(self)
        if background:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((50, 50, 50))

        title = self.title_font.render("Рекорды", True, (255, 255, 255))
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 50))

        from data.scripts.utils import load_records
        records = load_records()
        
        if not records:
            no_records = self.font.render("Пока нет рекордов!", True, (255, 255, 255))
            self.screen.blit(no_records, (self.WIDTH // 2 - no_records.get_width() // 2, 150))
        else:
            for i, record in enumerate(records[-5:]):
                record_text = self.font.render(
                    f"{record['name']} - Игрок {record['player_num']} - {record['date']}", 
                    True, (255, 255, 255)
                )
                self.screen.blit(record_text, (self.WIDTH // 2 - 250, 150 + i * 40))

        mouse_pos = pygame.mouse.get_pos()
        self.menu_button.render(self.screen, mouse_pos)
    
    def reset_game(self):
        self.game_over = False
        self.winner = 0
        self.player.current_player = 1
        self.player.player_cards = create_player_cards(self.player.NUM_PLAYERS, self.WIDTH, self.HEIGHT)
        self.dice.has_rolled = False
        self.dice.rolling = False
        self.show_exit_confirmation = False