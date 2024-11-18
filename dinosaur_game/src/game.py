import pygame
import sys
from player import Dinosaur
from obstacles import Cactus
import random

class DinosaurGame:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 400
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Dinosaur Game")
        self.clock = pygame.time.Clock()
        
        # Game states
        self.running = True
        self.game_active = False
        self.in_menu = True
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 74)
        
        self.reset_game()

    def reset_game(self):
        # Game objects
        self.player = Dinosaur(50, 300)
        self.obstacles = []
        
        # Game state
        self.score = 0
        self.game_speed = 5
        self.spawn_timer = 0
        self.min_spawn_time = 60

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_active:
                        self.game_active = False
                        self.in_menu = True
                    else:
                        self.running = False
                
                elif event.key == pygame.K_SPACE:
                    if self.game_active:
                        self.player.jump()
                    elif self.in_menu:
                        self.game_active = True
                        self.in_menu = False
                        self.reset_game()
                
                elif event.key == pygame.K_r and not self.game_active and not self.in_menu:
                    self.game_active = True
                    self.reset_game()

    def spawn_obstacle(self):
        if self.spawn_timer <= 0:
            if random.random() < 0.3:
                self.obstacles.append(Cactus(self.screen_width))
                self.spawn_timer = self.min_spawn_time - (self.score // 100)
                self.spawn_timer = max(30, self.spawn_timer)
        else:
            self.spawn_timer -= 1

    def update(self):
        if not self.game_active:
            return
            
        self.player.update()
        
        for obstacle in self.obstacles[:]:
            obstacle.update()
            
            if self.player.rect.colliderect(obstacle.rect):
                self.game_active = False
            
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
                self.score += 10
        
        self.spawn_obstacle()
        
        self.game_speed = 5 + (self.score // 100)
        self.min_spawn_time = max(30, 60 - (self.score // 100))
        
        for obstacle in self.obstacles:
            obstacle.speed = self.game_speed

    def draw_menu(self):
        self.screen.fill((255, 255, 255))
        
        # Calculate vertical spacing
        padding = 40
        section_spacing = 20
        
        # Draw title at the top with more space
        title_text = self.title_font.render("Dinosaur Game", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, padding))
        
        # Controls section
        controls_title = self.font.render("Controls:", True, (0, 0, 0))
        controls_rect = controls_title.get_rect(
            center=(self.screen_width//2, title_rect.bottom + section_spacing)
        )
        
        controls = [
            "SPACE - Jump over obstacles",
            "ESC - Return to menu/Quit game",
            "R - Restart after game over"
        ]
        
        # Render controls
        control_y = controls_rect.bottom + 10
        for line in controls:
            text = self.font.render(line, True, (0, 0, 0))
            rect = text.get_rect(center=(self.screen_width//2, control_y))
            self.screen.blit(text, rect)
            control_y += 30
        
        # How to Play section
        how_to_title = self.font.render("How to Play:", True, (0, 0, 0))
        how_to_rect = how_to_title.get_rect(
            center=(self.screen_width//2, control_y + section_spacing)
        )
        
        how_to = [
            "1. Press SPACE to start",
            "2. Jump over cacti to score points",
            "3. Game ends if you hit an obstacle"
        ]
        
        # Render how to play
        how_to_y = how_to_rect.bottom + 10
        for line in how_to:
            text = self.font.render(line, True, (0, 0, 0))
            rect = text.get_rect(center=(self.screen_width//2, how_to_y))
            self.screen.blit(text, rect)
            how_to_y += 30
        
        # Draw "Press SPACE to Start" at the bottom with more spacing
        start_text = self.font.render("Press SPACE to Start", True, (0, 0, 0))
        start_rect = start_text.get_rect(center=(self.screen_width//2, self.screen_height - padding))
        
        # Draw everything
        self.screen.blit(title_text, title_rect)
        self.screen.blit(controls_title, controls_rect)
        self.screen.blit(how_to_title, how_to_rect)
        self.screen.blit(start_text, start_rect)

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.title_font.render("Game Over!", True, (0, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//3))
        
        # Score text
        score_text = self.font.render(f'Final Score: {self.score}', True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        
        # Restart instructions
        restart_text = self.font.render("Press R to Restart", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height*2//3))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw_game(self):
        self.screen.fill((255, 255, 255))
        
        # Draw ground line
        pygame.draw.line(self.screen, (0, 0, 0), (0, 360), (self.screen_width, 360))
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, (0, 0, 0))
        self.screen.blit(score_text, (20, 20))

    def draw(self):
        if self.in_menu:
            self.draw_menu()
        elif self.game_active:
            self.draw_game()
        else:
            self.draw_game()
            self.draw_game_over()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = DinosaurGame()
    game.run() 