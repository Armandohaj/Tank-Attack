"""
Enemy Tank Spawner module for the Tank Game.

This module creates enemy tanks for each level.

Adapted for Tank-Attack:
- Creates three different enemy tank types.
- Keeps compatibility with LevelManager calls.
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

        Args:
            map_data: Map data used to validate positions.
            cell_size (int): Size of each map cell in pixels.
        """
        self.map_data = map_data
        self.cell_size = cell_size

    def set_map_data(self, map_data):
        """
        Set or update the map data.
        """
        self.map_data = map_data

        if map_data and hasattr(map_data, "cell_size"):
            self.cell_size = map_data.cell_size

    def _create_enemy_tank(self, x, y, difficulty):
        """
        Create one of the three enemy tank types.
        """

        enemy_classes = [
            LightEnemyTank,
            HeavyEnemyTank,
            SniperEnemyTank
        ]

        enemy_class = random.choice(enemy_classes)
        enemy_tank = enemy_class(x, y, difficulty=difficulty)

        return enemy_tank

    def spawn_enemy_tanks(
        self,
        level_number=1,
        player_position=None,
        game_engine=None,
        difficulty_manager=None,
        count=None
    ):
        """
        Spawn enemy tanks for a level.

        This signature is compatible with LevelManager, which calls:

        spawn_enemy_tanks(level_number, player_position, game_engine, difficulty_manager)

        Args:
            level_number (int): Current level.
            player_position (tuple): Player position in pixels or cells.
            game_engine: Current game engine.
            difficulty_manager: Optional difficulty manager.
            count (int): Optional number of enemies.

        Returns:
            list: List of enemy tanks.
        """

        difficulty = self._get_difficulty(level_number, difficulty_manager)

        if count is None:
            count = self._get_enemy_count_for_level(level_number)

        enemy_tanks = []

        for _ in range(count):
            position = self._find_valid_spawn_position(
                player_position=player_position,
                game_engine=game_engine
            )

            if position is None:
                position = self._find_fallback_position(
                    player_position=player_position,
                    game_engine=game_engine
                )

            if position is None:
                continue

            cell_x, cell_y = position

            pixel_x = cell_x * self.cell_size
            pixel_y = cell_y * self.cell_size

            enemy_tank = self._create_enemy_tank(
                pixel_x,
                pixel_y,
                difficulty
            )

            enemy_tanks.append(enemy_tank)

        return enemy_tanks

    def spawn_enemy_tank_at(self, cell_x, cell_y, difficulty=1):
        """
        Spawn one enemy tank at a specific cell.
        """

        pixel_x = cell_x * self.cell_size
        pixel_y = cell_y * self.cell_size

        return self._create_enemy_tank(pixel_x, pixel_y, difficulty)

    def spawn_enemy_tank_at_pixels(self, x, y, difficulty=1):
        """
        Spawn one enemy tank at a specific pixel position.
        """

        return self._create_enemy_tank(x, y, difficulty)

    def spawn_enemy_tanks_near_objectives(self, objectives, difficulty=1):
        """
        Spawn one enemy tank near each objective.
        """

        enemy_tanks = []

        for objective in objectives:
            if not getattr(objective, "active", True):
                continue

            objective_cell_x = int(objective.x // self.cell_size)
            objective_cell_y = int(objective.y // self.cell_size)

            position = self._find_position_near_cell(
                objective_cell_x,
                objective_cell_y
            )

            if position is None:
                position = self._find_valid_spawn_position()

            if position is None:
                continue

            cell_x, cell_y = position

            pixel_x = cell_x * self.cell_size
            pixel_y = cell_y * self.cell_size

            enemy_tank = self._create_enemy_tank(
                pixel_x,
                pixel_y,
                difficulty
            )

            enemy_tank.defended_objective = objective

            enemy_tanks.append(enemy_tank)

        return enemy_tanks

    def _get_difficulty(self, level_number, difficulty_manager=None):
        """
        Get difficulty value for the current level.
        """

        if difficulty_manager is None:
            return max(1, level_number)

        if hasattr(difficulty_manager, "get_difficulty"):
            try:
                return difficulty_manager.get_difficulty(level_number)
            except TypeError:
                return difficulty_manager.get_difficulty()

        if hasattr(difficulty_manager, "difficulty"):
            return difficulty_manager.difficulty

        return max(1, level_number)

    def _get_enemy_count_for_level(self, level_number):
        """
        Decide how many enemies should appear in each level.

        The project has a maximum of 3 levels.
        """

        if level_number <= 1:
            return 2

        if level_number == 2:
            return 3

        return 4

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
                return cell_x, cell_y

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
                    return cell_x, cell_y

        return None

    def _find_default_position(self):
        """
        Return a default position if there is no map data.
        """

        return 5, 5

    def _find_position_near_cell(self, center_cell_x, center_cell_y):
        """
        Find a valid position near a specific cell.
        """

        possible_offsets = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (2, 0),
            (-2, 0),
            (0, 2),
            (0, -2),
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1)
        ]

        random.shuffle(possible_offsets)

        for offset_x, offset_y in possible_offsets:
            cell_x = center_cell_x + offset_x
            cell_y = center_cell_y + offset_y

            if self._is_valid_spawn_position(cell_x, cell_y):
                return cell_x, cell_y

        return None

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

    def create_enemy_for_level(self, cell_x, cell_y, level_number):
        """
        Create an enemy tank according to the level number.
        """

        difficulty = max(1, level_number)

        return self.spawn_enemy_tank_at(
            cell_x,
            cell_y,
            difficulty=difficulty
        )

    def create_enemies_for_level(self, level_number, count=None):
        """
        Create enemies for a level.
        """

        difficulty = max(1, level_number)

        if count is None:
            count = self._get_enemy_count_for_level(level_number)

        enemy_tanks = []

        for _ in range(count):
            position = self._find_valid_spawn_position()

            if position is None:
                continue

            cell_x, cell_y = position

            enemy_tanks.append(
                self.spawn_enemy_tank_at(
                    cell_x,
                    cell_y,
                    difficulty=difficulty
                )
            )

        return enemy_tanks