"""
Enemy Tank module for the Tank Game.
This module defines the EnemyTank class that represents an AI-controlled enemy tank.

Adaptado para el proyecto Tank-Attack:
- Los tanques enemigos solo se mueven en cuatro direcciones.
- No usan movimiento diagonal.
- No usan rotación libre.
- Disparan solamente si están cerca y alineados con el jugador.
- Más adelante pueden recibir una ruta calculada por Prolog.
"""

import math
import random
from src.game_objects.tank import Tank


class EnemyTank(Tank):
    """
    Represents an AI-controlled enemy tank.
    """

    def __init__(self, x, y, difficulty=1, health=None, speed=None):
        """
        Initialize an enemy tank.

        Args:
            x (float): X-coordinate position.
            y (float): Y-coordinate position.
            difficulty (int): Difficulty level.
            health (int, optional): Initial health.
            speed (float, optional): Movement speed.
        """

        if health is None:
            health = 50 + (difficulty * 10)

        if speed is None:
            speed = 2 + (difficulty * 0.4)

        super().__init__(x, y, health, speed)

        self.tag = "enemy"
        self.difficulty = difficulty

        # IA básica
        self.target = None
        self.state = "patrol"

        # Tiempo para tomar decisiones
        self.reaction_time = max(0.4, 1.0 - (difficulty * 0.1))
        self.time_since_decision = 0
        self.decision_cooldown = self.reaction_time

        # Patrullaje
        self.patrol_timer = 0
        self.patrol_duration = random.uniform(1.0, 3.0)
        self.patrol_direction = random.choice(["up", "down", "left", "right"])

        # Rangos
        self.sight_range = 150 + (difficulty * 30)
        self.attack_range = 220 + (difficulty * 20)
        self.firing_accuracy = 1.0
        self.close_attack_range = 1.0

        # Control de movimiento para evitar que parezca diagonal
        self.current_move_direction = random.choice(["up", "down", "left", "right"])
        self.direction_timer = 0
        self.direction_change_interval = 0.35

        # Ruta que luego podrá venir desde Prolog
        self.route = []

    def update(self, delta_time, map_data, game_objects=None):
        """
        Update the enemy tank state.

        Args:
            delta_time (float): Time elapsed since the last update.
            map_data (MapData): The map data for collision detection.
            game_objects (list, optional): List of all game objects.

        Returns:
            Projectile: The fired projectile, or None if no projectile was fired.
        """

        super().update(delta_time, map_data)

        if game_objects is None:
            return None

        self.time_since_decision += delta_time

        if self.time_since_decision >= self.decision_cooldown:
            self._update_ai_state(game_objects, map_data)
            self.time_since_decision = 0

        projectile = None

        if self.state == "patrol":
            self._execute_patrol(delta_time, map_data)

        elif self.state == "chase":
            self._chase_target(delta_time, map_data)

        elif self.state == "attack":
            projectile = self._attack_target(delta_time, map_data)

        return projectile

    def _update_ai_state(self, game_objects, map_data):
        """
        Decide what the enemy should do.
        """

        player_tank = None

        for obj in game_objects:
            if getattr(obj, "tag", None) == "player" and obj.active:
                player_tank = obj
                break

        if player_tank is None:
            self.target = None
            self.state = "patrol"
            return

        self.target = player_tank
        distance = self._distance_to(player_tank)

        # Si el jugador está cerca y se puede disparar, atacar
        if distance <= self.attack_range:
            shoot_direction = self._get_direction_to_shoot_target(player_tank)

            if shoot_direction is not None:
                if self._has_line_of_sight(player_tank, map_data):
                    self.state = "attack"
                    return

        # Si está cerca pero no alineado, perseguir
        if distance <= self.sight_range:
            self.state = "chase"
        else:
            self.state = "patrol"

    def _execute_patrol(self, delta_time, map_data):
        """
        Move randomly while patrolling.
        The enemy keeps one direction for a short time.
        """

        self.patrol_timer += delta_time

        if self.patrol_timer >= self.patrol_duration:
            self.patrol_direction = random.choice(["up", "down", "left", "right"])
            self.current_move_direction = self.patrol_direction
            self.patrol_timer = 0
            self.patrol_duration = random.uniform(1.0, 3.0)

        moved = self._move_in_direction(
            self.patrol_direction,
            delta_time,
            map_data
        )

        if not moved:
            self.patrol_direction = random.choice(["up", "down", "left", "right"])
            self.current_move_direction = self.patrol_direction
            self.patrol_timer = 0

    def _chase_target(self, delta_time, map_data):
        """
        Move toward the player using only one direction at a time.
        This avoids diagonal-looking movement and constant direction changes.
        """

        if self.target is None or not self.target.active:
            self.state = "patrol"
            return

        self.direction_timer += delta_time

        if self.direction_timer >= self.direction_change_interval:
            self.current_move_direction = self._get_best_direction_to_target(self.target)
            self.direction_timer = 0

        moved = self._move_in_direction(
            self.current_move_direction,
            delta_time,
            map_data
        )

        if not moved:
            self.current_move_direction = self._get_alternative_direction(
                self.current_move_direction
            )
            self.direction_timer = 0

    def _attack_target(self, delta_time, map_data):
        """
        Attack the target if it is close and aligned.
        """

        if self.target is None or not self.target.active:
            self.state = "patrol"
            return None

        direction = self._get_direction_to_shoot_target(self.target)

        if direction is None:
            self.state = "chase"
            return None

        # Apunta hacia el jugador
        self.set_direction(direction)

        # Si hay una pared en medio, no dispara
        if not self._has_line_of_sight(self.target, map_data):
            self.state = "chase"
            return None

        # Dispara. Si el cooldown no ha terminado, fire() devuelve None.
        projectile = self.fire()

        # Se mantiene en modo ataque si todavía puede ver al jugador
        self.state = "attack"

        return projectile

    def _move_in_direction(self, direction, delta_time, map_data):
        """
        Move the enemy in one of the four basic directions.

        Args:
            direction (str): "up", "down", "left" or "right".

        Returns:
            bool: True if the enemy moved, False otherwise.
        """

        if direction == "up":
            return self.move_up(delta_time, map_data)

        if direction == "down":
            return self.move_down(delta_time, map_data)

        if direction == "left":
            return self.move_left(delta_time, map_data)

        if direction == "right":
            return self.move_right(delta_time, map_data)

        return False

    def _get_best_direction_to_target(self, target):
        """
        Decide the best direction to move toward the target.
        The enemy chooses only one axis at a time.
        """

        dx = target.x - self.x
        dy = target.y - self.y

        if abs(dx) > abs(dy):
            if dx > 0:
                return "right"
            else:
                return "left"
        else:
            if dy > 0:
                return "down"
            else:
                return "up"

    def _get_alternative_direction(self, current_direction):
        """
        Return an alternative direction if the main direction is blocked.
        """

        if current_direction in ["up", "down"]:
            return random.choice(["left", "right"])

        if current_direction in ["left", "right"]:
            return random.choice(["up", "down"])

        return random.choice(["up", "down", "left", "right"])

    def _get_direction_to_shoot_target(self, target):
        """
        Return the direction needed to shoot the target if aligned.

        The enemy can shoot if the player is in the same row or column,
        using a tolerance so it does not need to be perfectly aligned.
        """

        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        target_center_x = target.x + target.width / 2
        target_center_y = target.y + target.height / 2

        dx = target_center_x - center_x
        dy = target_center_y - center_y

        # Tolerancia para considerar que están alineados.
        # Si el tile es de 32px, 24 funciona bien.
        alignment_tolerance = 24

        # Misma fila aproximadamente: dispara izquierda o derecha
        if abs(dy) <= alignment_tolerance:
            if dx > 0:
                return Tank.RIGHT
            else:
                return Tank.LEFT

        # Misma columna aproximadamente: dispara arriba o abajo
        if abs(dx) <= alignment_tolerance:
            if dy > 0:
                return Tank.DOWN
            else:
                return Tank.UP

        return None

    def _is_aligned_with_target(self, target):
        """
        Check if enemy and player are aligned horizontally or vertically.
        """

        return self._get_direction_to_shoot_target(target) is not None

    def _distance_to(self, target):
        """
        Calculate distance to another object.
        """

        dx = target.x - self.x
        dy = target.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def _has_line_of_sight(self, target, map_data):
        """
        Check if there is no wall between the enemy and the player.
        """

        if map_data is None:
            return True

        start_x = self.x + self.width / 2
        start_y = self.y + self.height / 2

        end_x = target.x + target.width / 2
        end_y = target.y + target.height / 2

        dx = end_x - start_x
        dy = end_y - start_y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return True

        dx /= distance
        dy /= distance

        step_size = map_data.cell_size / 2
        steps = int(distance / step_size)

        for i in range(1, steps):
            check_x = start_x + dx * i * step_size
            check_y = start_y + dy * i * step_size

            cell_x = int(check_x / map_data.cell_size)
            cell_y = int(check_y / map_data.cell_size)

            if (
                cell_x >= 0
                and cell_y >= 0
                and cell_x < map_data.width
                and cell_y < map_data.height
            ):
                if map_data.is_obstacle_at(cell_x, cell_y):
                    return False

        return True

    def set_route(self, route):
        """
        Set a route calculated by Prolog.

        Args:
            route (list): List of positions returned by Prolog.
        """

        self.route = route

    def follow_route(self, delta_time, map_data):
        """
        Move the enemy following a route.

        This method is optional for now. Later, Persona 2 can use it
        when Prolog returns a list of cells.
        """

        if not self.route:
            return False

        next_position = self.route[0]

        target_x = next_position[0]
        target_y = next_position[1]

        dx = target_x - self.x
        dy = target_y - self.y

        if abs(dx) < 2 and abs(dy) < 2:
            self.route.pop(0)
            return True

        if abs(dx) > abs(dy):
            if dx > 0:
                return self.move_right(delta_time, map_data)
            else:
                return self.move_left(delta_time, map_data)
        else:
            if dy > 0:
                return self.move_down(delta_time, map_data)
            else:
                return self.move_up(delta_time, map_data)
            


class LightEnemyTank(EnemyTank):
    """
    Enemy tank type 1.

    Light enemy tank:
    - Moves faster.
    - Has less health.
    - Shoots faster.
    - Does less damage.
    """

    def __init__(self, x, y, difficulty=1):
        super().__init__(
            x,
            y,
            difficulty=difficulty,
            health=60,
            speed=3.8
        )

        self.tag = "enemy"
        self.enemy_type = "light"

        self.damage = 15
        self.fire_cooldown = 0.35

        self.sight_range = 180 + (difficulty * 20)
        self.attack_range = 200 + (difficulty * 20)
        self.close_attack_range = 70
        self.firing_accuracy = 0.8


class HeavyEnemyTank(EnemyTank):
    """
    Enemy tank type 2.

    Heavy enemy tank:
    - Moves slower.
    - Has more health.
    - Does more damage.
    - Shoots slower.
    """

    def __init__(self, x, y, difficulty=1):
        super().__init__(
            x,
            y,
            difficulty=difficulty,
            health=150,
            speed=1.8
        )

        self.tag = "enemy"
        self.enemy_type = "heavy"

        self.damage = 35
        self.fire_cooldown = 0.9

        self.sight_range = 160 + (difficulty * 20)
        self.attack_range = 190 + (difficulty * 20)
        self.close_attack_range = 75
        self.firing_accuracy = 0.7


class SniperEnemyTank(EnemyTank):
    """
    Enemy tank type 3.

    Sniper enemy tank:
    - Medium speed.
    - Medium health.
    - Long attack range.
    - High accuracy.
    - Shoots slower than the light tank.
    """

    def __init__(self, x, y, difficulty=1):
        super().__init__(
            x,
            y,
            difficulty=difficulty,
            health=80,
            speed=2.5
        )

        self.tag = "enemy"
        self.enemy_type = "sniper"

        self.damage = 25
        self.fire_cooldown = 0.7

        self.sight_range = 280 + (difficulty * 25)
        self.attack_range = 300 + (difficulty * 25)
        self.close_attack_range = 80
        self.firing_accuracy = 1.0



def create_random_enemy_tank(x, y, difficulty=1):
    """
    Create a random enemy tank type.

    Returns:
        EnemyTank: LightEnemyTank, HeavyEnemyTank or SniperEnemyTank.
    """

    enemy_classes = [
        LightEnemyTank,
        HeavyEnemyTank,
        SniperEnemyTank
    ]

    enemy_class = random.choice(enemy_classes)

    return enemy_class(x, y, difficulty)