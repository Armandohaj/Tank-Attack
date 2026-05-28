"""
Spawn Validator module for the Tank Game.
This module defines the SpawnValidator class that handles validation of spawn locations.
"""
import random
import math


class SpawnValidator:
    """
    Handles validation of spawn locations to ensure tanks don't spawn inside terrain or obstacles.
    """
    
    def __init__(self, map_data):
        """
        Initialize the spawn validator.
        
        Args:
            map_data (MapData): The map data for the current level
        """
        self.map_data = map_data
        
    def find_valid_spawn_location(self, tank_size=32, max_attempts=50, min_distance_from_obstacles=1):
        """
        Find a valid spawn location for a tank.
        
        Args:
            tank_size (int): Size of the tank in pixels (default: 32 for one cell)
            max_attempts (int): Maximum number of attempts to find a valid location
            min_distance_from_obstacles (int): Minimum distance from obstacles in cells
            
        Returns:
            tuple: (x, y) pixel coordinates if found, None otherwise
        """
        for attempt in range(max_attempts):
            # Generate random pixel coordinates within the map bounds
            # Leave some margin from the edges to ensure the tank fits
            margin = tank_size // 2 + min_distance_from_obstacles * self.map_data.cell_size
            
            x = random.randint(margin, 
                             self.map_data.width * self.map_data.cell_size - margin)
            y = random.randint(margin, 
                             self.map_data.height * self.map_data.cell_size - margin)
            
            if self.is_location_valid(x, y, tank_size, min_distance_from_obstacles):
                return (x, y)
                
        return None
        
    def is_location_valid(self, x, y, tank_size=32, min_distance_from_obstacles=1):
        """
        Check if the given location is valid for spawning a tank.
        
        Args:
            x (float): X-coordinate in pixels
            y (float): Y-coordinate in pixels
            tank_size (int): Size of the tank in pixels
            min_distance_from_obstacles (int): Minimum distance from obstacles in cells
            
        Returns:
            bool: True if the location is valid, False otherwise
        """
        # Check if the location is within map bounds
        if not self._is_within_bounds(x, y, tank_size):
            return False
            
        # Check for collision with obstacles
        if self._check_obstacle_collision(x, y, tank_size, min_distance_from_obstacles):
            return False
            
        # Check if there's enough maneuvering space around the spawn location
        if not self._has_maneuvering_space(x, y, tank_size):
            return False
            
        return True
        
    def _is_within_bounds(self, x, y, tank_size):
        """
        Check if the tank would be within map bounds at the given location.
        
        Args:
            x (float): X-coordinate in pixels
            y (float): Y-coordinate in pixels
            tank_size (int): Size of the tank in pixels
            
        Returns:
            bool: True if within bounds, False otherwise
        """
        half_size = tank_size // 2
        
        # Check if all corners of the tank would be within the map
        return (x - half_size >= 0 and 
                y - half_size >= 0 and
                x + half_size < self.map_data.width * self.map_data.cell_size and
                y + half_size < self.map_data.height * self.map_data.cell_size)
        
    def _check_obstacle_collision(self, x, y, tank_size, min_distance_from_obstacles):
        """
        Check if the tank would collide with obstacles at the given location.
        
        Args:
            x (float): X-coordinate in pixels
            y (float): Y-coordinate in pixels
            tank_size (int): Size of the tank in pixels
            min_distance_from_obstacles (int): Minimum distance from obstacles in cells
            
        Returns:
            bool: True if there would be a collision, False otherwise
        """
        # Convert tank position to cell coordinates
        center_cell_x = int(x // self.map_data.cell_size)
        center_cell_y = int(y // self.map_data.cell_size)
        
        # Calculate how many cells to check around the tank
        tank_radius_cells = max(1, int(math.ceil(tank_size / (2 * self.map_data.cell_size))))
        check_radius = tank_radius_cells + min_distance_from_obstacles
        
        # Check each cell in the area
        for dy in range(-check_radius, check_radius + 1):
            for dx in range(-check_radius, check_radius + 1):
                cell_x = center_cell_x + dx
                cell_y = center_cell_y + dy
                
                # Skip cells outside the map
                if (cell_x < 0 or cell_x >= self.map_data.width or 
                    cell_y < 0 or cell_y >= self.map_data.height):
                    continue
                    
                if self.map_data.is_obstacle_at(cell_x, cell_y):
                    # Calculate distance from tank center to obstacle cell center
                    obstacle_center_x = (cell_x + 0.5) * self.map_data.cell_size
                    obstacle_center_y = (cell_y + 0.5) * self.map_data.cell_size
                    
                    distance = math.sqrt((x - obstacle_center_x) ** 2 + 
                                       (y - obstacle_center_y) ** 2)
                    
                    # Required clearance: tank radius + buffer distance
                    required_clearance = (tank_size / 2) + (min_distance_from_obstacles * self.map_data.cell_size)
                    
                    if distance < required_clearance:
                        return True
                        
        return False
        
    def _has_maneuvering_space(self, x, y, tank_size):
        """
        Check if there's enough maneuvering space around the spawn location.
        
        Args:
            x (float): X-coordinate in pixels
            y (float): Y-coordinate in pixels
            tank_size (int): Size of the tank in pixels
            
        Returns:
            bool: True if there's enough maneuvering space, False otherwise
        """
        # Check if the tank can move in at least 2 directions from this position
        directions = [
            (0, -tank_size),   # Up
            (tank_size, 0),    # Right
            (0, tank_size),    # Down
            (-tank_size, 0)    # Left
        ]
        
        clear_directions = 0
        
        for dx, dy in directions:
            test_x = x + dx
            test_y = y + dy
            
            # Check if this direction is clear (no buffer distance for maneuvering check)
            if (self._is_within_bounds(test_x, test_y, tank_size) and
                not self._check_obstacle_collision(test_x, test_y, tank_size, 0)):
                clear_directions += 1
                
        # Require at least 2 clear directions for maneuvering
        return clear_directions >= 2
        
    def find_valid_spawn_location_with_distance(self, tank_size=32, max_attempts=50, 
                                              min_distance_from_obstacles=1,
                                              min_distance_from_point=None, 
                                              min_point_distance=0):
        """
        Find a valid spawn location with additional distance constraints.
        
        Args:
            tank_size (int): Size of the tank in pixels
            max_attempts (int): Maximum number of attempts to find a valid location
            min_distance_from_obstacles (int): Minimum distance from obstacles in cells
            min_distance_from_point (tuple): (x, y) point to maintain distance from
            min_point_distance (float): Minimum distance from the specified point in pixels
            
        Returns:
            tuple: (x, y) pixel coordinates if found, None otherwise
        """
        for attempt in range(max_attempts):
            # Find a basic valid location first
            location = self.find_valid_spawn_location(tank_size, 1, min_distance_from_obstacles)
            
            if location is None:
                continue
                
            x, y = location
            
            # Check distance constraint if specified
            if min_distance_from_point is not None:
                point_x, point_y = min_distance_from_point
                distance = math.sqrt((x - point_x) ** 2 + (y - point_y) ** 2)
                
                if distance >= min_point_distance:
                    return location
            else:
                return location
                
        return None
        
    def validate_existing_spawn(self, x, y, tank_size=32):
        """
        Validate an existing spawn location.
        
        Args:
            x (float): X-coordinate in pixels
            y (float): Y-coordinate in pixels
            tank_size (int): Size of the tank in pixels
            
        Returns:
            dict: Validation result with 'valid' boolean and 'issues' list
        """
        result = {
            'valid': True,
            'issues': []
        }
        
        # Check bounds
        if not self._is_within_bounds(x, y, tank_size):
            result['valid'] = False
            result['issues'].append('spawn_out_of_bounds')
            
        # Check obstacle collision
        if self._check_obstacle_collision(x, y, tank_size, 1):
            result['valid'] = False
            result['issues'].append('spawn_in_obstacle')
            
        # Check maneuvering space
        if not self._has_maneuvering_space(x, y, tank_size):
            result['valid'] = False
            result['issues'].append('insufficient_maneuvering_space')
            
        return result