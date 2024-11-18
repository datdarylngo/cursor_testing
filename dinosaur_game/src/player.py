import pygame

class Dinosaur:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.is_jumping = False
        
        # Load and scale image to match hitbox
        original_image = pygame.image.load('dinosaur_game/assets/dinosaur.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (40, 60))  # Match original rectangle size
        self.rect = self.image.get_rect(topleft=(x, y))

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

    def draw(self, screen):
        screen.blit(self.image, self.rect)