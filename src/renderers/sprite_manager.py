"""
Sprite Manager module for the Tank Game.
This module handles loading, caching, and managing game sprites.
"""
import pygame
import os


class SpriteManager:
    """
    Handles loading, caching, and managing game sprites.
    """
    def __init__(self):
        """Initialize the sprite manager."""
        self.sprites = {}  # Dictionary to cache loaded sprites
        
    def load_sprite(self, sprite_name, file_path):
        """
        Load a sprite from file and cache it.
        
        Args:
            sprite_name (str): Name to reference the sprite
            file_path (str): Path to the sprite image file
            
        Returns:
            pygame.Surface: The loaded sprite
        """
        if sprite_name in self.sprites:
            return self.sprites[sprite_name]
            
        if not os.path.exists(file_path):
            print(f"Warning: Sprite file not found: {file_path}")
            # Create a placeholder sprite (colored rectangle)
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta for missing textures
            self.sprites[sprite_name] = placeholder
            return placeholder
            
        try:
            sprite = pygame.image.load(file_path).convert_alpha()
            self.sprites[sprite_name] = sprite
            return sprite
        except pygame.error as e:
            print(f"Error loading sprite {file_path}: {e}")
            # Create a placeholder sprite
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta for missing textures
            self.sprites[sprite_name] = placeholder
            return placeholder
            
    def create_simple_sprite(self, sprite_name, width, height, color):
        """
        Create a simple colored rectangle sprite and cache it.
        
        Args:
            sprite_name (str): Name to reference the sprite
            width (int): Width of the sprite
            height (int): Height of the sprite
            color: RGB tuple representing the color
            
        Returns:
            pygame.Surface: The created sprite
        """
        sprite = pygame.Surface((width, height))
        sprite.fill(color)
        self.sprites[sprite_name] = sprite
        return sprite
        
    def get_sprite(self, sprite_name):
        """
        Get a cached sprite by name.
        
        Args:
            sprite_name (str): Name of the sprite to get
            
        Returns:
            pygame.Surface: The sprite, or None if not found
        """
        return self.sprites.get(sprite_name)
        
    def rotate_sprite(self, sprite, angle):
        """
        Rotate a sprite by the given angle.
        
        Args:
            sprite: Pygame surface to rotate
            angle (float): Rotation angle in degrees
            
        Returns:
            pygame.Surface: The rotated sprite
        """
        return pygame.transform.rotate(sprite, angle)
        
    def scale_sprite(self, sprite, width, height):
        """
        Scale a sprite to the given dimensions.
        
        Args:
            sprite: Pygame surface to scale
            width (int): New width
            height (int): New height
            
        Returns:
            pygame.Surface: The scaled sprite
        """
        return pygame.transform.scale(sprite, (width, height))
        
    def clear_cache(self):
        """Clear the sprite cache."""
        self.sprites.clear()