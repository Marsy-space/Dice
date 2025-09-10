import pygame
import sys
from data.scripts.game_state import GameState

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Игральные кости с карточками игроков")
        
        self.game_state = GameState(self.WIDTH, self.HEIGHT, self.screen)
        self.running = True
        
    def run(self):
        while self.running:
            self.game_state.handle_events()
            self.game_state.update()
            self.game_state.render()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()