import pygame

class Dinosaur:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.is_jumping = False
        
        # Create a simple rectangle for now
        self.rect = pygame.Rect(x, y, 40, 60)

    def jump(self):
        if not self.is_jumping:
            self.velocity = self.jump_power
            self.is_jumping = True

    def update(self):
        # Apply gravity
        self.velocity += self.gravity
        self.y += self.velocity

        # Ground collision
        if self.y > 300:  # Ground level
            self.y = 300
            self.velocity = 0
            self.is_jumping = False

        # Update rectangle position
        self.rect.y = self.y 