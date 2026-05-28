"""
Player Tank module for the Tank Game.
This module defines the PlayerTank class that represents the player-controlled tank.
"""

from src.game_objects.tank import Tank


class PlayerTank(Tank):
    """
    Represents the player-controlled tank.
    """

    def __init__(self, x, y, health=100, speed=5):
        """
        Initialize a player tank.

        Args:
            x (float): X-coordinate position.
            y (float): Y-coordinate position.
            health (int): Initial health of the tank.
            speed (float): Movement speed of the tank.
        """
        super().__init__(x, y, health, speed)
        self.tag = "player"

    def update(self, delta_time, map_data, input_handler):
        """
        Update the player tank state based on input.

        Args:
            delta_time (float): Time elapsed since the last update.
            map_data (MapData): The map data for collision detection.
            input_handler: The input handler for processing player input.

        Returns:
            Projectile: The fired projectile, or None if no projectile was fired.
        """
        super().update(delta_time, map_data)

        self._handle_movement(delta_time, map_data, input_handler)

        return self._handle_firing(input_handler)

    def _handle_movement(self, delta_time, map_data, input_handler):
        """
        Handle movement input for the player tank.

        The player moves directly in the four basic directions:
        up, down, left and right.
        """

        moved = False

        if input_handler.is_key_pressed("up"):
            moved = self.move_up(delta_time, map_data)

        elif input_handler.is_key_pressed("down"):
            moved = self.move_down(delta_time, map_data)

        elif input_handler.is_key_pressed("left"):
            moved = self.move_left(delta_time, map_data)

        elif input_handler.is_key_pressed("right"):
            moved = self.move_right(delta_time, map_data)

        else:
            self.stop_movement()

        self.is_moving = moved

    def _handle_firing(self, input_handler):
        """
        Handle firing input for the player tank.

        Returns:
            Projectile: The fired projectile, or None if no projectile was fired.
        """
        if input_handler.is_key_pressed("fire"):
            return self.fire()

        return None