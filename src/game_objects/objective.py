"""
Objective module for the Tank Game.

This module defines the primary objectives that the player must destroy
to complete each level.

Adapted for Tank-Attack:
- There are two types of primary objectives.
- Objectives can receive damage from projectiles.
- A level ends when all primary objectives are destroyed.
"""

from src.engine.game_object import GameObject


class PrimaryObjective(GameObject):
    """
    Base class for all primary objectives.
    """

    def __init__(self, x, y, health=100, objective_type="primary"):
        """
        Initialize a primary objective.

        Args:
            x (float): X-coordinate position.
            y (float): Y-coordinate position.
            health (int): Initial health.
            objective_type (str): Type of objective.
        """
        super().__init__(x, y)

        self.width = 32
        self.height = 32

        self.health = health
        self.max_health = health

        self.tag = "objective"
        self.objective_type = objective_type

        self.destructible = True

    def take_damage(self, amount):
        """
        Reduce the objective health.

        Args:
            amount (int): Damage amount.

        Returns:
            bool: True if the objective was destroyed.
        """
        self.health -= amount

        if self.health <= 0:
            self.health = 0
            self.active = False
            return True

        return False

    def is_destroyed(self):
        """
        Check if the objective is destroyed.

        Returns:
            bool: True if destroyed.
        """
        return self.health <= 0 or not self.active

    def blocks_movement(self):
        """
        Objectives block movement while active.

        Returns:
            bool: True if active.
        """
        return self.active

    def blocks_projectiles(self):
        """
        Objectives block projectiles while active.

        Returns:
            bool: True if active.
        """
        return self.active

    def render(self, screen):
        """
        Render the objective.
        """
        if not self.active:
            return

        super().render(screen)


class BaseObjective(PrimaryObjective):
    """
    Objective type 1.

    Represents a fortified base.
    It has more health and is harder to destroy.
    """

    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            health=120,
            objective_type="base"
        )


class RadarObjective(PrimaryObjective):
    """
    Objective type 2.

    Represents a radar/communication objective.
    It has less health than the base objective.
    """

    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            health=80,
            objective_type="radar"
        )


def create_objective_by_type(objective_type, x, y):
    """
    Create an objective according to its type.

    Args:
        objective_type (str): "base" or "radar".
        x (float): X-coordinate.
        y (float): Y-coordinate.

    Returns:
        PrimaryObjective: Created objective.
    """

    if objective_type == "base":
        return BaseObjective(x, y)

    if objective_type == "radar":
        return RadarObjective(x, y)

    return PrimaryObjective(x, y)