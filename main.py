"""
Main entry point for the Tank Game.
"""
import random
import pygame
import sys
import os
import math

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.level_editor.screen_editor import ScreenEditor
from src.services.prolog_service import PrologService
from src.engine.game_engine import GameEngine
from src.engine.input_handler import InputHandler

from src.game_objects.player_tank import PlayerTank
from src.game_objects.objective import BaseObjective, RadarObjective

from src.level_manager.level_manager import LevelManager

from src.renderers.enhanced_map_renderer import EnhancedMapRenderer
from src.renderers.enhanced_tank_renderer import EnhancedTankRenderer
from src.renderers.enhanced_projectile_renderer import EnhancedProjectileRenderer
from src.renderers.visual_effects_manager import VisualEffectsManager
from src.renderers.objective_renderer import ObjectiveRenderer


MAX_LEVEL = 3


def is_valid_objective_cell(cell_x, cell_y, map_data, game_engine=None):
    """
    Check if a cell is valid for placing an objective.
    The objective cannot appear on walls, rocks, barrels or other objects.
    """

    if map_data is None:
        return True

    if cell_x < 0 or cell_y < 0:
        return False

    if cell_x >= map_data.width or cell_y >= map_data.height:
        return False

    cell_type = map_data.get_cell(cell_x, cell_y)

    if cell_type != map_data.EMPTY:
        return False

    if game_engine is not None:
        for obj in game_engine.get_game_objects():
            if not getattr(obj, "active", True):
                continue

            obj_cell_x = int(obj.x // map_data.cell_size)
            obj_cell_y = int(obj.y // map_data.cell_size)

            if obj_cell_x == cell_x and obj_cell_y == cell_y:
                return False

    return True


def find_nearest_valid_objective_cell(preferred_cell, map_data, game_engine=None):
    """
    Find the nearest valid cell around the preferred position.
    """

    preferred_x, preferred_y = preferred_cell

    if is_valid_objective_cell(preferred_x, preferred_y, map_data, game_engine):
        return preferred_x, preferred_y

    for radius in range(1, 10):
        possible_cells = []

        for dx in range(-radius, radius + 1):
            possible_cells.append((preferred_x + dx, preferred_y - radius))
            possible_cells.append((preferred_x + dx, preferred_y + radius))

        for dy in range(-radius + 1, radius):
            possible_cells.append((preferred_x - radius, preferred_y + dy))
            possible_cells.append((preferred_x + radius, preferred_y + dy))

        for cell_x, cell_y in possible_cells:
            if is_valid_objective_cell(cell_x, cell_y, map_data, game_engine):
                return cell_x, cell_y

    for y in range(1, map_data.height - 1):
        for x in range(1, map_data.width - 1):
            if is_valid_objective_cell(x, y, map_data, game_engine):
                return x, y

    return preferred_x, preferred_y


def is_valid_cell_for_objective(cell_x, cell_y, map_data, game_engine=None):
    """
    Check if a cell is free for placing an objective.
    """

    if map_data is None:
        return False

    if cell_x < 0 or cell_y < 0:
        return False

    if cell_x >= map_data.width or cell_y >= map_data.height:
        return False

    if map_data.get_cell(cell_x, cell_y) != map_data.EMPTY:
        return False

    if game_engine is not None:
        for obj in game_engine.get_game_objects():
            if not getattr(obj, "active", True):
                continue

            obj_cell_x = int(obj.x // map_data.cell_size)
            obj_cell_y = int(obj.y // map_data.cell_size)

            if obj_cell_x == cell_x and obj_cell_y == cell_y:
                return False

    return True


def find_two_free_cells_together(preferred_cell, map_data, game_engine=None):
    """
    Find two nearby free cells for placing both primary objectives together.
    """

    preferred_x, preferred_y = preferred_cell

    possible_pairs = [
        ((preferred_x, preferred_y), (preferred_x + 1, preferred_y)),
        ((preferred_x, preferred_y), (preferred_x - 1, preferred_y)),
        ((preferred_x, preferred_y), (preferred_x, preferred_y + 1)),
        ((preferred_x, preferred_y), (preferred_x, preferred_y - 1)),
    ]

    for cell_a, cell_b in possible_pairs:
        if (
            is_valid_cell_for_objective(cell_a[0], cell_a[1], map_data, game_engine)
            and is_valid_cell_for_objective(cell_b[0], cell_b[1], map_data, game_engine)
        ):
            return cell_a, cell_b

    for radius in range(1, 10):
        for y in range(preferred_y - radius, preferred_y + radius + 1):
            for x in range(preferred_x - radius, preferred_x + radius + 1):

                possible_pairs = [
                    ((x, y), (x + 1, y)),
                    ((x, y), (x - 1, y)),
                    ((x, y), (x, y + 1)),
                    ((x, y), (x, y - 1)),
                ]

                random.shuffle(possible_pairs)

                for cell_a, cell_b in possible_pairs:
                    if (
                        is_valid_cell_for_objective(cell_a[0], cell_a[1], map_data, game_engine)
                        and is_valid_cell_for_objective(cell_b[0], cell_b[1], map_data, game_engine)
                    ):
                        return cell_a, cell_b

    return (preferred_x, preferred_y), (preferred_x + 1, preferred_y)


def create_level_objectives(game_engine, level_manager, level_number):
    """
    Create the two required primary objective types together.
    Both objectives appear next to each other so one tank can guard them.
    """

    map_data = level_manager.map_data
    cell_size = 32

    if map_data and hasattr(map_data, "cell_size"):
        cell_size = map_data.cell_size

    screen_editor = ScreenEditor()
    level_config = screen_editor.load_level_config(level_number)

    preferred_cell = (
        level_config["objective_x"],
        level_config["objective_y"]
    )

    base_cell, radar_cell = find_two_free_cells_together(
        preferred_cell,
        map_data,
        game_engine
    )

    base_objective = BaseObjective(
        base_cell[0] * cell_size,
        base_cell[1] * cell_size
    )

    radar_objective = RadarObjective(
        radar_cell[0] * cell_size,
        radar_cell[1] * cell_size
    )

    objectives = [base_objective, radar_objective]

    for objective in objectives:
        game_engine.add_game_object(objective)

    print(f"Base objective placed at cell {base_cell}")
    print(f"Radar objective placed at cell {radar_cell}")

    return objectives

def distance_between_cells(cell_a, cell_b):
    """
    Calculate Manhattan distance between two cells.
    """

    return abs(cell_a[0] - cell_b[0]) + abs(cell_a[1] - cell_b[1])


def is_valid_player_spawn_cell(cell_x, cell_y, map_data, game_engine, objectives, min_distance):
    """
    Check if a cell is valid for spawning the player.

    The player cannot appear:
    - outside the map
    - on a wall or obstacle
    - on another object
    - closer than min_distance to the primary objectives
    """

    if map_data is None:
        return False

    if cell_x < 0 or cell_y < 0:
        return False

    if cell_x >= map_data.width or cell_y >= map_data.height:
        return False

    if map_data.get_cell(cell_x, cell_y) != map_data.EMPTY:
        return False

    for objective in objectives:
        objective_cell_x = int(objective.x // map_data.cell_size)
        objective_cell_y = int(objective.y // map_data.cell_size)

        distance = distance_between_cells(
            (cell_x, cell_y),
            (objective_cell_x, objective_cell_y)
        )

        if distance < min_distance:
            return False

    if game_engine is not None:
        for obj in game_engine.get_game_objects():
            if not getattr(obj, "active", True):
                continue

            if getattr(obj, "tag", None) == "player":
                continue

            obj_cell_x = int(obj.x // map_data.cell_size)
            obj_cell_y = int(obj.y // map_data.cell_size)

            if obj_cell_x == cell_x and obj_cell_y == cell_y:
                return False

    return True


def place_player_by_min_distance(player_tank, game_engine, level_manager, objectives, min_distance=8):
    """
    Place the player according to the editable min_distance value.

    If min_distance is low, the player appears closer to the objectives.
    If min_distance is high, the player appears farther from the objectives.
    """

    map_data = level_manager.map_data

    if map_data is None:
        return

    valid_cells = []

    for y in range(1, map_data.height - 1):
        for x in range(1, map_data.width - 1):
            if is_valid_player_spawn_cell(
                x,
                y,
                map_data,
                game_engine,
                objectives,
                min_distance
            ):
                valid_cells.append((x, y))

    if not valid_cells:
        print("Warning: No valid player spawn found. Keeping current position.")
        return

    def total_distance_to_objectives(cell):
        total = 0

        for objective in objectives:
            objective_cell = (
                int(objective.x // map_data.cell_size),
                int(objective.y // map_data.cell_size)
            )

            total += distance_between_cells(cell, objective_cell)

        return total

    valid_cells.sort(
        key=total_distance_to_objectives
    )

    best_cells = valid_cells[:min(10, len(valid_cells))]
    spawn_cell = random.choice(best_cells)

    player_tank.x = spawn_cell[0] * map_data.cell_size
    player_tank.y = spawn_cell[1] * map_data.cell_size

    print(
        f"Player spawned at cell {spawn_cell} "
        f"with min_distance={min_distance}"
    )


def distance_between_cells(cell_a, cell_b):
    """
    Calculate Manhattan distance between two cells.
    """

    return abs(cell_a[0] - cell_b[0]) + abs(cell_a[1] - cell_b[1])


def is_valid_player_spawn_cell(cell_x, cell_y, map_data, game_engine, objectives, min_distance=8):
    """
    Check if a cell is valid for spawning the player.
    The player cannot appear on obstacles, objects or close to primary objectives.
    """

    if map_data is None:
        return False

    if cell_x < 0 or cell_y < 0:
        return False

    if cell_x >= map_data.width or cell_y >= map_data.height:
        return False

    if map_data.get_cell(cell_x, cell_y) != map_data.EMPTY:
        return False

    for objective in objectives:
        objective_cell_x = int(objective.x // map_data.cell_size)
        objective_cell_y = int(objective.y // map_data.cell_size)

        distance = distance_between_cells(
            (cell_x, cell_y),
            (objective_cell_x, objective_cell_y)
        )

        if distance < min_distance:
            return False

    if game_engine is not None:
        for obj in game_engine.get_game_objects():
            if not getattr(obj, "active", True):
                continue

            if getattr(obj, "tag", None) == "player":
                continue

            obj_cell_x = int(obj.x // map_data.cell_size)
            obj_cell_y = int(obj.y // map_data.cell_size)

            if obj_cell_x == cell_x and obj_cell_y == cell_y:
                return False

    return True


def place_player_far_from_objectives(player_tank, game_engine, level_manager, objectives, min_distance=8):
    """
    Place the player far from the primary objectives.
    """

    map_data = level_manager.map_data

    if map_data is None:
        return

    valid_cells = []

    for y in range(1, map_data.height - 1):
        for x in range(1, map_data.width - 1):
            if is_valid_player_spawn_cell(
                x,
                y,
                map_data,
                game_engine,
                objectives,
                min_distance
            ):
                valid_cells.append((x, y))

    if not valid_cells:
        print("Warning: No far spawn found for player. Keeping current position.")
        return

    # Choose one of the farthest cells from the objectives.
    def total_distance_to_objectives(cell):
        total = 0

        for objective in objectives:
            objective_cell = (
                int(objective.x // map_data.cell_size),
                int(objective.y // map_data.cell_size)
            )

            total += distance_between_cells(cell, objective_cell)

        return total

    valid_cells.sort(
        key=total_distance_to_objectives,
        reverse=True
    )

    # Pick among the best far cells so it is not always exactly the same.
    best_cells = valid_cells[:min(10, len(valid_cells))]
    spawn_cell = random.choice(best_cells)

    player_tank.x = spawn_cell[0] * map_data.cell_size
    player_tank.y = spawn_cell[1] * map_data.cell_size

    print(f"Player spawned far from objectives at cell {spawn_cell}")


def find_guard_cell_near_objectives(objectives, map_data):
    """
    Find a free cell near the group of primary objectives.
    """

    if not objectives or map_data is None:
        return None

    center_x = sum(int(obj.x // map_data.cell_size) for obj in objectives) // len(objectives)
    center_y = sum(int(obj.y // map_data.cell_size) for obj in objectives) // len(objectives)

    for radius in range(1, 6):
        possible_cells = []

        for dx in range(-radius, radius + 1):
            possible_cells.append((center_x + dx, center_y - radius))
            possible_cells.append((center_x + dx, center_y + radius))

        for dy in range(-radius + 1, radius):
            possible_cells.append((center_x - radius, center_y + dy))
            possible_cells.append((center_x + radius, center_y + dy))

        random.shuffle(possible_cells)

        for cell_x, cell_y in possible_cells:
            if cell_x < 0 or cell_y < 0:
                continue

            if cell_x >= map_data.width or cell_y >= map_data.height:
                continue

            if map_data.get_cell(cell_x, cell_y) != map_data.EMPTY:
                continue

            return cell_x, cell_y

    return None


def assign_single_guard_to_objectives(enemy_tanks, objectives, map_data):
    """
    Assign only one enemy tank to guard both primary objectives.
    The guardian appears near the objectives and is limited to that area.
    """

    if not enemy_tanks or not objectives or map_data is None:
        return None

    available_enemies = [
        enemy for enemy in enemy_tanks
        if enemy is not None and enemy.active
    ]

    if not available_enemies:
        return None

    guardian = random.choice(available_enemies)

    guard_cell = find_guard_cell_near_objectives(objectives, map_data)

    if guard_cell is not None:
        guardian.x = guard_cell[0] * map_data.cell_size
        guardian.y = guard_cell[1] * map_data.cell_size

    center_x = sum(objective.x for objective in objectives) / len(objectives)
    center_y = sum(objective.y for objective in objectives) / len(objectives)

    guardian.is_objective_guard = True
    guardian.guarded_objectives = objectives
    guardian.guard_center_x = center_x
    guardian.guard_center_y = center_y
    guardian.guard_limit_radius = 180

    print(
        f"One guardian assigned to both objectives: "
        f"{getattr(guardian, 'enemy_type', 'enemy')}"
    )

    return guardian



def keep_guardian_near_objectives(enemy_tank, map_data):
    """
    Keep the objective guardian close to the primary objectives.
    If the guardian moves too far away, it is returned near the objectives.
    """

    if enemy_tank is None:
        return

    if not getattr(enemy_tank, "active", True):
        return

    if not getattr(enemy_tank, "is_objective_guard", False):
        return

    if not hasattr(enemy_tank, "guard_center_x"):
        return

    dx = enemy_tank.x - enemy_tank.guard_center_x
    dy = enemy_tank.y - enemy_tank.guard_center_y

    distance = math.sqrt(dx * dx + dy * dy)

    if distance <= enemy_tank.guard_limit_radius:
        return

    objectives = getattr(enemy_tank, "guarded_objectives", [])

    guard_cell = find_guard_cell_near_objectives(
        objectives,
        map_data
    )

    if guard_cell is not None:
        enemy_tank.x = guard_cell[0] * map_data.cell_size
        enemy_tank.y = guard_cell[1] * map_data.cell_size

    enemy_tank.current_move_direction = None

    if hasattr(enemy_tank, "state"):
        enemy_tank.state = "patrol"

        

def find_guard_cell_around_objective(objective, map_data, used_cells=None):
    """
    Find a free cell near an objective where a guardian tank can be placed.
    """

    if used_cells is None:
        used_cells = set()

    objective_cell_x = int(objective.x // map_data.cell_size)
    objective_cell_y = int(objective.y // map_data.cell_size)

    for radius in range(1, 5):
        possible_cells = []

        for dx in range(-radius, radius + 1):
            possible_cells.append((objective_cell_x + dx, objective_cell_y - radius))
            possible_cells.append((objective_cell_x + dx, objective_cell_y + radius))

        for dy in range(-radius + 1, radius):
            possible_cells.append((objective_cell_x - radius, objective_cell_y + dy))
            possible_cells.append((objective_cell_x + radius, objective_cell_y + dy))

        random.shuffle(possible_cells)

        for cell_x, cell_y in possible_cells:
            if cell_x < 0 or cell_y < 0:
                continue

            if cell_x >= map_data.width or cell_y >= map_data.height:
                continue

            if (cell_x, cell_y) in used_cells:
                continue

            if map_data.get_cell(cell_x, cell_y) != map_data.EMPTY:
                continue

            return cell_x, cell_y

    return None


def assign_objective_guards(enemy_tanks, objectives, map_data):
    """
    Assign exactly one enemy tank to defend each primary objective.
    """

    if not enemy_tanks or not objectives or map_data is None:
        return

    available_enemies = [
        enemy for enemy in enemy_tanks
        if enemy is not None and enemy.active
    ]

    used_cells = set()

    for objective in objectives:
        if not available_enemies:
            break

        guardian = random.choice(available_enemies)
        available_enemies.remove(guardian)

        guard_cell = find_guard_cell_around_objective(
            objective,
            map_data,
            used_cells
        )

        if guard_cell is not None:
            used_cells.add(guard_cell)

            guardian.x = guard_cell[0] * map_data.cell_size
            guardian.y = guard_cell[1] * map_data.cell_size

        if hasattr(guardian, "set_guard_objective"):
            guardian.set_guard_objective(objective)
        else:
            guardian.is_guardian = True
            guardian.guard_objective = objective

        print(
            f"Guardian assigned: {getattr(guardian, 'enemy_type', 'enemy')} "
            f"guards {getattr(objective, 'objective_type', 'objective')}"
        )


def all_objectives_destroyed(objectives):
    """
    Check if all primary objectives were destroyed.
    """

    if not objectives:
        return False

    return all(not objective.active for objective in objectives)


def move_projectile(projectile, delta_time):
    """
    Move a projectile using the four basic directions.
    """

    rad = math.radians(projectile.direction)

    dx = math.sin(rad) * projectile.speed * delta_time * 60
    dy = -math.cos(rad) * projectile.speed * delta_time * 60

    projectile.x += dx
    projectile.y += dy


def projectile_hits_map(projectile, map_data):
    """
    Check if a projectile hits a wall or leaves the map.
    """

    if map_data is None:
        return False

    cell_size = map_data.cell_size

    center_x = projectile.x + projectile.width / 2
    center_y = projectile.y + projectile.height / 2

    cell_x = int(center_x // cell_size)
    cell_y = int(center_y // cell_size)

    if cell_x < 0 or cell_y < 0:
        return True

    if cell_x >= map_data.width or cell_y >= map_data.height:
        return True

    return map_data.is_obstacle_at(cell_x, cell_y)


def handle_projectile_collision(projectile, possible_targets, visual_effects=None):
    """
    Check projectile collisions against tanks and objectives.

    Rules:
    - Player bullets can damage enemy tanks and objectives.
    - Enemy bullets can damage only the player.
    - Enemy bullets cannot damage other enemy tanks.
    - A projectile cannot damage its owner.
    """

    projectile_owner = getattr(projectile, "owner", None)
    owner_tag = getattr(projectile_owner, "tag", None)

    for target in possible_targets:
        if target is None:
            continue

        if not getattr(target, "active", True):
            continue

        if target == projectile_owner:
            continue

        if getattr(target, "tag", None) == "projectile":
            continue

        target_tag = getattr(target, "tag", None)

        # Enemy bullets cannot damage enemy tanks.
        if owner_tag == "enemy" and target_tag == "enemy":
            continue

        # Enemy bullets should not damage objectives.
        if owner_tag == "enemy" and target_tag == "objective":
            continue

        # Player bullets should not damage the player.
        if owner_tag == "player" and target_tag == "player":
            continue

        if projectile.check_collision_with_object(target):
            if hasattr(target, "take_damage"):
                target.take_damage(projectile.damage)

            projectile.active = False

            if visual_effects:
                impact_x = projectile.x + projectile.width / 2
                impact_y = projectile.y + projectile.height / 2

                if hasattr(visual_effects, "add_impact"):
                    visual_effects.add_impact(impact_x, impact_y, size=12)

            return True

    return False


def render_map_safe(map_renderer, screen, map_data):
    """
    Render the map, supporting different renderer method signatures.
    """

    if map_renderer is None or map_data is None:
        return

    if hasattr(map_renderer, "render_map"):
        try:
            map_renderer.render_map(screen, map_data)
        except TypeError:
            map_renderer.render_map(map_data)
        return

    if hasattr(map_renderer, "render"):
        try:
            map_renderer.render(screen, map_data)
        except TypeError:
            map_renderer.render(map_data)


def render_projectile_safe(projectile_renderer, screen, projectile):
    """
    Render a projectile, supporting different renderer method signatures.
    """

    if projectile_renderer is None:
        projectile.render(screen)
        return

    if hasattr(projectile_renderer, "render_projectile"):
        try:
            projectile_renderer.render_projectile(screen, projectile)
        except TypeError:
            projectile_renderer.render_projectile(projectile)
        return

    if hasattr(projectile_renderer, "render"):
        try:
            projectile_renderer.render(screen, projectile)
        except TypeError:
            projectile_renderer.render(projectile)
        return

    projectile.render(screen)


def render_center_message(screen, title, subtitle=None, extra=None):
    """
    Render a centered message on the screen.
    """

    overlay = pygame.Surface(
        (screen.get_width(), screen.get_height()),
        pygame.SRCALPHA
    )
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    font_title = pygame.font.SysFont("Arial", 48, bold=True)
    font_subtitle = pygame.font.SysFont("Arial", 26)
    font_extra = pygame.font.SysFont("Arial", 22)

    title_surface = font_title.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 - 70)
    )
    screen.blit(title_surface, title_rect)

    if subtitle:
        subtitle_surface = font_subtitle.render(subtitle, True, (230, 230, 230))
        subtitle_rect = subtitle_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 - 10)
        )
        screen.blit(subtitle_surface, subtitle_rect)

    if extra:
        extra_surface = font_extra.render(extra, True, (200, 200, 200))
        extra_rect = extra_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 + 45)
        )
        screen.blit(extra_surface, extra_rect)


def render_start_screen(screen):
    """
    Render the initial start screen with a start button.
    """

    screen.fill((20, 20, 20))

    title_font = pygame.font.SysFont("Arial", 54, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 26)
    button_font = pygame.font.SysFont("Arial", 30, bold=True)

    title_surface = title_font.render("TANK ATTACK", True, (255, 255, 255))
    title_rect = title_surface.get_rect(
        center=(screen.get_width() // 2, 170)
    )
    screen.blit(title_surface, title_rect)

    subtitle_surface = subtitle_font.render(
        "Destruye los objetivos primarios y sobrevive",
        True,
        (220, 220, 220)
    )
    subtitle_rect = subtitle_surface.get_rect(
        center=(screen.get_width() // 2, 230)
    )
    screen.blit(subtitle_surface, subtitle_rect)

    button_rect = pygame.Rect(0, 0, 240, 70)
    button_rect.center = (screen.get_width() // 2, 340)

    pygame.draw.rect(screen, (40, 120, 220), button_rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=12)

    button_text = button_font.render("INICIAR JUEGO", True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)

    instruction_surface = subtitle_font.render(
        "También puede presionar ENTER para iniciar",
        True,
        (180, 180, 180)
    )
    instruction_rect = instruction_surface.get_rect(
        center=(screen.get_width() // 2, 430)
    )
    screen.blit(instruction_surface, instruction_rect)

    return button_rect



def render_hud(screen, current_level, player_tank, objectives, player_lives):
    """
    Render basic HUD information.
    """

    font = pygame.font.SysFont("Arial", 22, bold=True)

    level_text = font.render(f"Nivel: {current_level}/{MAX_LEVEL}", True, (255, 255, 255))
    screen.blit(level_text, (10, 10))

    if player_tank:
        health_text = font.render(f"Salud: {player_tank.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 38))

    lives_text = font.render(f"Vidas: {player_lives}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 66))

    remaining_objectives = len([
        obj for obj in objectives
        if getattr(obj, "active", True)
    ])

    objective_text = font.render(
        f"Objetivos restantes: {remaining_objectives}",
        True,
        (255, 255, 255)
    )
    screen.blit(objective_text, (10, 94))


def get_cell_position(obj, map_data):
    """
    Convert an object's pixel position to map cell position.
    """

    cell_x = int(obj.x // map_data.cell_size)
    cell_y = int(obj.y // map_data.cell_size)

    return cell_x, cell_y


def get_map_walls_for_prolog(map_data):
    """
    Get all blocked cells from the map to send them to Prolog.
    """

    walls = []

    if map_data is None:
        return walls

    for y in range(map_data.height):
        for x in range(map_data.width):
            if map_data.is_obstacle_at(x, y):
                walls.append((x, y))

    return walls


def get_objectives_for_prolog(objectives, map_data):
    """
    Convert game objectives to Prolog facts.
    """

    prolog_objectives = []

    for index, objective in enumerate(objectives, start=1):
        cell_x, cell_y = get_cell_position(objective, map_data)

        objective_type = getattr(objective, "objective_type", "")

        if objective_type == "radar":
            prolog_type = "radar"
        else:
            prolog_type = "bunker"

        prolog_objectives.append(
            (
                index,
                cell_x,
                cell_y,
                prolog_type
            )
        )

    return prolog_objectives


def get_enemy_tanks_for_prolog(enemy_tanks, map_data):
    """
    Convert enemy tanks to Prolog facts.
    """

    prolog_tanks = []

    for index, enemy in enumerate(enemy_tanks, start=1):
        enemy.prolog_id = index

        cell_x, cell_y = get_cell_position(enemy, map_data)

        enemy_type = getattr(enemy, "enemy_type", "light")

        prolog_tanks.append(
            (
                index,
                cell_x,
                cell_y,
                enemy_type,
                int(enemy.health)
            )
        )

    return prolog_tanks


def load_current_level_in_prolog(prolog_service, level_manager, objectives, player_tank):
    """
    Load the current game level into Prolog.
    """

    map_data = level_manager.map_data

    if map_data is None:
        return

    player_cell_x, player_cell_y = get_cell_position(player_tank, map_data)

    walls = get_map_walls_for_prolog(map_data)

    prolog_objectives = get_objectives_for_prolog(
        objectives,
        map_data
    )

    prolog_tanks = get_enemy_tanks_for_prolog(
        level_manager.enemy_tanks,
        map_data
    )

    prolog_service.cargar_nivel(
        ancho=map_data.width,
        alto=map_data.height,
        muros=walls,
        objetivos=prolog_objectives,
        tanques=prolog_tanks,
        jugador=(player_cell_x, player_cell_y)
    )

    print("Level loaded in Prolog")


def move_enemy_away_from_player(enemy_tank, player_tank, delta_time, map_data):
    """
    Move the enemy tank away from the player.
    Used when Prolog returns the action 'retroceder'.
    """

    dx = enemy_tank.x - player_tank.x
    dy = enemy_tank.y - player_tank.y

    if abs(dx) > abs(dy):
        if dx >= 0:
            enemy_tank.set_direction(enemy_tank.RIGHT)
            moved = enemy_tank.move_right(delta_time, map_data)

            if not moved:
                if dy >= 0:
                    enemy_tank.set_direction(enemy_tank.DOWN)
                    return enemy_tank.move_down(delta_time, map_data)

                enemy_tank.set_direction(enemy_tank.UP)
                return enemy_tank.move_up(delta_time, map_data)

            return moved

        enemy_tank.set_direction(enemy_tank.LEFT)
        moved = enemy_tank.move_left(delta_time, map_data)

        if not moved:
            if dy >= 0:
                enemy_tank.set_direction(enemy_tank.DOWN)
                return enemy_tank.move_down(delta_time, map_data)

            enemy_tank.set_direction(enemy_tank.UP)
            return enemy_tank.move_up(delta_time, map_data)

        return moved

    if dy >= 0:
        enemy_tank.set_direction(enemy_tank.DOWN)
        moved = enemy_tank.move_down(delta_time, map_data)

        if not moved:
            if dx >= 0:
                enemy_tank.set_direction(enemy_tank.RIGHT)
                return enemy_tank.move_right(delta_time, map_data)

            enemy_tank.set_direction(enemy_tank.LEFT)
            return enemy_tank.move_left(delta_time, map_data)

        return moved

    enemy_tank.set_direction(enemy_tank.UP)
    moved = enemy_tank.move_up(delta_time, map_data)

    if not moved:
        if dx >= 0:
            enemy_tank.set_direction(enemy_tank.RIGHT)
            return enemy_tank.move_right(delta_time, map_data)

        enemy_tank.set_direction(enemy_tank.LEFT)
        return enemy_tank.move_left(delta_time, map_data)

    return moved


def respawn_player(player_tank, game_engine, level_manager, objectives, level_config):
    """
    Respawn the player after losing one life.
    """

    player_tank.active = True
    player_tank.health = level_config.get("player_health", 100)
    player_tank.max_health = level_config.get("player_health", 100)
    player_tank.speed = level_config.get("player_speed", 5)

    place_player_by_min_distance(
        player_tank,
        game_engine,
        level_manager,
        objectives,
        min_distance=level_config.get("player_min_distance", 8)
    )

    print("Player respawned")
        


def create_game_state(game_engine, level_number):
    """
    Create or recreate the current game state.

    Returns:
        tuple: player_tank, level_manager, objectives, projectiles, visual_effects
    """

    if hasattr(game_engine, "clear_game_objects"):
        game_engine.clear_game_objects()
    else:
        game_engine.game_objects = []

    player_tank = PlayerTank(400, 300, health=100, speed=5)
    game_engine.add_game_object(player_tank)

    if game_engine.sound_manager:
        player_tank.set_sound_manager(game_engine.sound_manager)

    level_manager = LevelManager(game_engine, max_level=MAX_LEVEL)
    game_engine.level_manager = level_manager

    # Try to tell the LevelManager which level is active.
    if hasattr(level_manager, "current_level"):
        level_manager.current_level = level_number

    if hasattr(level_manager, "level_number"):
        level_manager.level_number = level_number

    level_manager.initialize(player_tank, level_number)

    # Set again after initialize, in case initialize resets it.
    if hasattr(level_manager, "current_level"):
        level_manager.current_level = level_number

    if hasattr(level_manager, "level_number"):
        level_manager.level_number = level_number

    screen_editor = ScreenEditor()
    level_config = screen_editor.load_level_config(level_number)

    player_tank.health = level_config.get("player_health", 100)
    player_tank.max_health = level_config.get("player_health", 100)

    objectives = create_level_objectives(game_engine, level_manager, level_number)

    place_player_by_min_distance(
        player_tank,
        game_engine,
        level_manager,
        objectives,
        min_distance=level_config["player_min_distance"]
    )

    guardian = assign_single_guard_to_objectives(
        level_manager.enemy_tanks,
        objectives,
        level_manager.map_data
    )

    if guardian is not None:
        guardian.guard_limit_radius = level_config["guardian_radius"]

    prolog_service = PrologService("logic.pl")

    load_current_level_in_prolog(
            prolog_service,
            level_manager,
            objectives,
            player_tank
        )

    projectiles = []

    visual_effects = VisualEffectsManager()

    return player_tank, level_manager, objectives, projectiles, visual_effects,prolog_service


def render_game_scene(
    game_engine,
    map_renderer,
    tank_renderer,
    projectile_renderer,
    objective_renderer,
    visual_effects,
    player_tank,
    level_manager,
    objectives,
    projectiles,
    current_level,
    player_lives
):
    """
    Render the complete game scene.
    """

    game_engine.screen.fill((0, 0, 0))

    render_map_safe(
        map_renderer,
        game_engine.screen,
        level_manager.map_data
    )

    for objective in objectives:
        if objective.active:
            objective_renderer.render_objective(
                game_engine.screen,
                objective
            )

    if player_tank.active:
        tank_renderer.render_tank(game_engine.screen, player_tank)

    for enemy_tank in level_manager.enemy_tanks:
        if enemy_tank.active:
            tank_renderer.render_tank(game_engine.screen, enemy_tank)

    for projectile in projectiles:
        if projectile.active:
            render_projectile_safe(
                projectile_renderer,
                game_engine.screen,
                projectile
            )

    if hasattr(visual_effects, "render"):
        visual_effects.render(game_engine.screen)

    render_hud(game_engine.screen, current_level, player_tank, objectives, player_lives)


def main():
    """
    Main function to start the tank game.
    """

    try:
        game_engine = GameEngine(
            width=800,
            height=600,
            title="Tank Attack",
            target_fps=60
        )

        game_engine.initialize()

        map_renderer = EnhancedMapRenderer(game_engine.renderer)
        tank_renderer = EnhancedTankRenderer(game_engine.renderer)
        projectile_renderer = EnhancedProjectileRenderer(game_engine.renderer)
        objective_renderer = ObjectiveRenderer()

        input_handler = InputHandler()

        current_level = 1

        player_tank, level_manager, objectives, projectiles, visual_effects, prolog_service = create_game_state(
            game_engine,
            current_level
        )
        
        player_lives = 3

        game_over = False
        level_completed = False
        final_victory = False
        game_started = False

        game_engine.running = True

        while game_engine.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_engine.running = False
                
                elif not game_started:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            game_started = True

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            start_button_rect = pygame.Rect(0, 0, 240, 70)
                            start_button_rect.center = (
                                game_engine.screen.get_width() // 2,
                                340
                            )

                            if start_button_rect.collidepoint(mouse_pos):
                                game_started = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_engine.running = False

                    elif event.key == pygame.K_r:
                        if final_victory:
                            current_level = 1

                        player_tank, level_manager, objectives, projectiles, visual_effects, prolog_service = create_game_state(
                            game_engine,
                            current_level
                        )
                        player_lives = 3

                        game_over = False
                        level_completed = False
                        final_victory = False

                    elif event.key == pygame.K_RETURN and level_completed:
                        if current_level < MAX_LEVEL:
                            current_level += 1

                            player_tank, level_manager, objectives, projectiles, visual_effects, prolog_service = create_game_state(
                                game_engine,
                                current_level
                            )
                            player_lives = 3

                            game_over = False
                            level_completed = False
                            final_victory = False

                        else:
                            level_completed = False
                            final_victory = True

            game_engine.calculate_delta_time()
            input_handler.process_events()

            if not game_started:
                render_start_screen(game_engine.screen)
                pygame.display.flip()
                game_engine.clock.tick(game_engine.target_fps)
                continue

            # -------------------------------------------------
            # If the game ended or level was completed
            # -------------------------------------------------
            if game_over or level_completed or final_victory:
                render_game_scene(
                    game_engine,
                    map_renderer,
                    tank_renderer,
                    projectile_renderer,
                    objective_renderer,
                    visual_effects,
                    player_tank,
                    level_manager,
                    objectives,
                    projectiles,
                    current_level,
                    player_lives
                    
                )

                if game_over:
                    render_center_message(
                        game_engine.screen,
                        "GAME OVER",
                        "El tanque del jugador fue destruido",
                        "Presione R para reiniciar el nivel o ESC para salir"
                    )

                elif level_completed:
                    if current_level < MAX_LEVEL:
                        render_center_message(
                            game_engine.screen,
                            "NIVEL COMPLETADO",
                            "Todos los objetivos primarios fueron destruidos",
                            "Presione ENTER para avanzar, R para reiniciar o ESC para salir"
                        )
                    else:
                        render_center_message(
                            game_engine.screen,
                            "NIVEL 3 COMPLETADO",
                            "Ha destruido todos los objetivos del último nivel",
                            "Presione ENTER para ver la victoria final"
                        )

                elif final_victory:
                    render_center_message(
                        game_engine.screen,
                        "VICTORIA FINAL",
                        "Ha completado los 3 niveles del juego",
                        "Presione R para jugar de nuevo o ESC para salir"
                    )

                pygame.display.flip()
                game_engine.clock.tick(game_engine.target_fps)
                continue

            # -------------------------------------------------
            # Update player
            # -------------------------------------------------
            if player_tank.active:
                new_projectile = player_tank.update(
                    game_engine.delta_time,
                    level_manager.map_data,
                    input_handler
                )

                if new_projectile:
                    new_projectile.age = 0.0
                    projectiles.append(new_projectile)
                    game_engine.add_game_object(new_projectile)

                    muzzle_x = (
                        player_tank.x
                        + player_tank.width // 2
                        + math.sin(math.radians(player_tank.direction))
                        * (player_tank.height // 2 + 5)
                    )

                    muzzle_y = (
                        player_tank.y
                        + player_tank.height // 2
                        - math.cos(math.radians(player_tank.direction))
                        * (player_tank.height // 2 + 5)
                    )

                    visual_effects.add_muzzle_flash(
                        muzzle_x,
                        muzzle_y,
                        player_tank.direction
                    )

            # -------------------------------------------------
            # Update enemies
            # -------------------------------------------------

                if player_tank.active:
                    player_cell_x, player_cell_y = get_cell_position(
                        player_tank,
                        level_manager.map_data
                )

                prolog_service.actualizar_jugador(
                    player_cell_x,
                    player_cell_y
                )




            game_objects_for_ai = (
                [player_tank]
                + level_manager.enemy_tanks
                + objectives
                + projectiles
            )

            for enemy_tank in level_manager.enemy_tanks[:]:
                if enemy_tank.active:

                    if not hasattr(enemy_tank, "prolog_timer"):
                        enemy_tank.prolog_timer = random.uniform(0.0, 0.5)
                        enemy_tank.prolog_action = "acercarse"
                        enemy_tank.prolog_route = []

                    enemy_tank.prolog_timer += game_engine.delta_time

                    if enemy_tank.prolog_timer >= 1.0:
                        enemy_cell_x, enemy_cell_y = get_cell_position(
                            enemy_tank,
                            level_manager.map_data
                        )

                        prolog_service.actualizar_tanque(
                            enemy_tank.prolog_id,
                            enemy_cell_x,
                            enemy_cell_y,
                            int(enemy_tank.health)
                        )

                        prolog_result = prolog_service.obtener_accion_y_ruta(
                            enemy_tank.prolog_id
                        )

                        enemy_tank.prolog_action = prolog_result["accion"]
                        enemy_tank.prolog_route = prolog_result["ruta"]

                        print(
                            f"[PROLOG] Tanque {enemy_tank.prolog_id} "
                            f"vida={enemy_tank.health} "
                            f"decision={enemy_tank.prolog_action} "
                            f"ruta={enemy_tank.prolog_route}"
                        )

                        enemy_tank.prolog_timer = 0

                    new_projectile = None

                    action = str(getattr(enemy_tank, "prolog_action", ""))

                    last_action = getattr(enemy_tank, "last_printed_action", None)

                    if action != last_action:
                        print(
                            f"[PYTHON] Tanque {enemy_tank.prolog_id} "
                            f"obedece a Prolog: {action}"
                        )

                        enemy_tank.last_printed_action = action

                    if action.startswith("retroceder"):
                        move_enemy_away_from_player(
                            enemy_tank,
                            player_tank,
                            game_engine.delta_time,
                            level_manager.map_data
                        )

                    elif getattr(enemy_tank, "prolog_action", "") == "atacar":
                        new_projectile = enemy_tank.update(
                            game_engine.delta_time,
                            level_manager.map_data,
                            game_objects_for_ai
                        )

                    else:
                        new_projectile = enemy_tank.update(
                            game_engine.delta_time,
                            level_manager.map_data,
                            game_objects_for_ai
                        )

                    keep_guardian_near_objectives(
                        enemy_tank,
                        level_manager.map_data
                    )

                    if new_projectile:
                        new_projectile.age = 0.0
                        projectiles.append(new_projectile)
                        game_engine.add_game_object(new_projectile)

                        muzzle_x = (
                            enemy_tank.x
                            + enemy_tank.width // 2
                            + math.sin(math.radians(enemy_tank.direction))
                            * (enemy_tank.height // 2 + 5)
                        )

                        muzzle_y = (
                            enemy_tank.y
                            + enemy_tank.height // 2
                            - math.cos(math.radians(enemy_tank.direction))
                            * (enemy_tank.height // 2 + 5)
                        )

                        visual_effects.add_muzzle_flash(
                            muzzle_x,
                            muzzle_y,
                            enemy_tank.direction
                        )

            # -------------------------------------------------
            # Update projectiles
            # -------------------------------------------------
            for projectile in projectiles[:]:
                if not projectile.active:
                    if projectile in projectiles:
                        projectiles.remove(projectile)

                    if projectile in game_engine.game_objects:
                        game_engine.remove_game_object(projectile)

                    continue

                if hasattr(projectile, "age"):
                    projectile.age += game_engine.delta_time

                move_projectile(projectile, game_engine.delta_time)

                if projectile_hits_map(projectile, level_manager.map_data):
                    projectile.active = False

                    if projectile in projectiles:
                        projectiles.remove(projectile)

                    if projectile in game_engine.game_objects:
                        game_engine.remove_game_object(projectile)

                    continue

                possible_targets = (
                    [player_tank]
                    + level_manager.enemy_tanks
                    + objectives
                )

                hit = handle_projectile_collision(
                    projectile,
                    possible_targets,
                    visual_effects
                )

                if hit:
                    if projectile in projectiles:
                        projectiles.remove(projectile)

                    if projectile in game_engine.game_objects:
                        game_engine.remove_game_object(projectile)

                    continue

            # -------------------------------------------------
            # Remove inactive enemies
            # -------------------------------------------------
            level_manager.enemy_tanks = [
                enemy for enemy in level_manager.enemy_tanks
                if enemy.active
            ]

            # -------------------------------------------------
            # Update visual effects
            # -------------------------------------------------
            if hasattr(visual_effects, "update"):
                visual_effects.update(game_engine.delta_time)

            # -------------------------------------------------
            # Check game over
            # -------------------------------------------------
            if not player_tank.active or player_tank.health <= 0:
                player_lives -= 1

                if player_lives > 0:
                    level_config = ScreenEditor().load_level_config(current_level)

                    respawn_player(
                        player_tank,
                        game_engine,
                        level_manager,
                        objectives,
                        level_config
                    )
                else:
                    game_over = True

            # -------------------------------------------------
            # Check level completed
            # -------------------------------------------------
            if all_objectives_destroyed(objectives):
                level_completed = True

            # -------------------------------------------------
            # Render
            # -------------------------------------------------
            render_game_scene(
                game_engine,
                map_renderer,
                tank_renderer,
                projectile_renderer,
                objective_renderer,
                visual_effects,
                player_tank,
                level_manager,
                objectives,
                projectiles,
                current_level,
                player_lives
            )

            pygame.display.flip()
            game_engine.clock.tick(game_engine.target_fps)

        game_engine.shutdown()

    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())