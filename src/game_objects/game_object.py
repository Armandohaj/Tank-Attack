"""
GameObject base class for the Tank Game.

This module defines the base GameObject class that all game entities inherit from.
It provides common functionality such as position, size, active state, sprite,
rotation, updating and rendering.
"""

import pygame


class GameObject:
    """
    Base class for all game objects.

    All game entities such as tanks, walls, projectiles and objectives
    inherit from this class.
    """

    def __init__(self, x=0, y=0):
        """
        Initialize a new GameObject.

        Args:
            x (float): Initial x-coordinate position.
            y (float): Initial y-coordinate position.
        """
        self.x = x
        self.y = y

        self.width = 32
        self.height = 32

        self.sprite = None
        self.original_sprite = None

        self.rotation = 0
        self.active = True

        self.tag = "game_object"

    def update(self, delta_time, *args, **kwargs):
        """
        Update the game object's state.

        This method can be overridden by subclasses.

        Args:
            delta_time (float): Time elapsed since the last update.
        """
        pass

    def render(self, screen):
        """
        Render the game object to the screen.

        Args:
            screen: Pygame surface to render on.
        """
        if not self.active:
            return

        if self.sprite:
            screen.blit(self.sprite, (self.x, self.y))
        else:
            # Fallback drawing if no sprite exists
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                pygame.Rect(self.x, self.y, self.width, self.height),
                1
            )

    def set_position(self, x, y):
        """
        Set the position of the game object.

        Args:
            x (float): New x-coordinate position.
            y (float): New y-coordinate position.
        """
        self.x = x
        self.y = y

    def get_position(self):
        """
        Get the current position of the game object.

        Returns:
            tuple: (x, y)
        """
        return self.x, self.y

    def set_sprite(self, sprite):
        """
        Set the sprite of the game object.

        Args:
            sprite: Pygame surface used as sprite.
        """
        self.original_sprite = sprite
        self.sprite = sprite

        if sprite:
            self.width = sprite.get_width()
            self.height = sprite.get_height()

    def set_rotation(self, rotation):
        """
        Set the visual rotation of the game object.

        Args:
            rotation (float): Rotation angle in degrees.
        """
        self.rotation = rotation

        if self.original_sprite:
            center = self.original_sprite.get_rect(
                topleft=(self.x, self.y)
            ).center

            rotated_sprite = pygame.transform.rotate(
                self.original_sprite,
                self.rotation
            )

            rotated_rect = rotated_sprite.get_rect(center=center)

            self.sprite = rotated_sprite
            self.x = rotated_rect.x
            self.y = rotated_rect.y
            self.width = rotated_rect.width
            self.height = rotated_rect.height

    def get_rect(self):
        """
        Get the rectangular area of the object.

        Returns:
            pygame.Rect: Rectangle representing the object.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def check_collision_with_object(self, other_object):
        """
        Check collision with another game object.

        Args:
            other_object: Another GameObject.

        Returns:
            bool: True if both objects collide.
        """
        if not other_object:
            return False

        if not self.active or not other_object.active:
            return False

        return self.get_rect().colliderect(other_object.get_rect())

    def destroy(self):
        """
        Deactivate the object.
        """
        self.active = False