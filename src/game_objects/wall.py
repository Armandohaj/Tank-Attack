"""
Wall module for the Tank Game.
This module defines the Wall class that represents indestructible wall obstacles.
"""
from src.engine.game_object import GameObject


class Wall(GameObject):
    """
    Represents an indestructible wall obstacle in the game map.
    Walls block movement and projectiles but cannot be destroyed.
    """
    
    def __init__(self, x, y):
        """
        Initialize a wall obstacle.
        
        Args:
            x (float): X-coordinate position
            y (float): Y-coordinate position
        """
        super().__init__(x, y)
        # Set default wall dimensions (32x32 pixels)
        self.width = 32
        self.height = 32
        self.destructible = False
        self.tag = "wall"
        
    def take_damage(self, amount):
        """
        Walls cannot take damage as they are indestructible.
        
        Args:
            amount (int): Amount of damage (ignored for walls)
            
        Returns:
            bool: Always returns False as walls cannot be destroyed
        """
        # Walls are indestructible, so they don't take damage
        return False
        
    def blocks_movement(self):
        """
        Check if this wall blocks movement.
        
        Returns:
            bool: Always returns True as walls block movement
        """
        return True
        
    def blocks_projectiles(self):
        """
        Check if this wall blocks projectiles.
        
        Returns:
            bool: Always returns True as walls block projectiles
        """
        return True
        
    def render(self, screen):
        """
        Render the wall on the screen.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.active:
            return
            
        # Call the parent render method
        super().render(screen)