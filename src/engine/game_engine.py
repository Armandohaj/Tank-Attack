"""
Game Engine module for the Tank Game.

Este motor se encarga de:
- Inicializar Pygame.
- Crear la ventana.
- Controlar el tiempo del juego.
- Guardar los objetos del juego.
- Renderizar objetos básicos.
- Manejar eventos de cierre.
- Evitar doble actualización de player, enemy y projectile.

La lógica principal del jugador, enemigos y proyectiles queda en main.py.
"""

import pygame
import time

from src.renderers.renderer import Renderer

try:
    from src.engine.game_state_manager import GameStateManager
except ImportError:
    GameStateManager = None




class GameEngine:
    """
    Main game engine class.

    Esta versión está simplificada y adaptada para el proyecto Tank-Attack.
    """

    def __init__(self, width=800, height=600, title="Tank Attack", target_fps=60):
        """
        Initialize the game engine.

        Args:
            width (int): Screen width.
            height (int): Screen height.
            title (str): Window title.
            target_fps (int): Target frames per second.
        """

        self.width = width
        self.height = height
        self.title = title
        self.target_fps = target_fps

        self.running = False
        self.clock = None
        self.screen = None
        self.renderer = None

        self.game_objects = []
        self.current_level = 1

        self.delta_time = 0
        self.last_frame_time = 0

        self.level_manager = None
        self.game_state_manager = None
        self.sound_manager = None

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(self):
        """
        Initialize pygame and the game window.

        Returns:
            bool: True if initialization was successful.
        """

        pygame.init()

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        self.clock = pygame.time.Clock()
        self.last_frame_time = time.time()

        self.renderer = Renderer(self.screen, self.target_fps)

        if GameStateManager is not None:
            self.game_state_manager = GameStateManager(self)

        

            try:
                self.sound_manager.load_sounds()
            except Exception:
                # El sonido no es obligatorio para el proyecto.
                self.sound_manager = None

        return True

    def start_game(self):
        """
        Start the game.

        Returns:
            bool: True if the game started.
        """

        if not pygame.get_init():
            if not self.initialize():
                return False

        self.running = True
        self.game_loop()
        return True

    # ---------------------------------------------------------
    # Main loop
    # ---------------------------------------------------------

    def game_loop(self):
        """
        Main game loop.

        Nota:
        Si su main.py ya tiene su propio ciclo principal, no es necesario usar este método.
        """

        while self.running:
            self.handle_events()

            if not self.running:
                break

            self.calculate_delta_time()
            self.update()
            self.render()

            self.clock.tick(self.target_fps)

        self.shutdown()

    def calculate_delta_time(self):
        """
        Calculate frame delta time.
        """

        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time

        # Evita saltos grandes si la ventana se congela por un momento.
        if self.delta_time > 0.1:
            self.delta_time = 0.1

    # ---------------------------------------------------------
    # Events
    # ---------------------------------------------------------

    def handle_events(self):
        """
        Handle pygame events.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(self):
        """
        Update game state.

        Importante:
        No actualiza player, enemy ni projectile porque esos se manejan en main.py.
        """

        self._do_update()

    def _do_update(self):
        """
        Internal update method.
        """

        map_data = None

        if self.level_manager and hasattr(self.level_manager, "map_data"):
            map_data = self.level_manager.map_data

        active_objects = [
            obj for obj in self.game_objects
            if getattr(obj, "active", True)
        ]

        for game_object in active_objects:
            tag = getattr(game_object, "tag", None)

            # Estos objetos ya se actualizan manualmente en main.py.
            if tag in ["player", "enemy", "projectile"]:
                continue

            if hasattr(game_object, "update"):
                try:
                    game_object.update(self.delta_time, map_data)
                except TypeError:
                    game_object.update(self.delta_time)

        # Elimina objetos inactivos.
        self.game_objects = [
            obj for obj in self.game_objects
            if getattr(obj, "active", True)
        ]

        # Actualiza manager de estado si existe.
        if self.game_state_manager:
            try:
                self.game_state_manager.update(self.delta_time)
            except Exception:
                pass

    # ---------------------------------------------------------
    # Render
    # ---------------------------------------------------------

    def render(self):
        """
        Render the current frame.
        """

        if self.screen is None:
            return

        self.screen.fill((0, 0, 0))

        active_objects = [
            obj for obj in self.game_objects
            if getattr(obj, "active", True)
        ]

        for obj in active_objects:
            if hasattr(obj, "render"):
                obj.render(self.screen)

        if self.game_state_manager:
            try:
                self.game_state_manager.render(self.renderer)
            except Exception:
                pass

        pygame.display.flip()

    # ---------------------------------------------------------
    # Game object management
    # ---------------------------------------------------------

    def add_game_object(self, game_object):
        """
        Add one game object.
        """

        if game_object not in self.game_objects:
            self.game_objects.append(game_object)

    def add_game_objects(self, game_objects):
        """
        Add multiple game objects.
        """

        for obj in game_objects:
            self.add_game_object(obj)

    def remove_game_object(self, game_object):
        """
        Remove one game object.
        """

        if game_object in self.game_objects:
            self.game_objects.remove(game_object)

    def remove_game_objects(self, game_objects):
        """
        Remove multiple game objects.
        """

        self.game_objects = [
            obj for obj in self.game_objects
            if obj not in game_objects
        ]

    def clear_game_objects(self):
        """
        Remove all game objects.
        """

        self.game_objects = []

    def get_game_objects(self, object_type=None):
        """
        Get active game objects.

        Args:
            object_type: Optional class type to filter objects.

        Returns:
            list: Active game objects.
        """

        active_objects = [
            obj for obj in self.game_objects
            if getattr(obj, "active", True)
        ]

        if object_type is None:
            return active_objects

        return [
            obj for obj in active_objects
            if isinstance(obj, object_type)
        ]

    def get_game_object_count(self, object_type=None):
        """
        Get active object count.
        """

        return len(self.get_game_objects(object_type))

    def find_game_objects_by_tag(self, tag):
        """
        Find active objects by tag.
        """

        return [
            obj for obj in self.game_objects
            if getattr(obj, "tag", None) == tag
            and getattr(obj, "active", True)
        ]

    def find_game_object_by_property(self, property_name, property_value):
        """
        Find first active object with a specific property value.
        """

        for obj in self.game_objects:
            if not getattr(obj, "active", True):
                continue

            if hasattr(obj, property_name):
                if getattr(obj, property_name) == property_value:
                    return obj

        return None

    # ---------------------------------------------------------
    # Collision helpers
    # ---------------------------------------------------------

    def check_collision(self, obj1, obj2):
        """
        Check collision between two objects.
        """

        if obj1 is None or obj2 is None:
            return False

        if not getattr(obj1, "active", True):
            return False

        if not getattr(obj2, "active", True):
            return False

        if hasattr(obj1, "get_rect") and hasattr(obj2, "get_rect"):
            return obj1.get_rect().colliderect(obj2.get_rect())

        if not all(hasattr(obj, "x") and hasattr(obj, "y") for obj in [obj1, obj2]):
            return False

        obj1_width = getattr(obj1, "width", 32)
        obj1_height = getattr(obj1, "height", 32)

        obj2_width = getattr(obj2, "width", 32)
        obj2_height = getattr(obj2, "height", 32)

        return (
            obj1.x < obj2.x + obj2_width and
            obj1.x + obj1_width > obj2.x and
            obj1.y < obj2.y + obj2_height and
            obj1.y + obj1_height > obj2.y
        )

    # ---------------------------------------------------------
    # Level and state helpers
    # ---------------------------------------------------------

    def change_level(self, level_number):
        """
        Change current level.
        """

        self.current_level = level_number

    def restart_game(self):
        """
        Restart game state.
        """

        self.current_level = 1
        self.clear_game_objects()

        if self.game_state_manager:
            try:
                self.game_state_manager.reset()
                self.game_state_manager.restart_requested = False
            except Exception:
                pass

        if self.level_manager:
            try:
                self.level_manager.reset()
            except Exception:
                pass

    # ---------------------------------------------------------
    # Compatibility methods
    # ---------------------------------------------------------

    def set_performance_options(
        self,
        spatial_partitioning=None,
        viewport_culling=None,
        render_batching=None,
        performance_monitoring=None
    ):
        """
        Compatibility method.

        Esta versión simplificada no usa esas optimizaciones,
        pero se deja el método para evitar errores si otro archivo lo llama.
        """
        pass

    def configure_collision_detection(self, enable_spatial_partitioning=None, grid_size=None):
        """
        Compatibility method.
        """
        pass

    def configure_rendering(self, enable_viewport_culling=None, enable_render_batching=None):
        """
        Compatibility method.
        """
        pass

    def configure_performance_monitoring(
        self,
        enable=None,
        show_overlay=None,
        fps_warning_threshold=None,
        fps_critical_threshold=None
    ):
        """
        Compatibility method.
        """
        pass

    def get_collision_stats(self):
        """
        Compatibility method.
        """

        return {
            "spatial_partitioning": False,
            "collision_pairs_checked": 0,
            "collision_time": 0
        }

    def get_render_stats(self):
        """
        Compatibility method.
        """

        return {
            "viewport_culling": False,
            "render_batching": False,
            "objects_rendered": len(self.get_game_objects()),
            "objects_culled": 0
        }

    def get_performance_summary(self):
        """
        Compatibility method.
        """

        return {
            "performance_monitoring": "disabled",
            "object_count": len(self.get_game_objects()),
            "target_fps": self.target_fps
        }

    def print_performance_summary(self):
        """
        Compatibility method.
        """

        print("Performance monitoring is disabled in the simplified GameEngine.")
        print(f"Active objects: {len(self.get_game_objects())}")
        print(f"Target FPS: {self.target_fps}")

    def get_performance_metrics(self, metric_type=None):
        """
        Compatibility method.
        """

        return self.get_performance_summary()

    def start_performance_profiling(self, duration_seconds=10):
        """
        Compatibility method.
        """

        print("Performance profiling is disabled in the simplified GameEngine.")
        return False

    def end_performance_profiling(self):
        """
        Compatibility method.
        """

        print("Performance profiling is disabled in the simplified GameEngine.")
        return False

    # ---------------------------------------------------------
    # Shutdown
    # ---------------------------------------------------------

    def shutdown(self):
        """
        Clean up resources and quit pygame.
        """

        if self.sound_manager:
            try:
                self.sound_manager.cleanup()
            except Exception:
                pass

        pygame.quit()

    def cleanup(self):
        """
        Clean up resources.
        """

        if self.sound_manager:
            try:
                self.sound_manager.cleanup()
            except Exception:
                pass

    def __del__(self):
        """
        Destructor.
        """

        try:
            self.cleanup()
        except Exception:
            pass