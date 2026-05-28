"""
Enhanced Projectile Renderer module for the Tank Game.
This module handles the rendering of projectiles with improved visuals and effects.
"""
import pygame
import math
import random


class EnhancedProjectileRenderer:
    """
    Handles enhanced rendering of projectiles with visual effects.
    """
    def __init__(self, renderer):
        """
        Initialize the enhanced projectile renderer.
        
        Args:
            renderer: The game renderer
        """
        self.renderer = renderer
        self.projectile_sprite = None
        self.trail_particles = {}  # Store trail particles for each projectile
        
        # Create enhanced sprite
        self._create_enhanced_sprite()
        
    def _create_enhanced_sprite(self):
        """Create enhanced sprite for projectiles."""
        # Create projectile sprite with glow effect
        self.projectile_sprite = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.projectile_sprite.fill((0, 0, 0, 0))  # Transparent background
        
        # Draw outer glow
        pygame.draw.circle(self.projectile_sprite, (255, 255, 100, 100), (5, 5), 5)
        pygame.draw.circle(self.projectile_sprite, (255, 255, 150, 150), (5, 5), 4)
        
        # Draw main projectile (bright yellow-orange core)
        pygame.draw.circle(self.projectile_sprite, (255, 200, 0), (5, 5), 3)
        pygame.draw.circle(self.projectile_sprite, (255, 255, 200), (5, 5), 2)
        pygame.draw.circle(self.projectile_sprite, (255, 255, 255), (5, 5), 1)
        
    def set_projectile_sprite(self, sprite):
        """
        Set the sprite for projectiles.
        
        Args:
            sprite: Pygame surface to use as projectile sprite
        """
        self.projectile_sprite = sprite
        
    def render_projectile(self, screen, projectile):
        """
        Render a projectile on the screen with enhanced effects.
        
        Args:
            screen: Pygame surface to render on
            projectile: The projectile to render
        """
        # Skip rendering if the projectile is not active
        if not projectile.active:
            # Clean up trail particles for inactive projectiles
            if id(projectile) in self.trail_particles:
                del self.trail_particles[id(projectile)]
            return
            
        # Set the projectile's sprite if it doesn't have one
        if projectile.sprite is None:
            projectile.set_sprite(self.projectile_sprite)
            
        # Render enhanced trail effect
        self._render_enhanced_trail(screen, projectile)
        
        # Render the projectile with glow effect
        self._render_projectile_with_glow(screen, projectile)
        
        # Add muzzle flash effect for newly fired projectiles
        if hasattr(projectile, 'age') and projectile.age < 0.1:  # First 0.1 seconds
            self._render_muzzle_flash(screen, projectile)
            
    def _render_projectile_with_glow(self, screen, projectile):
        """
        Render a projectile with glow effect.
        
        Args:
            screen: Pygame surface to render on
            projectile: The projectile to render
        """
        # Create a glow surface
        glow_size = 16
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        
        # Draw multiple circles for glow effect
        for i in range(4):
            alpha = 30 - i * 7
            radius = 8 - i * 2
            color = (255, 200, 100, alpha)
            pygame.draw.circle(glow_surface, color, (glow_size // 2, glow_size // 2), radius)
        
        # Render the glow
        glow_x = projectile.x + projectile.width // 2 - glow_size // 2
        glow_y = projectile.y + projectile.height // 2 - glow_size // 2
        screen.blit(glow_surface, (glow_x, glow_y), special_flags=pygame.BLEND_ADD)
        
        # Render the projectile normally
        projectile.render(screen)
        
    def _render_enhanced_trail(self, screen, projectile):
        """
        Render an enhanced trail effect behind the projectile.
        
        Args:
            screen: Pygame surface to render on
            projectile: The projectile to render the trail for
        """
        projectile_id = id(projectile)
        
        # Initialize trail particles for this projectile if not exists
        if projectile_id not in self.trail_particles:
            self.trail_particles[projectile_id] = []
        
        # Add new trail particle
        center_x = projectile.x + projectile.width // 2
        center_y = projectile.y + projectile.height // 2
        
        # Add some randomness to trail particles
        offset_x = random.uniform(-2, 2)
        offset_y = random.uniform(-2, 2)
        
        particle = {
            'x': center_x + offset_x,
            'y': center_y + offset_y,
            'life': 1.0,  # Life from 1.0 to 0.0
            'size': random.uniform(2, 4)
        }
        self.trail_particles[projectile_id].append(particle)
        
        # Update and render trail particles
        particles_to_remove = []
        for i, particle in enumerate(self.trail_particles[projectile_id]):
            # Update particle life
            particle['life'] -= 0.05  # Decay rate
            
            if particle['life'] <= 0:
                particles_to_remove.append(i)
                continue
            
            # Calculate particle properties based on life
            alpha = int(255 * particle['life'])
            size = int(particle['size'] * particle['life'])
            
            if size > 0:
                # Create particle surface
                particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                
                # Color transitions from white to yellow to red
                if particle['life'] > 0.7:
                    color = (255, 255, 255, alpha)
                elif particle['life'] > 0.4:
                    color = (255, 255, 100, alpha)
                else:
                    color = (255, 150, 50, alpha)
                
                pygame.draw.circle(particle_surface, color, (size, size), size)
                
                # Render the particle
                screen.blit(particle_surface, 
                          (particle['x'] - size, particle['y'] - size),
                          special_flags=pygame.BLEND_ADD)
        
        # Remove dead particles
        for i in reversed(particles_to_remove):
            del self.trail_particles[projectile_id][i]
        
        # Limit number of particles per projectile
        if len(self.trail_particles[projectile_id]) > 15:
            self.trail_particles[projectile_id] = self.trail_particles[projectile_id][-15:]
            
    def _render_muzzle_flash(self, screen, projectile):
        """
        Render muzzle flash effect for newly fired projectiles.
        
        Args:
            screen: Pygame surface to render on
            projectile: The projectile to render muzzle flash for
        """
        if not hasattr(projectile, 'owner') or not projectile.owner:
            return
            
        # Calculate muzzle position (at the tank's barrel tip)
        tank = projectile.owner
        rad = math.radians(tank.direction)
        muzzle_x = tank.x + tank.width // 2 + math.sin(rad) * (tank.height // 2 + 5)
        muzzle_y = tank.y + tank.height // 2 - math.cos(rad) * (tank.height // 2 + 5)
        
        # Create muzzle flash effect
        flash_size = 20
        flash_surface = pygame.Surface((flash_size, flash_size), pygame.SRCALPHA)
        
        # Draw multiple circles for flash effect
        colors = [(255, 255, 255, 200), (255, 255, 100, 150), (255, 200, 0, 100)]
        sizes = [8, 6, 4]
        
        for color, size in zip(colors, sizes):
            pygame.draw.circle(flash_surface, color, (flash_size // 2, flash_size // 2), size)
        
        # Add some random sparks
        for _ in range(5):
            spark_x = random.randint(0, flash_size)
            spark_y = random.randint(0, flash_size)
            pygame.draw.circle(flash_surface, (255, 255, 255, 150), (spark_x, spark_y), 1)
        
        # Render the muzzle flash
        screen.blit(flash_surface, 
                   (muzzle_x - flash_size // 2, muzzle_y - flash_size // 2),
                   special_flags=pygame.BLEND_ADD)
                   
    def render_explosion(self, screen, x, y, size=50, color=(255, 100, 0)):
        """
        Render an explosion effect at the given position.
        
        Args:
            screen: Pygame surface to render on
            x (float): X-coordinate of explosion center
            y (float): Y-coordinate of explosion center
            size (int): Size of the explosion
            color: RGB tuple for explosion color
        """
        explosion_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw multiple circles for explosion effect
        for i in range(5):
            alpha = 200 - i * 40
            radius = size - i * (size // 5)
            if radius > 0:
                # Color gradient from white to orange to red
                if i == 0:
                    exp_color = (255, 255, 255, alpha)
                elif i == 1:
                    exp_color = (255, 255, 100, alpha)
                elif i == 2:
                    exp_color = (255, 200, 0, alpha)
                else:
                    exp_color = (*color, alpha)
                
                pygame.draw.circle(explosion_surface, exp_color, (size, size), radius)
        
        # Add some random sparks around the explosion
        for _ in range(10):
            spark_angle = random.uniform(0, 2 * math.pi)
            spark_distance = random.uniform(size * 0.5, size * 1.2)
            spark_x = size + math.cos(spark_angle) * spark_distance
            spark_y = size + math.sin(spark_angle) * spark_distance
            
            if 0 <= spark_x < size * 2 and 0 <= spark_y < size * 2:
                pygame.draw.circle(explosion_surface, (255, 255, 0, 150), 
                                 (int(spark_x), int(spark_y)), 2)
        
        # Render the explosion
        screen.blit(explosion_surface, (x - size, y - size), special_flags=pygame.BLEND_ADD)
        
    def render_impact_effect(self, screen, x, y, size=20):
        """
        Render an impact effect at the given position.
        
        Args:
            screen: Pygame surface to render on
            x (float): X-coordinate of impact
            y (float): Y-coordinate of impact
            size (int): Size of the impact effect
        """
        impact_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw impact flash
        pygame.draw.circle(impact_surface, (255, 255, 255, 200), (size, size), size // 2)
        pygame.draw.circle(impact_surface, (255, 255, 100, 150), (size, size), size // 3)
        
        # Add impact sparks
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(size * 0.3, size * 0.8)
            spark_x = size + math.cos(angle) * distance
            spark_y = size + math.sin(angle) * distance
            
            if 0 <= spark_x < size * 2 and 0 <= spark_y < size * 2:
                pygame.draw.circle(impact_surface, (255, 200, 0, 180), 
                                 (int(spark_x), int(spark_y)), 1)
        
        # Render the impact
        screen.blit(impact_surface, (x - size, y - size), special_flags=pygame.BLEND_ADD)
        
    def cleanup_projectile_effects(self, projectile):
        """
        Clean up visual effects for a projectile that's being removed.
        
        Args:
            projectile: The projectile being removed
        """
        projectile_id = id(projectile)
        if projectile_id in self.trail_particles:
            del self.trail_particles[projectile_id]