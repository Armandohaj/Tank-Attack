"""
Map Generator module for the Tank Game.
This module defines the MapGenerator class that generates open playing fields with obstacles.
"""
import random
from src.level_manager.map_data import MapData


class MapGenerator:
    """
    Generates open playing fields with strategically placed obstacles for the game.
    """
    def __init__(self, width, height):
        """
        Initialize the map generator.
        
        Args:
            width (int): Width of the map in cells
            height (int): Height of the map in cells
        """
        self.width = width
        self.height = height
        
    def generate_map(self, difficulty=1):
        """
        Generate an open playing field with strategically placed obstacles.
        
        Args:
            difficulty (int): Difficulty level affecting obstacle density and placement
            
        Returns:
            MapData: The generated map
        """
        map_data = MapData(self.width, self.height)
        
        # Start with all empty cells
        for y in range(self.height):
            for x in range(self.width):
                map_data.set_cell(x, y, MapData.EMPTY)
        
        # Add walls around the edges to create boundaries
        self._add_boundary_walls(map_data)
        
        # Add strategic obstacles
        self._add_strategic_obstacles(map_data, difficulty)
        
        # Add destructible elements
        self._add_destructible_elements(map_data, difficulty)
        
        return map_data
    
    def _add_boundary_walls(self, map_data):
        """
        Add walls around the edges of the map to create boundaries.
        
        Args:
            map_data (MapData): The map to add boundary walls to
        """
        for x in range(self.width):
            map_data.set_cell(x, 0, MapData.WALL)
            map_data.set_cell(x, self.height - 1, MapData.WALL)
        
        for y in range(self.height):
            map_data.set_cell(0, y, MapData.WALL)
            map_data.set_cell(self.width - 1, y, MapData.WALL)
    
    def _add_strategic_obstacles(self, map_data, difficulty):
        """
        Add strategic obstacles to the map.
        
        Args:
            map_data (MapData): The map to add obstacles to
            difficulty (int): Difficulty level affecting obstacle density
        """
        # Calculate the number of obstacle clusters based on map size and difficulty
        map_area = self.width * self.height
        num_obstacle_clusters = int(map_area * 0.01 * difficulty)
        
        # Create obstacle clusters
        for _ in range(num_obstacle_clusters):
            # Choose a random position for the obstacle cluster
            center_x = random.randint(3, self.width - 4)
            center_y = random.randint(3, self.height - 4)
            
            # Determine cluster size (smaller at higher difficulties for more tactical gameplay)
            cluster_size = random.randint(1, 3)
            
            # Create different obstacle patterns
            pattern_type = random.randint(0, 3)
            
            if pattern_type == 0:
                # Single obstacle or small cluster
                for dy in range(-cluster_size // 2, cluster_size // 2 + 1):
                    for dx in range(-cluster_size // 2, cluster_size // 2 + 1):
                        if random.random() < 0.7:  # 70% chance to place an obstacle in the cluster
                            x, y = center_x + dx, center_y + dy
                            if self._is_valid_obstacle_position(map_data, x, y):
                                map_data.set_cell(x, y, MapData.WALL)
            
            elif pattern_type == 1:
                # Line obstacle
                direction = random.choice([(0, 1), (1, 0), (1, 1), (-1, 1)])
                dx, dy = direction
                line_length = random.randint(2, 4)
                
                for i in range(line_length):
                    x, y = center_x + dx * i, center_y + dy * i
                    if self._is_valid_obstacle_position(map_data, x, y):
                        map_data.set_cell(x, y, MapData.WALL)
            
            elif pattern_type == 2:
                # L-shaped obstacle
                for i in range(3):
                    x, y = center_x + i, center_y
                    if self._is_valid_obstacle_position(map_data, x, y):
                        map_data.set_cell(x, y, MapData.WALL)
                
                for i in range(1, 3):
                    x, y = center_x, center_y + i
                    if self._is_valid_obstacle_position(map_data, x, y):
                        map_data.set_cell(x, y, MapData.WALL)
            
            else:
                # U-shaped obstacle
                for i in range(3):
                    x, y = center_x + i, center_y
                    if self._is_valid_obstacle_position(map_data, x, y):
                        map_data.set_cell(x, y, MapData.WALL)
                
                for i in range(1, 3):
                    x, y = center_x, center_y + i
                    if self._is_valid_obstacle_position(map_data, x, y):
                        map_data.set_cell(x, y, MapData.WALL)
                
                for i in range(1, 3):
                    x, y = center_x + 2, center_y + i
                    if self._is_valid_obstacle_position(map_data, x, y):
                        map_data.set_cell(x, y, MapData.WALL)
    
    def _is_valid_obstacle_position(self, map_data, x, y):
        """
        Check if a position is valid for placing an obstacle.
        
        Args:
            map_data (MapData): The map data
            x (int): X-coordinate
            y (int): Y-coordinate
            
        Returns:
            bool: True if the position is valid for an obstacle, False otherwise
        """
        # Check if the position is within bounds and not too close to the edge
        if x <= 1 or x >= self.width - 2 or y <= 1 or y >= self.height - 2:
            return False
        
        # Check if the position is empty
        if map_data.get_cell(x, y) != MapData.EMPTY:
            return False
        
        # Ensure there's enough space around for tank movement
        # Check if there are at least 2 empty cells in each cardinal direction
        empty_directions = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if (0 <= x + dx < self.width and 0 <= y + dy < self.height and 
                map_data.get_cell(x + dx, y + dy) == MapData.EMPTY):
                empty_directions += 1
        
        return empty_directions >= 2
                        
    def _add_destructible_elements(self, map_data, difficulty):
        """
        Add destructible elements to the map.
        
        Args:
            map_data (MapData): The map to add destructible elements to
            difficulty (int): Difficulty level affecting the number of destructible elements
        """
        # Number of destructible elements based on map size and difficulty
        map_area = self.width * self.height
        num_rock_piles = int(map_area * 0.02 * difficulty)
        num_petrol_barrels = int(map_area * 0.01 * difficulty)
        
        # Get all empty cells
        empty_cells = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if map_data.get_cell(x, y) == MapData.EMPTY:
                    empty_cells.append((x, y))
        
        # Shuffle the empty cells
        random.shuffle(empty_cells)
        
        # Add rock piles
        for i in range(min(num_rock_piles, len(empty_cells))):
            if i < len(empty_cells):
                x, y = empty_cells[i]
                map_data.set_cell(x, y, MapData.ROCK_PILE)
        
        # Add petrol barrels
        for i in range(min(num_petrol_barrels, len(empty_cells) - num_rock_piles)):
            if num_rock_piles + i < len(empty_cells):
                x, y = empty_cells[num_rock_piles + i]
                map_data.set_cell(x, y, MapData.PETROL_BARREL)
            
    def generate_simple_map(self, difficulty=1):
        """
        Generate a simple open field map with basic obstacles.
        This is a simpler alternative to the strategic obstacle placement.
        
        Args:
            difficulty (int): Difficulty level affecting obstacle density
            
        Returns:
            MapData: The generated map
        """
        map_data = MapData(self.width, self.height)
        
        # Start with all empty
        for y in range(self.height):
            for x in range(self.width):
                map_data.set_cell(x, y, MapData.EMPTY)
        
        # Add walls around the edges
        self._add_boundary_walls(map_data)
        
        # Add some random obstacles inside
        num_obstacles = int((self.width * self.height) * 0.05 * difficulty)
        for _ in range(num_obstacles):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if map_data.get_cell(x, y) == MapData.EMPTY:
                map_data.set_cell(x, y, MapData.WALL)
        
        # Add some rock piles
        num_rock_piles = int((self.width * self.height) * 0.04 * difficulty)
        for _ in range(num_rock_piles):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if map_data.get_cell(x, y) == MapData.EMPTY:
                map_data.set_cell(x, y, MapData.ROCK_PILE)
        
        # Add some petrol barrels
        num_petrol_barrels = int((self.width * self.height) * 0.02 * difficulty)
        for _ in range(num_petrol_barrels):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if map_data.get_cell(x, y) == MapData.EMPTY:
                map_data.set_cell(x, y, MapData.PETROL_BARREL)
        
        return map_data