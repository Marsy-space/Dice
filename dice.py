import pygame
import random
import time

class Dice:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.dice_size = 100
        self.dice_images = []
        self.load_dice_images()
        
        self.dice_positions = [(self.WIDTH // 2 - 120, 100), (self.WIDTH // 2 + 20, 100)]
        self.current_dice = [1, 1]
        self.dice_sum = sum(self.current_dice)
        self.available_numbers = set(self.current_dice + [self.dice_sum])
        
        self.rolling = False
        self.last_roll_time = 0
        self.has_rolled = False
        
    def load_dice_images(self):
        for i in range(6):
            try:
                img = pygame.image.load(f"ice_{i+1}.png").convert_alpha()
                img = pygame.transform.scale(img, (self.dice_size, self.dice_size))
                self.dice_images.append(img)
            except FileNotFoundError:
                surf = pygame.Surface((self.dice_size, self.dice_size), pygame.SRCALPHA)
                pygame.draw.rect(surf, (222, 184, 135), (0, 0, self.dice_size, self.dice_size))
                pygame.draw.rect(surf, (0, 0, 0), (0, 0, self.dice_size, self.dice_size), 2)
                dots = [
                    [(1,1)], [(0,0), (2,2)], [(0,0), (1,1), (2,2)],
                    [(0,0), (0,2), (2,0), (2,2)], [(0,0), (0,2), (1,1), (2,0), (2,2)],
                    [(0,0), (0,1), (0,2), (2,0), (2,1), (2,2)]
                ][i]
                for x, y in dots:
                    pygame.draw.circle(surf, (0, 0, 0), 
                                    (int((x+0.5)*self.dice_size//3), int((y+0.5)*self.dice_size//3)), 
                                    self.dice_size//10)
                self.dice_images.append(surf)
    
    def roll(self):
        self.rolling = True
        self.last_roll_time = time.time()
        
    def stop(self):
        self.rolling = False
        self.dice_sum = sum(self.current_dice)
        self.available_numbers = set(self.current_dice + [self.dice_sum])
        self.has_rolled = True
        return self.dice_sum, self.available_numbers
        
    def update(self):
        current_time = time.time()
        if self.rolling and current_time - self.last_roll_time > 0.1:
            self.current_dice = [random.randint(1, 6), random.randint(1, 6)]
            self.last_roll_time = current_time
            
    def render(self, screen):
        for i in range(2):
            screen.blit(self.dice_images[self.current_dice[i]-1], self.dice_positions[i])