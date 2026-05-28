"""
Renderer module for the Tank Game.
This module handles the visual representation of game objects and UI elements.
"""
import pygame
import os
from src.renderers.sprite_manager import SpriteManager


class Renderer:
    """
    Handles rendering of game objects and UI elements.
    """
    def __init__(self, screen, target_fps=60):
        """
        Initialize the renderer.
        
        Args:
            screen: Pygame surface to render on
            target_fps (int): Target frames per second
        """
        self.screen = screen
        self.target_fps = target_fps
        self.clock = pygame.time.Clock()
        self.sprite_manager = SpriteManager()
        self.fonts = {}    # Cache for loaded fonts
        self.background_color = (0, 0, 0)  # Default background color (black)
        
    def clear_screen(self):
        """Clear the screen with the background color."""
        self.screen.fill(self.background_color)
        
    def set_background_color(self, color):
        """
        Set the background color.
        
        Args:
            color: RGB tuple representing the color
        """
        self.background_color = color
        
    def render_game_objects(self, game_objects):
        """
        Render all game objects.
        
        Args:
            game_objects (list): List of game objects to render
        """
        for game_object in game_objects:
            game_object.render(self.screen)
            
    def render_ui(self, game_state):
        """
        Render UI elements based on game state.
        
        Args:
            game_state: Current game state containing UI information
        """
        # Render score
        if hasattr(game_state, 'score'):
            score_text = f"Score: {game_state.score}"
            self.render_text(score_text, None, 24, (255, 255, 255), 10, 10)
            
        # Render level
        if hasattr(game_state, 'current_level') and hasattr(game_state, 'max_level'):
            level_text = f"Level: {game_state.current_level}/{game_state.max_level}"
            self.render_text(level_text, None, 24, (255, 255, 255), 10, 40)
            
        # Render player health if available
        player = self._find_player(game_state)
        if player and hasattr(player, 'health') and hasattr(player, 'max_health'):
            health_text = f"Health: {player.health}/{player.max_health}"
            self.render_text(health_text, None, 24, (255, 255, 255), 10, 70)
            
            # Render health bar
            health_bar_width = 200
            health_bar_height = 20
            health_percentage = max(0, min(1, player.health / player.max_health))
            
            # Background (red)
            pygame.draw.rect(self.screen, (255, 0, 0), 
                            (10, 100, health_bar_width, health_bar_height))
            
            # Foreground (green)
            pygame.draw.rect(self.screen, (0, 255, 0), 
                            (10, 100, int(health_bar_width * health_percentage), health_bar_height))
            
    def _find_player(self, game_state):
        """
        Find the player object in the game state.
        
        Args:
            game_state: Current game state
            
        Returns:
            The player object, or None if not found
        """
        if hasattr(game_state, 'player'):
            return game_state.player
            
        if hasattr(game_state, 'game_objects'):
            for obj in game_state.game_objects:
                if hasattr(obj, 'tag') and obj.tag == "player":
                    return obj
                    
        return None
        
    def update_display(self):
        """Update the display and control frame rate."""
        pygame.display.flip()
        return self.clock.tick(self.target_fps) / 1000.0  # Return delta time in seconds
        
    def load_sprite(self, sprite_name, file_path):
        """
        Load a sprite from file and cache it.
        
        Args:
            sprite_name (str): Name to reference the sprite
            file_path (str): Path to the sprite image file
            
        Returns:
            pygame.Surface: The loaded sprite
        """
        return self.sprite_manager.load_sprite(sprite_name, file_path)
            
    def load_font(self, font_name, size):
        """
        Load a font with the specified size and cache it.
        
        Args:
            font_name (str): Name of the font or path to font file
            size (int): Font size
            
        Returns:
            pygame.font.Font: The loaded font
        """
        # If font_name is None, use the default system font
        if font_name is None:
            font = pygame.font.SysFont(None, size)
            return font
            
        key = f"{font_name}_{size}"
        if key in self.fonts:
            return self.fonts[key]
            
        try:
            if os.path.exists(font_name):
                font = pygame.font.Font(font_name, size)
            else:
                font = pygame.font.SysFont(font_name, size)
            self.fonts[key] = font
            return font
        except pygame.error as e:
            print(f"Error loading font {font_name}: {e}")
            # Use default font as fallback
            font = pygame.font.SysFont(None, size)
            self.fonts[key] = font
            return font
            
    def render_text(self, text, font_name, size, color, x, y, centered=False):
        """
        Render text on the screen.
        
        Args:
            text (str): Text to render
            font_name (str): Name of the font or path to font file
            size (int): Font size
            color: RGB tuple representing the text color
            x (int): X-coordinate position
            y (int): Y-coordinate position
            centered (bool): If True, the text will be centered at (x, y)
        """
        font = self.load_font(font_name, size)
        text_surface = font.render(text, True, color)
        
        if centered:
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))
            
    def create_simple_sprite(self, sprite_name, width, height, color):
        """
        Create a simple colored rectangle sprite.
        
        Args:
            sprite_name (str): Name to reference the sprite
            width (int): Width of the sprite
            height (int): Height of the sprite
            color: RGB tuple representing the color
            
        Returns:
            pygame.Surface: The created sprite
        """
        return self.sprite_manager.create_simple_sprite(sprite_name, width, height, color)
        
    def get_sprite(self, sprite_name):
        """
        Get a cached sprite by name.
        
        Args:
            sprite_name (str): Name of the sprite to get
            
        Returns:
            pygame.Surface: The sprite, or None if not found
        """
        return self.sprite_manager.get_sprite(sprite_name)
        
    def rotate_sprite(self, sprite, angle):
        """
        Rotate a sprite by the given angle.
        
        Args:
            sprite: Pygame surface to rotate
            angle (float): Rotation angle in degrees
            
        Returns:
            pygame.Surface: The rotated sprite
        """
        return self.sprite_manager.rotate_sprite(sprite, angle)
        
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
        return self.sprite_manager.scale_sprite(sprite, width, height)