import pygame
import sys
from player import Dinosaur
from obstacles import Cactus
import random
import math
from powerups import Star

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
        
        # High score tracking
        self.high_score = 0
        
        # Power-up properties
        self.powerups = []
        self.powerup_timer = 0
        self.powerup_duration = 300  # 5 seconds at 60 FPS
        self.is_powered_up = False
        self.powerup_spawn_chance = 0.002  # Reduced from 0.01 to 0.002 (0.2% chance per frame)

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
        self.powerups = []
        self.powerup_timer = 0
        self.is_powered_up = False

    def handle_events(self):
        # Get current keyboard state
        keys = pygame.key.get_pressed()
        
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
                        if not self.player.is_jumping:
                            self.player.start_charge()
                    elif self.in_menu:
                        self.game_active = True
                        self.in_menu = False
                        self.reset_game()
                
                elif event.key == pygame.K_f and self.game_active:
                    self.player.apply_fart_boost()
                
                elif event.key == pygame.K_r and not self.game_active and not self.in_menu:
                    self.game_active = True
                    self.reset_game()
        
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.game_active:
                    if self.player.is_charging:
                        self.player.release_jump()
        
        # Check for gliding - only glide while G is held
        if self.game_active:
            if keys[pygame.K_g]:
                self.player.start_glide()
            else:
                self.player.stop_glide()

    def spawn_obstacle(self):
        if self.spawn_timer <= 0:
            # Increase spawn chance as score increases
            spawn_chance = 0.3 + (self.score / 1000)  # Gradually increase spawn rate
            spawn_chance = min(0.5, spawn_chance)  # Cap at 50% chance
            
            if random.random() < spawn_chance:
                # Sometimes spawn multiple cacti in a group
                if random.random() < 0.2:  # 20% chance for group spawn
                    num_cacti = random.randint(2, 3)
                    spacing = random.randint(60, 100)  # Random spacing between grouped cacti
                    
                    for i in range(num_cacti):
                        cactus = Cactus(self.screen_width + (i * spacing))
                        self.obstacles.append(cactus)
                else:
                    self.obstacles.append(Cactus(self.screen_width))
                
                # Decrease minimum spawn time as score increases
                self.spawn_timer = self.min_spawn_time - (self.score // 50)  # Faster spawn rate
                self.spawn_timer = max(20, self.spawn_timer)  # Don't go below 20 frames
        else:
            self.spawn_timer -= 1

    def spawn_powerup(self):
        if not self.powerups and not self.is_powered_up:  # Only spawn if no powerups exist
            if random.random() < self.powerup_spawn_chance:
                y_pos = random.randint(100, 250)  # Random height between these values
                self.powerups.append(Star(self.screen_width, y_pos))

    def update(self):
        if not self.game_active:
            return
            
        self.player.update()
        
        # Update power-up timer
        if self.is_powered_up:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.is_powered_up = False
        
        # Update and check powerup collisions
        for powerup in self.powerups[:]:
            powerup.update()
            if self.player.rect.colliderect(powerup.rect):
                self.is_powered_up = True
                self.powerup_timer = self.powerup_duration
                self.powerups.remove(powerup)
            elif powerup.is_off_screen():
                self.powerups.remove(powerup)
        
        # Update and check obstacle collisions
        for obstacle in self.obstacles[:]:
            obstacle.update()
            
            if self.player.rect.colliderect(obstacle.rect):
                if not self.is_powered_up:
                    self.game_active = False
                    self.high_score = max(self.score, self.high_score)
                else:
                    # Remove obstacle with fade effect
                    obstacle.start_fade()
                    if obstacle.alpha <= 0:
                        self.obstacles.remove(obstacle)
                        self.score += 15  # Bonus points for destroying obstacle
            
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
                self.score += 10
        
        self.spawn_obstacle()
        self.spawn_powerup()
        
        self.game_speed = 5 + (self.score // 100)
        self.min_spawn_time = max(30, 60 - (self.score // 100))
        
        for obstacle in self.obstacles:
            obstacle.speed = self.game_speed

    def draw_menu(self):
        self.screen.fill((255, 255, 255))
        
        # Calculate spacing
        padding = 40
        section_spacing = 20
        column_width = self.screen_width // 2
        
        # Create smaller font for instructions
        instruction_font = pygame.font.Font(None, 24)  # Reduced from 28 to 24
        
        # Draw title at the top with more space
        title_text = self.title_font.render("Dinosaur Game", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, padding))
        
        # Left column - Controls section
        controls_title = self.font.render("Controls:", True, (0, 0, 0))
        controls_rect = controls_title.get_rect(
            midtop=(column_width//2, title_rect.bottom + section_spacing * 2)
        )
        
        controls = [
            "SPACE (tap) - Jump over obstacles",
            "G (hold) - Glide while falling",
            "F - Fart boost while gliding (once per glide)",
            "ESC - Return to menu/Quit game",
            "R - Restart after game over"
        ]
        
        # Right column - How to Play section
        how_to_title = self.font.render("How to Play:", True, (0, 0, 0))
        how_to_rect = how_to_title.get_rect(
            midtop=(column_width + column_width//2, title_rect.bottom + section_spacing * 2)
        )
        
        how_to = [
            "1. Press SPACE to start",
            "2. Tap SPACE to jump over cacti",
            "3. Hold G anytime to glide down",
            "4. Press F once per glide for fart boost!",
            "5. Collect stars for invincibility!",
            "6. Game ends if you hit an obstacle"
        ]
        
        # Render controls (left column)
        control_y = controls_rect.bottom + 10
        for line in controls:
            text = instruction_font.render(line, True, (0, 0, 0))
            rect = text.get_rect(midtop=(column_width//2, control_y))
            self.screen.blit(text, rect)
            control_y += 22  # Reduced from 25 to 22
        
        # Render how to play (right column)
        how_to_y = how_to_rect.bottom + 10
        for line in how_to:
            text = instruction_font.render(line, True, (0, 0, 0))
            rect = text.get_rect(midtop=(column_width + column_width//2, how_to_y))
            self.screen.blit(text, rect)
            how_to_y += 22  # Reduced from 25 to 22
        
        # Draw "Press SPACE to Start" at the bottom with more spacing
        start_text = self.font.render("Press SPACE to Start", True, (0, 0, 0))
        start_rect = start_text.get_rect(center=(self.screen_width//2, self.screen_height - padding))
        
        # Optional: Add separator line between columns
        pygame.draw.line(self.screen, (200, 200, 200),  # Light gray color
                        (self.screen_width//2, title_rect.bottom + section_spacing),
                        (self.screen_width//2, self.screen_height - padding * 2),
                        2)  # Line thickness
        
        # Draw everything
        self.screen.blit(title_text, title_rect)
        self.screen.blit(controls_title, controls_rect)
        self.screen.blit(how_to_title, how_to_rect)
        self.screen.blit(start_text, start_rect)

    def draw_game(self):
        self.screen.fill((255, 255, 255))
        
        # Draw ground line
        pygame.draw.line(self.screen, (0, 0, 0), (0, 360), (self.screen_width, 360))
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw player with power-up effect
        if self.is_powered_up:
            # Create pulsing glow effect
            glow_size = math.sin(pygame.time.get_ticks() * 0.01) * 5 + 5
            glow_surf = pygame.Surface((self.player.rect.width + glow_size * 2, 
                                      self.player.rect.height + glow_size * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 255, 0, 100), glow_surf.get_rect())
            self.screen.blit(glow_surf, (self.player.rect.x - glow_size, self.player.rect.y - glow_size))
            
            # Draw power-up timer
            timer_width = 100
            timer_height = 10
            timer_x = self.screen_width // 2 - timer_width // 2
            timer_y = 20
            
            # Draw timer background
            pygame.draw.rect(self.screen, (200, 200, 200), 
                           (timer_x, timer_y, timer_width, timer_height))
            
            # Draw timer fill
            timer_fill = (self.powerup_timer / self.powerup_duration) * timer_width
            if timer_fill > 0:
                pygame.draw.rect(self.screen, (255, 215, 0),  # Gold color
                               (timer_x, timer_y, timer_fill, timer_height))
            
            # Draw timer border
            pygame.draw.rect(self.screen, (0, 0, 0), 
                           (timer_x, timer_y, timer_width, timer_height), 1)
            
            # Draw "STAR POWER!" text
            power_text = self.font.render("STAR POWER!", True, (255, 215, 0))  # Gold color
            text_rect = power_text.get_rect(midtop=(self.screen_width // 2, timer_y + timer_height + 5))
            self.screen.blit(power_text, text_rect)
        
        self.player.draw(self.screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw current score
        score_text = self.font.render(f'Score: {self.score}', True, (0, 0, 0))
        self.screen.blit(score_text, (20, 20))
        
        # Draw high score
        high_score_text = self.font.render(f'High Score: {self.high_score}', True, (0, 0, 0))
        high_score_rect = high_score_text.get_rect(topright=(self.screen_width - 20, 20))
        self.screen.blit(high_score_text, high_score_rect)

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
        
        # High Score text
        if self.score >= self.high_score:
            high_score_text = self.font.render("New High Score!", True, (255, 0, 0))  # Red color for new high score
        else:
            high_score_text = self.font.render(f'High Score: {self.high_score}', True, (0, 0, 0))
        high_score_rect = high_score_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 40))
        
        # Restart instructions
        restart_text = self.font.render("Press R to Restart", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height*2//3))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(high_score_text, high_score_rect)
        self.screen.blit(restart_text, restart_rect)

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