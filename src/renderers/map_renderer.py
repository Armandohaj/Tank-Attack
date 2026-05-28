"""
Map Renderer module for the Tank Game.
This module handles the rendering of the game map.
"""
import pygame
import random
from src.level_manager.map_data import MapData


class MapRenderer:
    """
    Handles rendering of the game map.
    """
    def __init__(self, renderer):
        """
        Initialize the map renderer.
        
        Args:
            renderer: The game renderer
        """
        self.renderer = renderer
        self.wall_sprite = None
        self.rock_pile_sprite = None
        self.rock_pile_damaged_sprite = None
        self.petrol_barrel_sprite = None
        self.petrol_barrel_damaged_sprite = None
        self.ground_sprite = None
        self.cell_size = 32  # Default cell size in pixels
        
        # Create default sprites
        self._create_default_sprites()
        
    def _create_default_sprites(self):
        """Create default sprites for map elements."""
        # Create ground sprite (light green)
        self.ground_sprite = self.renderer.create_simple_sprite(
            "ground", self.cell_size, self.cell_size, (100, 180, 100)
        )
        
        # Add some texture to the ground
        for _ in range(5):
            x = random.randint(0, self.cell_size - 1)
            y = random.randint(0, self.cell_size - 1)
            pygame.draw.circle(
                self.ground_sprite,
                (90, 160, 90),
                (x, y),
                1
            )
        
        # Create wall sprite (dark gray)
        self.wall_sprite = self.renderer.create_simple_sprite(
            "wall", self.cell_size, self.cell_size, (80, 80, 80)
        )
        
        # Add some texture to the wall
        pygame.draw.line(
            self.wall_sprite,
            (60, 60, 60),
            (5, 5),
            (self.cell_size - 5, 5),
            2
        )
        pygame.draw.line(
            self.wall_sprite,
            (60, 60, 60),
            (5, self.cell_size - 5),
            (self.cell_size - 5, self.cell_size - 5),
            2
        )
        
        # Create rock pile sprite (brown)
        self.rock_pile_sprite = self.renderer.create_simple_sprite(
            "rock_pile", self.cell_size, self.cell_size, (139, 69, 19)
        )
        
        # Add rock texture
        for _ in range(8):
            x = random.randint(4, self.cell_size - 5)
            y = random.randint(4, self.cell_size - 5)
            size = random.randint(3, 6)
            pygame.draw.circle(
                self.rock_pile_sprite,
                (120, 60, 10),
                (x, y),
                size
            )
        
        # Create damaged rock pile sprite
        self.rock_pile_damaged_sprite = self.renderer.create_simple_sprite(
            "rock_pile_damaged", self.cell_size, self.cell_size, (160, 82, 45)
        )
        
        # Add fewer rocks for damaged state
        for _ in range(4):
            x = random.randint(4, self.cell_size - 5)
            y = random.randint(4, self.cell_size - 5)
            size = random.randint(3, 6)
            pygame.draw.circle(
                self.rock_pile_damaged_sprite,
                (120, 60, 10),
                (x, y),
                size
            )
        
        # Create petrol barrel sprite (red)
        self.petrol_barrel_sprite = self.renderer.create_simple_sprite(
            "petrol_barrel", self.cell_size, self.cell_size, (180, 30, 30)
        )
        
        # Add barrel shape
        pygame.draw.rect(
            self.petrol_barrel_sprite,
            (200, 40, 40),
            (self.cell_size // 4, self.cell_size // 4, 
             self.cell_size // 2, self.cell_size // 2),
            2
        )
        
        # Create damaged petrol barrel sprite
        self.petrol_barrel_damaged_sprite = self.renderer.create_simple_sprite(
            "petrol_barrel_damaged", self.cell_size, self.cell_size, (200, 60, 60)
        )
        
        # Add "leaking" effect
        pygame.draw.line(
            self.petrol_barrel_damaged_sprite,
            (220, 20, 20),
            (self.cell_size // 4, self.cell_size * 3 // 4),
            (self.cell_size * 3 // 4, self.cell_size // 4),
            3
        )
        
    def set_cell_size(self, cell_size):
        """
        Set the size of each cell in pixels.
        
        Args:
            cell_size (int): Size of each cell in pixels
        """
        self.cell_size = cell_size
        self._create_default_sprites()
        
    def set_wall_sprite(self, sprite):
        """
        Set the sprite for wall cells.
        
        Args:
            sprite: Pygame surface to use as wall sprite
        """
        self.wall_sprite = sprite
        
    def set_rock_pile_sprite(self, sprite, damaged_sprite=None):
        """
        Set the sprite for rock pile cells.
        
        Args:
            sprite: Pygame surface to use as rock pile sprite
            damaged_sprite: Pygame surface to use as damaged rock pile sprite
        """
        self.rock_pile_sprite = sprite
        if damaged_sprite:
            self.rock_pile_damaged_sprite = damaged_sprite
            
    def set_petrol_barrel_sprite(self, sprite, damaged_sprite=None):
        """
        Set the sprite for petrol barrel cells.
        
        Args:
            sprite: Pygame surface to use as petrol barrel sprite
            damaged_sprite: Pygame surface to use as damaged petrol barrel sprite
        """
        self.petrol_barrel_sprite = sprite
        if damaged_sprite:
            self.petrol_barrel_damaged_sprite = damaged_sprite
        
    def set_ground_sprite(self, sprite):
        """
        Set the sprite for ground/empty cells.
        
        Args:
            sprite: Pygame surface to use as ground sprite
        """
        self.ground_sprite = sprite
        
    def render_map(self, screen, map_data):
        """
        Render the map on the screen.
        
        Args:
            screen: Pygame surface to render on
            map_data (MapData): The map data to render
        """
        # First render the ground/empty cells as the base layer
        for y in range(map_data.height):
            for x in range(map_data.width):
                pixel_x, pixel_y = map_data.get_pixel_position(x, y)
                screen.blit(self.ground_sprite, (pixel_x, pixel_y))
        
        # Then render obstacles and destructible elements on top
        for y in range(map_data.height):
            for x in range(map_data.width):
                cell_type = map_data.get_cell(x, y)
                pixel_x, pixel_y = map_data.get_pixel_position(x, y)
                
                if cell_type == MapData.WALL:
                    # Render wall
                    screen.blit(self.wall_sprite, (pixel_x, pixel_y))
                    
                elif cell_type == MapData.ROCK_PILE:
                    # Render rock pile
                    screen.blit(self.rock_pile_sprite, (pixel_x, pixel_y))
                    
                elif cell_type == MapData.PETROL_BARREL:
                    # Render petrol barrel
                    screen.blit(self.petrol_barrel_sprite, (pixel_x, pixel_y))
                    
    def render_rock_pile(self, screen, x, y, health, max_health):
        """
        Render a rock pile with health indication.
        
        Args:
            screen: Pygame surface to render on
            x (int): X-coordinate in pixels
            y (int): Y-coordinate in pixels
            health (int): Current health of the rock pile
            max_health (int): Maximum health of the rock pile
        """
        # Choose sprite based on health
        if health > max_health / 2:
            screen.blit(self.rock_pile_sprite, (x, y))
        else:
            screen.blit(self.rock_pile_damaged_sprite, (x, y))
            
    def render_petrol_barrel(self, screen, x, y, health, max_health):
        """
        Render a petrol barrel with health indication.
        
        Args:
            screen: Pygame surface to render on
            x (int): X-coordinate in pixels
            y (int): Y-coordinate in pixels
            health (int): Current health of the petrol barrel
            max_health (int): Maximum health of the petrol barrel
        """
        # Choose sprite based on health
        if health > max_health / 2:
            screen.blit(self.petrol_barrel_sprite, (x, y))
        else:
            screen.blit(self.petrol_barrel_damaged_sprite, (x, y))