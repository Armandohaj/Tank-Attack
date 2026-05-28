"""
Game State Manager module for the Tank Game.

This module manages the main game states:
- Playing
- Game over
- Level completed
- Final victory
- Restart current level
- Advance to next level
"""

import pygame


class GameStateManager:
    """
    Manages the game state for Tank-Attack.
    """

    def __init__(self, game_engine=None, max_level=3):
        """
        Initialize the game state manager.

        Args:
            game_engine: Optional GameEngine instance.
            max_level (int): Maximum number of levels.
        """
        self.game_engine = game_engine

        self.max_level = max_level
        self.current_level = 1

        self.game_over = False
        self.level_completed = False
        self.final_victory = False

        self.restart_requested = False
        self.next_level_requested = False
        self.exit_requested = False

        self.score = 0
        self.high_score = 0

    # ---------------------------------------------------------
    # State setters
    # ---------------------------------------------------------

    def set_game_over(self):
        """
        Set the game over state.
        """
        self.game_over = True
        self.level_completed = False
        self.final_victory = False

    def set_level_completed(self):
        """
        Set the level completed state.
        """
        self.level_completed = True
        self.game_over = False
        self.final_victory = False

    def set_final_victory(self):
        """
        Set the final victory state.
        """
        self.final_victory = True
        self.level_completed = False
        self.game_over = False

    def add_score(self, points):
        """
        Add points to the score.
        """
        self.score += points

        if self.score > self.high_score:
            self.high_score = self.score

    # ---------------------------------------------------------
    # State checks
    # ---------------------------------------------------------

    def is_playing(self):
        """
        Check if the game is currently playable.
        """
        return (
            not self.game_over
            and not self.level_completed
            and not self.final_victory
        )

    def is_game_over(self):
        """
        Check if the game is over.
        """
        return self.game_over

    def is_level_completed(self):
        """
        Check if the current level is completed.
        """
        return self.level_completed

    def is_final_victory(self):
        """
        Check if the player completed all levels.
        """
        return self.final_victory

    # ---------------------------------------------------------
    # Level control
    # ---------------------------------------------------------

    def advance_level(self):
        """
        Advance to the next level.

        Returns:
            bool: True if advanced to another level, False if final victory.
        """
        if self.current_level < self.max_level:
            self.current_level += 1
            self.clear_state_flags()
            return True

        self.set_final_victory()
        return False

    def restart_current_level(self):
        """
        Request restarting the current level.

        Important:
        The restart_requested flag must remain True so main.py can detect it.
        """
        self.clear_state_flags()
        self.restart_requested = True

    def restart_game(self):
        """
        Restart the game from level 1.

        Important:
        The restart_requested flag must remain True so main.py can detect it.
        """
        self.current_level = 1
        self.score = 0
        self.clear_state_flags()
        self.restart_requested = True

    def clear_state_flags(self):
        """
        Clear game state flags but do not clear action requests.
        """
        self.game_over = False
        self.level_completed = False
        self.final_victory = False

    def clear_action_requests(self):
        """
        Clear temporary input requests.
        """
        self.restart_requested = False
        self.next_level_requested = False
        self.exit_requested = False

    def reset(self):
        """
        Full reset.
        """
        self.current_level = 1
        self.score = 0
        self.high_score = 0

        self.game_over = False
        self.level_completed = False
        self.final_victory = False

        self.restart_requested = False
        self.next_level_requested = False
        self.exit_requested = False

    # ---------------------------------------------------------
    # Event processing
    # ---------------------------------------------------------

    def process_event(self, event):
        """
        Process one pygame event.

        Args:
            event: Pygame event.
        """
        if event.type == pygame.QUIT:
            self.exit_requested = True
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.exit_requested = True

        elif event.key == pygame.K_r:
            if self.final_victory:
                self.restart_game()
            else:
                self.restart_current_level()

        elif event.key == pygame.K_RETURN:
            if self.level_completed:
                self.next_level_requested = True

    def process_events(self, events):
        """
        Process a list of pygame events.
        """
        for event in events:
            self.process_event(event)

    # ---------------------------------------------------------
    # Automatic state update
    # ---------------------------------------------------------

    def update_from_game(self, player_tank, objectives):
        """
        Update the state based on player and objective status.

        Args:
            player_tank: Player tank object.
            objectives (list): List of primary objectives.
        """
        if not self.is_playing():
            return

        if player_tank is not None:
            if not getattr(player_tank, "active", True):
                self.set_game_over()
                return

            if getattr(player_tank, "health", 1) <= 0:
                self.set_game_over()
                return

        if objectives:
            all_destroyed = all(
                not getattr(objective, "active", True)
                for objective in objectives
            )

            if all_destroyed:
                self.set_level_completed()

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------

    def render_overlay(self, screen):
        """
        Render overlay messages depending on the current state.
        """
        if self.is_playing():
            return

        overlay = pygame.Surface(
            (screen.get_width(), screen.get_height()),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if self.game_over:
            self._render_center_message(
                screen,
                "GAME OVER",
                "El tanque del jugador fue destruido",
                "Presione R para reiniciar el nivel o ESC para salir"
            )

        elif self.level_completed:
            if self.current_level < self.max_level:
                self._render_center_message(
                    screen,
                    "NIVEL COMPLETADO",
                    "Todos los objetivos primarios fueron destruidos",
                    "Presione ENTER para avanzar, R para reiniciar o ESC para salir"
                )
            else:
                self._render_center_message(
                    screen,
                    "NIVEL 3 COMPLETADO",
                    "Ha destruido todos los objetivos del último nivel",
                    "Presione ENTER para ver la victoria final"
                )

        elif self.final_victory:
            self._render_center_message(
                screen,
                "VICTORIA FINAL",
                "Ha completado los 3 niveles del juego",
                "Presione R para jugar de nuevo o ESC para salir"
            )

    def render_hud(self, screen, player_tank, objectives):
        """
        Render basic HUD.
        """
        font = pygame.font.SysFont("Arial", 22, bold=True)

        level_text = font.render(
            f"Nivel: {self.current_level}/{self.max_level}",
            True,
            (255, 255, 255)
        )
        screen.blit(level_text, (10, 10))

        if player_tank:
            health_text = font.render(
                f"Vida: {getattr(player_tank, 'health', 0)}",
                True,
                (255, 255, 255)
            )
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

    def _render_center_message(self, screen, title, subtitle=None, extra=None):
        """
        Render a centered message.
        """
        font_title = pygame.font.SysFont("Arial", 48, bold=True)
        font_subtitle = pygame.font.SysFont("Arial", 26)
        font_extra = pygame.font.SysFont("Arial", 22)

        title_surface = font_title.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 - 70)
        )
        screen.blit(title_surface, title_rect)

        if subtitle:
            subtitle_surface = font_subtitle.render(
                subtitle,
                True,
                (230, 230, 230)
            )
            subtitle_rect = subtitle_surface.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2 - 10)
            )
            screen.blit(subtitle_surface, subtitle_rect)

        if extra:
            extra_surface = font_extra.render(
                extra,
                True,
                (200, 200, 200)
            )
            extra_rect = extra_surface.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2 + 45)
            )
            screen.blit(extra_surface, extra_rect)