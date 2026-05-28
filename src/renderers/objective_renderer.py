"""
Objective Renderer module for the Tank Game.

This module renders the two types of primary objectives.
"""

import pygame


class ObjectiveRenderer:
    """
    Renders primary objectives with different colors.
    """

    def __init__(self):
        self.base_sprite = self._create_objective_sprite((180, 80, 40))
        self.radar_sprite = self._create_objective_sprite((180, 180, 40))

        self.health_bar_width = 30
        self.health_bar_height = 5

    def _create_objective_sprite(self, color):
        """
        Create a simple objective sprite.
        """

        sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        sprite.fill((0, 0, 0, 0))

        darker = tuple(max(0, c - 50) for c in color)
        lighter = tuple(min(255, c + 50) for c in color)

        # Base square
        pygame.draw.rect(sprite, darker, (4, 8, 24, 20), border_radius=3)
        pygame.draw.rect(sprite, color, (6, 10, 20, 16), border_radius=3)

        # Top detail
        pygame.draw.rect(sprite, lighter, (10, 5, 12, 8), border_radius=2)

        # Center mark
        pygame.draw.circle(sprite, darker, (16, 18), 5)
        pygame.draw.circle(sprite, lighter, (16, 18), 3)

        return sprite

    def render_objective(self, screen, objective):
        """
        Render an objective.
        """

        if not getattr(objective, "active", True):
            return

        objective_type = getattr(objective, "objective_type", "primary")

        if objective_type == "base":
            objective.set_sprite(self.base_sprite)

        elif objective_type == "radar":
            objective.set_sprite(self.radar_sprite)

        objective.render(screen)
        self._render_health_bar(screen, objective)

    def _render_health_bar(self, screen, objective):
        """
        Render health bar above the objective.
        """

        if not hasattr(objective, "health") or not hasattr(objective, "max_health"):
            return

        if objective.max_health <= 0:
            return

        bar_x = objective.x + (objective.width - self.health_bar_width) / 2
        bar_y = objective.y - self.health_bar_height - 4

        health_percentage = max(
            0,
            min(1, objective.health / objective.max_health)
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (
                int(bar_x - 1),
                int(bar_y - 1),
                self.health_bar_width + 2,
                self.health_bar_height + 2
            )
        )

        pygame.draw.rect(
            screen,
            (100, 20, 20),
            (
                int(bar_x),
                int(bar_y),
                self.health_bar_width,
                self.health_bar_height
            )
        )

        health_width = int(self.health_bar_width * health_percentage)

        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (
                int(bar_x),
                int(bar_y),
                health_width,
                self.health_bar_height
            )
        )