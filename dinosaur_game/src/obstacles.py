import pygame
import random

class Cactus:
    def __init__(self, screen_width):
        self.width = 20
        self.height = random.randint(30, 50)  # Random height
        self.x = screen_width
        self.y = 360 - self.height  # Ground level - height
        self.speed = 5
        
        # Load and scale image to match hitbox
        original_image = pygame.image.load('dinosaur_game/assets/cactus.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (self.width, self.height))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def is_off_screen(self):
        return self.x < -self.width 

    def draw(self, screen):
        screen.blit(self.image, self.rect)