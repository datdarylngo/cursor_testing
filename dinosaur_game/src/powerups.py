import pygame
import math

class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        
        # Load and scale star image
        original_image = pygame.image.load('../../dinosaur_game/assets/star.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (30, 30))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Animation properties
        self.float_offset = 0
        self.float_speed = 0.1
        self.float_range = 20

    def update(self):
        self.x -= self.speed
        # Add floating motion
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * self.float_range
        self.rect.x = self.x
        self.rect.y = self.y + self.float_offset

    def is_off_screen(self):
        return self.x < -self.rect.width

    def draw(self, screen):
        screen.blit(self.image, self.rect) 