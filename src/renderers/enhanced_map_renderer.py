"""
Enhanced Map Renderer module for the Tank Game.
This module handles the rendering of the game map with improved visuals.
"""
import pygame
import random
import math
from src.level_manager.map_data import MapData


class EnhancedMapRenderer:
    """
    Handles enhanced rendering of the game map with improved visuals.
    """
    def __init__(self, renderer):
        """
        Initialize the enhanced map renderer.
        
        Args:
            renderer: The game renderer
        """
        self.renderer = renderer
        self.wall_sprite = None
        self.rock_pile_sprite = None
        self.rock_pile_damaged_sprite = None
        self.petrol_barrel_sprite = None
        self.petrol_barrel_damaged_sprite = None
        self.ground_sprites = []  # Multiple ground variations
        self.cell_size = 32  # Default cell size in pixels
        
        # Create enhanced sprites
        self._create_enhanced_sprites()
        
    def _create_enhanced_sprites(self):
        """Create enhanced sprites for map elements."""
        # Create multiple ground sprite variations for more natural look
        self._create_ground_variations()
        
        # Create enhanced wall sprite
        self._create_enhanced_wall_sprite()
        
        # Create enhanced rock pile sprites
        self._create_enhanced_rock_pile_sprites()
        
        # Create enhanced petrol barrel sprites
        self._create_enhanced_petrol_barrel_sprites()
        
    def _create_ground_variations(self):
        """Create multiple ground sprite variations."""
        self.ground_sprites = []
        base_colors = [
            (190, 170, 110),
            (180, 160, 100),
            (200, 180, 120),
            (170, 150, 90)
        ]
        
        for i, base_color in enumerate(base_colors):
            ground_sprite = pygame.Surface((self.cell_size, self.cell_size))
            ground_sprite.fill(base_color)
            
            # Add grass texture
            for _ in range(8):
                x = random.randint(0, self.cell_size - 1)
                y = random.randint(0, self.cell_size - 1)
                darker_color = tuple(max(0, c - 20) for c in base_color)
                pygame.draw.circle(ground_sprite, darker_color, (x, y), 1)
            
            # Add some small rocks/dirt patches
            for _ in range(3):
                x = random.randint(2, self.cell_size - 3)
                y = random.randint(2, self.cell_size - 3)
                dirt_color = (80, 60, 40)
                pygame.draw.circle(ground_sprite, dirt_color, (x, y), random.randint(1, 2))
            
            # Add subtle gradient
            for y in range(self.cell_size):
                alpha = int(10 * (y / self.cell_size))
                gradient_color = tuple(max(0, c - alpha) for c in base_color)
                pygame.draw.line(ground_sprite, gradient_color, (0, y), (self.cell_size, y))
            
            self.ground_sprites.append(ground_sprite)
            
    def _create_enhanced_wall_sprite(self):
        """Create enhanced wall sprite with 3D effect."""
        self.wall_sprite = pygame.Surface((self.cell_size, self.cell_size))
        
        # Base colors
        base_color = (70, 70, 70)
        dark_color = (35, 35, 35)
        light_color = (120, 120, 120)
        
        # Fill with base color
        self.wall_sprite.fill(base_color)
        
        # Add 3D effect with highlights and shadows
        # Top highlight
        pygame.draw.line(self.wall_sprite, light_color, (0, 0), (self.cell_size - 1, 0), 2)
        # Left highlight
        pygame.draw.line(self.wall_sprite, light_color, (0, 0), (0, self.cell_size - 1), 2)
        # Bottom shadow
        pygame.draw.line(self.wall_sprite, dark_color, (0, self.cell_size - 1), (self.cell_size - 1, self.cell_size - 1), 2)
        # Right shadow
        pygame.draw.line(self.wall_sprite, dark_color, (self.cell_size - 1, 0), (self.cell_size - 1, self.cell_size - 1), 2)
        
        # Add brick pattern
        brick_height = self.cell_size // 4
        for row in range(4):
            y = row * brick_height
            # Alternate brick pattern
            if row % 2 == 0:
                # Even rows - full bricks
                for col in range(2):
                    x = col * (self.cell_size // 2)
                    pygame.draw.rect(self.wall_sprite, dark_color, (x, y, self.cell_size // 2 - 1, brick_height - 1), 1)
            else:
                # Odd rows - offset bricks
                pygame.draw.rect(self.wall_sprite, dark_color, (self.cell_size // 4, y, self.cell_size // 2 - 1, brick_height - 1), 1)
        
        # Add some weathering effects
        for _ in range(5):
            x = random.randint(0, self.cell_size - 1)
            y = random.randint(0, self.cell_size - 1)
            weather_color = tuple(c + random.randint(-10, 10) for c in base_color)
            weather_color = tuple(max(0, min(255, c)) for c in weather_color)
            pygame.draw.circle(self.wall_sprite, weather_color, (x, y), 1)
            
    def _create_enhanced_rock_pile_sprites(self):
        """Create enhanced rock pile sprites."""
        # Intact rock pile
        self.rock_pile_sprite = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        self.rock_pile_sprite.fill((0, 0, 0, 0))
        
        base_color = (110, 110, 110)
        rock_colors = [
            (90, 90, 90),
            (120, 120, 120),
            (70, 70, 70),
            (150, 150, 150)
        ]
        
        # Draw multiple rocks with varying sizes and colors
        for _ in range(12):
            x = random.randint(4, self.cell_size - 5)
            y = random.randint(4, self.cell_size - 5)
            size = random.randint(3, 7)
            color = random.choice(rock_colors)
            
            # Draw rock with highlight and shadow
            pygame.draw.circle(self.rock_pile_sprite, tuple(max(0, c - 20) for c in color), (x + 1, y + 1), size)
            pygame.draw.circle(self.rock_pile_sprite, color, (x, y), size)
            pygame.draw.circle(self.rock_pile_sprite, tuple(min(255, c + 30) for c in color), (x - 1, y - 1), size // 2)
        
        # Damaged rock pile
        self.rock_pile_damaged_sprite = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        self.rock_pile_damaged_sprite.fill((0, 0, 0, 0))
        
        # Draw fewer, more scattered rocks
        for _ in range(6):
            x = random.randint(2, self.cell_size - 3)
            y = random.randint(2, self.cell_size - 3)
            size = random.randint(2, 5)
            color = random.choice(rock_colors)
            
            pygame.draw.circle(self.rock_pile_damaged_sprite, tuple(max(0, c - 20) for c in color), (x + 1, y + 1), size)
            pygame.draw.circle(self.rock_pile_damaged_sprite, color, (x, y), size)
        
        # Add some debris
        for _ in range(8):
            x = random.randint(0, self.cell_size - 1)
            y = random.randint(0, self.cell_size - 1)
            pygame.draw.circle(self.rock_pile_damaged_sprite, (100, 50, 10), (x, y), 1)
            
    def _create_enhanced_petrol_barrel_sprites(self):
        """Create enhanced petrol barrel sprites."""
        # Intact petrol barrel
        self.petrol_barrel_sprite = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        self.petrol_barrel_sprite.fill((0, 0, 0, 0))
        
        # Barrel dimensions
        barrel_width = self.cell_size - 8
        barrel_height = self.cell_size - 6
        barrel_x = 4
        barrel_y = 3
        
        # Base colors
        barrel_color = (210, 170, 30)
        dark_color = (140, 100, 20)
        light_color = (240, 210, 80)
        
        # Draw barrel shadow
        pygame.draw.ellipse(self.petrol_barrel_sprite, (0, 0, 0, 100), 
                        (barrel_x + 2, barrel_y + barrel_height - 2, barrel_width, 4))
        
        # Draw main barrel body
        pygame.draw.rect(self.petrol_barrel_sprite, dark_color, 
                        (barrel_x, barrel_y, barrel_width, barrel_height), border_radius=3)
        pygame.draw.rect(self.petrol_barrel_sprite, barrel_color, 
                        (barrel_x + 1, barrel_y + 1, barrel_width - 2, barrel_height - 2), border_radius=3)
        
        # Add cylindrical highlights
        pygame.draw.rect(self.petrol_barrel_sprite, light_color, 
                        (barrel_x + 2, barrel_y + 2, 3, barrel_height - 4))
        
        # Add barrel rings
        for i in range(3):
            ring_y = barrel_y + 4 + i * 6
            pygame.draw.line(self.petrol_barrel_sprite, dark_color, 
                           (barrel_x, ring_y), (barrel_x + barrel_width, ring_y), 1)
        
        # Add warning symbol
        symbol_x = barrel_x + barrel_width // 2
        symbol_y = barrel_y + barrel_height // 2
        pygame.draw.circle(self.petrol_barrel_sprite, (255, 255, 0), (symbol_x, symbol_y), 4)
        pygame.draw.polygon(self.petrol_barrel_sprite, (255, 0, 0), 
                           [(symbol_x, symbol_y - 2), (symbol_x - 2, symbol_y + 2), (symbol_x + 2, symbol_y + 2)])
        
        # Damaged petrol barrel
        self.petrol_barrel_damaged_sprite = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        self.petrol_barrel_damaged_sprite.fill((0, 0, 0, 0))
        
        # Draw damaged barrel (more dented and leaking)
        damaged_color = (200, 60, 60)
        
        # Draw barrel with dents
        pygame.draw.rect(self.petrol_barrel_damaged_sprite, dark_color, 
                        (barrel_x, barrel_y, barrel_width, barrel_height), border_radius=3)
        pygame.draw.rect(self.petrol_barrel_damaged_sprite, damaged_color, 
                        (barrel_x + 1, barrel_y + 1, barrel_width - 2, barrel_height - 2), border_radius=3)
        
        # Add dent effects
        for _ in range(3):
            dent_x = random.randint(barrel_x + 2, barrel_x + barrel_width - 4)
            dent_y = random.randint(barrel_y + 2, barrel_y + barrel_height - 4)
            pygame.draw.circle(self.petrol_barrel_damaged_sprite, dark_color, (dent_x, dent_y), 2)
        
        # Add leak effect
        leak_color = (100, 50, 0)
        for i in range(3):
            leak_x = barrel_x + barrel_width // 2 + random.randint(-3, 3)
            leak_y = barrel_y + barrel_height + i
            pygame.draw.circle(self.petrol_barrel_damaged_sprite, leak_color, (leak_x, leak_y), 1)
        
        # Add sparks/danger indicators
        for _ in range(2):
            spark_x = random.randint(barrel_x, barrel_x + barrel_width)
            spark_y = random.randint(barrel_y, barrel_y + barrel_height)
            pygame.draw.circle(self.petrol_barrel_damaged_sprite, (255, 255, 0), (spark_x, spark_y), 1)
            
    def set_cell_size(self, cell_size):
        """
        Set the size of each cell in pixels.
        
        Args:
            cell_size (int): Size of each cell in pixels
        """
        self.cell_size = cell_size
        self._create_enhanced_sprites()
        
    def render_map(self, screen, map_data, game_objects=None):
        """
        Render the enhanced map on the screen.
        
        Args:
            screen: Pygame surface to render on
            map_data (MapData): The map data to render
            game_objects (list): List of game objects to check for destructible elements
        """
        # First render the ground/empty cells as the base layer with variations
        for y in range(map_data.height):
            for x in range(map_data.width):
                pixel_x, pixel_y = map_data.get_pixel_position(x, y)
                
                # Use different ground sprites for variation
                ground_index = (x + y) % len(self.ground_sprites)
                screen.blit(self.ground_sprites[ground_index], (pixel_x, pixel_y))
        
        # Then render obstacles and destructible elements on top
        for y in range(map_data.height):
            for x in range(map_data.width):
                cell_type = map_data.get_cell(x, y)
                pixel_x, pixel_y = map_data.get_pixel_position(x, y)
                
                if cell_type == MapData.WALL:
                    # Render enhanced wall
                    screen.blit(self.wall_sprite, (pixel_x, pixel_y))
                    
                elif cell_type == MapData.ROCK_PILE:
                    # Find the corresponding rock pile game object
                    rock_pile_obj = self._find_destructible_at_position(game_objects, pixel_x, pixel_y, "rock_pile")
                    if rock_pile_obj and rock_pile_obj.active and rock_pile_obj.sprite:
                        # Use the rock pile's custom sprite
                        screen.blit(rock_pile_obj.sprite, (pixel_x, pixel_y))
                    else:
                        # Fallback to default sprite
                        screen.blit(self.rock_pile_sprite, (pixel_x, pixel_y))
                    
                elif cell_type == MapData.PETROL_BARREL:
                    # Find the corresponding petrol barrel game object
                    barrel_obj = self._find_destructible_at_position(game_objects, pixel_x, pixel_y, "petrol_barrel")
                    if barrel_obj and barrel_obj.active and barrel_obj.sprite:
                        # Use the petrol barrel's custom sprite
                        screen.blit(barrel_obj.sprite, (pixel_x, pixel_y))
                    else:
                        # Fallback to default sprite
                        screen.blit(self.petrol_barrel_sprite, (pixel_x, pixel_y))
                        
    def _find_destructible_at_position(self, game_objects, pixel_x, pixel_y, tag):
        """
        Find a destructible element at the given pixel position.
        
        Args:
            game_objects (list): List of game objects
            pixel_x (int): X-coordinate in pixels
            pixel_y (int): Y-coordinate in pixels
            tag (str): Tag of the object to find
            
        Returns:
            GameObject or None: The found object or None
        """
        if not game_objects:
            return None
            
        for obj in game_objects:
            if (hasattr(obj, 'tag') and obj.tag == tag and 
                hasattr(obj, 'x') and hasattr(obj, 'y')):
                # Check if the object is at approximately the same position
                if (abs(obj.x - pixel_x) < 16 and abs(obj.y - pixel_y) < 16):
                    return obj
        return None
                    
    def render_rock_pile(self, screen, x, y, health, max_health):
        """
        Render an enhanced rock pile with health indication.
        
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
            
        # Add dust effect for damaged rock piles
        if health <= max_health / 2:
            self._render_dust_effect(screen, x, y)
            
    def render_petrol_barrel(self, screen, x, y, health, max_health):
        """
        Render an enhanced petrol barrel with health indication.
        
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
            
        # Add danger glow for damaged barrels
        if health <= max_health / 2:
            self._render_danger_glow(screen, x, y)
            
    def _render_dust_effect(self, screen, x, y):
        """
        Render dust effect for damaged rock piles.
        
        Args:
            screen: Pygame surface to render on
            x (int): X-coordinate
            y (int): Y-coordinate
        """
        dust_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        
        for _ in range(3):
            dust_x = random.randint(0, self.cell_size)
            dust_y = random.randint(0, self.cell_size)
            dust_size = random.randint(1, 3)
            pygame.draw.circle(dust_surface, (150, 120, 80, 100), (dust_x, dust_y), dust_size)
        
        screen.blit(dust_surface, (x, y))
        
    def _render_danger_glow(self, screen, x, y):
        """
        Render danger glow effect for damaged petrol barrels.
        
        Args:
            screen: Pygame surface to render on
            x (int): X-coordinate
            y (int): Y-coordinate
        """
        glow_surface = pygame.Surface((self.cell_size + 8, self.cell_size + 8), pygame.SRCALPHA)
        
        # Pulsing red glow
        import time
        pulse = abs(math.sin(time.time() * 3))  # Pulse 3 times per second
        alpha = int(50 + 30 * pulse)
        
        pygame.draw.circle(glow_surface, (255, 0, 0, alpha), 
                          (self.cell_size // 2 + 4, self.cell_size // 2 + 4), 
                          self.cell_size // 2 + 4)
        
        screen.blit(glow_surface, (x - 4, y - 4), special_flags=pygame.BLEND_ADD)
        
    def render_background_effects(self, screen, map_data):
        """
        Render background atmospheric effects.
        
        Args:
            screen: Pygame surface to render on
            map_data: The map data
        """
        # Add subtle ambient particles
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        for _ in range(5):
            particle_x = random.randint(0, screen_width)
            particle_y = random.randint(0, screen_height)
            particle_size = random.randint(1, 2)
            
            # Only render particles over ground areas
            map_x = particle_x // self.cell_size
            map_y = particle_y // self.cell_size
            
            if (0 <= map_x < map_data.width and 0 <= map_y < map_data.height and 
                map_data.get_cell(map_x, map_y) == MapData.EMPTY):
                
                particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, (255, 255, 255, 30), 
                                 (particle_size, particle_size), particle_size)
                screen.blit(particle_surface, (particle_x - particle_size, particle_y - particle_size))