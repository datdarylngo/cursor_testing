import pygame

class Dinosaur:
    def __init__(self, x, y):
        self.ground_level = 360  # Ground level
        
        self.x = x
        self.y = self.ground_level - 60 - 35  # Adjusted: ground level - dino height - offset
        self.velocity = 0
        self.gravity = 0.8
        self.min_jump_power = -12
        self.max_jump_power = -20
        self.charge_rate = 0.8
        self.jump_charge = 0
        self.is_jumping = False
        self.is_charging = False
        
        # Update path to be relative to the project root
        original_image = pygame.image.load('../../dinosaur_game/assets/dinosaur.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (40, 60))
        self.rect = self.image.get_rect(topleft=(x, self.y))
        
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
        self.fart_boost_power = -8  # Weaker than poop boost
        self.fart_forward = 50  # Less forward momentum than poop
        self.fart_duration = 10
        self.fart_timer = 0
        self.can_fart = True  # Track if we can fart in this jump
        
        # Load fart image
        fart_image = pygame.image.load('../../dinosaur_game/assets/fart.png').convert_alpha()
        self.fart_image = pygame.transform.scale(fart_image, (30, 30))
        
        # Poop properties
        self.poop_count = 0
        self.poop_boost_power = -12
        self.poop_forward = 80
        self.poop_duration = 15
        self.poop_timer = 0
        
        # Load poop image
        poop_image = pygame.image.load('../../dinosaur_game/assets/poop.png').convert_alpha()
        self.poop_image = pygame.transform.scale(poop_image, (35, 35))
        
        # Add poop animation properties
        self.active_poops = []  # List to track falling poops
        self.ground_poops = []  # List to track poops that have landed

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
            self.can_fart = True  # Reset fart ability at the start of each jump

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

        # Update poop timer
        if self.poop_timer > 0:
            self.poop_timer -= 1

        # Ground collision
        if self.y >= self.ground_level - 60:  # Adjusted: ground level - dino height
            self.y = self.ground_level - 60  # Adjusted: ground level - dino height
            self.velocity = 0
            self.is_jumping = False
            self.is_gliding = False
            self.can_fart = True

        # Update rectangle position
        self.rect.y = self.y

        # Update falling poops
        for poop in self.active_poops[:]:
            poop['y'] += poop['velocity']
            poop['velocity'] += 0.5  # Add gravity
            
            # When poop hits ground, move it to ground_poops list
            if poop['y'] >= self.ground_level - 35:  # Adjusted to match ground level minus poop height
                poop['y'] = self.ground_level - 35  # Place poop exactly at ground level
                self.ground_poops.append(poop)
                self.active_poops.remove(poop)

        # Update ground poops - remove when off screen
        for poop in self.ground_poops[:]:
            poop['x'] -= 5  # Move with game speed
            if poop['x'] < -self.poop_image.get_width():  # Off screen
                self.ground_poops.remove(poop)

    def start_glide(self):
        if self.velocity > 0:  # Allow gliding whenever falling
            self.is_gliding = True
            # Reset velocity to ensure consistent gliding speed
            if self.velocity > self.min_glide_speed:
                self.velocity = self.min_glide_speed + 1

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

    def add_poop(self):
        self.poop_count += 1

    def drop_poop(self):
        if self.poop_count > 0:  # Can drop poop anytime
            self.velocity = self.poop_boost_power
            self.x += self.poop_forward
            self.rect.x = self.x
            self.poop_count -= 1
            self.poop_timer = self.poop_duration

    def apply_boost(self):
        if self.is_gliding and self.can_fart:  # Try fart first if available
            self.velocity = self.fart_boost_power
            self.x += self.fart_forward
            self.rect.x = self.x
            self.fart_timer = self.fart_duration
            self.can_fart = False  # Use up the fart
        elif self.poop_count > 0:  # Use poop if we can't fart
            # Create a new falling poop
            self.active_poops.append({
                'x': self.rect.x,
                'y': self.rect.y,
                'velocity': 2,  # Initial vertical velocity
            })
            self.velocity = self.poop_boost_power
            self.x += self.poop_forward
            self.rect.x = self.x
            self.poop_count -= 1
            self.poop_timer = self.poop_duration

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
        
        # Draw all falling poops
        for poop in self.active_poops:
            poop_rect = self.poop_image.get_rect(
                center=(poop['x'], poop['y'])
            )
            screen.blit(self.poop_image, poop_rect)
        
        # Draw all ground poops
        for poop in self.ground_poops:
            poop_rect = self.poop_image.get_rect(
                center=(poop['x'], poop['y'])
            )
            screen.blit(self.poop_image, poop_rect)
        
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
        
        # Draw poop boost counter if any are available
        if self.poop_count > 0:
            boost_text = pygame.font.Font(None, 24).render(f'Boosts: {self.poop_count}', True, (255, 140, 0))
            screen.blit(boost_text, (self.rect.right + 10, self.rect.top))