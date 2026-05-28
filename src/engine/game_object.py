"""
Game Object module for the Tank Game.
This module defines the base GameObject class that all game entities will inherit from.
"""
import pygame
import math


class GameObject:
    """
    Base class for all game objects.
    """
    def __init__(self, x, y):
        """
        Initialize a game object.
        
        Args:
            x (float): X-coordinate position
            y (float): Y-coordinate position
        """
        self.x = x
        self.y = y
        self.sprite = None
        self.width = 0
        self.height = 0
        self.rotation = 0  # Rotation in degrees
        self.active = True  # Whether the object is active in the game
        self.tag = ""  # Tag for identifying object type
        
    def update(self, delta_time):
        """
        Update the object state.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
        """
        pass
        
    def render(self, screen):
        """
        Render the object on the screen.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.active or not self.sprite:
            return
            
        if self.rotation == 0:
            screen.blit(self.sprite, (int(self.x), int(self.y)))
        else:
            # Rotate the sprite and maintain center position
            rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation)
            # Get the rect of the rotated sprite and set its center to the original center
            rect = rotated_sprite.get_rect(center=self.sprite.get_rect(topleft=(int(self.x), int(self.y))).center)
            screen.blit(rotated_sprite, rect.topleft)
            
    def get_rect(self):
        """
        Get the rectangle representing this object's position and size.
        
        Returns:
            pygame.Rect: Rectangle representing this object
        """
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
    def collides_with(self, other):
        """
        Check if this object collides with another object.
        
        Args:
            other: Another GameObject to check collision with
            
        Returns:
            bool: True if collision detected, False otherwise
        """
        if not self.active or not other.active:
            return False
        return self.get_rect().colliderect(other.get_rect())
        
    def set_position(self, x, y):
        """
        Set the position of the object.
        
        Args:
            x (float): New X-coordinate
            y (float): New Y-coordinate
        """
        self.x = x
        self.y = y
        
    def move(self, dx, dy):
        """
        Move the object by the given delta.
        
        Args:
            dx (float): Change in X-coordinate
            dy (float): Change in Y-coordinate
        """
        self.x += dx
        self.y += dy
        
    def set_rotation(self, degrees):
        """
        Set the rotation of the object.
        
        Args:
            degrees (float): Rotation angle in degrees
        """
        self.rotation = degrees % 360
        
    def rotate(self, delta_degrees):
        """
        Rotate the object by the given delta.
        
        Args:
            delta_degrees (float): Change in rotation angle in degrees
        """
        self.rotation = (self.rotation + delta_degrees) % 360
        
    def set_sprite(self, sprite):
        """
        Set the sprite for this object.
        
        Args:
            sprite: Pygame surface to use as sprite
        """
        self.sprite = sprite
        if sprite:
            self.width = sprite.get_width()
            self.height = sprite.get_height()
            
    def distance_to(self, other):
        """
        Calculate the distance to another game object.
        
        Args:
            other: Another GameObject
            
        Returns:
            float: Distance between the centers of the two objects
        """
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        other_center_x = other.x + other.width / 2
        other_center_y = other.y + other.height / 2
        
        dx = center_x - other_center_x
        dy = center_y - other_center_y
        
        return math.sqrt(dx * dx + dy * dy)
        
    def angle_to(self, other):
        """
        Calculate the angle to another game object.
        
        Args:
            other: Another GameObject
            
        Returns:
            float: Angle in degrees from this object to the other
        """
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        other_center_x = other.x + other.width / 2
        other_center_y = other.y + other.height / 2
        
        dx = other_center_x - center_x
        dy = other_center_y - center_y
        
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg