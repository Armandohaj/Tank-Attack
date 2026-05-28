"""
Input Handler module for the Tank Game.
This module processes keyboard/mouse events and translates them to game actions.
"""

import pygame


class InputHandler:
    """
    Handles input from the user.
    """

    def __init__(self):
        """Initialize the input handler."""
        self.key_states = {}
        self.previous_key_states = {}

    def process_events(self):
        """
        Process keyboard/mouse events.
        Should be called once per frame.
        """
        self.previous_key_states = self.key_states.copy()

        keys = pygame.key.get_pressed()

        self.key_states = {
            "up": keys[pygame.K_UP] or keys[pygame.K_w],
            "down": keys[pygame.K_DOWN] or keys[pygame.K_s],
            "left": keys[pygame.K_LEFT] or keys[pygame.K_a],
            "right": keys[pygame.K_RIGHT] or keys[pygame.K_d],
            "fire": keys[pygame.K_SPACE],
            "escape": keys[pygame.K_ESCAPE],
            "enter": keys[pygame.K_RETURN],
            "restart": keys[pygame.K_r]
        }

    def is_key_pressed(self, key):
        """
        Check if a key is currently pressed.
        """
        return self.key_states.get(key, False)

    def is_key_just_pressed(self, key):
        """
        Check if a key was just pressed this frame.
        """
        return (
            self.key_states.get(key, False)
            and not self.previous_key_states.get(key, False)
        )

    def get_movement_direction(self):
        """
        Return the current movement direction.

        Returns:
            str or None: up, down, left, right or None.
        """
        if self.is_key_pressed("up"):
            return "up"

        if self.is_key_pressed("down"):
            return "down"

        if self.is_key_pressed("left"):
            return "left"

        if self.is_key_pressed("right"):
            return "right"

        return None

    def is_fire_pressed(self):
        """
        Check if the fire key is pressed.
        """
        return self.is_key_pressed("fire")

    def is_escape_pressed(self):
        """
        Check if ESC is pressed.
        """
        return self.is_key_pressed("escape")

    def is_enter_just_pressed(self):
        """
        Check if ENTER was just pressed.
        """
        return self.is_key_just_pressed("enter")

    def is_restart_just_pressed(self):
        """
        Check if R was just pressed.
        """
        return self.is_key_just_pressed("restart")