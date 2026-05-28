"""
PetrolBarrel module for the Tank Game.
This module defines the PetrolBarrel class that represents explosive petrol barrel obstacles.
"""
import math
from src.game_objects.destructible_element import DestructibleElement


class PetrolBarrel(DestructibleElement):
    """
    Represents an explosive petrol barrel obstacle in the game map.
    Petrol barrels can be destroyed by projectiles and create explosions that damage nearby objects.
    """
    
    def __init__(self, x, y, health=30):
        """
        Initialize a petrol barrel obstacle.
        
        Args:
            x (float): X-coordinate position
            y (float): Y-coordinate position
            health (int): Initial health of the petrol barrel (default: 30)
        """
        super().__init__(x, y, health)
        self.tag = "petrol_barrel"
        self.explosion_radius = 96  # Increased explosion radius in pixels (3 cells)
        self.explosion_damage = 75  # Increased base explosion damage
        
    def blocks_movement(self):
        """
        Check if this petrol barrel blocks movement.
        
        Returns:
            bool: True if active (barrel blocks movement), False if destroyed
        """
        return self.active
        
    def blocks_projectiles(self):
        """
        Check if this petrol barrel blocks projectiles.
        
        Returns:
            bool: True if active (barrel blocks projectiles), False if destroyed
        """
        return self.active
        
    def take_damage(self, amount):
        """
        Reduce the health of the petrol barrel by the given amount.
        When destroyed, triggers an explosion that damages nearby objects.
        
        Args:
            amount (int): Amount of damage to take
            
        Returns:
            dict: Contains 'destroyed' (bool) and 'explosion' (dict) if explosion occurred
        """
        old_health = self.health
        destroyed = super().take_damage(amount)
        
        result = {'destroyed': destroyed, 'explosion': None}
        
        # Add visual effects for damage
        if not destroyed and self.health != old_health:
            # Calculate damage percentage
            health_percentage = self.health / self.max_health
            
            # Make the barrel visually "wobble" when damaged
            # This is simulated by slightly changing its position
            wobble_amount = (1 - health_percentage) * 2  # More wobble as health decreases
            self.x += math.sin(self.health) * wobble_amount
            self.y += math.cos(self.health) * wobble_amount
            
            # Also change color intensity based on damage (handled by sprite in real implementation)
            # Here we just log it
            print(f"PetrolBarrel at ({self.x}, {self.y}) wobbling with intensity {wobble_amount}")
        
        # Log damage for debugging/testing
        if destroyed:
            print(f"PetrolBarrel at ({self.x}, {self.y}) destroyed! Health: {old_health} -> {self.health}")
            # Create explosion data
            result['explosion'] = self._create_explosion()
        elif self.health != old_health:
            print(f"PetrolBarrel at ({self.x}, {self.y}) damaged! Health: {old_health} -> {self.health}")
            
        return result
        
    def _create_explosion(self):
        """
        Create explosion data when the barrel is destroyed.
        
        Returns:
            dict: Explosion data containing center position, radius, and damage
        """
        # Calculate explosion center (center of the barrel)
        explosion_center_x = self.x + self.width / 2
        explosion_center_y = self.y + self.height / 2
        
        explosion_data = {
            'center_x': explosion_center_x,
            'center_y': explosion_center_y,
            'radius': self.explosion_radius,
            'damage': self.explosion_damage
        }
        
        print(f"Explosion created at ({explosion_center_x}, {explosion_center_y}) with radius {self.explosion_radius}")
        
        return explosion_data
        
    def calculate_explosion_damage(self, target_x, target_y, target_width=0, target_height=0):
        """
        Calculate explosion damage for a target at the given position.
        Damage decreases with distance from the explosion center.
        
        Args:
            target_x (float): X-coordinate of target
            target_y (float): Y-coordinate of target
            target_width (float): Width of target (default: 0)
            target_height (float): Height of target (default: 0)
            
        Returns:
            int: Damage amount (0 if target is outside explosion radius)
        """
        # Calculate explosion center
        explosion_center_x = self.x + self.width / 2
        explosion_center_y = self.y + self.height / 2
        
        # Calculate target center
        target_center_x = target_x + target_width / 2
        target_center_y = target_y + target_height / 2
        
        # Calculate distance from explosion center to target center
        dx = target_center_x - explosion_center_x
        dy = target_center_y - explosion_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If target is outside explosion radius, no damage
        if distance >= self.explosion_radius:
            return 0
            
        # Calculate damage based on distance (closer = more damage)
        damage_ratio = 1.0 - (distance / self.explosion_radius)
        damage = int(self.explosion_damage * damage_ratio)
        
        return max(damage, 1)  # Minimum 1 damage if within radius
        
    def is_in_explosion_radius(self, target_x, target_y, target_width=0, target_height=0):
        """
        Check if a target is within the explosion radius.
        
        Args:
            target_x (float): X-coordinate of target
            target_y (float): Y-coordinate of target
            target_width (float): Width of target (default: 0)
            target_height (float): Height of target (default: 0)
            
        Returns:
            bool: True if target is within explosion radius, False otherwise
        """
        return self.calculate_explosion_damage(target_x, target_y, target_width, target_height) > 0
        
    def render(self, screen):
        """
        Render the petrol barrel on the screen.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.active:
            return
            
        # Call the parent render method
        super().render(screen)