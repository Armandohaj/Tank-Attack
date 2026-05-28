"""
Main entry point for the Tank Game.
"""

import pygame
import sys
import os
import math

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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


def create_level_objectives(game_engine, level_manager, level_number):
    """
    Create the two required primary objective types for each level.
    """

    cell_size = 32

    if level_manager.map_data and hasattr(level_manager.map_data, "cell_size"):
        cell_size = level_manager.map_data.cell_size

    # Different objective positions per level.
    if level_number == 1:
        base_cell = (18, 6)
        radar_cell = (21, 12)

    elif level_number == 2:
        base_cell = (20, 5)
        radar_cell = (16, 13)

    else:
        base_cell = (22, 4)
        radar_cell = (19, 14)

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

    return objectives


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
    """

    for target in possible_targets:
        if target is None:
            continue

        if not getattr(target, "active", True):
            continue

        if target == projectile.owner:
            continue

        if getattr(target, "tag", None) == "projectile":
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


def render_hud(screen, current_level, player_tank, objectives):
    """
    Render basic HUD information.
    """

    font = pygame.font.SysFont("Arial", 22, bold=True)

    level_text = font.render(f"Nivel: {current_level}/{MAX_LEVEL}", True, (255, 255, 255))
    screen.blit(level_text, (10, 10))

    if player_tank:
        health_text = font.render(f"Vida: {player_tank.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 38))

    remaining_objectives = len([
        obj for obj in objectives
        if getattr(obj, "active", True)
    ])

    objective_text = font.render(
        f"Objetivos restantes: {remaining_objectives}",
        True,
        (255, 255, 255)
    )
    screen.blit(objective_text, (10, 66))


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

    level_manager.initialize(player_tank)

    # Set again after initialize, in case initialize resets it.
    if hasattr(level_manager, "current_level"):
        level_manager.current_level = level_number

    if hasattr(level_manager, "level_number"):
        level_manager.level_number = level_number

    objectives = create_level_objectives(game_engine, level_manager, level_number)

    projectiles = []

    visual_effects = VisualEffectsManager()

    return player_tank, level_manager, objectives, projectiles, visual_effects


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
    current_level
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

    render_hud(game_engine.screen, current_level, player_tank, objectives)


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

        player_tank, level_manager, objectives, projectiles, visual_effects = create_game_state(
            game_engine,
            current_level
        )

        game_over = False
        level_completed = False
        final_victory = False

        game_engine.running = True

        while game_engine.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_engine.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_engine.running = False

                    elif event.key == pygame.K_r:
                        if final_victory:
                            current_level = 1

                        player_tank, level_manager, objectives, projectiles, visual_effects = create_game_state(
                            game_engine,
                            current_level
                        )

                        game_over = False
                        level_completed = False
                        final_victory = False

                    elif event.key == pygame.K_RETURN and level_completed:
                        if current_level < MAX_LEVEL:
                            current_level += 1

                            player_tank, level_manager, objectives, projectiles, visual_effects = create_game_state(
                                game_engine,
                                current_level
                            )

                            game_over = False
                            level_completed = False
                            final_victory = False

                        else:
                            level_completed = False
                            final_victory = True

            game_engine.calculate_delta_time()
            input_handler.process_events()

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
                    current_level
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
            game_objects_for_ai = (
                [player_tank]
                + level_manager.enemy_tanks
                + objectives
                + projectiles
            )

            for enemy_tank in level_manager.enemy_tanks[:]:
                if enemy_tank.active:
                    new_projectile = enemy_tank.update(
                        game_engine.delta_time,
                        level_manager.map_data,
                        game_objects_for_ai
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
                current_level
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