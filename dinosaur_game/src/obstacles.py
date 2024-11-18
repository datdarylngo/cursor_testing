import pygame
import random

class Cactus:
    def __init__(self, screen_width):
        # Create more extreme size variations
        self.type = random.choice(['small', 'medium', 'large', 'extra_large'])
        
        # Size configurations based on type
        self.size_configs = {
            'small': {
                'width_range': (20, 30),
                'height_range': (40, 60)
            },
            'medium': {
                'width_range': (30, 45),
                'height_range': (60, 80)
            },
            'large': {
                'width_range': (40, 55),
                'height_range': (70, 90)
            },
            'extra_large': {
                'width_range': (50, 65),
                'height_range': (85, 110)
            }
        }
        
        # Set random dimensions based on type
        config = self.size_configs[self.type]
        self.width = random.randint(*config['width_range'])
        self.height = random.randint(*config['height_range'])
        
        # Sometimes create wider but shorter cacti for variety
        if random.random() < 0.3:
            self.width = int(self.width * 1.5)
            self.height = int(self.height * 0.8)
        
        self.x = screen_width
        self.y = 360 - self.height  # Ground level - height
        self.speed = 5
        
        # Update path to be relative to the project root
        original_image = pygame.image.load('../../dinosaur_game/assets/cactus.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (self.width, self.height))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        self.alpha = 255
        self.fading = False

    def start_fade(self):
        self.fading = True

    def update(self):
        self.x -= self.speed
        if self.fading:
            self.alpha -= 15  # Fade speed
            if self.alpha < 0:
                self.alpha = 0
        self.rect.x = self.x

    def is_off_screen(self):
        return self.x < -self.width 

    def draw(self, screen):
        if self.fading:
            # Create a copy of the image with new alpha
            fade_image = self.image.copy()
            fade_image.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(fade_image, self.rect)
        else:
            screen.blit(self.image, self.rect)
        
        # Optional: Draw hitbox for debugging
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)