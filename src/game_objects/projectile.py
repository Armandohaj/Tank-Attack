"""
Projectile module for the Tank Game.
This module defines the Projectile class that represents a projectile fired by a tank.
"""

import math
from src.engine.game_object import GameObject


class Projectile(GameObject):
    """
    Represents a projectile fired by a tank.
    """

    def __init__(self, x, y, direction, speed=10, damage=20, owner=None):
        """
        Initialize a projectile.

        Args:
            x (float): X-coordinate position
            y (float): Y-coordinate position
            direction (float): Direction in degrees (0 = up, 90 = right, 180 = down, 270 = left)
            speed (float): Movement speed of the projectile
            damage (int): Damage the projectile deals on impact
            owner: The game object that fired the projectile
        """
        super().__init__(x, y)
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.tag = "projectile"
        self.lifetime = 3.0  # Projectile lifetime in seconds
        self.time_alive = 0.0

    def update(self, delta_time, map_data):
        """
        Update the projectile state.

        Args:
            delta_time (float): Time elapsed since the last update in seconds
            map_data (MapData): The map data for collision detection

        Returns:
            bool: True if the projectile is still active, False if it should be removed
        """
        # This method is now simplified since the main game loop handles movement and collision detection
        # We just need to check if the projectile is still active
        return self.active

    def _check_collision(self, new_x, new_y, map_data):
        """
        Check if the projectile would collide with an obstacle at the given position.

        Args:
            new_x (float): New X-coordinate to check
            new_y (float): New Y-coordinate to check
            map_data (MapData): The map data for collision detection

        Returns:
            tuple: (bool, hit_object) where bool is True if there would be a collision,
                  and hit_object is the object that was hit (or None if no collision)
        """
        # Convert pixel coordinates to cell coordinates
        cell_size = map_data.cell_size
        cell_x = int((new_x + self.width / 2) // cell_size)
        cell_y = int((new_y + self.height / 2) // cell_size)

        # Check if the cell contains an obstacle
        if map_data.is_obstacle_at(cell_x, cell_y):
            # Check if it's a destructible element
            if map_data.is_destructible_at(cell_x, cell_y):
                # Add debugging output
                cell_type = map_data.get_cell(cell_x, cell_y)
                print(f"Projectile collision with destructible element at ({cell_x}, {cell_y}), cell type: {cell_type}")
                
                # Return the cell coordinates for the destructible element
                return True, (cell_x, cell_y)
            else:
                # Wall collision
                print(f"Projectile collision with wall at ({cell_x}, {cell_y})")
                return True, None

        # No collision
        return False, None

    def handle_collision(self, hit_object, game_objects, map_data):
        """
        Handle collision with another game object or map element.

        Args:
            hit_object: The object that was hit or cell coordinates for map element
            game_objects: List of all game objects
            map_data: The map data

        Returns:
            bool: True if the projectile should be removed, False otherwise
        """
        # If hit_object is a tuple, it's a destructible element in the map
        if isinstance(hit_object, tuple):
            cell_x, cell_y = hit_object
            cell_type = map_data.get_cell(cell_x, cell_y)
            print(f"Handling collision with cell type {cell_type} at ({cell_x}, {cell_y})")

            # Find the destructible element at this position
            for obj in game_objects:
                # Check for both "destructible" tag and specific destructible element tags
                if obj.tag in ["destructible", "rock_pile", "petrol_barrel"] and obj.active:
                    obj_cell_x = int((obj.x + obj.width / 2) // map_data.cell_size)
                    obj_cell_y = int((obj.y + obj.height / 2) // map_data.cell_size)

                    if obj_cell_x == cell_x and obj_cell_y == cell_y:
                        print(f"Found destructible element {obj.tag} at ({obj_cell_x}, {obj_cell_y})")
                        
                        # Damage the destructible element
                        result = obj.take_damage(self.damage)
                        
                        # If it's a petrol barrel and it was destroyed, handle explosion
                        if obj.tag == "petrol_barrel" and isinstance(result, dict) and result.get('destroyed'):
                            print(f"Petrol barrel destroyed, explosion triggered")
                            # Explosion is handled by the collision detector
                        
                        # If the element was destroyed, update the map data
                        if (isinstance(result, bool) and result) or \
                           (isinstance(result, dict) and result.get('destroyed')):
                            print(f"Destructible element destroyed, updating map data")
                            map_data.set_cell(cell_x, cell_y, map_data.EMPTY)
                        
                        return True

            print(f"No destructible element found at ({cell_x}, {cell_y})")

        # If hit_object is a game object, damage it
        elif hit_object is not None and hit_object != self.owner:
            if hasattr(hit_object, "take_damage"):
                hit_object.take_damage(self.damage)
                return True

        # Default: remove the projectile
        return True

    def check_collision_with_object(self, other_object):
        """
        Check if this projectile collides with another game object.
        
        Args:
            other_object: The other game object to check collision with
            
        Returns:
            bool: True if there is a collision, False otherwise
        """
        if not other_object or not other_object.active or other_object == self.owner:
            return False
            
        # Simple rectangular collision detection
        proj_left = self.x
        proj_right = self.x + self.width
        proj_top = self.y
        proj_bottom = self.y + self.height
        
        obj_left = other_object.x
        obj_right = other_object.x + other_object.width
        obj_top = other_object.y
        obj_bottom = other_object.y + other_object.height
        
        # Check if rectangles overlap
        return (proj_left < obj_right and proj_right > obj_left and
                proj_top < obj_bottom and proj_bottom > obj_top)
