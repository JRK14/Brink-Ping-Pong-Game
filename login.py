import pygame
import sys
import os
import json
import math
import random
from users import create_user, authenticate_user, get_top_scores

# Initialize Pygame
pygame.init()

# Screen setup
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
FULLSCREEN = True

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
DARK_GRAY = (30, 30, 30)
DARKER_GRAY = (20, 20, 20)
DARKEST_GRAY = (10, 10, 15)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Professional UI Colors
NEON_BLUE = (41, 121, 255)       # Refined blue
NEON_RED = (235, 87, 87)         # Softer red
NEON_GREEN = (33, 150, 83)       # Calmer green
NEON_PURPLE = (111, 93, 198)     # Muted purple
NEON_ORANGE = (242, 153, 74)     # Warmer orange
ACCENT_TEAL = (6, 174, 213)      # Professional teal
ACCENT_INDIGO = (75, 0, 130)     # Deep indigo
ACCENT_SLATE = (47, 79, 79)      # Dark slate
ACCENT_CORAL = (255, 127, 80)    # Soft coral

# UI Section Colors - professional scheme
SCORES_SECTION_BORDER = (235, 87, 87)    # Refined red
LOGIN_SECTION_BORDER = (242, 153, 74)    # Professional orange
PREVIEW_SECTION_BORDER = (41, 121, 255)  # Enterprise blue

# Section background colors
SECTION_BG = (18, 18, 24)        # Deep background
CARD_BG = (28, 28, 35)           # Card background
HOVER_BG = (38, 38, 45)          # Hover state
INPUT_BG = (45, 45, 55)          # Input background
SUCCESS_GREEN = (33, 150, 83)    # Success message
ERROR_RED = (235, 87, 87)        # Error message

# Font setup
try:
    font_path = os.path.join(os.path.dirname(__file__), "AlumniSansSC-Regular.ttf")
    if os.path.exists(font_path):
        FONT = pygame.font.Font(font_path, int(HEIGHT * 0.1))
        FONT_LARGE = pygame.font.Font(font_path, int(HEIGHT * 0.07))
        FONT_MEDIUM = pygame.font.Font(font_path, int(HEIGHT * 0.05))
        FONT_SMALL = pygame.font.Font(font_path, int(HEIGHT * 0.03))
        FONT_TINY = pygame.font.Font(font_path, int(HEIGHT * 0.02))
    else:
        FONT = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.1))
        FONT_LARGE = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.07))
        FONT_MEDIUM = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.05))
        FONT_SMALL = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.03))
        FONT_TINY = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.02))
except:
    FONT = pygame.font.SysFont("Arial", int(HEIGHT * 0.08))
    FONT_LARGE = pygame.font.SysFont("Arial", int(HEIGHT * 0.06))
    FONT_MEDIUM = pygame.font.SysFont("Arial", int(HEIGHT * 0.04))
    FONT_SMALL = pygame.font.SysFont("Arial", int(HEIGHT * 0.025))
    FONT_TINY = pygame.font.SysFont("Arial", int(HEIGHT * 0.018))

# Load background image
background_image = None
try:
    background_image = pygame.image.load("background.jpg")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    print("Successfully loaded background image")
except:
    print("Failed to load background image")

class InputBox:
    def __init__(self, x, y, width, height, text='', placeholder='', password=False, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = INPUT_BG
        self.border_color = (80, 80, 90)
        self.active_border = NEON_BLUE
        self.text = text
        self.placeholder = placeholder
        self.txt_surface = FONT_SMALL.render(text, True, WHITE)
        self.active = False
        self.password = password
        self.blink_timer = 0
        self.show_cursor = True
        self.icon = icon
        self.icon_surface = None
        self.icon_rect = None
        
        # For animation effects
        self.focus_animation = 0  # 0 to 1 animation progress
        self.error = False
        self.error_timer = 0
        self.success = False
        self.success_timer = 0
        
        if icon:
            try:
                self.icon_surface = pygame.image.load(icon)
                icon_size = height - 10
                self.icon_surface = pygame.transform.scale(self.icon_surface, (icon_size, icon_size))
                self.icon_rect = self.icon_surface.get_rect(midleft=(x + 10, y + height//2))
            except:
                self.icon = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input box, toggle active status
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            
            # Start animation when focus changes
            if not was_active and self.active:
                self.focus_animation = 0
            
            # Update colors based on active state
            if self.active:
                self.color = INPUT_BG
                self.border_color = self.active_border
            else:
                self.color = INPUT_BG
                self.border_color = (80, 80, 90)
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_TAB:
                    # Handle tab key to move between fields
                    return "TAB"
                else:
                    # Only add printable characters
                    if event.unicode.isprintable():
                        self.text += event.unicode
                
                # Re-render the text
                if self.password:
                    self.txt_surface = FONT_SMALL.render('•' * len(self.text), True, WHITE)
                else:
                    self.txt_surface = FONT_SMALL.render(self.text, True, WHITE)
        
        return None

    def update(self):
        # Update the size of the box if the text is too long
        width = max(200, self.txt_surface.get_width() + 30)  # Ensure minimum width
        if self.icon:
            width += 30  # Make room for icon
        self.rect.w = width
        
        # Update cursor blink
        self.blink_timer += 1
        if self.blink_timer > 30:  # Adjust blink speed
            self.blink_timer = 0
            self.show_cursor = not self.show_cursor
        
        # Update focus animation
        if self.active:
            self.focus_animation = min(1.0, self.focus_animation + 0.1)
        else:
            self.focus_animation = max(0.0, self.focus_animation - 0.1)
        
        # Update error/success timers
        if self.error_timer > 0:
            self.error_timer -= 1
            if self.error_timer == 0:
                self.error = False
        
        if self.success_timer > 0:
            self.success_timer -= 1
            if self.success_timer == 0:
                self.success = False

    def set_error(self, duration=180):
        self.error = True
        self.error_timer = duration
        self.success = False
        self.success_timer = 0

    def set_success(self, duration=180):
        self.success = True
        self.success_timer = duration
        self.error = False
        self.error_timer = 0

    def draw(self, screen):
        # Determine border color based on state
        if self.error:
            current_border = ERROR_RED
        elif self.success:
            current_border = SUCCESS_GREEN
        elif self.active:
            current_border = self.active_border
        else:
            current_border = self.border_color
        
        # Create a gradient background
        box_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for y in range(self.rect.height):
            # Subtle gradient
            alpha = 220 - int(y * 0.5)
            if alpha < 180: alpha = 180
            pygame.draw.line(box_surface, (*self.color, alpha), 
                           (0, y), (self.rect.width, y))
        
        # Draw the input box background with rounded corners
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)
        screen.blit(box_surface, self.rect)
        
        # Draw border with animation
        border_thickness = 1 + int(self.focus_animation * 1)
        pygame.draw.rect(screen, current_border, self.rect, border_thickness, border_radius=4)
        
        # Add subtle inner highlight
        inner_rect = self.rect.inflate(-4, -4)
        pygame.draw.rect(screen, (255, 255, 255, 20), inner_rect, 1, border_radius=3)
        
        # Draw icon if available
        text_offset = 0
        if self.icon and self.icon_surface:
            screen.blit(self.icon_surface, self.icon_rect)
            text_offset = self.icon_surface.get_width() + 5
        
        # Show placeholder if no text and not active
        if not self.text and not self.active:
            placeholder_surface = FONT_SMALL.render(self.placeholder, True, (120, 120, 120))
            screen.blit(placeholder_surface, (self.rect.x + 10 + text_offset, self.rect.y + (self.rect.height - placeholder_surface.get_height()) // 2))
        else:
            # Blit the text
            screen.blit(self.txt_surface, (self.rect.x + 10 + text_offset, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))
        
        # Draw the cursor if active
        if self.active and self.show_cursor:
            cursor_pos = self.rect.x + 10 + text_offset + self.txt_surface.get_width()
            cursor_height = self.txt_surface.get_height() + 2
            cursor_y = self.rect.y + (self.rect.height - cursor_height) // 2
            pygame.draw.line(screen, WHITE, 
                           (cursor_pos, cursor_y), 
                           (cursor_pos, cursor_y + cursor_height), 2)
        
        # Draw error/success indicators
        if self.error or self.success:
            indicator_color = ERROR_RED if self.error else SUCCESS_GREEN
            indicator_radius = 4
            indicator_x = self.rect.right - 15
            indicator_y = self.rect.centery
            
            # Draw indicator with glow
            for r in range(indicator_radius + 2, indicator_radius - 1, -1):
                alpha = 255 if r == indicator_radius else 100 - ((indicator_radius - r) * 30)
                if alpha < 0: alpha = 0
                pygame.draw.circle(screen, (*indicator_color, alpha), (indicator_x, indicator_y), r)

class Button:
    def __init__(self, x, y, width, height, text, color, pill_shaped=False, circle=False, has_dot=False, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.hover_color = (min(color[0] + 20, 255), min(color[1] + 20, 255), min(color[2] + 20, 255))
        self.pressed_color = (max(color[0] - 30, 0), max(color[1] - 30, 0), max(color[2] - 30, 0))
        self.hover_alpha = 0
        self.hover = False
        self.pressed = False
        self.glow_alpha = 0
        self.icon = icon
        
        # Use smaller font for professional look
        if len(text) > 12:
            self.text_surface = FONT_TINY.render(text, True, WHITE)
        else:
            self.text_surface = FONT_SMALL.render(text, True, WHITE)
            
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.pill_shaped = pill_shaped
        self.circle = circle
        self.has_dot = has_dot
        self.animation_time = 0
        self.ripple_effect = False
        self.ripple_radius = 0
        self.ripple_pos = (0, 0)
        self.ripple_alpha = 0
        self.ripple_color = (255, 255, 255, 80)

    def start_ripple(self, pos):
        # Create a ripple effect from the clicked position
        self.ripple_effect = True
        self.ripple_radius = 0
        rel_x = pos[0] - self.rect.x
        rel_y = pos[1] - self.rect.y
        self.ripple_pos = (rel_x, rel_y)
        self.ripple_alpha = 80

    def draw(self, screen):
        self.animation_time += 0.05
        
        # Create main button surface with transparency
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if self.circle:
            # Draw a circular button with professional styling
            radius = min(self.rect.width, self.rect.height) // 2
            center = (self.rect.width // 2, self.rect.height // 2)
            
            # Create gradient effect for background
            for r in range(radius, 0, -1):
                alpha = 180 - int((radius - r) * 1.5)
                if alpha < 0: alpha = 0
                pygame.draw.circle(button_surface, (*self.color, alpha), center, r)
            
            # Add outer glow if hovered
            if self.hover:
                for r in range(radius + 3, radius, -1):
                    alpha = 40 - ((r - radius) * 10)
                    if alpha < 0: alpha = 0
                    pygame.draw.circle(button_surface, (*self.color, alpha), center, r)
            
            # Add border
            pygame.draw.circle(button_surface, (*self.color, 255), center, radius, 2)
            
            # Add thin white border for contrast
            pygame.draw.circle(button_surface, (255, 255, 255, 120), center, radius, 1)
            
            # Add inner highlight
            pygame.draw.circle(button_surface, (255, 255, 255, 30), 
                             (center[0] - 1, center[1] - 1), radius - 2, 1)
            
            # Apply ripple effect if active
            if self.ripple_effect:
                pygame.draw.circle(button_surface, self.ripple_color,
                                 self.ripple_pos, self.ripple_radius)
                self.ripple_radius += 1
                self.ripple_alpha -= 2
                if self.ripple_alpha <= 0:
                    self.ripple_effect = False
                self.ripple_color = (255, 255, 255, self.ripple_alpha)
            
            # Apply to screen
            screen.blit(button_surface, self.rect)
            
            return
        
        # Non-circular buttons
        if self.pill_shaped:
            # Draw a professional pill-shaped button with subtle gradient
            border_radius = self.rect.height // 2
            
            # Fill with gradient
            for y in range(self.rect.height):
                # Create vertical gradient
                alpha = 220 - int(y * 0.8)
                if alpha < 160: alpha = 160  # Keep minimum opacity
                
                color = self.color
                if self.pressed:
                    color = self.pressed_color
                elif self.hover:
                    color = self.hover_color
                    
                pygame.draw.line(button_surface, (*color, alpha), 
                               (border_radius, y), (self.rect.width - border_radius, y))
                
                # Draw rounded ends of pill
                if y < border_radius:
                    # Calculate how far from the edge we need to draw
                    dx = int(border_radius - math.sqrt(border_radius**2 - (y - border_radius)**2))
                    if dx < 0: dx = 0
                    pygame.draw.line(button_surface, (*color, alpha), 
                                   (dx, y), (border_radius, y))
                    pygame.draw.line(button_surface, (*color, alpha), 
                                   (self.rect.width - border_radius, y), (self.rect.width - dx, y))
                    
                if y > self.rect.height - border_radius:
                    bottom_y = self.rect.height - y - 1
                    dx = int(border_radius - math.sqrt(border_radius**2 - (bottom_y - border_radius)**2))
                    if dx < 0: dx = 0
                    pygame.draw.line(button_surface, (*color, alpha), 
                                   (dx, y), (border_radius, y))
                    pygame.draw.line(button_surface, (*color, alpha), 
                                   (self.rect.width - border_radius, y), (self.rect.width - dx, y))
            
            # Outer border
            pygame.draw.rect(button_surface, self.color, button_surface.get_rect(), 2, 
                          border_radius=border_radius)
            
            # Inner highlight for depth
            inner_rect = button_surface.get_rect().inflate(-4, -4)
            pygame.draw.rect(button_surface, (255, 255, 255, 30), inner_rect, 1, 
                          border_radius=border_radius-2)
            
            # Bottom shadow for 3D effect
            shadow_rect = pygame.Rect(2, self.rect.height-3, self.rect.width-4, 2)
            pygame.draw.rect(button_surface, (0, 0, 0, 60), shadow_rect, 0, 
                          border_radius=2)
            
            # Add dot if needed
            if self.has_dot:
                dot_x = 15
                dot_y = self.rect.height // 2
                # Draw dot with subtle gradient
                for r in range(5, 0, -1):
                    alpha = 220 - ((5 - r) * 40)
                    pygame.draw.circle(button_surface, (*self.color, alpha), (dot_x, dot_y), r)
                # Add highlight to dot
                pygame.draw.circle(button_surface, (255, 255, 255, 100), (dot_x-1, dot_y-1), 2)
        else:
            # Standard rectangle button with professional styling
            border_radius = 5
            
            # Background fill with gradient
            for y in range(self.rect.height):
                alpha = 220 - int(y * 0.8)
                if alpha < 160: alpha = 160
                
                color = self.color
                if self.pressed:
                    color = self.pressed_color
                elif self.hover:
                    color = self.hover_color
                    
                pygame.draw.line(button_surface, (*color, alpha), 
                               (border_radius, y), (self.rect.width - border_radius, y))
                
                # Handle rounded corners
                if y < border_radius:
                    dx = int(border_radius - math.sqrt(border_radius**2 - (y - border_radius)**2))
                    if dx < 0: dx = 0
                    pygame.draw.line(button_surface, (*color, alpha), 
                                   (dx, y), (border_radius, y))
                    pygame.draw.line(button_surface, (*color, alpha), 
                                   (self.rect.width - border_radius, y), (self.rect.width - dx, y))
                    
                if y > self.rect.height - border_radius:
                    bottom_y = self.rect.height - y - 1
                    dx = int(border_radius - math.sqrt(border_radius**2 - (bottom_y - border_radius)**2))
                    if dx < 0: dx = 0
                    pygame.draw.line(button_surface, (*color, alpha), 
                                   (dx, y), (border_radius, y))
                    pygame.draw.line(button_surface, (*color, alpha), 
                                   (self.rect.width - border_radius, y), (self.rect.width - dx, y))
            
            # Draw borders
            pygame.draw.rect(button_surface, self.color, button_surface.get_rect(), 2, 
                          border_radius=border_radius)
            
            # Inner highlight
            inner_rect = button_surface.get_rect().inflate(-4, -4)
            pygame.draw.rect(button_surface, (255, 255, 255, 30), inner_rect, 1, 
                          border_radius=border_radius-1)
        
        # Apply ripple effect if active (for all non-circular buttons)
        if self.ripple_effect:
            # Create a circular ripple mask
            ripple_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surface, self.ripple_color, 
                            self.ripple_pos, self.ripple_radius)
            
            # Apply the ripple to the button
            button_surface.blit(ripple_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            # Update ripple animation
            self.ripple_radius += 2
            self.ripple_alpha -= 3
            if self.ripple_alpha <= 0:
                self.ripple_effect = False
            self.ripple_color = (255, 255, 255, self.ripple_alpha)
        
        # Apply to screen
        screen.blit(button_surface, self.rect)
        
        # Draw text with proper positioning and shadow for depth
        if self.text:
            # Text shadow for depth
            shadow_surface = self.text_surface.copy()
            shadow_surface.set_alpha(100)
            shadow_rect = self.text_rect.copy()
            shadow_rect.x += 1
            shadow_rect.y += 1
            screen.blit(shadow_surface, shadow_rect)
            
            # Adjust text position if has_dot
            if self.has_dot and self.pill_shaped:
                text_rect = self.text_rect.copy()
                text_rect.x += 10  # Offset text to make room for dot
                screen.blit(self.text_surface, text_rect)
            else:
                screen.blit(self.text_surface, self.text_rect)
            
        # Draw dot on left side if needed for non-pill buttons
        if self.has_dot and not self.pill_shaped:
            dot_x = self.rect.left - 15
            dot_y = self.rect.centery
            # Draw dot with gradient
            for r in range(5, 0, -1):
                alpha = 220 - ((5 - r) * 40)
                pygame.draw.circle(screen, (*self.color, alpha), (dot_x, dot_y), r)
            # Add highlight
            pygame.draw.circle(screen, (255, 255, 255, 100), (dot_x-1, dot_y-1), 2)

    def update(self, mouse_pos):
        prev_hover = self.hover
        self.hover = self.rect.collidepoint(mouse_pos)
        
        # Trigger animation if hover state changed
        if self.hover and not prev_hover:
            self.glow_alpha = 0  # Reset glow animation
            
        self.glow_alpha = min(255, self.glow_alpha + 5) if self.hover else max(0, self.glow_alpha - 5)

    def is_clicked(self, pos):
        was_clicked = self.rect.collidepoint(pos)
        if was_clicked:
            self.pressed = True
            self.start_ripple(pos)
            # Schedule button to return to normal state
            pygame.time.set_timer(pygame.USEREVENT, 100)
        return was_clicked
        
    def reset_state(self):
        self.pressed = False

class MiniGameDemo:
    """A small demo of the ping pong game to be displayed in preview section"""
    def __init__(self, rect):
        self.rect = rect
        self.ball_x = rect.width // 2
        self.ball_y = rect.height // 2
        self.ball_dx = 2
        self.ball_dy = 2
        self.ball_size = 10
        self.paddle1_y = rect.height // 2 - 25
        self.paddle2_y = rect.height // 2 - 25
        self.paddle_height = 50
        self.paddle_width = 8
        self.ai_speed = 1.5
        self.surface = pygame.Surface((rect.width, rect.height))

    def update(self):
        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ball collision with top/bottom
        if self.ball_y <= 0 or self.ball_y >= self.rect.height - self.ball_size:
            self.ball_dy *= -1
        
        # Ball collision with paddles
        if (self.ball_x <= self.paddle_width and 
            self.ball_y >= self.paddle1_y and 
            self.ball_y <= self.paddle1_y + self.paddle_height):
            self.ball_dx *= -1
        
        if (self.ball_x >= self.rect.width - self.paddle_width - self.ball_size and 
            self.ball_y >= self.paddle2_y and 
            self.ball_y <= self.paddle2_y + self.paddle_height):
            self.ball_dx *= -1
        
        # Ball out of bounds - reset
        if self.ball_x < 0 or self.ball_x > self.rect.width:
            self.ball_x = self.rect.width // 2
            self.ball_y = self.rect.height // 2
            self.ball_dx = 2 if self.ball_dx < 0 else -2
            self.ball_dy = 2 if self.ball_dy < 0 else -2
        
        # Simple AI for both paddles
        # Left paddle
        if self.paddle1_y + self.paddle_height // 2 < self.ball_y:
            self.paddle1_y += self.ai_speed
        elif self.paddle1_y + self.paddle_height // 2 > self.ball_y:
            self.paddle1_y -= self.ai_speed
        
        # Right paddle
        if self.paddle2_y + self.paddle_height // 2 < self.ball_y:
            self.paddle2_y += self.ai_speed
        elif self.paddle2_y + self.paddle_height // 2 > self.ball_y:
            self.paddle2_y -= self.ai_speed
        
        # Keep paddles within bounds
        self.paddle1_y = max(0, min(self.rect.height - self.paddle_height, self.paddle1_y))
        self.paddle2_y = max(0, min(self.rect.height - self.paddle_height, self.paddle2_y))

    def draw(self):
        # Clear surface
        self.surface.fill(BLACK)
        
        # Draw border
        pygame.draw.rect(self.surface, NEON_BLUE, (0, 0, self.rect.width, self.rect.height), 2)
        
        # Draw center line
        for y in range(0, self.rect.height, 10):
            pygame.draw.rect(self.surface, (50, 50, 50), (self.rect.width // 2 - 1, y, 2, 5))
        
        # Draw paddles
        pygame.draw.rect(self.surface, NEON_GREEN, (0, self.paddle1_y, self.paddle_width, self.paddle_height))
        pygame.draw.rect(self.surface, NEON_RED, (self.rect.width - self.paddle_width, self.paddle2_y, self.paddle_width, self.paddle_height))
        
        # Draw ball
        pygame.draw.circle(self.surface, WHITE, (self.ball_x, self.ball_y), self.ball_size)
        
        return self.surface

def draw_section_header(screen, rect, text, border_color):
    """Draw a section header with the given border color"""
    # Create a subtle gradient background
    gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        # Gradually darken from top to bottom
        alpha = 220 - int(y * 0.5)
        if alpha < 0: alpha = 0
        pygame.draw.line(gradient_surface, (*SECTION_BG, alpha), 
                       (0, y), (rect.width, y))
    
    # Draw section background
    pygame.draw.rect(screen, SECTION_BG, rect, border_radius=3)
    screen.blit(gradient_surface, rect)
    
    # Draw a subtle inset shadow effect
    shadow_width = 2
    for i in range(shadow_width):
        alpha = 40 - (i * 10)
        if alpha < 0: alpha = 0
        shadow_rect = rect.inflate(-(i*2), -(i*2))
        pygame.draw.rect(screen, (0, 0, 0, alpha), shadow_rect, 1, border_radius=3)
    
    # Draw professional border (slightly rounded corners, thinner)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=3)
    
    # Add an inner highlight for a premium look
    highlight_rect = rect.inflate(-4, -4)
    pygame.draw.rect(screen, (*border_color, 30), highlight_rect, 1, border_radius=2)
    
    # Draw header text with a more professional font style
    header_text = FONT_MEDIUM.render(text.upper(), True, WHITE)
    header_rect = header_text.get_rect(midtop=(rect.centerx, rect.top + 15))
    
    # Add subtle text shadow for depth
    shadow_text = FONT_MEDIUM.render(text.upper(), True, (0, 0, 0))
    shadow_rect = shadow_text.get_rect(midtop=(header_rect.centerx + 1, header_rect.top + 1))
    screen.blit(shadow_text, shadow_rect)
    screen.blit(header_text, header_rect)
    
    # Add a professional separator line
    line_y = rect.top + 55
    line_width = rect.width - 60
    
    # Draw line with gradient effect
    line_surf = pygame.Surface((line_width, 2), pygame.SRCALPHA)
    for x in range(line_width):
        # Create gradient along the line
        position = x / line_width
        if position < 0.5:
            alpha = int(position * 510)  # 0 to 255
        else:
            alpha = int((1 - position) * 510)  # 255 to 0
        
        if alpha > 255: alpha = 255
        pygame.draw.line(line_surf, (*border_color, alpha), (x, 0), (x, 1))
    
    screen.blit(line_surf, (rect.left + 30, line_y))

def draw_score_item(screen, x, y, username, score, index, width):
    """Draw a single score item in the scores section as a square icon with professional styling"""
    # Create a square icon with premium styling
    item_size = 80
    margin = 10
    row = index // 8  # 8 items per row
    col = index % 8
    
    item_x = x + col * (item_size + margin)
    item_y = y + row * (item_size + margin)
    
    item_rect = pygame.Rect(item_x, item_y, item_size, item_size)
    
    # Professional color scheme based on position
    if index < 8:  # First row uses lighter colors
        base_color = (210, 210, 210) if index == 0 else (180, 180, 180)
        text_color = (40, 40, 40)  # Dark text on light background
        number_color = (30, 30, 30)
    else:  # Second row uses darker colors
        base_color = (60, 60, 60)
        text_color = (220, 220, 220)  # Light text on dark background
        number_color = (200, 200, 200)
    
    # Apply gradient based on column position
    brightness_factor = 1.0 - (col * 0.05)  # Subtle gradient across columns
    base_color = tuple(int(c * brightness_factor) for c in base_color)
    
    # Create gradient surface for professional look
    gradient_surface = pygame.Surface((item_size, item_size), pygame.SRCALPHA)
    for y_offset in range(item_size):
        # Calculate gradient intensity
        gradient_factor = 1.0 - (y_offset / item_size * 0.2)  # Top to bottom gradient
        pixel_color = tuple(int(c * gradient_factor) for c in base_color)
        pygame.draw.line(gradient_surface, (*pixel_color, 255), 
                       (0, y_offset), (item_size, y_offset))
    
    # Border colors with premium styling
    if index == 0:  # First place
        border_color = NEON_RED
        glow_color = (*NEON_RED, 100)  # Semi-transparent glow
        has_glow = True
    elif index == 1:  # Second place
        border_color = NEON_ORANGE
        glow_color = (*NEON_ORANGE, 70)
        has_glow = True
    elif index == 2:  # Third place
        border_color = NEON_PURPLE
        glow_color = (*NEON_PURPLE, 50)
        has_glow = True
    else:
        border_color = (120, 120, 120)
        glow_color = (120, 120, 120, 30)
        has_glow = False
    
    # Draw base with rounded corners
    pygame.draw.rect(screen, base_color, item_rect, border_radius=8)
    screen.blit(gradient_surface, item_rect)
    
    # Add subtle shadow at bottom
    shadow_rect = pygame.Rect(item_x + 2, item_y + item_size - 4, item_size - 4, 4)
    shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    for i in range(shadow_rect.height):
        alpha = 40 - (i * 10)
        if alpha < 0: alpha = 0
        pygame.draw.line(shadow_surface, (0, 0, 0, alpha), 
                       (0, i), (shadow_rect.width, i))
    screen.blit(shadow_surface, shadow_rect)
    
    # Add subtle inner highlight at top
    highlight_rect = pygame.Rect(item_x + 2, item_y + 2, item_size - 4, 2)
    highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(highlight_surf, (255, 255, 255, 30), 
                   (0, 0, highlight_rect.width, highlight_rect.height))
    screen.blit(highlight_surf, highlight_rect)
    
    # Draw premium border
    pygame.draw.rect(screen, border_color, item_rect, 2, border_radius=8)
    
    # Add glow effect for top 3
    if has_glow:
        for i in range(1, 4):
            glow_rect = item_rect.inflate(i*2, i*2)
            glow_alpha = 30 - (i * 10)
            if glow_alpha > 0:
                pygame.draw.rect(screen, (*border_color, glow_alpha), 
                               glow_rect, 1, border_radius=8 + i)
    
    # Draw rank number with subtle shadow for depth
    rank_text = f"#{index + 1}"
    if index < 3:  # Special styling for top 3
        rank_surf = FONT_SMALL.render(rank_text, True, number_color)
        rank_shadow = FONT_SMALL.render(rank_text, True, (0, 0, 0))
    else:
        rank_surf = FONT_TINY.render(rank_text, True, number_color)
        rank_shadow = FONT_TINY.render(rank_text, True, (0, 0, 0))
    
    rank_rect = rank_surf.get_rect(midtop=(item_x + item_size//2, item_y + 5))
    shadow_rect = rank_shadow.get_rect(midtop=(rank_rect.x + 1, rank_rect.y + 1))
    shadow_rect.x = rank_rect.x + 1
    shadow_rect.y = rank_rect.y + 1
    
    # Apply shadow with reduced alpha
    shadow_temp = rank_shadow.copy()
    shadow_temp.set_alpha(70)
    screen.blit(shadow_temp, shadow_rect)
    screen.blit(rank_surf, rank_rect)
    
    # Draw username with truncation and professional styling
    max_name_len = 8
    display_name = username if len(username) <= max_name_len else username[:max_name_len-1] + "…"
    
    name_surf = FONT_TINY.render(display_name, True, text_color)
    name_shadow = FONT_TINY.render(display_name, True, (0, 0, 0))
    
    name_rect = name_surf.get_rect(center=(item_x + item_size//2, item_y + item_size//2))
    shadow_rect = name_shadow.get_rect(center=(name_rect.x + 1, name_rect.y + 1))
    
    # Apply shadow with reduced alpha
    shadow_temp = name_shadow.copy()
    shadow_temp.set_alpha(70)
    screen.blit(shadow_temp, shadow_rect)
    screen.blit(name_surf, name_rect)
    
    # Draw score at bottom with subtle highlight
    score_text = str(score)
    score_surf = FONT_TINY.render(score_text, True, border_color)
    score_glow = FONT_TINY.render(score_text, True, (255, 255, 255))
    
    score_rect = score_surf.get_rect(midbottom=(item_x + item_size//2, item_y + item_size - 8))
    glow_rect = score_glow.get_rect(midbottom=(score_rect.x, score_rect.y))
    
    # Apply glow with reduced alpha
    glow_temp = score_glow.copy()
    glow_temp.set_alpha(30)
    
    screen.blit(glow_temp, (glow_rect.x - 1, glow_rect.y - 1))
    screen.blit(score_surf, score_rect)
    
    # Add subtle divider line above score
    divider_y = score_rect.top - 6
    pygame.draw.line(screen, (*border_color, 60), 
                   (item_x + 15, divider_y), (item_x + item_size - 15, divider_y))

def get_login_choice():
    """Show login screen and handle authentication"""
    global screen
    
    if FULLSCREEN:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    pygame.display.set_caption("Brink")
    
    # Setup UI elements
    clock = pygame.time.Clock()
    
    # Define the deception mode effects
    deception_effects = [
        "INVISIBLE_ENEMY",       # Enemy paddle is invisible but still works
        "INVISIBLE_PLAYER",      # Player paddle is invisible but still works
        "BALL_MULTIPLY",         # Multiple balls appear
        "INVISIBLE_BALL",        # Ball becomes invisible
        "REVERSE_CONTROLS",      # Player controls are reversed
        "SHRINKING_PADDLES",     # Paddles get smaller over time
        "TELEPORTING_BALL",      # Ball randomly teleports
        "SPEED_CHANGES",         # Ball randomly changes speed
        "GRAVITY_SHIFT",         # Ball path affected by "gravity"
        "COLOR_CHAOS"            # Screen colors rapidly change
    ]
    
    # Define the three main sections based on the image
    section_margin = 20
    
    # Left sidebar section - orange border
    sidebar_width = WIDTH // 6
    sidebar_rect = pygame.Rect(0, 0, sidebar_width, HEIGHT)
    
    # Main content area - blue border
    main_rect = pygame.Rect(sidebar_width, 0, WIDTH - sidebar_width, HEIGHT)
    
    # Create mini game demo for preview section
    mini_game = MiniGameDemo(pygame.Rect(main_rect.left + WIDTH // 4, main_rect.top + HEIGHT // 5, 
                                       WIDTH // 3, HEIGHT // 3))
    
    # Create exit button in top right corner
    exit_button_radius = 20
    exit_button = Button(WIDTH - exit_button_radius*2 - 20, 20, 
                       exit_button_radius*2, exit_button_radius*2, "", WHITE, circle=True)
    
    # Create back button
    back_button_width = 80
    back_button_height = 30
    back_button = Button(20, 20, back_button_width, back_button_height, 
                       "BACK", NEON_RED, pill_shaped=True)
    
    # Create input fields with minimal styling
    input_width = sidebar_width - 40
    
    # Username and password fields
    username_box = InputBox(sidebar_rect.left + 20, sidebar_rect.top + HEIGHT // 3, 
                          input_width, 40, placeholder="Username")
    password_box = InputBox(sidebar_rect.left + 20, sidebar_rect.top + HEIGHT // 3 + 60, 
                          input_width, 40, placeholder="Password", password=True)
    
    # Create buttons with minimal styling
    button_width = input_width
    button_height = 40
    button_spacing = 20
    button_y = sidebar_rect.top + HEIGHT // 3 + 140
    
    # Use pill-shaped buttons for login and register
    login_button = Button(sidebar_rect.left + 20, button_y, 
                       button_width, button_height, "LOGIN", NEON_BLUE, pill_shaped=True)
    
    register_button = Button(sidebar_rect.left + 20, button_y + button_height + button_spacing, 
                          button_width, button_height, "REGISTER", NEON_GREEN, pill_shaped=True)
    
    # Game mode buttons
    mode_button_width = input_width
    mode_button_y_start = sidebar_rect.top + HEIGHT // 2 + 50
    mode_button_spacing = 20
    
    # Simplified pill-shaped buttons for game modes
    pvc_button = Button(sidebar_rect.left + 20, mode_button_y_start, 
                      mode_button_width, button_height, "PVC MODE", NEON_BLUE, pill_shaped=True)
    
    pvp_button = Button(sidebar_rect.left + 20, mode_button_y_start + button_height + mode_button_spacing, 
                      mode_button_width, button_height, "PVP MODE", NEON_RED, pill_shaped=True)
    
    deception_button = Button(sidebar_rect.left + 20, mode_button_y_start + (button_height + mode_button_spacing) * 2,
                           mode_button_width, button_height, "DECEPTION", NEON_PURPLE, pill_shaped=True)
    
    # Deception mode sub-buttons (only shown when deception is selected)
    deception_pvc_button = Button(sidebar_rect.left + 20, mode_button_y_start + (button_height + mode_button_spacing) * 3,
                               mode_button_width, button_height, "DECEPTION PVC", NEON_BLUE, pill_shaped=True)
    
    deception_pvp_button = Button(sidebar_rect.left + 20, mode_button_y_start + (button_height + mode_button_spacing) * 4,
                               mode_button_width, button_height, "DECEPTION PVP", NEON_RED, pill_shaped=True)
    
    # State variables
    username = ""
    authenticated = False
    selected_mode = None
    error_message = ""
    error_timer = 0
    previous_state = None  # To track states for the back button
    show_deception_submodes = False  # Flag to show/hide deception sub-modes
    selected_deception_effects = []  # To store selected deception effects
    
    # Animation variables
    current_time = 0
    
    # Main loop
    running = True
    while running:
        current_time += 0.02
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            
            # Handle input box events
            if not authenticated:
                username_result = username_box.handle_event(event)
                password_result = password_box.handle_event(event)
                
                # Handle tab key to move between fields
                if username_result == "TAB":
                    password_box.active = True
                    username_box.active = False
                elif password_result == "TAB":
                    password_box.active = False
                    username_box.active = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.is_clicked(event.pos):
                    pygame.quit()
                    sys.exit()
                
                if back_button.is_clicked(event.pos):
                    if authenticated:
                        # Go back to login screen
                        authenticated = False
                        previous_state = "login"
                    elif previous_state == "login":
                        # Already at login screen, could exit or do nothing
                        pass
                    
                if not authenticated:
                    if login_button.is_clicked(event.pos):
                        if username_box.text and password_box.text:
                            if authenticate_user(username_box.text, password_box.text):
                                authenticated = True
                                username = username_box.text
                                error_message = ""
                            else:
                                error_message = "Invalid username or password"
                                error_timer = 180  # Show for 3 seconds
                                password_box.set_error()
                        else:
                            error_message = "Please enter username and password"
                            error_timer = 180
                            if not username_box.text:
                                username_box.set_error()
                            if not password_box.text:
                                password_box.set_error()
                    
                    elif register_button.is_clicked(event.pos):
                        if username_box.text and password_box.text:
                            # Check for existing username before registration
                            if len(username_box.text) < 3:
                                error_message = "Username must be at least 3 characters"
                                error_timer = 180
                                username_box.set_error()
                            elif len(password_box.text) < 4:
                                error_message = "Password must be at least 4 characters"
                                error_timer = 180
                                password_box.set_error()
                            else:
                                # Get all usernames to check for duplicates
                                existing_users = []
                                try:
                                    with open("users.json", "r") as f:
                                        users_data = json.load(f)
                                        existing_users = [user["username"].lower() for user in users_data]
                                except:
                                    existing_users = []
                                
                                if username_box.text.lower() in existing_users:
                                    error_message = "Username already exists"
                                    error_timer = 180
                                    username_box.set_error()
                                else:
                                    if create_user(username_box.text, password_box.text):
                                        authenticated = True
                                        username = username_box.text
                                        error_message = ""
                                        username_box.set_success()
                                        password_box.set_success()
                                    else:
                                        error_message = "Failed to create user"
                                        error_timer = 180
                                        username_box.set_error()
                        else:
                            error_message = "Please enter username and password"
                            error_timer = 180
                            if not username_box.text:
                                username_box.set_error()
                            if not password_box.text:
                                password_box.set_error()
                else:
                    # User is authenticated, handle game mode selection
                    if pvc_button.is_clicked(event.pos):
                        selected_mode = "PVC"
                        running = False
                    elif pvp_button.is_clicked(event.pos):
                        selected_mode = "PVP"
                        running = False
                    elif deception_button.is_clicked(event.pos):
                        # Toggle showing deception sub-modes
                        show_deception_submodes = not show_deception_submodes
                        if not show_deception_submodes:
                            # If hiding submodes, also reset any deception effect selections
                            selected_deception_effects = []
                    
                    # Handle deception sub-mode buttons if they're shown
                    if show_deception_submodes:
                        if deception_pvc_button.is_clicked(event.pos):
                            try:
                                # For compatibility with the main game
                                selected_mode = "DECEPTION"  # The main game expects DECEPTION as the mode
                                running = False
                            except Exception as e:
                                print(f"Error selecting deception mode: {e}")
                                selected_mode = "DECEPTION"
                                running = False
                        elif deception_pvp_button.is_clicked(event.pos):
                            try:
                                # For compatibility with the main game
                                selected_mode = "DECEPTION"  # The main game expects DECEPTION as the mode
                                running = False
                            except Exception as e:
                                print(f"Error selecting deception mode: {e}")
                                selected_mode = "DECEPTION" 
                                running = False
        
        # Update UI elements
        exit_button.update(mouse_pos)
        back_button.update(mouse_pos)
        
        if not authenticated:
            username_box.update()
            password_box.update()
            login_button.update(mouse_pos)
            register_button.update(mouse_pos)
        else:
            pvc_button.update(mouse_pos)
            pvp_button.update(mouse_pos)
            deception_button.update(mouse_pos)
            
            # Update deception sub-mode buttons if they're shown
            if show_deception_submodes:
                deception_pvc_button.update(mouse_pos)
                deception_pvp_button.update(mouse_pos)
        
        # Update mini game demo
        mini_game.update()
        
        # Update error timer
        if error_timer > 0:
            error_timer -= 1
        
        # Drawing
        # Draw background (matte black)
        screen.fill(BLACK)
        
        # Draw left sidebar with orange border
        pygame.draw.rect(screen, SECTION_BG, sidebar_rect)
        pygame.draw.line(screen, NEON_ORANGE, 
                       (sidebar_width, 0), 
                       (sidebar_width, HEIGHT), 2)
        
        # Draw main content area with blue border
        pygame.draw.rect(screen, SECTION_BG, main_rect)
        
        # Draw blue vertical line
        pygame.draw.line(screen, NEON_BLUE, 
                       (sidebar_width + 50, 0), 
                       (sidebar_width + 50, HEIGHT), 2)
        
        # Draw green accent line segment
        pygame.draw.line(screen, NEON_GREEN, 
                       (sidebar_width + 50, 120), 
                       (sidebar_width + 100, 120), 4)
        
        # Draw the mini game in the preview section
        game_surface = mini_game.draw()
        screen.blit(game_surface, (main_rect.left + WIDTH // 4, main_rect.top + HEIGHT // 5))
        
        # Draw exit button
        exit_button.draw(screen)
        
        # Draw back button
        back_button.draw(screen)
        
        # Draw cross inside exit button
        cross_size = exit_button_radius - 5
        cross_color = BLACK
        cross_thickness = 2
        
        # Draw cross lines
        pygame.draw.line(screen, cross_color, 
                       (exit_button.rect.centerx - cross_size, exit_button.rect.centery - cross_size),
                       (exit_button.rect.centerx + cross_size, exit_button.rect.centery + cross_size),
                       cross_thickness)
        pygame.draw.line(screen, cross_color, 
                       (exit_button.rect.centerx + cross_size, exit_button.rect.centery - cross_size),
                       (exit_button.rect.centerx - cross_size, exit_button.rect.centery + cross_size),
                       cross_thickness)
        
        # Draw login content if not authenticated
        if not authenticated:
            # Draw input boxes
            username_box.draw(screen)
            password_box.draw(screen)
            
            # Draw buttons
            login_button.draw(screen)
            register_button.draw(screen)
            
            # Draw error message if any
            if error_timer > 0:
                error_surf = FONT_TINY.render(error_message, True, NEON_RED)
                screen.blit(error_surf, (sidebar_rect.centerx - error_surf.get_width()//2, 
                                      button_y + button_height + 15))
        else:
            # Draw welcome message
            welcome_text = FONT_SMALL.render(f"WELCOME, {username.upper()}", True, NEON_GREEN)
            screen.blit(welcome_text, (sidebar_rect.centerx - welcome_text.get_width()//2, 
                                    sidebar_rect.top + 50))
            
            # Draw game mode selection prompt
            mode_text = FONT_TINY.render("SELECT GAME MODE:", True, WHITE)
            screen.blit(mode_text, (sidebar_rect.centerx - mode_text.get_width()//2, 
                                 sidebar_rect.top + 100))
            
            # Draw game mode buttons
            pvc_button.draw(screen)
            pvp_button.draw(screen)
            deception_button.draw(screen)
            
            # Draw deception sub-mode buttons if they're shown
            if show_deception_submodes:
                deception_pvc_button.draw(screen)
                deception_pvp_button.draw(screen)
                
                # Draw info about deception mode
                deception_info = FONT_TINY.render("DECEPTION MODE INCLUDES:", True, NEON_PURPLE)
                screen.blit(deception_info, (sidebar_rect.centerx - deception_info.get_width()//2, 
                                          sidebar_rect.bottom - 200))
                
                # List some of the deception effects
                effect_y = sidebar_rect.bottom - 180
                for i, effect in enumerate(deception_effects[:5]):
                    effect_text = FONT_TINY.render(f"• {effect.replace('_', ' ')}", True, WHITE)
                    screen.blit(effect_text, (sidebar_rect.left + 30, effect_y + i * 20))
                
                more_effects = FONT_TINY.render("...AND MORE SURPRISES!", True, NEON_RED)
                screen.blit(more_effects, (sidebar_rect.centerx - more_effects.get_width()//2, 
                                        effect_y + 5 * 20 + 10))
            
            # Draw mode description
            mode_desc = {
                "PVC": "Player vs Computer - Test your skills against AI",
                "PVP": "Player vs Player - Challenge a friend",
                "DECEPTION": "Unpredictable gameplay with random events"
            }
            
            hover_desc = None
            if pvc_button.hover:
                hover_desc = mode_desc["PVC"]
            elif pvp_button.hover:
                hover_desc = mode_desc["PVP"]
            elif deception_button.hover:
                hover_desc = mode_desc["DECEPTION"]
            elif show_deception_submodes and deception_pvc_button.hover:
                hover_desc = "Deception Mode vs Computer - Chaos and AI combined!"
            elif show_deception_submodes and deception_pvp_button.hover:
                hover_desc = "Deception Mode vs Player - Double the chaos, double the fun!"
            
            if hover_desc:
                desc_surf = FONT_TINY.render(hover_desc, True, WHITE)
                desc_rect = desc_surf.get_rect(center=(sidebar_rect.centerx, sidebar_rect.bottom - 50))
                
                # Draw description background
                bg_rect = desc_rect.inflate(20, 10)
                pygame.draw.rect(screen, DARK_GRAY, bg_rect, border_radius=5)
                pygame.draw.rect(screen, LIGHT_GRAY, bg_rect, 1, border_radius=5)
                
                screen.blit(desc_surf, desc_rect)
        
        # Draw app title at the bottom with superimposition
        title_text1 = FONT_MEDIUM.render("BRINK", True, NEON_PURPLE)
        title_text2 = FONT_MEDIUM.render("BRINK", True, NEON_BLUE)
        title_text3 = FONT_MEDIUM.render("BRINK", True, NEON_RED)
        
        # Position the title texts with slight offsets for superimposition effect
        title_rect1 = title_text1.get_rect(bottomleft=(20, HEIGHT - 20))
        title_rect2 = title_text2.get_rect(bottomleft=(23, HEIGHT - 23))
        title_rect3 = title_text3.get_rect(bottomleft=(26, HEIGHT - 26))
        
        # Draw the titles in reverse order (back to front)
        screen.blit(title_text3, title_rect3)  # Bottom layer
        screen.blit(title_text2, title_rect2)  # Middle layer
        screen.blit(title_text1, title_rect1)  # Top layer
        
        # Add semi-transparent connecting lines between the title instances
        purple_line_color = (NEON_PURPLE[0], NEON_PURPLE[1], NEON_PURPLE[2], 100)
        blue_line_color = (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], 100)
        
        pygame.draw.line(screen, purple_line_color, 
                       (title_rect1.right, title_rect1.centery),
                       (title_rect2.left, title_rect2.centery), 1)
        pygame.draw.line(screen, blue_line_color, 
                       (title_rect2.right, title_rect2.centery),
                       (title_rect3.left, title_rect3.centery), 1)
        
        # Draw horizontal blue line connecting with orange border at the bottom
        pygame.draw.line(screen, NEON_BLUE, 
                       (sidebar_width, HEIGHT - 5), 
                       (WIDTH, HEIGHT - 5), 2)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Return selected game mode and username
    return selected_mode, username, selected_deception_effects if "DECEPTION" in str(selected_mode) else None

def start_login_interface():
    """Entry point for the login interface"""
    try:
        game_mode, username, deception_effects = get_login_choice()
        # Ensure we always return valid values even if there's an issue
        if game_mode and "DECEPTION" in str(game_mode) and not deception_effects:
            # If deception mode but no effects, provide default effects
            deception_effects = [
                "INVISIBLE_ENEMY", 
                "INVISIBLE_PLAYER",
                "BALL_MULTIPLY",
                "INVISIBLE_BALL",
                "REVERSE_CONTROLS"
            ]
        # For compatibility with the main game, return only mode and username
        return game_mode, username
    except Exception as e:
        print(f"Error in login interface: {e}")
        pygame.quit()
        return None, None

if __name__ == "__main__":
    try:
        result = start_login_interface()
        if isinstance(result, tuple) and len(result) >= 2:
            print(f"Selected mode: {result[0]}")
            print(f"Username: {result[1]}")
    except Exception as e:
        print(f"Error running login interface: {e}")
    finally:
        pygame.quit()
        sys.exit() 