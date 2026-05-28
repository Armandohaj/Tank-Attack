"""
Tank module for the Tank Game.
This module defines the Tank base class that represents a tank in the game.

This version is adapted for the Tank-Attack project:
- Tanks only move in four basic directions.
- Projectiles also move in four basic directions.
- This class can be inherited by PlayerTank and different enemy tank types.
"""

from src.engine.game_object import GameObject
from src.game_objects.projectile import Projectile


class Tank(GameObject):
    """
    Base class for all tanks in the game.

    This class contains the common behavior of every tank:
    movement, direction, health, shooting, damage and collision detection.
    """

    # Cardinal directions used by the project
    UP = 0
    RIGHT = 90
    DOWN = 180
    LEFT = 270

    VALID_DIRECTIONS = [UP, RIGHT, DOWN, LEFT]

    def __init__(self, x, y, health=100, speed=5, damage=20, fire_cooldown=0.5):
        """
        Initialize a tank.

        Args:
            x (float): X-coordinate position.
            y (float): Y-coordinate position.
            health (int): Initial health of the tank.
            speed (float): Movement speed of the tank.
            damage (int): Damage caused by the tank projectiles.
            fire_cooldown (float): Time between shots.
        """
        super().__init__(x, y)

        # Default tank dimensions
        self.width = 32
        self.height = 32

        self.collision_width = 24
        self.collision_height = 24
        self.collision_offset_x = (self.width - self.collision_width) / 2
        self.collision_offset_y = (self.height - self.collision_height) / 2

        # Tank state
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage

        # Direction:
        # 0 = up, 90 = right, 180 = down, 270 = left
        self.direction = Tank.UP

        # Collision
        self.collision_radius = 16
        self.tag = "tank"

        # Shooting
        self.fire_cooldown = fire_cooldown
        self.last_fire_time = fire_cooldown

        # Sound-related attributes
        self.sound_manager = None
        self.movement_sound_channel = None
        self.is_moving = False

    def update(self, delta_time, map_data=None):
        """
        Update the tank state.

        Args:
            delta_time (float): Time elapsed since the last update.
            map_data: The map data for collision detection.
        """
        self.last_fire_time += delta_time
        self._update_movement_sound()

    # ---------------------------------------------------------
    # Direction methods
    # ---------------------------------------------------------

    def set_direction(self, direction):
        """
        Set the tank direction only if it is one of the four valid directions.

        Args:
            direction (int): Direction in degrees. Must be 0, 90, 180 or 270.
        """
        if direction in Tank.VALID_DIRECTIONS:
            self.direction = direction
            self.set_rotation(-self.direction)

    def rotate_left(self, delta_time=None):
        """
        Rotate the tank 90 degrees to the left.

        delta_time is optional to keep compatibility with previous code.
        """
        if self.direction == Tank.UP:
            self.set_direction(Tank.LEFT)
        elif self.direction == Tank.LEFT:
            self.set_direction(Tank.DOWN)
        elif self.direction == Tank.DOWN:
            self.set_direction(Tank.RIGHT)
        elif self.direction == Tank.RIGHT:
            self.set_direction(Tank.UP)

    def rotate_right(self, delta_time=None):
        """
        Rotate the tank 90 degrees to the right.

        delta_time is optional to keep compatibility with previous code.
        """
        if self.direction == Tank.UP:
            self.set_direction(Tank.RIGHT)
        elif self.direction == Tank.RIGHT:
            self.set_direction(Tank.DOWN)
        elif self.direction == Tank.DOWN:
            self.set_direction(Tank.LEFT)
        elif self.direction == Tank.LEFT:
            self.set_direction(Tank.UP)

    # ---------------------------------------------------------
    # Movement methods
    # ---------------------------------------------------------

    def move_up(self, delta_time, map_data):
        """
        Move the tank up.
        """
        self.set_direction(Tank.UP)
        return self.move_forward(delta_time, map_data)

    def move_right(self, delta_time, map_data):
        """
        Move the tank right.
        """
        self.set_direction(Tank.RIGHT)
        return self.move_forward(delta_time, map_data)

    def move_down(self, delta_time, map_data):
        """
        Move the tank down.
        """
        self.set_direction(Tank.DOWN)
        return self.move_forward(delta_time, map_data)

    def move_left(self, delta_time, map_data):
        """
        Move the tank left.
        """
        self.set_direction(Tank.LEFT)
        return self.move_forward(delta_time, map_data)

    def move_forward(self, delta_time, map_data):
        """
        Move the tank forward in its current direction.

        Args:
            delta_time (float): Time elapsed since the last update.
            map_data: The map data for collision detection.

        Returns:
            bool: True if the movement was successful, False otherwise.
        """
        dx, dy = self._get_direction_vector()

        movement_x = dx * self.speed * delta_time * 60
        movement_y = dy * self.speed * delta_time * 60

        new_x = self.x + movement_x
        new_y = self.y + movement_y

        if self._check_collision(new_x, new_y, map_data):
            self.is_moving = False
            return False

        self.x = new_x
        self.y = new_y
        self.is_moving = True
        return True

    def move_backward(self, delta_time, map_data):
        """
        Move the tank backward, opposite to its current direction.

        Args:
            delta_time (float): Time elapsed since the last update.
            map_data: The map data for collision detection.

        Returns:
            bool: True if the movement was successful, False otherwise.
        """
        dx, dy = self._get_direction_vector()

        movement_x = -dx * self.speed * 0.5 * delta_time * 60
        movement_y = -dy * self.speed * 0.5 * delta_time * 60

        new_x = self.x + movement_x
        new_y = self.y + movement_y

        if self._check_collision(new_x, new_y, map_data):
            self.is_moving = False
            return False

        self.x = new_x
        self.y = new_y
        self.is_moving = True
        return True

    def stop_movement(self):
        """
        Mark the tank as not moving.
        Useful when no movement key is being pressed.
        """
        self.is_moving = False

    def _get_direction_vector(self):
        """
        Return the movement vector according to the current direction.

        Returns:
            tuple: (dx, dy)
        """
        if self.direction == Tank.UP:
            return 0, -1
        elif self.direction == Tank.RIGHT:
            return 1, 0
        elif self.direction == Tank.DOWN:
            return 0, 1
        elif self.direction == Tank.LEFT:
            return -1, 0

        return 0, 0

    # ---------------------------------------------------------
    # Shooting methods
    # ---------------------------------------------------------

    def fire(self):
        """
        Fire a projectile from the tank.

        Returns:
            Projectile: The fired projectile, or None if the tank cannot fire.
        """
        if self.last_fire_time < self.fire_cooldown:
            return None

        self.last_fire_time = 0

        dx, dy = self._get_direction_vector()

        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        barrel_length = self.width / 2 + 5

        projectile_center_x = center_x + dx * barrel_length
        projectile_center_y = center_y + dy * barrel_length

        projectile_x = projectile_center_x - 4
        projectile_y = projectile_center_y - 4

        self._play_fire_sound()

        return Projectile(
            projectile_x,
            projectile_y,
            self.direction,
            speed=10,
            damage=self.damage,
            owner=self
        )

    # ---------------------------------------------------------
    # Damage methods
    # ---------------------------------------------------------

    def take_damage(self, amount):
        """
        Reduce the health of the tank.

        Args:
            amount (int): Amount of damage.

        Returns:
            bool: True if the tank was destroyed, False otherwise.
        """
        self.health -= amount

        if self.health <= 0:
            self.health = 0
            self.active = False
            self._stop_movement_sound()
            return True

        return False

    def is_destroyed(self):
        """
        Check if the tank is destroyed.

        Returns:
            bool: True if health is 0 or the tank is inactive.
        """
        return self.health <= 0 or not self.active

    # ---------------------------------------------------------
    # Collision methods
    # ---------------------------------------------------------

    def _check_collision(self, new_x, new_y, map_data):
        """
        Check if the tank would collide with an obstacle.

        This method uses a smaller collision hitbox than the visual sprite.
        That allows the tank to move through one-cell corridors more naturally.

        Args:
            new_x (float): New X-coordinate.
            new_y (float): New Y-coordinate.
            map_data: The map data for collision detection.

        Returns:
            bool: True if there would be a collision, False otherwise.
        """

        if map_data is None:
            return False

        cell_size = map_data.cell_size

        hitbox_left = new_x + self.collision_offset_x
        hitbox_top = new_y + self.collision_offset_y
        hitbox_right = hitbox_left + self.collision_width
        hitbox_bottom = hitbox_top + self.collision_height

        # A small margin avoids touching adjacent wall cells too aggressively.
        margin = 2

        points_to_check = [
            (hitbox_left + margin, hitbox_top + margin),
            (hitbox_right - margin, hitbox_top + margin),
            (hitbox_left + margin, hitbox_bottom - margin),
            (hitbox_right - margin, hitbox_bottom - margin),
            (
                hitbox_left + self.collision_width / 2,
                hitbox_top + self.collision_height / 2
            )
        ]

        for check_x, check_y in points_to_check:
            cell_x = int(check_x // cell_size)
            cell_y = int(check_y // cell_size)

            if cell_x < 0 or cell_y < 0:
                return True

            if cell_x >= map_data.width or cell_y >= map_data.height:
                return True

            if map_data.is_obstacle_at(cell_x, cell_y):
                return True

        return False

    def check_collision_with_object(self, other_object):
        """
        Check if this tank collides with another game object.

        Args:
            other_object: The other game object.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        if not other_object or not other_object.active:
            return False

        tank_left = self.x
        tank_right = self.x + self.width
        tank_top = self.y
        tank_bottom = self.y + self.height

        obj_left = other_object.x
        obj_right = other_object.x + other_object.width
        obj_top = other_object.y
        obj_bottom = other_object.y + other_object.height

        return (
            tank_left < obj_right and
            tank_right > obj_left and
            tank_top < obj_bottom and
            tank_bottom > obj_top
        )

    # ---------------------------------------------------------
    # Sound methods
    # ---------------------------------------------------------

    def set_sound_manager(self, sound_manager):
        """
        Set the sound manager for this tank.
        """
        self.sound_manager = sound_manager

    def _play_movement_sound(self):
        """
        Play the tank movement sound if available.
        """
        if (
            self.sound_manager and
            self.sound_manager.is_sound_enabled() and
            (
                not self.movement_sound_channel or
                not self.movement_sound_channel.get_busy()
            )
        ):
            self.movement_sound_channel = self.sound_manager.play_sound(
                "tank_move",
                loops=-1
            )

    def _stop_movement_sound(self):
        """
        Stop the tank movement sound.
        """
        if self.movement_sound_channel and self.movement_sound_channel.get_busy():
            self.movement_sound_channel.stop()
            self.movement_sound_channel = None

    def _update_movement_sound(self):
        """
        Update the movement sound based on current movement state.
        """
        if self.is_moving:
            self._play_movement_sound()
        else:
            self._stop_movement_sound()

    def _play_fire_sound(self):
        """
        Play the tank firing sound if available.
        """
        if self.sound_manager and self.sound_manager.is_sound_enabled():
            self.sound_manager.play_sound("tank_fire")