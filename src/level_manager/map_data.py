"""
Map Data module for the Tank Game.
This module defines the MapData class that represents the game map.
"""


class MapData:
    """
    Represents the game map data structure.
    """
    # Map cell types
    EMPTY = 0
    WALL = 1  # Indestructible wall
    ROCK_PILE = 2  # Destructible rock pile
    PETROL_BARREL = 3  # Explosive petrol barrel
    
    def __init__(self, width, height):
        """
        Initialize a map data structure.
        
        Args:
            width (int): Width of the map in cells
            height (int): Height of the map in cells
        """
        self.width = width
        self.height = height
        self.grid = [[self.EMPTY for _ in range(width)] for _ in range(height)]
        self.cell_size = 32  # Default cell size in pixels
        
    def set_cell(self, x, y, cell_type):
        """
        Set the type of a cell in the map.
        
        Args:
            x (int): X-coordinate of the cell
            y (int): Y-coordinate of the cell
            cell_type (int): Type of the cell (EMPTY, WALL, ROCK_PILE, or PETROL_BARREL)
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = cell_type
            
    def get_cell(self, x, y):
        """
        Get the type of a cell in the map.
        
        Args:
            x (int): X-coordinate of the cell
            y (int): Y-coordinate of the cell
            
        Returns:
            int: Type of the cell (EMPTY, WALL, ROCK_PILE, or PETROL_BARREL)
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return self.WALL  # Out of bounds is treated as a wall/obstacle
        
    def is_wall_at(self, x, y):
        """
        Check if there's a wall at the given position.
        
        Args:
            x (int): X-coordinate of the cell
            y (int): Y-coordinate of the cell
            
        Returns:
            bool: True if there's a wall, False otherwise
        """
        return self.get_cell(x, y) == self.WALL
    
    def is_obstacle_at(self, x, y):
        """
        Check if there's any obstacle at the given position.
        
        Args:
            x (int): X-coordinate of the cell
            y (int): Y-coordinate of the cell
            
        Returns:
            bool: True if there's an obstacle, False otherwise
        """
        cell_type = self.get_cell(x, y)
        return cell_type != self.EMPTY
        
    def is_rock_pile_at(self, x, y):
        """
        Check if there's a rock pile at the given position.
        
        Args:
            x (int): X-coordinate of the cell
            y (int): Y-coordinate of the cell
            
        Returns:
            bool: True if there's a rock pile, False otherwise
        """
        return self.get_cell(x, y) == self.ROCK_PILE
        
    def is_petrol_barrel_at(self, x, y):
        """
        Check if there's a petrol barrel at the given position.
        
        Args:
            x (int): X-coordinate of the cell
            y (int): Y-coordinate of the cell
            
        Returns:
            bool: True if there's a petrol barrel, False otherwise
        """
        return self.get_cell(x, y) == self.PETROL_BARREL
        
    def is_destructible_at(self, x, y):
        """
        Check if there's a destructible element at the given position.
        
        Args:
            x (int): X-coordinate of the cell
            y (int): Y-coordinate of the cell
            
        Returns:
            bool: True if there's a destructible element, False otherwise
        """
        cell_type = self.get_cell(x, y)
        return cell_type == self.ROCK_PILE or cell_type == self.PETROL_BARREL
        
    def is_empty_at(self, x, y):
        """
        Check if the cell at the given position is empty.
        
        Args:
            x (int): X-coordinate of the cell
            y (int): Y-coordinate of the cell
            
        Returns:
            bool: True if the cell is empty, False otherwise
        """
        return self.get_cell(x, y) == self.EMPTY
        
    def set_cell_size(self, cell_size):
        """
        Set the size of each cell in pixels.
        
        Args:
            cell_size (int): Size of each cell in pixels
        """
        self.cell_size = cell_size
        
    def get_pixel_position(self, cell_x, cell_y):
        """
        Convert cell coordinates to pixel coordinates.
        
        Args:
            cell_x (int): X-coordinate of the cell
            cell_y (int): Y-coordinate of the cell
            
        Returns:
            tuple: (x, y) pixel coordinates of the top-left corner of the cell
        """
        return cell_x * self.cell_size, cell_y * self.cell_size
        
    def get_cell_from_pixel(self, pixel_x, pixel_y):
        """
        Convert pixel coordinates to cell coordinates.
        
        Args:
            pixel_x (int): X-coordinate in pixels
            pixel_y (int): Y-coordinate in pixels
            
        Returns:
            tuple: (x, y) cell coordinates
        """
        cell_x = pixel_x // self.cell_size
        cell_y = pixel_y // self.cell_size
        return cell_x, cell_y
        
    def clear(self):
        """Clear the map by setting all cells to EMPTY."""
        self.grid = [[self.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
    def count_empty_cells(self):
        """
        Count the number of empty cells in the map.
        
        Returns:
            int: Number of empty cells
        """
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.EMPTY:
                    count += 1
        return count
        
    def count_wall_cells(self):
        """
        Count the number of wall cells in the map.
        
        Returns:
            int: Number of wall cells
        """
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.WALL:
                    count += 1
        return count
    
    def count_obstacle_cells(self):
        """
        Count the number of obstacle cells in the map.
        
        Returns:
            int: Number of obstacle cells
        """
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != self.EMPTY:
                    count += 1
        return count
        
    def count_rock_pile_cells(self):
        """
        Count the number of rock pile cells in the map.
        
        Returns:
            int: Number of rock pile cells
        """
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.ROCK_PILE:
                    count += 1
        return count
        
    def count_petrol_barrel_cells(self):
        """
        Count the number of petrol barrel cells in the map.
        
        Returns:
            int: Number of petrol barrel cells
        """
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.PETROL_BARREL:
                    count += 1
        return count
        
    def count_destructible_cells(self):
        """
        Count the number of destructible cells in the map.
        
        Returns:
            int: Number of destructible cells
        """
        return self.count_rock_pile_cells() + self.count_petrol_barrel_cells()
        
    def count_cells(self, cell_type):
        """
        Count the number of cells of a specific type in the map.
        
        Args:
            cell_type (int): The type of cell to count (EMPTY, WALL, ROCK_PILE, or PETROL_BARREL)
            
        Returns:
            int: Number of cells of the specified type
        """
        if cell_type == self.EMPTY:
            return self.count_empty_cells()
        elif cell_type == self.WALL:
            return self.count_wall_cells()
        elif cell_type == self.ROCK_PILE:
            return self.count_rock_pile_cells()
        elif cell_type == self.PETROL_BARREL:
            return self.count_petrol_barrel_cells()
        else:
            return 0