"""
Enemy Tank Spawner module for the Tank Game.

This module creates enemy tanks for each level.

For Tank-Attack:
- Every level has exactly three enemy tanks.
- One LightEnemyTank.
- One HeavyEnemyTank.
- One SniperEnemyTank.
"""

import random

from src.game_objects.enemy_tank import (
    LightEnemyTank,
    HeavyEnemyTank,
    SniperEnemyTank
)


class EnemyTankSpawner:
    """
    Responsible for spawning enemy tanks in the map.
    """

    def __init__(self, map_data=None, cell_size=32):
        """
        Initialize the enemy tank spawner.
        """

        self.map_data = map_data
        self.cell_size = cell_size

        if map_data and hasattr(map_data, "cell_size"):
            self.cell_size = map_data.cell_size

    def set_map_data(self, map_data):
        """
        Set or update the map data.
        """

        self.map_data = map_data

        if map_data and hasattr(map_data, "cell_size"):
            self.cell_size = map_data.cell_size

    def spawn_enemy_tanks(
        self,
        level_number=1,
        player_position=None,
        game_engine=None,
        difficulty_manager=None,
        count=None
    ):
        """
        Spawn exactly three enemy tanks per level:
        one light, one heavy and one sniper.
        """

        enemy_tanks = []

        enemy_classes_to_spawn = [
            LightEnemyTank,
            HeavyEnemyTank,
            SniperEnemyTank
        ]

        difficulties = [
            level_number,
            level_number,
            level_number
        ]

        if difficulty_manager is not None:
            difficulties = difficulty_manager.get_enemy_tank_difficulties(
                level_number,
                3
            )

        random.shuffle(enemy_classes_to_spawn)

        for i, enemy_class in enumerate(enemy_classes_to_spawn):
            difficulty = difficulties[i] if i < len(difficulties) else level_number

            spawn_position = self._find_valid_spawn_position(
                player_position,
                game_engine
            )

            if spawn_position is None:
                spawn_position = self._find_fallback_position(
                    player_position,
                    game_engine
                )

            if spawn_position is None:
                continue

            spawn_x, spawn_y = spawn_position

            enemy_tank = enemy_class(
                spawn_x,
                spawn_y,
                difficulty=difficulty
            )

            if game_engine is not None:
                game_engine.add_game_object(enemy_tank)

            enemy_tanks.append(enemy_tank)

            print(
                f"Enemy spawned: {getattr(enemy_tank, 'enemy_type', 'enemy')} "
                f"at ({spawn_x}, {spawn_y})"
            )

        return enemy_tanks

    def spawn_enemy_tank_at(self, cell_x, cell_y, enemy_type="light", difficulty=1):
        """
        Spawn one specific enemy tank type at a specific cell.
        """

        pixel_x = cell_x * self.cell_size
        pixel_y = cell_y * self.cell_size

        return self._create_enemy_by_type(
            pixel_x,
            pixel_y,
            enemy_type,
            difficulty
        )

    def spawn_enemy_tank_at_pixels(self, x, y, enemy_type="light", difficulty=1):
        """
        Spawn one specific enemy tank type at a specific pixel position.
        """

        return self._create_enemy_by_type(
            x,
            y,
            enemy_type,
            difficulty
        )

    def _create_enemy_by_type(self, x, y, enemy_type, difficulty):
        """
        Create an enemy tank by type.
        """

        if enemy_type == "light":
            return LightEnemyTank(x, y, difficulty=difficulty)

        if enemy_type == "heavy":
            return HeavyEnemyTank(x, y, difficulty=difficulty)

        if enemy_type == "sniper":
            return SniperEnemyTank(x, y, difficulty=difficulty)

        return LightEnemyTank(x, y, difficulty=difficulty)

    def _find_valid_spawn_position(self, player_position=None, game_engine=None):
        """
        Find a valid random position in the map.
        """

        if self.map_data is None:
            return self._find_default_position()

        max_attempts = 100

        for _ in range(max_attempts):
            cell_x = random.randint(1, self.map_data.width - 2)
            cell_y = random.randint(1, self.map_data.height - 2)

            if self._is_valid_spawn_position(
                cell_x,
                cell_y,
                player_position,
                game_engine
            ):
                return cell_x * self.cell_size, cell_y * self.cell_size

        return None

    def _find_fallback_position(self, player_position=None, game_engine=None):
        """
        Find the first valid position by scanning the map.
        """

        if self.map_data is None:
            return self._find_default_position()

        for cell_y in range(1, self.map_data.height - 1):
            for cell_x in range(1, self.map_data.width - 1):
                if self._is_valid_spawn_position(
                    cell_x,
                    cell_y,
                    player_position,
                    game_engine
                ):
                    return cell_x * self.cell_size, cell_y * self.cell_size

        return None

    def _find_default_position(self):
        """
        Return a default pixel position if there is no map data.
        """

        return 160, 160

    def _is_valid_spawn_position(
        self,
        cell_x,
        cell_y,
        player_position=None,
        game_engine=None
    ):
        """
        Check if a cell is valid for spawning an enemy.
        """

        if self.map_data is not None:
            if cell_x < 0 or cell_y < 0:
                return False

            if cell_x >= self.map_data.width:
                return False

            if cell_y >= self.map_data.height:
                return False

            if self.map_data.is_obstacle_at(cell_x, cell_y):
                return False

        if self._is_too_close_to_player(cell_x, cell_y, player_position):
            return False

        if self._is_occupied_by_object(cell_x, cell_y, game_engine):
            return False

        return True

    def _is_too_close_to_player(self, cell_x, cell_y, player_position):
        """
        Avoid spawning enemies too close to the player.
        """

        if player_position is None:
            return False

        try:
            player_x, player_y = player_position
        except ValueError:
            return False

        player_cell_x = int(player_x // self.cell_size)
        player_cell_y = int(player_y // self.cell_size)

        distance_x = abs(cell_x - player_cell_x)
        distance_y = abs(cell_y - player_cell_y)

        return distance_x <= 3 and distance_y <= 3

    def _is_occupied_by_object(self, cell_x, cell_y, game_engine):
        """
        Avoid spawning enemies on top of other game objects.
        """

        if game_engine is None:
            return False

        if not hasattr(game_engine, "get_game_objects"):
            return False

        objects = game_engine.get_game_objects()

        for obj in objects:
            if not getattr(obj, "active", True):
                continue

            obj_cell_x = int(obj.x // self.cell_size)
            obj_cell_y = int(obj.y // self.cell_size)

            if obj_cell_x == cell_x and obj_cell_y == cell_y:
                return True

        return False

    def create_enemies_for_level(self, level_number, count=None):
        """
        Create exactly the three required enemy types for a level.
        """

        enemy_tanks = []

        enemy_types = [
            "light",
            "heavy",
            "sniper"
        ]

        for enemy_type in enemy_types:
            position = self._find_valid_spawn_position()

            if position is None:
                position = self._find_fallback_position()

            if position is None:
                continue

            pixel_x, pixel_y = position

            enemy_tanks.append(
                self._create_enemy_by_type(
                    pixel_x,
                    pixel_y,
                    enemy_type,
                    difficulty=level_number
                )
            )

        return enemy_tanks