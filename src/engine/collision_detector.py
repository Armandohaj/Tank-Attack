"""
Collision Detector module for the Tank Game.

This module handles collision detection between game objects.

Adapted for Tank-Attack:
- Projectiles collide with walls, tanks and objectives.
- Walls are indestructible.
- Tanks use map collision for movement, so tank-wall collision is not resolved here.
- Uses the current tags: player, enemy, projectile, wall, objective.
"""


class CollisionDetector:
    """
    Handles collision detection between game objects.
    """

    def __init__(self, game_objects=None, map_data=None):
        """
        Initialize the collision detector.

        Args:
            game_objects (list): List of game objects.
            map_data: Map data used for obstacle information.
        """
        self.game_objects = game_objects or []
        self.map_data = map_data

    def set_game_objects(self, game_objects):
        """
        Set the list of game objects.
        """
        self.game_objects = game_objects or []

    def set_map_data(self, map_data):
        """
        Set the map data.
        """
        self.map_data = map_data

    def check_collisions(self):
        """
        Check collisions between all active game objects.

        Returns:
            list: List of collision pairs.
        """
        collisions = []

        active_objects = [
            obj for obj in self.game_objects
            if getattr(obj, "active", True)
        ]

        for i, obj1 in enumerate(active_objects):
            for obj2 in active_objects[i + 1:]:
                if self._objects_collide(obj1, obj2):
                    collisions.append((obj1, obj2))

        return collisions

    def handle_collisions(self):
        """
        Check and handle all collisions.
        """
        collisions = self.check_collisions()

        for obj1, obj2 in collisions:
            self._handle_collision_pair(obj1, obj2)

    def _objects_collide(self, obj1, obj2):
        """
        Check if two objects collide.
        """

        if obj1 is None or obj2 is None:
            return False

        if not getattr(obj1, "active", True):
            return False

        if not getattr(obj2, "active", True):
            return False

        # Do not check projectile with its owner.
        if getattr(obj1, "tag", None) == "projectile":
            if getattr(obj1, "owner", None) == obj2:
                return False

        if getattr(obj2, "tag", None) == "projectile":
            if getattr(obj2, "owner", None) == obj1:
                return False

        # Prefer object custom method if available.
        if hasattr(obj1, "check_collision_with_object"):
            return obj1.check_collision_with_object(obj2)

        if hasattr(obj2, "check_collision_with_object"):
            return obj2.check_collision_with_object(obj1)

        # Fallback rectangle collision.
        return self._rects_collide(obj1, obj2)

    def _rects_collide(self, obj1, obj2):
        """
        Basic rectangular collision.
        """

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

    def _handle_collision_pair(self, obj1, obj2):
        """
        Handle collision between two objects.
        """

        tag1 = getattr(obj1, "tag", None)
        tag2 = getattr(obj2, "tag", None)

        # Projectile collisions
        if tag1 == "projectile":
            self._handle_projectile_collision(obj1, obj2)
            return

        if tag2 == "projectile":
            self._handle_projectile_collision(obj2, obj1)
            return

        # Tank-wall collision is mainly prevented in movement methods.
        # No extra action needed here.

    def _handle_projectile_collision(self, projectile, hit_object):
        """
        Handle a projectile hitting another object.

        Args:
            projectile: Projectile object.
            hit_object: Object hit by the projectile.
        """

        if not getattr(projectile, "active", True):
            return

        if hit_object is None:
            projectile.active = False
            return

        if hit_object == getattr(projectile, "owner", None):
            return

        hit_tag = getattr(hit_object, "tag", None)

        # Ignore projectile-projectile collision.
        if hit_tag == "projectile":
            return

        # Wall blocks projectile but does not get destroyed.
        if hit_tag == "wall":
            projectile.active = False
            return

        # Player, enemy, objectives and destructible objects can receive damage.
        if hasattr(hit_object, "take_damage"):
            hit_object.take_damage(getattr(projectile, "damage", 20))

        projectile.active = False


class EnhancedCollisionDetector(CollisionDetector):
    """
    Compatibility class.

    It behaves like CollisionDetector but keeps the name EnhancedCollisionDetector
    so other parts of the project do not break if they import it.
    """

    def get_performance_stats(self):
        """
        Return basic collision statistics.
        """
        active_count = len([
            obj for obj in self.game_objects
            if getattr(obj, "active", True)
        ])

        return {
            "collision_pairs_checked": active_count * (active_count - 1) // 2,
            "spatial_partitioning_enabled": False
        }