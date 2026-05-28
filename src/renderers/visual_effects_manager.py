"""
Visual Effects Manager for the Tank Game.
This module handles various visual effects like explosions, impacts, and particles.
"""
import pygame
import math
import random
import time


class VisualEffect:
    """Base class for visual effects."""
    
    def __init__(self, x, y, duration):
        """
        Initialize a visual effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            duration (float): Duration in seconds
        """
        self.x = x
        self.y = y
        self.duration = duration
        self.start_time = time.time()
        self.active = True
        
    def update(self, delta_time):
        """
        Update the effect.
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.active = False
            
    def render(self, screen):
        """
        Render the effect.
        
        Args:
            screen: Pygame surface to render on
        """
        pass
        
    def get_progress(self):
        """
        Get the progress of the effect (0.0 to 1.0).
        
        Returns:
            float: Progress from 0.0 (start) to 1.0 (end)
        """
        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / self.duration)


class ExplosionEffect(VisualEffect):
    """Explosion visual effect."""
    
    def __init__(self, x, y, size=50, color=(255, 100, 0), duration=0.5):
        """
        Initialize an explosion effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            size (int): Maximum size of explosion
            color: RGB tuple for explosion color
            duration (float): Duration in seconds
        """
        super().__init__(x, y, duration)
        self.size = size
        self.color = color
        self.particles = []
        
        # Create explosion particles
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 80)
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'size': random.uniform(2, 6),
                'color': (
                    random.randint(200, 255),
                    random.randint(50, 200),
                    random.randint(0, 100)
                )
            }
            self.particles.append(particle)
            
    def update(self, delta_time):
        """Update the explosion effect."""
        super().update(delta_time)
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx'] * delta_time
            particle['y'] += particle['vy'] * delta_time
            particle['life'] -= delta_time * 2  # Particles fade quickly
            particle['vy'] += 50 * delta_time  # Gravity effect
            
    def render(self, screen):
        """Render the explosion effect."""
        if not self.active:
            return
            
        progress = self.get_progress()
        
        # Main explosion blast
        current_size = int(self.size * (1 - progress * 0.5))  # Shrinks over time
        alpha = int(255 * (1 - progress))
        
        if current_size > 0 and alpha > 0:
            explosion_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            
            # Multiple circles for explosion effect
            for i in range(4):
                radius = current_size - i * (current_size // 4)
                if radius > 0:
                    if i == 0:
                        color = (255, 255, 255, alpha)
                    elif i == 1:
                        color = (255, 255, 100, alpha)
                    elif i == 2:
                        color = (255, 150, 0, alpha)
                    else:
                        color = (*self.color, alpha)
                    
                    pygame.draw.circle(explosion_surface, color, (current_size, current_size), radius)
            
            screen.blit(explosion_surface, (self.x - current_size, self.y - current_size), 
                       special_flags=pygame.BLEND_ADD)
        
        # Render particles
        for particle in self.particles:
            if particle['life'] > 0:
                particle_alpha = int(255 * particle['life'])
                particle_size = int(particle['size'] * particle['life'])
                
                if particle_size > 0:
                    particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
                    color_with_alpha = (*particle['color'], particle_alpha)
                    pygame.draw.circle(particle_surface, color_with_alpha, 
                                     (particle_size, particle_size), particle_size)
                    
                    screen.blit(particle_surface, 
                               (particle['x'] - particle_size, particle['y'] - particle_size),
                               special_flags=pygame.BLEND_ADD)


class ImpactEffect(VisualEffect):
    """Impact visual effect for projectile hits."""
    
    def __init__(self, x, y, size=15, duration=0.2):
        """
        Initialize an impact effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            size (int): Size of impact effect
            duration (float): Duration in seconds
        """
        super().__init__(x, y, duration)
        self.size = size
        self.sparks = []
        
        # Create impact sparks
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 60)
            spark = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'size': random.uniform(1, 3)
            }
            self.sparks.append(spark)
            
    def update(self, delta_time):
        """Update the impact effect."""
        super().update(delta_time)
        
        # Update sparks
        for spark in self.sparks:
            spark['x'] += spark['vx'] * delta_time
            spark['y'] += spark['vy'] * delta_time
            spark['life'] -= delta_time * 5  # Sparks fade very quickly
            spark['vy'] += 100 * delta_time  # Gravity
            
    def render(self, screen):
        """Render the impact effect."""
        if not self.active:
            return
            
        progress = self.get_progress()
        
        # Main impact flash
        if progress < 0.5:  # Flash only for first half of duration
            flash_alpha = int(255 * (1 - progress * 2))
            flash_size = int(self.size * (1 + progress))
            
            flash_surface = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (255, 255, 255, flash_alpha), 
                             (flash_size, flash_size), flash_size)
            pygame.draw.circle(flash_surface, (255, 255, 100, flash_alpha // 2), 
                             (flash_size, flash_size), flash_size // 2)
            
            screen.blit(flash_surface, (self.x - flash_size, self.y - flash_size),
                       special_flags=pygame.BLEND_ADD)
        
        # Render sparks
        for spark in self.sparks:
            if spark['life'] > 0:
                spark_alpha = int(255 * spark['life'])
                spark_size = int(spark['size'] * spark['life'])
                
                if spark_size > 0:
                    spark_color = (255, 200, 0, spark_alpha)
                    pygame.draw.circle(screen, spark_color[:3], 
                                     (int(spark['x']), int(spark['y'])), spark_size)


class SmokeEffect(VisualEffect):
    """Smoke visual effect for damaged objects."""
    
    def __init__(self, x, y, intensity=1.0, duration=2.0):
        """
        Initialize a smoke effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            intensity (float): Smoke intensity (0.0 to 1.0)
            duration (float): Duration in seconds
        """
        super().__init__(x, y, duration)
        self.intensity = intensity
        self.smoke_particles = []
        
    def update(self, delta_time):
        """Update the smoke effect."""
        super().update(delta_time)
        
        # Add new smoke particles
        if random.random() < self.intensity * 0.3:
            particle = {
                'x': self.x + random.uniform(-5, 5),
                'y': self.y,
                'vx': random.uniform(-10, 10),
                'vy': random.uniform(-30, -10),  # Upward movement
                'life': random.uniform(1.0, 2.0),
                'size': random.uniform(3, 8),
                'alpha': random.uniform(100, 200)
            }
            self.smoke_particles.append(particle)
        
        # Update existing particles
        for particle in self.smoke_particles[:]:
            particle['x'] += particle['vx'] * delta_time
            particle['y'] += particle['vy'] * delta_time
            particle['life'] -= delta_time
            particle['size'] += delta_time * 2  # Particles grow as they rise
            
            if particle['life'] <= 0:
                self.smoke_particles.remove(particle)
                
    def render(self, screen):
        """Render the smoke effect."""
        if not self.active:
            return
            
        for particle in self.smoke_particles:
            if particle['life'] > 0:
                alpha = int(particle['alpha'] * (particle['life'] / 2.0))
                size = int(particle['size'])
                
                if size > 0 and alpha > 0:
                    smoke_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    smoke_color = (80, 80, 80, alpha)
                    pygame.draw.circle(smoke_surface, smoke_color, (size, size), size)
                    
                    screen.blit(smoke_surface, 
                               (particle['x'] - size, particle['y'] - size))


class MuzzleFlashEffect(VisualEffect):
    """Muzzle flash effect for tank firing."""
    
    def __init__(self, x, y, angle, duration=0.1):
        """
        Initialize a muzzle flash effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            angle (float): Angle of the flash in degrees
            duration (float): Duration in seconds
        """
        super().__init__(x, y, duration)
        self.angle = angle
        
    def render(self, screen):
        """Render the muzzle flash effect."""
        if not self.active:
            return
            
        progress = self.get_progress()
        alpha = int(255 * (1 - progress))
        
        if alpha > 0:
            flash_size = 20
            flash_surface = pygame.Surface((flash_size, flash_size), pygame.SRCALPHA)
            
            # Multiple circles for flash effect
            colors = [(255, 255, 255, alpha), (255, 255, 100, alpha // 2), (255, 200, 0, alpha // 3)]
            sizes = [8, 6, 4]
            
            for color, size in zip(colors, sizes):
                pygame.draw.circle(flash_surface, color, (flash_size // 2, flash_size // 2), size)
            
            # Add directional sparks
            for i in range(5):
                spark_angle = self.angle + random.uniform(-30, 30)
                spark_length = random.uniform(5, 15)
                spark_x = flash_size // 2 + math.sin(math.radians(spark_angle)) * spark_length
                spark_y = flash_size // 2 - math.cos(math.radians(spark_angle)) * spark_length
                
                if 0 <= spark_x < flash_size and 0 <= spark_y < flash_size:
                    pygame.draw.circle(flash_surface, (255, 255, 0, alpha), 
                                     (int(spark_x), int(spark_y)), 1)
            
            screen.blit(flash_surface, 
                       (self.x - flash_size // 2, self.y - flash_size // 2),
                       special_flags=pygame.BLEND_ADD)


class ParticleEffect(VisualEffect):
    """Particle visual effect for debris and dust."""
    
    def __init__(self, x, y, size, color, duration=1.0, velocity=(0, 0), gravity=False):
        """
        Initialize a particle effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            size (int): Size of particle
            color: RGB tuple for particle color
            duration (float): Duration in seconds
            velocity (tuple): Initial velocity (vx, vy)
            gravity (bool): Whether gravity affects the particle
        """
        super().__init__(x, y, duration)
        self.size = size
        self.color = color
        self.vx, self.vy = velocity
        self.gravity = gravity
        
    def update(self, delta_time):
        """Update the particle effect."""
        super().update(delta_time)
        
        # Update position based on velocity
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Apply gravity if enabled
        if self.gravity:
            self.vy += 100 * delta_time  # Gravity effect
            
    def render(self, screen):
        """Render the particle effect."""
        if not self.active:
            return
            
        progress = self.get_progress()
        alpha = int(255 * (1 - progress))
        current_size = max(1, int(self.size * (1 - progress * 0.5)))
        
        if alpha > 0 and current_size > 0:
            particle_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(particle_surface, color_with_alpha, 
                             (current_size, current_size), current_size)
            
            screen.blit(particle_surface, 
                       (self.x - current_size, self.y - current_size))


class DustCloudEffect(VisualEffect):
    """Dust cloud visual effect."""
    
    def __init__(self, x, y, size=20, duration=0.7):
        """
        Initialize a dust cloud effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            size (int): Size of dust cloud
            duration (float): Duration in seconds
        """
        super().__init__(x, y, duration)
        self.size = size
        self.particles = []
        
        # Create dust particles
        num_particles = int(size * 0.5)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 20)
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(0.5, 1.0),
                'size': random.uniform(1, 4),
                'color': (
                    random.randint(100, 150),
                    random.randint(80, 120),
                    random.randint(60, 100)
                )
            }
            self.particles.append(particle)
            
    def update(self, delta_time):
        """Update the dust cloud effect."""
        super().update(delta_time)
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx'] * delta_time
            particle['y'] += particle['vy'] * delta_time
            particle['life'] -= delta_time
            particle['vx'] *= 0.95  # Slow down over time
            particle['vy'] *= 0.95
            
    def render(self, screen):
        """Render the dust cloud effect."""
        if not self.active:
            return
            
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * particle['life'])
                size = int(particle['size'])
                
                if size > 0 and alpha > 0:
                    particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    color_with_alpha = (*particle['color'], alpha)
                    pygame.draw.circle(particle_surface, color_with_alpha, 
                                     (size, size), size)
                    
                    screen.blit(particle_surface, 
                               (particle['x'] - size, particle['y'] - size))


class VisualEffectsManager:
    """Manages all visual effects in the game."""
    
    def __init__(self):
        """Initialize the visual effects manager."""
        self.effects = []
        
    def add_explosion(self, x, y, size=50, color=(255, 100, 0), duration=0.5):
        """
        Add an explosion effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            size (int): Size of explosion
            color: RGB tuple for explosion color
            duration (float): Duration in seconds
        """
        effect = ExplosionEffect(x, y, size, color, duration)
        self.effects.append(effect)
        
    def add_impact(self, x, y, size=15, duration=0.2):
        """
        Add an impact effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            size (int): Size of impact
            duration (float): Duration in seconds
        """
        effect = ImpactEffect(x, y, size, duration)
        self.effects.append(effect)
        
    def add_smoke(self, x, y, intensity=1.0, duration=2.0):
        """
        Add a smoke effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            intensity (float): Smoke intensity
            duration (float): Duration in seconds
        """
        effect = SmokeEffect(x, y, intensity, duration)
        self.effects.append(effect)
        
    def add_muzzle_flash(self, x, y, angle, duration=0.1):
        """
        Add a muzzle flash effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            angle (float): Angle in degrees
            duration (float): Duration in seconds
        """
        effect = MuzzleFlashEffect(x, y, angle, duration)
        self.effects.append(effect)
        
    def add_particle(self, x, y, size, color, duration=1.0, velocity=(0, 0), gravity=False):
        """
        Add a particle effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            size (int): Size of particle
            color: RGB tuple for particle color
            duration (float): Duration in seconds
            velocity (tuple): Initial velocity (vx, vy)
            gravity (bool): Whether gravity affects the particle
        """
        effect = ParticleEffect(x, y, size, color, duration, velocity, gravity)
        self.effects.append(effect)
        
    def add_dust_cloud(self, x, y, size=20, duration=0.7):
        """
        Add a dust cloud effect.
        
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            size (int): Size of dust cloud
            duration (float): Duration in seconds
        """
        effect = DustCloudEffect(x, y, size, duration)
        self.effects.append(effect)
        
    def update(self, delta_time):
        """
        Update all visual effects.
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update all effects
        for effect in self.effects[:]:
            effect.update(delta_time)
            if not effect.active:
                self.effects.remove(effect)
                
    def render(self, screen):
        """
        Render all visual effects.
        
        Args:
            screen: Pygame surface to render on
        """
        for effect in self.effects:
            effect.render(screen)
            
    def clear_all_effects(self):
        """Clear all active effects."""
        self.effects.clear()
        
    def get_effect_count(self):
        """
        Get the number of active effects.
        
        Returns:
            int: Number of active effects
        """
        return len(self.effects)