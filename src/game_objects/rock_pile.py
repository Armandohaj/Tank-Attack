"""
RockPile module for the Tank Game.
This module defines the RockPile class that represents destructible rock pile obstacles.
"""
from src.game_objects.destructible_element import DestructibleElement


class RockPile(DestructibleElement):
    """
    Represents a destructible rock pile obstacle in the game map.
    Rock piles can be damaged and destroyed by projectiles, and show visual damage states.
    """
    
    def __init__(self, x, y, health=50):
        """
        Initialize a rock pile obstacle.
        
        Args:
            x (float): X-coordinate position
            y (float): Y-coordinate position
            health (int): Initial health of the rock pile (default: 50)
        """
        super().__init__(x, y, health)
        self.tag = "rock_pile"
        self.original_width = 32
        self.original_height = 32
        self.original_x = x
        self.original_y = y
        
        # Create the initial sprite
        self.take_damage(1.0)  # Full health
        
    def blocks_movement(self):
        """
        Check if this rock pile blocks movement.
        
        Returns:
            bool: True if active (rock pile blocks movement), False if destroyed
        """
        return self.active
        
    def blocks_projectiles(self):
        """
        Check if this rock pile blocks projectiles.
        
        Returns:
            bool: True if active (rock pile blocks projectiles), False if destroyed
        """
        return self.active
        
    def take_damage(self, amount):
        """
        Reduce the health of the rock pile by the given amount.
        Shows visual damage indicators when partially damaged.
        
        Args:
            amount (int): Amount of damage to take
            
        Returns:
            bool: True if the rock pile was destroyed, False otherwise
        """
        import random
        import pygame
        
        old_health = self.health
        destroyed = super().take_damage(amount)
        
        # Update the sprite based on damage level
        if not destroyed:
            # Calculate health percentage
            health_percentage = self.health / self.max_health
            
            # Create a new sprite surface based on damage level
            self._create_damaged_sprite(health_percentage)
            
            print(f"RockPile at ({self.x}, {self.y}) updated sprite for damage level: {1 - health_percentage:.2f}")
            
            # Create visual debris effect when taking damage
            print(f"Rock pile debris scattered from impact! Amount: {amount}")
            
            # Add a dramatic "shake" effect for significant damage
            if amount > 15:
                print(f"Rock pile shaking violently from impact!")
        
        # Log damage for debugging/testing
        if destroyed:
            print(f"RockPile at ({self.x}, {self.y}) DESTROYED! Health: {old_health} -> {self.health}")
        elif self.health != old_health:
            damage_state = "HEAVILY DAMAGED" if self.health < self.max_health * 0.3 else "damaged"
            print(f"RockPile at ({self.x}, {self.y}) {damage_state}! Health: {old_health} -> {self.health}")
            
        return destroyed
        
    def _create_damaged_sprite(self, health_percentage):
        """
        Create a sprite that shows damage based on health percentage.
        
        Args:
            health_percentage (float): Health percentage (0.0 to 1.0)
        """
        import pygame
        import random
        
        # Create a new surface for the sprite
        sprite_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Calculate damage level (0 to 1, where 1 is fully damaged)
        damage_level = 1.0 - health_percentage
        
        # Use more dramatic colors to make damage more visible
        if damage_level < 0.3:
            # Almost intact - brown/gray color
            base_color = (150, 130, 110)  # Brown/gray
        elif damage_level < 0.7:
            # Moderately damaged - darker brown with reddish tint
            base_color = (130, 90, 70)  # Darker brown with reddish tint
        else:
            # Heavily damaged - dark reddish brown
            base_color = (100, 60, 40)  # Dark reddish brown
        
        # Draw the rock based on damage level
        if damage_level < 0.3:
            # Almost intact - draw a solid rectangle with some texture
            pygame.draw.rect(sprite_surface, base_color, (0, 0, 32, 32))
            
            # Add some texture/detail
            for i in range(5):
                detail_color = (base_color[0] - 30, base_color[1] - 30, base_color[2] - 30)
                detail_x = int(random.uniform(0.2, 0.8) * 32)
                detail_y = int(random.uniform(0.2, 0.8) * 32)
                detail_size = int(32 * 0.15)
                pygame.draw.circle(sprite_surface, detail_color, (detail_x, detail_y), detail_size)
                
        elif damage_level < 0.7:
            # Moderately damaged - draw multiple fragments with visible cracks
            # Clear background for transparency between cracks
            sprite_surface.fill((0, 0, 0, 0))
            
            # Draw 3-4 fragments
            num_fragments = 4
            for i in range(num_fragments):
                frag_width = int(32 / 2)
                frag_height = int(32 / 2)
                frag_x = int((i % 2) * 16 + random.uniform(-2, 2))
                frag_y = int((i // 2) * 16 + random.uniform(-2, 2))
                
                # Vary the fragment color slightly
                frag_color = (
                    min(255, base_color[0] + random.randint(-20, 20)),
                    min(255, base_color[1] + random.randint(-20, 20)),
                    min(255, base_color[2] + random.randint(-20, 20))
                )
                
                # Draw the fragment with irregular shape
                points = [
                    (frag_x + random.uniform(-2, 2), frag_y + random.uniform(-2, 2)),
                    (frag_x + frag_width + random.uniform(-2, 2), frag_y + random.uniform(-2, 2)),
                    (frag_x + frag_width + random.uniform(-2, 2), frag_y + frag_height + random.uniform(-2, 2)),
                    (frag_x + random.uniform(-2, 2), frag_y + frag_height + random.uniform(-2, 2))
                ]
                pygame.draw.polygon(sprite_surface, frag_color, points)
                
            # Draw cracks between fragments - black lines
            crack_color = (0, 0, 0)
            pygame.draw.line(sprite_surface, crack_color, (16, 0), (16, 32), 2)
            pygame.draw.line(sprite_surface, crack_color, (0, 16), (32, 16), 2)
            
            # Add some small debris around the cracks
            for i in range(5):
                debris_x = int(16 + random.uniform(-10, 10))
                debris_y = int(16 + random.uniform(-10, 10))
                debris_size = random.randint(1, 3)
                pygame.draw.circle(sprite_surface, (80, 70, 60), (debris_x, debris_y), debris_size)
                
        else:
            # Heavily damaged - draw scattered rubble
            # Clear background for transparency between rubble
            sprite_surface.fill((0, 0, 0, 0))
            
            # Draw 6-10 rubble pieces
            num_rubble = random.randint(6, 10)
            for i in range(num_rubble):
                rubble_size = int(32 * random.uniform(0.1, 0.25))
                rubble_x = int(random.uniform(0, 32 - rubble_size))
                rubble_y = int(random.uniform(0, 32 - rubble_size))
                
                # Vary the rubble color
                rubble_color = (
                    min(255, base_color[0] + random.randint(-30, 30)),
                    min(255, base_color[1] + random.randint(-30, 30)),
                    min(255, base_color[2] + random.randint(-30, 30))
                )
                
                # Draw the rubble piece with varied shapes
                shape = random.randint(0, 2)
                if shape == 0:
                    # Rectangle
                    pygame.draw.rect(sprite_surface, rubble_color, 
                                    (rubble_x, rubble_y, rubble_size, rubble_size))
                elif shape == 1:
                    # Circle
                    pygame.draw.circle(sprite_surface, rubble_color, 
                                    (rubble_x + rubble_size//2, rubble_y + rubble_size//2), 
                                    rubble_size // 2)
                else:
                    # Triangle
                    points = [
                        (rubble_x, rubble_y + rubble_size),
                        (rubble_x + rubble_size, rubble_y + rubble_size),
                        (rubble_x + rubble_size//2, rubble_y)
                    ]
                    pygame.draw.polygon(sprite_surface, rubble_color, points)
            
            # Add dust effect (small particles)
            for i in range(15):
                dust_x = int(random.uniform(0, 32))
                dust_y = int(random.uniform(0, 32))
                dust_size = random.randint(1, 2)
                dust_color = (100, 90, 80, 150)  # Semi-transparent dust
                pygame.draw.circle(sprite_surface, dust_color, (dust_x, dust_y), dust_size)
        
        # Set the sprite
        self.sprite = sprite_surface
        
    def get_damage_state(self):
        """
        Get the current damage state of the rock pile.
        
        Returns:
            str: "intact" if health > 50%, "damaged" if health <= 50%, "destroyed" if health <= 0
        """
        if not self.active or self.health <= 0:
            return "destroyed"
        elif self.health <= self.max_health / 2:
            return "damaged"
        else:
            return "intact"
            
    # We're now using the default render method from GameObject
    # which will use our dynamically created sprites