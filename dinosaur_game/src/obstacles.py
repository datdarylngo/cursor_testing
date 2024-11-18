import pygame
import random

class Cactus:
    def __init__(self, screen_width):
        self.width = 20
        self.height = random.randint(30, 50)  # Random height
        self.x = screen_width
        self.y = 360 - self.height  # Ground level - height
        self.speed = 5
        
        # Create a simple rectangle for now
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def is_off_screen(self):
        return self.x < -self.width 