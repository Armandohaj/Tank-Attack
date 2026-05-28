"""
Level Transition module for the Tank Game.
This module defines the LevelTransition class that handles level transition animations.
"""
import pygame
import random
import math


class LevelTransition:
    """
    Handles level transition animations and effects.
    """
    def __init__(self, game_engine):
        """
        Initialize the level transition.
        
        Args:
            game_engine (GameEngine): The game engine instance
        """
        self.game_engine = game_engine
        self.duration = 3.0  # 3 seconds for level transition
        self.timer = 0.0
        self.active = False
        self.game_complete = False
        self.current_level = 1
        self.score = 0
        self.particles = []
        
    def start(self, current_level, score, game_complete=False):
        """
        Start the level transition.
        
        Args:
            current_level (int): The current level number
            score (int): The current score
            game_complete (bool): Whether the game is complete
        """
        self.active = True
        self.timer = 0.0
        self.current_level = current_level
        self.score = score
        self.game_complete = game_complete
        self.particles = []
        
        # Create transition particles
        self._create_transition_particles()
        
    def update(self, delta_time):
        """
        Update the level transition.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
            
        Returns:
            bool: True if the transition is complete, False otherwise
        """
        if not self.active:
            return False
            
        # Update timer
        self.timer += delta_time
        
        # Update particles
        self._update_particles(delta_time)
        
        # Check if transition is complete
        if self.timer >= self.duration:
            self.active = False
            self.particles = []
            return True
            
        return False
        
    def render(self, screen):
        """
        Render the level transition.
        
        Args:
            screen: The pygame screen to render on
        """
        if not self.active:
            return
            
        # Calculate transition progress (0.0 to 1.0)
        progress = self.timer / self.duration
        
        # Create a semi-transparent overlay with opacity based on progress
        overlay = pygame.Surface((self.game_engine.width, self.game_engine.height), pygame.SRCALPHA)
        
        # Fade in at the start, fade out at the end
        if progress < 0.2:
            # Fade in (0.0 -> 0.2)
            alpha = int(255 * (progress / 0.2))
        elif progress > 0.8:
            # Fade out (0.8 -> 1.0)
            alpha = int(255 * (1 - (progress - 0.8) / 0.2))
        else:
            # Stay fully visible (0.2 -> 0.8)
            alpha = 255
            
        overlay.fill((0, 0, 0, alpha))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Only render text when the overlay is visible enough
        if alpha > 50:
            # Create fonts for the text
            large_font = pygame.font.SysFont(None, 64)
            medium_font = pygame.font.SysFont(None, 48)
            small_font = pygame.font.SysFont(None, 32)
            
            # Display appropriate message
            if self.game_complete:
                title = "GAME COMPLETE!"
                message = f"Final Score: {self.score}"
                sub_message = "Thanks for playing!"
            else:
                title = f"LEVEL {self.current_level} COMPLETE!"
                message = f"Score: {self.score}"
                
                # Show countdown to next level
                time_left = max(0, self.duration - self.timer)
                sub_message = f"Next level in {time_left:.1f}s"
                
            # Render the text with a glow effect
            # First render the glow (larger, colored version behind)
            glow_color = (100, 100, 255)  # Blue glow
            title_glow = large_font.render(title, True, glow_color)
            message_glow = medium_font.render(message, True, glow_color)
            sub_message_glow = small_font.render(sub_message, True, glow_color)
            
            # Then render the main text
            title_surface = large_font.render(title, True, (255, 255, 255))
            message_surface = medium_font.render(message, True, (255, 255, 255))
            sub_message_surface = small_font.render(sub_message, True, (255, 255, 255))
            
            # Position the text in the center of the screen
            title_rect = title_surface.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2 - 60))
            message_rect = message_surface.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2))
            sub_message_rect = sub_message_surface.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2 + 60))
            
            # Draw the glow effect (slightly offset)
            for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
                glow_rect = title_rect.copy()
                glow_rect.x += offset[0]
                glow_rect.y += offset[1]
                screen.blit(title_glow, glow_rect)
                
                glow_rect = message_rect.copy()
                glow_rect.x += offset[0]
                glow_rect.y += offset[1]
                screen.blit(message_glow, glow_rect)
                
                glow_rect = sub_message_rect.copy()
                glow_rect.x += offset[0]
                glow_rect.y += offset[1]
                screen.blit(sub_message_glow, glow_rect)
            
            # Draw the main text
            screen.blit(title_surface, title_rect)
            screen.blit(message_surface, message_rect)
            screen.blit(sub_message_surface, sub_message_rect)
            
            # If game is complete, show additional stats
            if self.game_complete:
                stats = [
                    f"Total Score: {self.score}",
                    "Press 'R' to restart"
                ]
                
                for i, stat in enumerate(stats):
                    stat_surface = small_font.render(stat, True, (200, 200, 200))
                    stat_rect = stat_surface.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2 + 120 + i * 30))
                    screen.blit(stat_surface, stat_rect)
        
        # Render particles
        self._render_particles(screen)
        
    def _create_transition_particles(self):
        """Create particles for the level transition effect."""
        # Create particles around the screen edges
        num_particles = 100
        
        for _ in range(num_particles):
            # Randomly position particles around the screen edges
            side = random.randint(0, 3)
            if side == 0:  # Top
                x = random.randint(0, self.game_engine.width)
                y = 0
                dx = random.uniform(-2, 2)
                dy = random.uniform(1, 5)
            elif side == 1:  # Right
                x = self.game_engine.width
                y = random.randint(0, self.game_engine.height)
                dx = random.uniform(-5, -1)
                dy = random.uniform(-2, 2)
            elif side == 2:  # Bottom
                x = random.randint(0, self.game_engine.width)
                y = self.game_engine.height
                dx = random.uniform(-2, 2)
                dy = random.uniform(-5, -1)
            else:  # Left
                x = 0
                y = random.randint(0, self.game_engine.height)
                dx = random.uniform(1, 5)
                dy = random.uniform(-2, 2)
                
            # Create the particle
            particle = {
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'radius': random.randint(2, 6),
                'color': (
                    random.randint(150, 255),
                    random.randint(150, 255),
                    random.randint(200, 255)
                ),
                'lifetime': random.uniform(0.5, self.duration),
                'time_alive': 0
            }
            
            self.particles.append(particle)
            
    def _update_particles(self, delta_time):
        """
        Update the particles.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
        """
        # Update existing particles
        for particle in self.particles[:]:
            # Update position
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Update lifetime
            particle['time_alive'] += delta_time
            
            # Remove particles that have exceeded their lifetime
            if particle['time_alive'] >= particle['lifetime']:
                self.particles.remove(particle)
                
    def _render_particles(self, screen):
        """
        Render the particles.
        
        Args:
            screen: The pygame screen to render on
        """
        for particle in self.particles:
            # Calculate opacity based on lifetime
            progress = particle['time_alive'] / particle['lifetime']
            alpha = 255 * (1 - progress)
            
            # Create a surface for the particle
            particle_surface = pygame.Surface((particle['radius'] * 2, particle['radius'] * 2), pygame.SRCALPHA)
            
            # Draw the particle
            pygame.draw.circle(
                particle_surface,
                (*particle['color'], int(alpha)),
                (particle['radius'], particle['radius']),
                particle['radius']
            )
            
            # Draw the particle on the screen
            screen.blit(
                particle_surface,
                (particle['x'] - particle['radius'], particle['y'] - particle['radius'])
            )