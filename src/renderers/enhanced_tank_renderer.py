"""
Enhanced Tank Renderer module for the Tank Game.
This module handles the rendering of tanks with improved visuals.

Adapted for Tank-Attack:
- Player tank has its own color.
- Each enemy tank type has a different color:
  light = green
  heavy = red
  sniper = blue
"""

import pygame
import random


class EnhancedTankRenderer:
    """
    Handles enhanced rendering of tanks with improved visuals.
    """

    def __init__(self, renderer):
        """
        Initialize the enhanced tank renderer.

        Args:
            renderer: The game renderer.
        """
        self.renderer = renderer

        self.player_tank_sprite = None

        self.enemy_tank_sprite = None
        self.light_enemy_sprite = None
        self.heavy_enemy_sprite = None
        self.sniper_enemy_sprite = None

        self.health_bar_width = 30
        self.health_bar_height = 5

        self._create_enhanced_sprites()

    def _create_enhanced_sprites(self):
        """
        Create enhanced sprites for player and enemy tanks.
        """

        # Player tank: blue
        self.player_tank_sprite = self._create_enhanced_tank_sprite(
            (0, 100, 255)
        )

        # Enemy tank types
        self.enemy_tank_sprite = self._create_enhanced_tank_sprite(
            (255, 50, 50)
        )

        # Light enemy: green
        self.light_enemy_sprite = self._create_enhanced_tank_sprite(
            (40, 220, 80)
        )

        # Heavy enemy: red/orange
        self.heavy_enemy_sprite = self._create_enhanced_tank_sprite(
            (220, 40, 40)
        )

        # Sniper enemy: blue/purple
        self.sniper_enemy_sprite = self._create_enhanced_tank_sprite(
            (80, 120, 255)
        )

    def _create_enhanced_tank_sprite(self, color):
        """
        Create an enhanced tank sprite with the given color.

        Args:
            color: RGB tuple representing the color.

        Returns:
            pygame.Surface: The created tank sprite.
        """

        tank_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        tank_sprite.fill((0, 0, 0, 0))

        darker_color = tuple(max(0, c - 40) for c in color)
        lighter_color = tuple(min(255, c + 40) for c in color)
        shadow_color = tuple(max(0, c - 60) for c in color)

        # Tracks
        pygame.draw.rect(
            tank_sprite,
            shadow_color,
            (2, 6, 4, 20),
            border_radius=2
        )
        pygame.draw.rect(
            tank_sprite,
            shadow_color,
            (26, 6, 4, 20),
            border_radius=2
        )

        # Tread details
        for i in range(4):
            y_pos = 8 + i * 4
            pygame.draw.line(tank_sprite, darker_color, (2, y_pos), (6, y_pos), 1)
            pygame.draw.line(tank_sprite, darker_color, (26, y_pos), (30, y_pos), 1)

        # Body
        pygame.draw.rect(
            tank_sprite,
            shadow_color,
            (6, 8, 20, 16),
            border_radius=3
        )
        pygame.draw.rect(
            tank_sprite,
            color,
            (7, 9, 18, 14),
            border_radius=3
        )
        pygame.draw.rect(
            tank_sprite,
            lighter_color,
            (8, 10, 16, 3)
        )

        # Turret
        pygame.draw.circle(tank_sprite, shadow_color, (17, 17), 9)
        pygame.draw.circle(tank_sprite, darker_color, (16, 16), 9)
        pygame.draw.circle(tank_sprite, color, (16, 16), 8)
        pygame.draw.circle(tank_sprite, lighter_color, (14, 14), 4)
        pygame.draw.circle(tank_sprite, color, (14, 14), 3)

        # Barrel pointing upward
        pygame.draw.rect(tank_sprite, shadow_color, (13, -1, 6, 17))
        pygame.draw.rect(tank_sprite, darker_color, (14, 0, 4, 16))
        pygame.draw.rect(tank_sprite, color, (14, 0, 4, 15))
        pygame.draw.rect(tank_sprite, lighter_color, (15, 1, 2, 14))

        # Muzzle brake
        pygame.draw.rect(tank_sprite, darker_color, (13, -2, 6, 3))
        pygame.draw.rect(tank_sprite, color, (14, -1, 4, 2))

        # Details
        pygame.draw.line(tank_sprite, darker_color, (8, 12), (24, 12), 1)
        pygame.draw.line(tank_sprite, darker_color, (8, 20), (24, 20), 1)

        for x in [10, 16, 22]:
            pygame.draw.circle(tank_sprite, darker_color, (x, 14), 1)
            pygame.draw.circle(tank_sprite, lighter_color, (x - 1, 13), 1)

        # Antenna
        pygame.draw.line(tank_sprite, (200, 200, 200), (20, 10), (22, 6), 2)
        pygame.draw.circle(tank_sprite, (255, 255, 0), (22, 6), 1)

        return tank_sprite

    def set_player_tank_sprite(self, sprite):
        """
        Set the sprite for the player tank.
        """
        self.player_tank_sprite = sprite

    def set_enemy_tank_sprite(self, sprite):
        """
        Set the default sprite for enemy tanks.
        """
        self.enemy_tank_sprite = sprite

    def render_tank(self, screen, tank):
        """
        Render a tank on the screen with enhanced visuals.

        Args:
            screen: Pygame surface to render on.
            tank: The tank to render.
        """

        if not getattr(tank, "active", True):
            return

        sprite = self._get_sprite_for_tank(tank)

        # Important:
        # Always set the correct sprite, because enemy type may vary.
        tank.set_sprite(sprite)

        self._render_tank_with_effects(screen, tank)
        self._render_enhanced_health_bar(screen, tank)

    def _get_sprite_for_tank(self, tank):
        """
        Return the correct sprite according to tank type.

        Returns:
            pygame.Surface: Tank sprite.
        """

        if getattr(tank, "tag", None) == "player":
            return self.player_tank_sprite

        enemy_type = getattr(tank, "enemy_type", "normal")

        if enemy_type == "light":
            return self.light_enemy_sprite

        if enemy_type == "heavy":
            return self.heavy_enemy_sprite

        if enemy_type == "sniper":
            return self.sniper_enemy_sprite

        return self.enemy_tank_sprite

    def _render_tank_with_effects(self, screen, tank):
        """
        Render a tank with visual effects.
        """

        shadow_surface = pygame.Surface(
            (tank.width + 4, tank.height + 4),
            pygame.SRCALPHA
        )
        shadow_surface.fill((0, 0, 0, 50))
        screen.blit(shadow_surface, (tank.x - 2, tank.y + 2))

        tank.render(screen)

        if hasattr(tank, "health") and hasattr(tank, "max_health"):
            damage_ratio = 1 - (tank.health / tank.max_health)

            if damage_ratio > 0.3:
                self._render_damage_effects(screen, tank, damage_ratio)

    def _render_damage_effects(self, screen, tank, damage_ratio):
        """
        Render damage effects on the tank.
        """

        if damage_ratio > 0.5:
            for _ in range(int(damage_ratio * 3)):
                smoke_x = tank.x + random.randint(0, int(tank.width))
                smoke_y = tank.y + random.randint(0, int(tank.height // 2))
                smoke_size = random.randint(2, 4)
                smoke_alpha = int(100 * damage_ratio)

                smoke_surface = pygame.Surface(
                    (smoke_size * 2, smoke_size * 2),
                    pygame.SRCALPHA
                )

                pygame.draw.circle(
                    smoke_surface,
                    (80, 80, 80, smoke_alpha),
                    (smoke_size, smoke_size),
                    smoke_size
                )

                screen.blit(
                    smoke_surface,
                    (smoke_x - smoke_size, smoke_y - smoke_size)
                )

        if damage_ratio > 0.7:
            for _ in range(int(damage_ratio * 2)):
                spark_x = tank.x + random.randint(0, int(tank.width))
                spark_y = tank.y + random.randint(0, int(tank.height))

                pygame.draw.circle(
                    screen,
                    (255, 255, 0),
                    (int(spark_x), int(spark_y)),
                    1
                )

    def _render_enhanced_health_bar(self, screen, tank):
        """
        Render an enhanced health bar above the tank.
        """

        if not hasattr(tank, "health") or not hasattr(tank, "max_health"):
            return

        if tank.max_health <= 0:
            return

        bar_x = tank.x + (tank.width - self.health_bar_width) / 2
        bar_y = tank.y - self.health_bar_height - 4

        health_percentage = max(
            0,
            min(1, tank.health / tank.max_health)
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

        if health_percentage > 0.6:
            health_color = (0, 200, 0)
            highlight_color = (50, 255, 50)
        elif health_percentage > 0.3:
            health_color = (200, 200, 0)
            highlight_color = (255, 255, 50)
        else:
            health_color = (200, 0, 0)
            highlight_color = (255, 50, 50)

        pygame.draw.rect(
            screen,
            health_color,
            (
                int(bar_x),
                int(bar_y),
                health_width,
                self.health_bar_height
            )
        )

        if health_width > 0:
            pygame.draw.rect(
                screen,
                highlight_color,
                (
                    int(bar_x),
                    int(bar_y),
                    health_width,
                    max(1, self.health_bar_height // 2)
                )
            )