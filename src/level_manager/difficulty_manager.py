"""
Difficulty Manager module for the Tank Game.

This module defines the DifficultyManager class.
It controls difficulty scaling for the 3 levels of Tank-Attack.
"""

import random


class DifficultyManager:
    """
    Manages difficulty scaling for the game.
    """

    def __init__(self, max_difficulty=3):
        """
        Initialize the difficulty manager.

        Args:
            max_difficulty (int): Maximum difficulty level.
        """
        self.max_difficulty = max_difficulty

    def get_map_difficulty(self, level):
        """
        Get the map difficulty for a given level.

        Args:
            level (int): Current level number.

        Returns:
            int: Map difficulty.
        """
        return min(max(1, level), self.max_difficulty)

    def get_num_enemy_tanks(self, level):
        """
        Get the number of enemy tanks for a given level.

        Each level has exactly three enemy tanks:
        one light, one heavy and one sniper.
        """

        return 3

    def get_enemy_tank_difficulties(self, level, num_tanks):
        """
        Get the difficulty levels for enemy tanks.

        Args:
            level (int): Current level number.
            num_tanks (int): Number of tanks to spawn.

        Returns:
            list: List of difficulty levels for each tank.
        """

        base_difficulty = self.get_map_difficulty(level)
        difficulties = []

        for _ in range(num_tanks):
            rand = random.random()

            if rand < 0.25:
                difficulty = max(1, base_difficulty - 1)

            elif rand < 0.75:
                difficulty = base_difficulty

            else:
                difficulty = min(self.max_difficulty, base_difficulty + 1)

            difficulties.append(difficulty)

        return difficulties

    def get_enemy_spawn_params(self, level):
        """
        Get enemy spawn parameters for a given level.

        Args:
            level (int): Current level number.

        Returns:
            dict: Dictionary of spawn parameters.
        """

        if level <= 1:
            return {
                "min_distance_between_tanks": 5,
                "min_distance_from_player": 8,
                "spawn_attempts": 50
            }

        if level == 2:
            return {
                "min_distance_between_tanks": 4,
                "min_distance_from_player": 7,
                "spawn_attempts": 60
            }

        return {
            "min_distance_between_tanks": 4,
            "min_distance_from_player": 6,
            "spawn_attempts": 75
        }

    def get_score_multiplier(self, level, tank_difficulty):
        """
        Get score for destroying an enemy tank.

        Args:
            level (int): Current level number.
            tank_difficulty (int): Difficulty of the destroyed tank.

        Returns:
            int: Score value.
        """

        base_score = 100
        return base_score * level * tank_difficulty

    def get_player_params(self, level):
        """
        Get player parameters for a given level.

        Args:
            level (int): Current level number.

        Returns:
            dict: Dictionary of player parameters.
        """

        if level <= 1:
            return {
                "health": 100,
                "speed": 5,
                "fire_cooldown": 0.5
            }

        if level == 2:
            return {
                "health": 100,
                "speed": 5,
                "fire_cooldown": 0.5
            }

        return {
            "health": 100,
            "speed": 5,
            "fire_cooldown": 0.45
        }

    def get_difficulty(self, level=None):
        """
        Compatibility method used by other classes.

        Args:
            level (int, optional): Current level.

        Returns:
            int: Difficulty value.
        """

        if level is None:
            return 1

        return self.get_map_difficulty(level)