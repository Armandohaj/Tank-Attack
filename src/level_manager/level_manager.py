"""
Level Manager module for the Tank Game.
This module defines the LevelManager class that handles level progression and management.
"""

import pygame
import random
import math

from src.level_manager.map_generator import MapGenerator
from src.level_manager.enemy_tank_spawner import EnemyTankSpawner
from src.level_manager.difficulty_manager import DifficultyManager
from src.level_manager.level_transition import LevelTransition
from src.level_manager.spawn_validator import SpawnValidator


class LevelManager:
    """
    Manages game levels, progression, and difficulty scaling.
    """

    def __init__(self, game_engine, map_width=25, map_height=19, max_level=3):
        """
        Initialize the level manager.

        Args:
            game_engine (GameEngine): The game engine instance.
            map_width (int): Width of the map in cells.
            map_height (int): Height of the map in cells.
            max_level (int): Maximum level number.
        """

        self.game_engine = game_engine
        self.map_width = map_width
        self.map_height = map_height
        self.current_level = 1
        self.max_level = max_level

        self.map_generator = MapGenerator(map_width, map_height)
        self.map_data = None

        self.enemy_tanks = []
        self.player_tank = None

        self.level_complete = False
        self.game_complete = False
        self.score = 0

        self.difficulty_manager = DifficultyManager(max_difficulty=3)
        self.transition = LevelTransition(game_engine)

    def initialize(self, player_tank, level_number=1):
        """
        Initialize the level manager with a player tank.

        Args:
            player_tank: The player's tank.
            level_number (int): Level number to start.
        """

        self.player_tank = player_tank
        self.start_level(level_number)

    def start_level(self, level_number):
        """
        Start a new level.

        Args:
            level_number (int): The level number to start.

        Returns:
            bool: True if the level was started successfully, False otherwise.
        """

        if level_number < 1 or level_number > self.max_level:
            return False

        self.current_level = level_number
        self.game_engine.current_level = level_number

        self.level_complete = False

        map_difficulty = self.difficulty_manager.get_map_difficulty(level_number)
        self.map_data = self.map_generator.generate_map(map_difficulty)
        self.map_data.set_cell_size(32)

        # In this version, rocks and barrels are map obstacles.
        # They are not created as destructible GameObjects.
        self._create_destructible_elements()

        for tank in self.enemy_tanks:
            self.game_engine.remove_game_object(tank)

        self.enemy_tanks = []

        spawner = EnemyTankSpawner(self.map_data)

        player_position = (
            self.player_tank.x,
            self.player_tank.y
        )

        try:
            self.enemy_tanks = spawner.spawn_enemy_tanks(
                level_number,
                player_position,
                self.game_engine,
                self.difficulty_manager
            )

        except TypeError:
            self.enemy_tanks = spawner.spawn_enemy_tanks(
                level_number,
                player_position,
                self.game_engine
            )

        player_params = self.difficulty_manager.get_player_params(level_number)

        self.player_tank.health = player_params["health"]
        self.player_tank.max_health = player_params["health"]
        self.player_tank.speed = player_params["speed"]
        self.player_tank.fire_cooldown = player_params["fire_cooldown"]

        spawn_validator = SpawnValidator(self.map_data)

        player_spawn = spawn_validator.find_valid_spawn_location(
            tank_size=32,
            max_attempts=100,
            min_distance_from_obstacles=2
        )

        if player_spawn:
            self.player_tank.x, self.player_tank.y = player_spawn

        else:
            print("Warning: Could not find valid spawn location for player tank, using center")
            self.player_tank.x = self.map_data.width * self.map_data.cell_size / 2
            self.player_tank.y = self.map_data.height * self.map_data.cell_size / 2

        return True

    def update(self, delta_time):
        """
        Update the level manager.

        Args:
            delta_time (float): Time elapsed since the last update in seconds.

        Returns:
            bool: True if the game is still running, False otherwise.
        """

        if self.transition.active:
            transition_complete = self.transition.update(delta_time)

            if transition_complete:
                if self.game_complete:
                    return False

                self.start_level(self.current_level + 1)

            return True

        for tank in self.enemy_tanks[:]:
            if tank is None or not tank.active:
                if tank is not None:
                    self.game_engine.remove_game_object(tank)

                    if hasattr(tank, "difficulty"):
                        score_multiplier = self.difficulty_manager.get_score_multiplier(
                            self.current_level,
                            tank.difficulty
                        )

                        self.score += score_multiplier

                self.enemy_tanks.remove(tank)

        active_enemy_count = len([
            tank for tank in self.enemy_tanks
            if tank is not None and tank.active
        ])

        if active_enemy_count == 0:
            self.level_complete = True

            if self.current_level >= self.max_level:
                self.game_complete = True

            self.transition.start(
                self.current_level,
                self.score,
                self.game_complete
            )

        return True

    def render_transition(self, screen):
        """
        Render the level transition on the screen.

        Args:
            screen: The pygame screen to render on.
        """

        self.transition.render(screen)

    def is_level_complete(self):
        """
        Check if the current level is complete.

        Returns:
            bool: True if the level is complete, False otherwise.
        """

        return self.level_complete

    def is_game_complete(self):
        """
        Check if the game is complete.

        Returns:
            bool: True if the game is complete, False otherwise.
        """

        return self.game_complete

    def get_current_level(self):
        """
        Get the current level number.

        Returns:
            int: The current level number.
        """

        return self.current_level

    def get_max_level(self):
        """
        Get the maximum level number.

        Returns:
            int: The maximum level number.
        """

        return self.max_level

    def get_score(self):
        """
        Get the current score.

        Returns:
            int: The current score.
        """

        return self.score

    def add_score(self, points):
        """
        Add points to the score.

        Args:
            points (int): The number of points to add.
        """

        self.score += points

    def _create_destructible_elements(self):
        """
        In this version, rock piles and petrol barrels are handled as map obstacles.

        They are not created as destructible game objects because the project
        will treat them like indestructible map obstacles.
        """

        return

    def reset(self):
        """
        Reset the level manager to its initial state.
        """

        self.current_level = 1
        self.level_complete = False
        self.game_complete = False
        self.score = 0

        if self.player_tank:
            self.start_level(1)

    def spawn_enemy_tank(self, difficulty=None):
        """
        Spawn a single enemy tank.

        Args:
            difficulty (int, optional): Difficulty level of the tank.

        Returns:
            EnemyTank: The spawned enemy tank, or None if no valid position was found.
        """

        if self.map_data is None:
            return None

        if difficulty is None:
            difficulty = self.difficulty_manager.get_map_difficulty(
                self.current_level
            )

        spawner = EnemyTankSpawner(self.map_data)

        player_position = (
            self.player_tank.x,
            self.player_tank.y
        )

        enemy_tank = spawner.spawn_single_enemy_tank(
            difficulty,
            player_position,
            self.game_engine
        )

        if enemy_tank:
            self.enemy_tanks.append(enemy_tank)

        return enemy_tank