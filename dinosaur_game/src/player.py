import pygame

class Dinosaur:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.gravity = 0.8
        self.min_jump_power = -12  # Minimum jump power
        self.max_jump_power = -20  # Maximum jump power
        self.charge_rate = 0.8     # Increased from 0.5 to 0.8 for faster charging
        self.jump_charge = 0       # Current jump charge
        self.is_jumping = False
        self.is_charging = False   # New state for charging jump
        
        # Update path to be relative to the project root
        original_image = pygame.image.load('../../dinosaur_game/assets/dinosaur.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (40, 60))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Visual feedback colors
        self.charge_colors = {
            'low': (255, 200, 0),    # Yellow
            'medium': (255, 140, 0),  # Orange
            'high': (255, 0, 0)       # Red
        }
        
        # Adjust gliding properties for better feel
        self.is_gliding = False
        self.glide_gravity = 0.05  # Reduced from 0.1 to 0.05 for much slower falling
        self.normal_gravity = 0.8  # Store normal gravity value
        self.min_glide_speed = 1   # Reduced minimum falling speed while gliding
        
        # Load glider image
        glider_image = pygame.image.load('../../dinosaur_game/assets/glider.png').convert_alpha()
        self.glider_image = pygame.transform.scale(glider_image, (60, 40))  # Adjust size as needed
        
        # Fart boost properties
        self.can_fart = True  # One fart per glide
        self.boost_power = -8  # Renamed from fart_boost to avoid conflict
        self.fart_forward = 50  # Forward movement
        self.fart_duration = 10  # Frames the fart image shows
        self.fart_timer = 0
        
        # Load fart image
        fart_image = pygame.image.load('../../dinosaur_game/assets/fart.png').convert_alpha()
        self.fart_image = pygame.transform.scale(fart_image, (30, 30))

    def start_charge(self):
        if not self.is_jumping:
            self.is_charging = True
            self.jump_charge = self.min_jump_power

    def release_jump(self):
        if self.is_charging and not self.is_jumping:
            self.velocity = self.jump_charge
            self.is_jumping = True
            self.is_charging = False
            self.jump_charge = 0

    def update(self):
        # Charge jump while space is held
        if self.is_charging and self.jump_charge > self.max_jump_power:
            self.jump_charge -= self.charge_rate

        # Apply appropriate gravity with smoother transition
        if self.is_gliding and self.velocity > 0:
            # Add a terminal velocity while gliding to prevent too slow falling
            if self.velocity < self.min_glide_speed:
                self.velocity = self.min_glide_speed
            else:
                self.velocity += self.glide_gravity
        else:
            self.velocity += self.normal_gravity

        self.y += self.velocity

        # Update fart timer
        if self.fart_timer > 0:
            self.fart_timer -= 1

        # Reset fart ability when landing
        if self.y >= 300:  # Ground level
            self.y = 300
            self.velocity = 0
            self.is_jumping = False
            self.is_gliding = False
            self.can_fart = True  # Reset fart ability when landing

        # Update rectangle position
        self.rect.y = self.y

    def start_glide(self):
        if self.velocity > 0:  # Allow gliding whenever falling
            self.is_gliding = True
            # Reset velocity to ensure consistent gliding speed
            if self.velocity > self.min_glide_speed:
                self.velocity = self.min_glide_speed + 1  # Set to slightly above minimum glide speed

    def stop_glide(self):
        self.is_gliding = False

    def get_charge_color(self):
        charge_percent = (self.min_jump_power - self.jump_charge) / (self.min_jump_power - self.max_jump_power)
        if charge_percent < 0.33:
            return self.charge_colors['low']
        elif charge_percent < 0.66:
            return self.charge_colors['medium']
        else:
            return self.charge_colors['high']

    def apply_fart_boost(self):  # Renamed from fart_boost to apply_fart_boost
        if self.is_gliding and self.can_fart:
            self.velocity = self.boost_power  # Use the renamed property
            self.x += self.fart_forward
            self.rect.x = self.x
            self.can_fart = False
            self.fart_timer = self.fart_duration

    def draw(self, screen):
        # Draw the dinosaur
        screen.blit(self.image, self.rect)
        
        # Draw glider when active
        if self.is_gliding:
            glider_rect = self.glider_image.get_rect(
                midbottom=(self.rect.centerx, self.rect.top + 10)
            )
            screen.blit(self.glider_image, glider_rect)
            
            # Draw fart effect if timer is active
            if self.fart_timer > 0:
                fart_rect = self.fart_image.get_rect(
                    midright=(self.rect.left - 5, self.rect.centery)
                )
                screen.blit(self.fart_image, fart_rect)
        
        # Draw jump charge meter and visual feedback
        if self.is_charging:
            charge_percent = (self.min_jump_power - self.jump_charge) / (self.min_jump_power - self.max_jump_power)
            
            # Draw charge meter background
            pygame.draw.rect(screen, (200, 200, 200), 
                           (self.rect.x, self.rect.y - 15, 
                            40, 10))
            
            # Draw charge meter fill
            pygame.draw.rect(screen, self.get_charge_color(), 
                           (self.rect.x, self.rect.y - 15, 
                            40 * charge_percent, 10))
            
            # Draw charge meter border
            pygame.draw.rect(screen, (0, 0, 0), 
                           (self.rect.x, self.rect.y - 15, 
                            40, 10), 1)
            
            # Draw arrow indicating jump height
            arrow_height = 50 * charge_percent
            pygame.draw.line(screen, self.get_charge_color(),
                           (self.rect.right + 5, self.rect.y),
                           (self.rect.right + 5, self.rect.y - arrow_height),
                           2)
            # Draw arrow head
            pygame.draw.polygon(screen, self.get_charge_color(), [
                (self.rect.right + 5, self.rect.y - arrow_height),
                (self.rect.right, self.rect.y - arrow_height + 5),
                (self.rect.right + 10, self.rect.y - arrow_height + 5)
            ])