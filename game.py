import pygame
import sys
import random
import math
import os
import time
import gc  # Garbage collection
from login import start_login_interface
from users import update_stats

# Initialize Pygame
pygame.init()

# Screen setup
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
FULLSCREEN = True

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
DARK_GRAY = (30, 30, 30)
DARKER_GRAY = (20, 20, 20)
DARKEST_GRAY = (10, 10, 15)
NEON_BLUE = (0, 195, 255)
NEON_RED = (255, 50, 50)
NEON_GREEN = (0, 255, 128)
NEON_PURPLE = (200, 0, 255)

# Game parameters - adjusted for screen size
PADDLE_WIDTH = int(WIDTH * 0.01)  # 1% of screen width
PADDLE_HEIGHT = int(HEIGHT * 0.15)  # 15% of screen height
BALL_SIZE = int(min(WIDTH, HEIGHT) * 0.025)  # 2.5% of smaller screen dimension
PADDLE_SPEED = int(HEIGHT * 0.01)  # 1% of screen height
BALL_SPEED_X = int(WIDTH * 0.005)  # 0.5% of screen width
BALL_SPEED_Y = int(HEIGHT * 0.01)  # 1% of screen height

# Maximum ball speed to prevent instability
MAX_BALL_SPEED = int(min(WIDTH, HEIGHT) * 0.02)  # Cap at 2% of screen dimension

# Deception mode parameters
DECEPTION_EFFECT_DURATION = 10  # Duration of each effect in seconds
DECEPTION_EFFECTS = [
    "INVISIBLE_ENEMY",      # Enemy paddle is invisible but still works
    "INVISIBLE_PLAYER",     # Player paddle is invisible but still works
    "BALL_MULTIPLY",        # Multiple balls appear
    "INVISIBLE_BALL",       # Ball becomes invisible
    "REVERSE_CONTROLS",     # Player controls are reversed
    "SHRINKING_PADDLES",    # Paddles get smaller over time
    "TELEPORTING_BALL",     # Ball randomly teleports
    "SPEED_CHANGES",        # Ball randomly changes speed
    "GRAVITY_SHIFT",        # Ball path affected by "gravity"
    "COLOR_CHAOS"           # Screen colors rapidly change
]

# Font setup
try:
    # First try to load the Alumni Sans SC font
    font_path = os.path.join(os.path.dirname(__file__), "AlumniSansSC-Regular.ttf")
    if os.path.exists(font_path):
        FONT = pygame.font.Font(font_path, int(HEIGHT * 0.1))  # 10% of screen height
        FONT_LARGE = pygame.font.Font(font_path, int(HEIGHT * 0.07))
        FONT_MEDIUM = pygame.font.Font(font_path, int(HEIGHT * 0.05))
        FONT_SMALL = pygame.font.Font(font_path, int(HEIGHT * 0.03))
        FONT_TINY = pygame.font.Font(font_path, int(HEIGHT * 0.02))
    else:
        # If font file doesn't exist, use system font
        FONT = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.1))
        FONT_LARGE = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.07))
        FONT_MEDIUM = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.05))
        FONT_SMALL = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.03))
        FONT_TINY = pygame.font.SysFont("Alumni Sans SC", int(HEIGHT * 0.02))
except:
    # Fallback to Arial if Alumni Sans SC is not available
    FONT = pygame.font.SysFont("Arial", int(HEIGHT * 0.08))
    FONT_LARGE = pygame.font.SysFont("Arial", int(HEIGHT * 0.06))
    FONT_MEDIUM = pygame.font.SysFont("Arial", int(HEIGHT * 0.04))
    FONT_SMALL = pygame.font.SysFont("Arial", int(HEIGHT * 0.025))
    FONT_TINY = pygame.font.SysFont("Arial", int(HEIGHT * 0.018))

# Pre-render common text to improve performance
GAME_OVER_TEXT = None
RESTART_TEXT = None

# Load difficulty logos
difficulty_logos = {
    "New Born": None,
    "Normie": None,
    "Knight of Hell": None
}

# Difficulty descriptions
difficulty_descriptions = {
    "New Born": "For beginners - AI makes mistakes and moves slowly",
    "Normie": "Standard difficulty - AI plays competently",
    "Knight of Hell": "Expert difficulty - AI predicts ball path and uses special moves"
}

def pre_render_text():
    """Pre-render commonly used text surfaces to improve performance"""
    global GAME_OVER_TEXT, RESTART_TEXT
    try:
        GAME_OVER_TEXT = FONT.render("GAME OVER", True, NEON_RED)
        RESTART_TEXT = FONT_SMALL.render("PRESS 'R' TO RESTART", True, NEON_BLUE)
    except Exception as e:
        print(f"Error pre-rendering text: {e}")
        # Create empty surfaces as fallback
        GAME_OVER_TEXT = pygame.Surface((1, 1))
        RESTART_TEXT = pygame.Surface((1, 1))

def load_difficulty_logos():
    """Load the difficulty logo images from the Images of Sans folder"""
    try:
        difficulty_logos["New Born"] = pygame.image.load(os.path.join("Images of Sans", "Login for NewBorn.png"))
        difficulty_logos["Normie"] = pygame.image.load(os.path.join("Images of Sans", "Login for Normie.webp"))
        difficulty_logos["Knight of Hell"] = pygame.image.load(os.path.join("Images of Sans", "Logo for knight of hell.png"))
        
        # Scale images to appropriate size
        max_width = WIDTH * 0.4
        max_height = HEIGHT * 0.4
        
        for key in difficulty_logos:
            if difficulty_logos[key] is not None:
                img = difficulty_logos[key]
                img_ratio = img.get_width() / img.get_height()
                
                if img.get_width() > max_width:
                    new_width = max_width
                    new_height = new_width / img_ratio
                    difficulty_logos[key] = pygame.transform.scale(img, (int(new_width), int(new_height)))
                
                if difficulty_logos[key].get_height() > max_height:
                    new_height = max_height
                    new_width = new_height * img_ratio
                    difficulty_logos[key] = pygame.transform.scale(img, (int(new_width), int(new_height)))
    except Exception as e:
        print(f"Error loading difficulty logos: {e}")
        # Use fallback text if images can't be loaded
        difficulty_logos["New Born"] = None
        difficulty_logos["Normie"] = None 
        difficulty_logos["Knight of Hell"] = None

# Game state variables
game_mode = None
current_user = None
opponent_user = "Computer"  # Default for PVC mode
left_score = 0
right_score = 0
winner = None
game_over = False
ai_difficulty = None  # Initialize as None, will be set based on mode
pvc_difficulty_selected = False  # Flag to track if difficulty has been selected
consecutive_defeats = 0  # Track consecutive defeats in Knight of Hell mode
consecutive_ai_scores = 0  # Track consecutive AI scores without player scoring
displayed_thresholds = set()  # Track which quote thresholds have already been displayed

# Deception mode variables
current_deception_effect = None
deception_effect_start_time = 0
deception_balls = []  # For ball multiplication effect
original_paddle_height = 0  # For shrinking paddles effect
is_reverse_controls = False  # For reverse controls effect

# Motivational quotes for consecutive defeats in Knight of Hell mode
defeat_quotes = {
    5: "Life must go on",
    10: "Stop overthinking, you can't control everything, just let it be",
    15: "There are no secrets to success. It is the result of preparation, hard work, and learning from failure",
    20: "NOTHING IS MORE\nDANGEROUS THAN\nSTUPID PEOPLE\nWHO THINK\nTHEY'RE SMART",
    25: "It's amazing how dumb people can impress you with how much stupider they can be when they really assert themselves",
    30: "YOU THINK A PIECE OF SHIT FEELS POPULAR BECAUSE IT'S SURROUNDED BY FLIES?"
}

# Performance monitoring
frame_times = []
MAX_FRAME_TIMES = 60  # Track last 60 frames
performance_issue_detected = False
last_gc_time = 0  # For tracking garbage collection

# Sound setup - Load sounds once at startup
try:
    paddle_hit_sound = pygame.mixer.Sound("ping-pong-64516.mp3")
    other_sound = pygame.mixer.Sound("23lostbutw_iCSUTgIG.mp3")
    other_sound.set_volume(0.3)  # Lower volume (30%)
except Exception as e:
    print(f"Error loading sound: {e}")
    # Create dummy sound objects if files not found
    paddle_hit_sound = pygame.mixer.Sound(buffer=bytearray())
    other_sound = pygame.mixer.Sound(buffer=bytearray())

def play_paddle_hit_sound():
    try:
        paddle_hit_sound.play()
    except:
        pass  # Silently fail if sound can't be played

def play_other_sound():
    try:
        other_sound.play()
    except:
        pass  # Silently fail if sound can't be played

def reset_game():
    global left_paddle, right_paddle, ball, ball_dx, ball_dy, left_score, right_score, winner, game_over, consecutive_ai_scores, displayed_thresholds
    
    # Paddle positions
    left_paddle = pygame.Rect(30, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WIDTH-40, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # Ball position
    ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
    
    # Ball direction - use constants for stability
    ball_dx = BALL_SPEED_X
    ball_dy = BALL_SPEED_Y
    
    # Reset scores
    left_score = 0
    right_score = 0
    
    # Reset game state
    winner = None
    game_over = False
    consecutive_ai_scores = 0  # Reset consecutive AI scores
    displayed_thresholds = set()  # Reset displayed thresholds
    
    # Force garbage collection to clear memory
    gc.collect()

def reset_ball():
    global ball, ball_dx, ball_dy
    ball.x = WIDTH//2 - BALL_SIZE//2
    ball.y = HEIGHT//2 - BALL_SIZE//2
    
    # Reset to default speeds for stability
    ball_dx = BALL_SPEED_X * (-1 if ball_dx < 0 else 1)
    
    # Randomize y direction slightly but with controlled range
    ball_dy = random.uniform(-BALL_SPEED_Y, BALL_SPEED_Y)
    
    # Ensure ball is never moving too slowly in Y direction
    if abs(ball_dy) < BALL_SPEED_Y * 0.3:
        ball_dy = BALL_SPEED_Y * 0.3 * (1 if ball_dy >= 0 else -1)

def check_performance():
    global performance_issue_detected, last_gc_time, frame_times
    
    # Add current frame time
    current_time = time.time()
    if frame_times:
        frame_time = current_time - frame_times[-1]
        frame_times.append(current_time)
    else:
        frame_times.append(current_time)
    
    # Keep only the last MAX_FRAME_TIMES
    if len(frame_times) > MAX_FRAME_TIMES:
        frame_times.pop(0)
    
    # Check if we need to run garbage collection (every 5 seconds)
    if current_time - last_gc_time > 5:
        gc.collect()
        last_gc_time = current_time
    
    # Check if we have enough frames to analyze
    if len(frame_times) >= 10:
        # Calculate average FPS over last 10 frames
        avg_frame_time = (frame_times[-1] - frame_times[-10]) / 10
        
        # If FPS drops below threshold, take action
        if avg_frame_time > 0.033:  # Less than 30 FPS
            performance_issue_detected = True
            # Emergency memory cleanup
            gc.collect()

def computer_ai():
    # Different AI behaviors based on difficulty
    if game_mode == "PVC":
        if ai_difficulty == "New Born":
            new_born_ai()
        elif ai_difficulty == "Normie":
            normie_ai()
        elif ai_difficulty == "Knight of Hell":
            knight_of_hell_ai()
    elif game_mode == "DECEPTION":
        deception_ai()

def new_born_ai():
    """
    Very basic AI - moves randomly and slowly, often misses the ball
    """
    # 40% chance to not move at all (simulate inattention)
    if random.random() < 0.4:
        return
    
    # 30% chance to move in wrong direction
    if random.random() < 0.3:
        if ball.centery > right_paddle.centery and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED * 0.5  # Move slower than player
        elif ball.centery < right_paddle.centery and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED * 0.5
    else:
        # Otherwise move correctly but slowly
        if ball.centery > right_paddle.centery and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED * 0.6
        elif ball.centery < right_paddle.centery and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED * 0.6

def normie_ai():
    """
    Standard AI - follows the ball competently but not perfectly
    """
    # Calculate target position with some offset based on ball direction
    target_y = ball.centery
    
    # Add a small reaction delay
    if ball.centery > right_paddle.centery + 10 and right_paddle.bottom < HEIGHT:
        right_paddle.y += PADDLE_SPEED * 0.85
    elif ball.centery < right_paddle.centery - 10 and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED * 0.85

def knight_of_hell_ai():
    """
    Expert AI - predicts ball trajectory, reacts quickly, and positions optimally
    """
    # Predict where the ball will be when it reaches the paddle's x position
    if ball_dx > 0:  # Only predict when ball is moving toward AI paddle
        # Calculate time to reach paddle
        distance = right_paddle.x - ball.x
        time_to_reach = distance / ball_dx if ball_dx != 0 else 0
        
        # Predict y position
        predicted_y = ball.y + (ball_dy * time_to_reach)
        
        # Account for bounces off top/bottom walls
        while predicted_y < 0 or predicted_y > HEIGHT:
            if predicted_y < 0:
                predicted_y = -predicted_y  # Reflect off top
            if predicted_y > HEIGHT:
                predicted_y = 2 * HEIGHT - predicted_y  # Reflect off bottom
        
        # Move faster than player and with perfect accuracy
        speed_multiplier = 1.2
        
        # Add some "trick shots" - sometimes aim to hit with edge of paddle for more angle
        if random.random() < 0.3:
            if random.random() < 0.5:
                # Aim to hit with top edge
                predicted_y -= PADDLE_HEIGHT * 0.4
            else:
                # Aim to hit with bottom edge
                predicted_y += PADDLE_HEIGHT * 0.4
        
        # Move toward predicted position
        if predicted_y > right_paddle.centery + 5 and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED * speed_multiplier
        elif predicted_y < right_paddle.centery - 5 and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED * speed_multiplier
    else:
        # When ball moving away, return to center with some randomness
        center_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        if abs(right_paddle.y - center_y) > PADDLE_HEIGHT * 0.2:
            if right_paddle.y > center_y:
                right_paddle.y -= PADDLE_SPEED * 0.7
            else:
                right_paddle.y += PADDLE_SPEED * 0.7

def deception_ai():
    """
    Unpredictable AI for deception mode - much smarter and more adaptive
    """
    global right_paddle, ball
    
    # Different behaviors based on the active deception effect
    if current_deception_effect == "REVERSE_CONTROLS":
        # In reverse controls, AI sometimes does the opposite to confuse player
        if random.random() < 0.7:  # 70% chance of normal behavior (increased from 80%)
            # Predict ball trajectory with added difficulty
            if ball_dx > 0:  # Ball moving toward AI
                # Predict future position with some randomness
                distance = right_paddle.x - ball.x
                time_to_reach = distance / ball_dx if ball_dx != 0 else 0
                predicted_y = ball.y + (ball_dy * time_to_reach)
                
                # Add some randomness to prediction
                predicted_y += random.randint(-20, 20)
                
                # Move toward predicted position with faster speed
                speed_multiplier = random.uniform(1.0, 1.3)  # Variable speed
                if predicted_y > right_paddle.centery + 5 and right_paddle.bottom < HEIGHT:
                    right_paddle.y += PADDLE_SPEED * speed_multiplier
                elif predicted_y < right_paddle.centery - 5 and right_paddle.top > 0:
                    right_paddle.y -= PADDLE_SPEED * speed_multiplier
            else:
                # Return to center when ball moving away
                center_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
                if abs(right_paddle.y - center_y) > PADDLE_HEIGHT * 0.2:
                    if right_paddle.y > center_y:
                        right_paddle.y -= PADDLE_SPEED * 0.7
                    else:
                        right_paddle.y += PADDLE_SPEED * 0.7
        else:
            # Deliberate wrong moves to confuse player
            if ball.centery > right_paddle.centery and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED * 1.2  # Move opposite with higher speed
            elif ball.centery < right_paddle.centery and right_paddle.bottom < HEIGHT:
                right_paddle.y += PADDLE_SPEED * 1.2
    
    elif current_deception_effect == "INVISIBLE_ENEMY" or current_deception_effect == "INVISIBLE_BALL":
        # When AI paddle or ball is invisible, AI plays more aggressively
        if ball_dx > 0:  # Ball moving toward AI
            # Perfect prediction with higher speed
            distance = right_paddle.x - ball.x
            time_to_reach = distance / ball_dx if ball_dx != 0 else 0
            predicted_y = ball.y + (ball_dy * time_to_reach)
            
            # Account for bounces
            while predicted_y < 0 or predicted_y > HEIGHT:
                if predicted_y < 0:
                    predicted_y = -predicted_y
                if predicted_y > HEIGHT:
                    predicted_y = 2 * HEIGHT - predicted_y
            
            # Move with higher speed for advantage
            speed_multiplier = 1.4
            if predicted_y > right_paddle.centery + 5 and right_paddle.bottom < HEIGHT:
                right_paddle.y += PADDLE_SPEED * speed_multiplier
            elif predicted_y < right_paddle.centery - 5 and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED * speed_multiplier
    
    elif current_deception_effect == "BALL_MULTIPLY":
        # Focus on the real ball with high accuracy
        if ball_dx > 0:
            distance = right_paddle.x - ball.x
            time_to_reach = distance / ball_dx if ball_dx != 0 else 0
            predicted_y = ball.y + (ball_dy * time_to_reach)
            
            # More precise movement
            if predicted_y > right_paddle.centery + 3 and right_paddle.bottom < HEIGHT:
                right_paddle.y += PADDLE_SPEED * 1.2
            elif predicted_y < right_paddle.centery - 3 and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED * 1.2
    
    elif current_deception_effect == "SHRINKING_PADDLES":
        # More aggressive to compensate for smaller paddle
        if ball_dx > 0:
            distance = right_paddle.x - ball.x
            time_to_reach = distance / ball_dx if ball_dx != 0 else 0
            predicted_y = ball.y + (ball_dy * time_to_reach)
            
            # Faster movement to compensate for smaller paddle
            if predicted_y > right_paddle.centery + 2 and right_paddle.bottom < HEIGHT:
                right_paddle.y += PADDLE_SPEED * 1.3
            elif predicted_y < right_paddle.centery - 2 and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED * 1.3
    
    else:
        # Default AI behavior - play competently with some randomness
        if random.random() < 0.9:  # 90% accurate
            if ball.centery > right_paddle.centery and right_paddle.bottom < HEIGHT:
                right_paddle.y += PADDLE_SPEED * random.uniform(0.9, 1.1)
            elif ball.centery < right_paddle.centery and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED * random.uniform(0.9, 1.1)
        else:
            # Occasional wrong move
            if ball.centery > right_paddle.centery and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED * 0.8
            elif ball.centery < right_paddle.centery and right_paddle.bottom < HEIGHT:
                right_paddle.y += PADDLE_SPEED * 0.8

def handle_deception_effects():
    global ball_dx, ball_dy, ball, left_paddle, right_paddle, current_deception_effect, deception_effect_start_time
    global deception_balls, original_paddle_height, is_reverse_controls
    
    current_time = time.time()
    
    # Initialize effect if none is active
    if current_deception_effect is None:
        current_deception_effect = random.choice(DECEPTION_EFFECTS)
        deception_effect_start_time = current_time
        print(f"Starting deception effect: {current_deception_effect}")
        
        # Initialize effect-specific variables
        if current_deception_effect == "BALL_MULTIPLY":
            # Create 3-4 additional balls (increased from 2)
            for _ in range(random.randint(3, 4)):
                new_ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
                new_dx = random.choice([-1, 1]) * BALL_SPEED_X * random.uniform(0.8, 1.2)
                new_dy = random.choice([-1, 1]) * BALL_SPEED_Y * random.uniform(0.8, 1.2)
                # Make some fake balls larger or smaller for added confusion
                size_multiplier = random.uniform(0.8, 1.2)
                new_size = int(BALL_SIZE * size_multiplier)
                new_ball.width = new_ball.height = new_size
                deception_balls.append({
                    "ball": new_ball,
                    "dx": new_dx,
                    "dy": new_dy,
                    "color": (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(200, 255)
                    ),
                    "alpha": random.randint(180, 255),
                    "size": new_size
                })
        elif current_deception_effect == "SHRINKING_PADDLES":
            original_paddle_height = PADDLE_HEIGHT
        elif current_deception_effect == "REVERSE_CONTROLS":
            is_reverse_controls = True
    
    # Check if it's time to change the effect (every DECEPTION_EFFECT_DURATION seconds)
    if current_time - deception_effect_start_time >= DECEPTION_EFFECT_DURATION:
        # Clean up current effect
        if current_deception_effect == "BALL_MULTIPLY":
            deception_balls = []
        elif current_deception_effect == "SHRINKING_PADDLES":
            # Restore original paddle sizes
            left_paddle.height = original_paddle_height
            right_paddle.height = original_paddle_height
            # Recenter paddles
            left_paddle.y = left_paddle.centery - left_paddle.height // 2
            right_paddle.y = right_paddle.centery - right_paddle.height // 2
        elif current_deception_effect == "REVERSE_CONTROLS":
            is_reverse_controls = False
        
        # Choose a new effect (different from the current one)
        available_effects = [e for e in DECEPTION_EFFECTS if e != current_deception_effect]
        current_deception_effect = random.choice(available_effects)
        deception_effect_start_time = current_time
        print(f"Changing to deception effect: {current_deception_effect}")
        
        # Initialize new effect
        if current_deception_effect == "BALL_MULTIPLY":
            # Create 3-4 additional balls with varying properties
            for _ in range(random.randint(3, 4)):
                new_ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
                new_dx = random.choice([-1, 1]) * BALL_SPEED_X * random.uniform(0.8, 1.2)
                new_dy = random.choice([-1, 1]) * BALL_SPEED_Y * random.uniform(0.8, 1.2)
                # Make some fake balls larger or smaller for added confusion
                size_multiplier = random.uniform(0.8, 1.2)
                new_size = int(BALL_SIZE * size_multiplier)
                new_ball.width = new_ball.height = new_size
                deception_balls.append({
                    "ball": new_ball,
                    "dx": new_dx,
                    "dy": new_dy,
                    "color": (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(200, 255)
                    ),
                    "alpha": random.randint(180, 255),
                    "size": new_size
                })
        elif current_deception_effect == "SHRINKING_PADDLES":
            original_paddle_height = PADDLE_HEIGHT
        elif current_deception_effect == "REVERSE_CONTROLS":
            is_reverse_controls = True
    
    # Apply the current effect
    if current_deception_effect == "GRAVITY_SHIFT":
        # Apply gravity effect to ball
        ball_dy += 0.15  # Increased from 0.1 for more challenge
        ball_dy = min(ball_dy, MAX_BALL_SPEED)  # Cap speed
        
        # Add slight horizontal drift for extra challenge
        if random.random() < 0.05:  # 5% chance per frame
            ball_dx += random.uniform(-0.1, 0.1)
            ball_dx = max(min(ball_dx, MAX_BALL_SPEED), -MAX_BALL_SPEED)  # Cap speed
    
    elif current_deception_effect == "TELEPORTING_BALL":
        # Random chance of teleporting
        if random.random() < 0.02:  # 2% chance per frame (increased from 1%)
            # Teleport ball to a random position that's not too close to paddles
            safe_margin = WIDTH // 5  # Decreased safe margin to make it harder
            ball.x = random.randint(safe_margin, WIDTH - safe_margin)
            ball.y = random.randint(BALL_SIZE, HEIGHT - BALL_SIZE)
    
    elif current_deception_effect == "SPEED_CHANGES":
        # Random chance of changing speed
        if random.random() < 0.03:  # 3% chance per frame (increased from 2%)
            speed_factor = random.uniform(0.7, 1.6)  # Wider range for more unpredictability
            ball_dx *= speed_factor
            ball_dy *= speed_factor
            # Apply speed caps
            ball_dx = max(min(ball_dx, MAX_BALL_SPEED), -MAX_BALL_SPEED)
            ball_dy = max(min(ball_dy, MAX_BALL_SPEED), -MAX_BALL_SPEED)
    
    elif current_deception_effect == "SHRINKING_PADDLES":
        # Gradually shrink paddles
        shrink_factor = 0.9996  # Slightly faster shrinking (was 0.9998)
        left_paddle.height = max(int(left_paddle.height * shrink_factor), PADDLE_HEIGHT // 4)  # Smaller minimum (was 1/3)
        right_paddle.height = max(int(right_paddle.height * shrink_factor), PADDLE_HEIGHT // 4)
        
        # Keep paddles centered at their current position
        left_paddle.y = left_paddle.centery - left_paddle.height // 2
        right_paddle.y = right_paddle.centery - right_paddle.height // 2
    
    elif current_deception_effect == "BALL_MULTIPLY":
        # Update all additional balls
        for ball_data in deception_balls[:]:  # Use a copy to allow modifications
            fake_ball = ball_data["ball"]
            fake_ball.x += ball_data["dx"]
            fake_ball.y += ball_data["dy"]
            
            # Random speed variations for extra challenge
            if random.random() < 0.02:  # 2% chance per frame
                ball_data["dx"] *= random.uniform(0.9, 1.1)
                ball_data["dy"] *= random.uniform(0.9, 1.1)
            
            # Bounce off top and bottom walls
            if fake_ball.top <= 0 or fake_ball.bottom >= HEIGHT:
                ball_data["dy"] *= -1
                if fake_ball.top < 0:
                    fake_ball.y = 0
                elif fake_ball.bottom > HEIGHT:
                    fake_ball.y = HEIGHT - fake_ball.height
            
            # Bounce off paddles occasionally (looks like they can interact)
            if fake_ball.colliderect(left_paddle) and random.random() < 0.7:
                ball_data["dx"] = abs(ball_data["dx"]) * random.uniform(1.0, 1.1)
            if fake_ball.colliderect(right_paddle) and random.random() < 0.7:
                ball_data["dx"] = -abs(ball_data["dx"]) * random.uniform(1.0, 1.1)
            
            # Remove ball if it goes out of bounds horizontally
            if fake_ball.right < 0 or fake_ball.left > WIDTH:
                deception_balls.remove(ball_data)
                
                # Create a new ball to replace the removed one (maintain challenge)
                if random.random() < 0.7:  # 70% chance to replace
                    new_ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
                    new_dx = random.choice([-1, 1]) * BALL_SPEED_X * random.uniform(0.8, 1.2)
                    new_dy = random.choice([-1, 1]) * BALL_SPEED_Y * random.uniform(0.8, 1.2)
                    size_multiplier = random.uniform(0.8, 1.2)
                    new_size = int(BALL_SIZE * size_multiplier)
                    new_ball.width = new_ball.height = new_size
                    deception_balls.append({
                        "ball": new_ball,
                        "dx": new_dx,
                        "dy": new_dy,
                        "color": (
                            random.randint(200, 255),
                            random.randint(200, 255),
                            random.randint(200, 255)
                        ),
                        "alpha": random.randint(180, 255),
                        "size": new_size
                    })

def handle_knight_of_hell_effects():
    global ball_dx, ball_dy, ball, left_paddle
    
    # Special effects for Knight of Hell mode with stability limits
    if random.random() < 0.003:  # 0.3% chance per frame
        effect = random.choice(["speed_burst", "ball_teleport"])
        
        if effect == "speed_burst":
            # Sudden speed increase with cap
            ball_dx *= 1.5
            ball_dy *= 1.5
            # Apply speed caps
            ball_dx = max(min(ball_dx, MAX_BALL_SPEED), -MAX_BALL_SPEED)
            ball_dy = max(min(ball_dy, MAX_BALL_SPEED), -MAX_BALL_SPEED)
        elif effect == "ball_teleport" and ball_dx > 0:
            # Teleport ball closer to player's paddle
            safe_x = left_paddle.x + PADDLE_WIDTH * 3
            safe_y = random.randint(PADDLE_HEIGHT, HEIGHT - PADDLE_HEIGHT)
            # Ensure coordinates are within bounds
            safe_x = max(min(safe_x, WIDTH - BALL_SIZE), 0)
            safe_y = max(min(safe_y, HEIGHT - BALL_SIZE), 0)
            ball.x = safe_x
            ball.y = safe_y

class AnimatedBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.lines = []
        self.grid_points = []
        self.generate_lines()
        self.generate_grid()
        self.time = 0
        # Create a static background surface
        self.static_background = self.create_static_background()
    
    def generate_lines(self):
        # Generate wavy lines pattern inspired by the image
        for i in range(50):
            # Randomize starting positions and parameters
            x_offset = self.width * 0.1 + (self.width * 0.8) * (i / 50)
            amplitude = self.height * 0.05 + (self.height * 0.3) * random.random()
            frequency = 0.001 + 0.003 * random.random()
            phase = 2 * math.pi * random.random()
            thickness = 1 + int(3 * random.random())
            alpha = 30 + int(100 * random.random())
            
            self.lines.append({
                'x_offset': x_offset,
                'amplitude': amplitude,
                'frequency': frequency,
                'phase': phase,
                'thickness': thickness,
                'alpha': alpha
            })
    
    def generate_grid(self):
        # Generate a grid of points for cyberpunk effect
        spacing = 40
        for x in range(0, self.width, spacing):
            for y in range(0, self.height, spacing):
                if random.random() < 0.3:  # Only show some points
                    size = random.randint(1, 3)
                    alpha = random.randint(30, 150)
                    self.grid_points.append({
                        'x': x,
                        'y': y,
                        'size': size,
                        'alpha': alpha
                    })
    
    def create_static_background(self):
        """Create a static background surface that will be reused"""
        try:
            surface = pygame.Surface((self.width, self.height))
            # Solid black background
            surface.fill(BLACK)
            return surface
        except Exception as e:
            print(f"Error creating background: {e}")
            # Return a small black surface as fallback
            return pygame.Surface((1, 1))
    
    def update(self):
        # Keep time updated for any remaining animations
        self.time += 0.01
        
    def draw(self, screen):
        try:
            # Draw the static background
            screen.blit(self.static_background, (0, 0))
        except Exception as e:
            print(f"Error drawing background: {e}")
            # Fallback to simple fill
            screen.fill(BLACK)

def draw_dashed_line():
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 2, y, 4, 10))

def draw_borders():
    for x in range(0, WIDTH, 20):
        pygame.draw.rect(screen, WHITE, (x, 0, 10, 4))
        pygame.draw.rect(screen, WHITE, (x, HEIGHT-4, 10, 4))

def difficulty_selection_screen():
    global ai_difficulty, pvc_difficulty_selected
    
    # Create animated background
    background = AnimatedBackground(WIDTH, HEIGHT)
    
    # Load difficulty logos if not already loaded
    if difficulty_logos["New Born"] is None:
        load_difficulty_logos()
    
    # Setup for difficulty selection
    difficulties = ["New Born", "Normie", "Knight of Hell"]
    selected_difficulty = None
    difficulty_selection_time = 0
    show_difficulty_info = False
    user_wants_to_go_back = False  # Flag to track if user wants to go back
    
    # Create difficulty cards
    card_width = int(WIDTH * 0.2)
    card_height = int(HEIGHT * 0.5)
    card_spacing = int(WIDTH * 0.05)
    total_width = card_width * 3 + card_spacing * 2
    start_x = (WIDTH - total_width) // 2
    
    card_rects = {}
    for i, diff in enumerate(difficulties):
        x = start_x + i * (card_width + card_spacing)
        y = HEIGHT // 2 - card_height // 2
        card_rects[diff] = pygame.Rect(x, y, card_width, card_height)
    
    # Create navigation buttons
    button_width = int(WIDTH * 0.15)
    button_height = int(HEIGHT * 0.06)
    
    back_button = AAA_Button(WIDTH - button_width - 40, HEIGHT - button_height - 40, 
                          button_width, button_height, "BACK", NEON_RED)
    
    select_button = AAA_Button(WIDTH - button_width*2 - 60, HEIGHT - button_height - 40, 
                            button_width, button_height, "SELECT", NEON_BLUE)
    
    # Main selection loop
    clock = pygame.time.Clock()
    selecting = True
    current_time = 0
    hovered_difficulty = None
    
    while selecting:
        current_time += 0.02
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_BACKSPACE and show_difficulty_info:
                    # Go back to difficulty selection
                    show_difficulty_info = False
                    selected_difficulty = None
            
            if not show_difficulty_info:
                # Handle mouse clicks on difficulty cards
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    for diff, rect in card_rects.items():
                        if rect.collidepoint(mouse_pos):
                            ai_difficulty = diff
                            selected_difficulty = diff
                            show_difficulty_info = True
                            difficulty_selection_time = pygame.time.get_ticks()
                            break
                    
                    # Check button clicks
                    if back_button.is_clicked(mouse_pos):
                        selecting = False
                        pvc_difficulty_selected = False
                        user_wants_to_go_back = True  # Set flag to go back to login
                        print("DEBUG: Back button clicked in difficulty selection, returning to login")
                    
                    if select_button.is_clicked(mouse_pos) and hovered_difficulty:
                        ai_difficulty = hovered_difficulty
                        selected_difficulty = hovered_difficulty
                        show_difficulty_info = True
                        difficulty_selection_time = pygame.time.get_ticks()
            
            # Handle mouse movement for hover effects
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                hovered_difficulty = None
                
                for diff, rect in card_rects.items():
                    if rect.collidepoint(mouse_pos):
                        hovered_difficulty = diff
                        break
        
        # Update background
        background.update()
        
        # Update buttons
        back_button.update(current_time)
        select_button.update(current_time)
        
        # Draw background
        background.draw(screen)
        
        if not show_difficulty_info:
            # Draw header with cyberpunk style
            header_rect = pygame.Rect(WIDTH//4, 20, WIDTH//2, 60)
            pygame.draw.rect(screen, (0, 0, 0, 100), header_rect)
            
            # Draw title
            draw_aaa_text(screen, "SELECT DIFFICULTY LEVEL", WIDTH//2, 50, NEON_BLUE)
            
            # Draw difficulty cards
            for diff in difficulties:
                is_selected = diff == selected_difficulty
                is_hovered = diff == hovered_difficulty
                draw_difficulty_card(screen, diff, 
                                  card_rects[diff].x, card_rects[diff].y, 
                                  card_width, card_height, 
                                  is_selected, is_hovered, current_time)
            
            # Draw explanation text
            explanation_text = "Opponents will have all the tools at their disposal, but only higher levels will prove a significant challenge."
            text_rect = draw_aaa_text(screen, explanation_text, WIDTH//2, HEIGHT - 120, 
                                   NEON_BLUE, FONT_TINY, glow=False)
            
            # Draw navigation buttons
            back_button.draw(screen)
            
            if hovered_difficulty:
                select_button.draw(screen)
            
            # Draw navigation hints
            hint_text = "ESC - Exit    BACKSPACE - Back"
            draw_aaa_text(screen, hint_text, 20, HEIGHT - 20, WHITE, FONT_TINY, 
                        glow=False, align='left')
        else:
            # Draw only the selected difficulty info
            if selected_difficulty:
                # Get difficulty color
                if selected_difficulty == "New Born":
                    color = NEON_BLUE
                elif selected_difficulty == "Normie":
                    color = NEON_GREEN
                else:  # Knight of Hell
                    color = NEON_RED
                
                # Draw header
                draw_aaa_text(screen, "DIFFICULTY SELECTED", WIDTH//2, 50, color)
                
                # Draw difficulty name with glow effect
                draw_aaa_text(screen, selected_difficulty, WIDTH//2, HEIGHT//5, color, FONT)
                
                # Draw difficulty logo
                if difficulty_logos[selected_difficulty]:
                    logo = difficulty_logos[selected_difficulty]
                    logo_rect = logo.get_rect(center=(WIDTH//2, HEIGHT//2))
                    screen.blit(logo, logo_rect)
                else:
                    # Fallback if image not available
                    no_image_text = FONT_SMALL.render("Image not available", True, WHITE)
                    screen.blit(no_image_text, (WIDTH//2 - no_image_text.get_width()//2, HEIGHT//2))
                
                # Draw difficulty description
                desc_text = FONT_SMALL.render(difficulty_descriptions[selected_difficulty], True, color)
                screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT*3//4))
                
                # Draw navigation hint
                backspace_hint = FONT_TINY.render("Press BACKSPACE to go back", True, (100, 100, 100))
                screen.blit(backspace_hint, (20, HEIGHT - backspace_hint.get_height() - 10))
                
                # Show for 3 seconds then proceed
                current_time_ms = pygame.time.get_ticks()
                if current_time_ms - difficulty_selection_time > 3000:  # 3 seconds
                    selecting = False
                    pvc_difficulty_selected = True
                
                # Draw countdown
                remaining_time = 3 - int((current_time_ms - difficulty_selection_time) / 1000)
                if remaining_time > 0:
                    time_text = FONT_SMALL.render(f"Starting in {remaining_time}...", True, WHITE)
                    screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, HEIGHT*7//8))
        
        pygame.display.flip()
        clock.tick(60)
    
    if user_wants_to_go_back:
        print("DEBUG: Returning to login screen from difficulty selection")
        return False  # Return False to indicate we want to go back to login
    
    pvc_difficulty_selected = True
    return True  # Return True to indicate we want to continue with the game

def display_defeat_quote(screen, quote_text, defeat_count, force_exit=False):
    """
    Function to display a defeat quote with pause until user acknowledges.
    Returns True if user wants to continue, False if user wants to exit.
    """
    clock = pygame.time.Clock()
    quote_showing = True
    start_time = pygame.time.get_ticks()
    
    print(f"QUOTE DISPLAY: Showing quote for {defeat_count} defeats")
    
    # Load the corresponding image from Images of Sans folder
    image = None
    try:
        # Try to load the image that matches the defeat count threshold
        for threshold in sorted(defeat_quotes.keys(), reverse=True):
            if defeat_count >= threshold:
                image_path = os.path.join("Images of Sans", f"{threshold}.png")
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                    print(f"QUOTE DISPLAY: Loaded image for threshold {threshold}")
                    
                    # Scale the image to fit the screen nicely
                    max_width = WIDTH * 0.2  # Reduced to 20% of screen width
                    max_height = HEIGHT * 0.2  # Reduced to 20% of screen height
                    
                    # Calculate scaling to maintain aspect ratio
                    img_ratio = image.get_width() / image.get_height()
                    if image.get_width() > max_width:
                        new_width = max_width
                        new_height = new_width / img_ratio
                        image = pygame.transform.scale(image, (int(new_width), int(new_height)))
                    
                    if image.get_height() > max_height:
                        new_height = max_height
                        new_width = new_height * img_ratio
                        image = pygame.transform.scale(image, (int(new_width), int(new_height)))
                    
                    break
    except Exception as e:
        print(f"QUOTE DISPLAY ERROR: Failed to load image: {e}")
        image = None
    
    while quote_showing:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Exit game
                elif event.key == pygame.K_SPACE and not force_exit:
                    print("QUOTE DISPLAY: User pressed SPACE to continue")
                    return True  # Continue game
                elif event.key == pygame.K_x and force_exit:
                    print("QUOTE DISPLAY: User pressed X to exit")
                    return False  # Exit game
        
        try:
            # Clear screen with black background
            screen.fill(BLACK)
            
            # Create semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))  # Almost black background
            screen.blit(overlay, (0, 0))
            
            # Display a title
            title_text = "DEFEAT MESSAGE"
            title_surf = FONT_LARGE.render(title_text, True, NEON_RED)
            title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 8))
            screen.blit(title_surf, title_rect)
            
            # Use consistent layout for all thresholds
            if image:
                # Position image at the top center
                image_rect = image.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 20))
                screen.blit(image, image_rect)
                
                # Position text in center of screen below the image
                quote_x = WIDTH // 2
                quote_y = HEIGHT // 2
            else:
                # Centered text layout (original behavior)
                quote_x = WIDTH // 2
                quote_y = HEIGHT // 2 - 50  # Move up a bit to center better
            
            # Special formatting for threshold 20
            if defeat_count >= 20 and defeat_count < 25:
                # Draw the quote with special multi-color formatting
                lines = quote_text.split('\n')
                line_height = int(HEIGHT * 0.08)  # Adjust line spacing
                y_offset = quote_y
                
                for i, line in enumerate(lines):
                    # Alternate colors for each line
                    if i % 3 == 0:
                        color = NEON_RED
                    elif i % 3 == 1:
                        color = NEON_BLUE
                    else:
                        color = NEON_GREEN
                    
                    # Special words highlighting
                    if "DANGEROUS" in line:
                        line_surf = FONT.render(line, True, NEON_BLUE)
                    elif "STUPID" in line:
                        line_surf = FONT.render(line, True, NEON_GREEN)
                    elif "SMART" in line:
                        line_surf = FONT.render(line, True, NEON_GREEN)
                    else:
                        # Use smaller font for regular text
                        line_surf = FONT_MEDIUM.render(line, True, color)
                    
                    # Center align all text
                    line_rect = line_surf.get_rect(center=(quote_x, y_offset))
                    
                    # Add glow effect
                    for j in range(3):
                        glow_rect = line_rect.copy()
                        glow_rect.x += j
                        glow_rect.y += j
                        glow_surf = pygame.Surface((line_surf.get_width() + j*2, line_surf.get_height() + j*2), pygame.SRCALPHA)
                        pygame.draw.rect(glow_surf, (*color[:3], 50 - j*15), glow_surf.get_rect(), border_radius=3)
                        screen.blit(glow_surf, glow_rect)
                    
                    screen.blit(line_surf, line_rect)
                    y_offset += line_height
            else:
                # For long quotes like 25 and 30, we need to optimize layout
                words = quote_text.split()
                
                # Determine an appropriate font size based on quote length
                if len(words) > 15 or defeat_count >= 25:
                    font = FONT_SMALL  # Use smaller font for longer quotes
                    line_height = 40
                else:
                    font = FONT_MEDIUM
                    line_height = 60
                
                # Calculate max width based on screen size
                max_line_width = WIDTH * 0.8
                
                # Break text into lines
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if font.size(test_line)[0] < max_line_width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # Position text with enough space
                y_offset = quote_y - (len(lines) * line_height) // 2
                
                # Adjust starting position if needed
                if y_offset < HEIGHT // 3:
                    y_offset = HEIGHT // 3
                
                # Draw each line
                for line in lines:
                    line_surf = font.render(line, True, NEON_RED)
                    line_rect = line_surf.get_rect(center=(quote_x, y_offset))
                    
                    # Simpler glow effect
                    glow_surf = font.render(line, True, (NEON_RED[0]//2, NEON_RED[1]//2, NEON_RED[2]//2))
                    glow_rect = glow_surf.get_rect(center=(quote_x+2, y_offset+2))
                    screen.blit(glow_surf, glow_rect)
                    
                    screen.blit(line_surf, line_rect)
                    y_offset += line_height
                    
                    # Safety check to avoid going off-screen
                    if y_offset > HEIGHT - 200:
                        break
            
            # Display defeat counter
            defeat_counter_text = f"Consecutive scores: {defeat_count}"
            counter_surf = FONT_SMALL.render(defeat_counter_text, True, NEON_BLUE)
            counter_rect = counter_surf.get_rect(center=(WIDTH // 2, HEIGHT - 100))
            screen.blit(counter_surf, counter_rect)
            
            # Special warning for threshold 30
            if defeat_count >= 30:
                warning_text = "YOU HAVE BEEN DEFEATED TOO MANY TIMES"
                warning_surf = FONT_SMALL.render(warning_text, True, NEON_RED)
                warning_rect = warning_surf.get_rect(center=(WIDTH // 2, HEIGHT - 150))
                screen.blit(warning_surf, warning_rect)
            
            # Display continue prompt based on defeat count
            if force_exit:
                # For 30th defeat or higher, only allow exit
                continue_text = "PRESS X TO EXIT GAME"
                continue_surf = FONT_MEDIUM.render(continue_text, True, NEON_RED)
                continue_rect = continue_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50))
                
                # Pulsing effect
                pulse_intensity = int(50 * math.sin(current_time * 0.005))
                pulse_color = (min(255, NEON_RED[0] + pulse_intensity), 
                              min(255, NEON_RED[1] + pulse_intensity),
                              min(255, NEON_RED[2] + pulse_intensity))
                
                pulse_surf = FONT_MEDIUM.render(continue_text, True, pulse_color)
                screen.blit(pulse_surf, continue_rect)
            else:
                # Normal continue prompt
                continue_text = "Press SPACE to continue"
                continue_surf = FONT_SMALL.render(continue_text, True, WHITE)
                continue_rect = continue_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50))
                screen.blit(continue_surf, continue_rect)
            
            # Update display
            pygame.display.flip()
            
            # Auto-continue after 5 seconds only if not force exit
            if not force_exit and current_time - start_time > 5000:
                print("QUOTE DISPLAY: Auto-continuing after timeout")
                return True  # Continue game
            
            # Cap frame rate
            clock.tick(30)
        
        except Exception as e:
            print(f"QUOTE DISPLAY ERROR: {e}")
            # Last resort emergency display if all else fails
            try:
                screen.fill(BLACK)
                error_text = FONT_SMALL.render("Error displaying quote. Press SPACE to continue.", True, WHITE)
                screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                pygame.display.flip()
            except:
                pass
            
            # Wait for space key
            waiting = True
            while waiting and force_exit:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_x or event.key == pygame.K_SPACE:
                            waiting = False
                            return False  # Exit on error for force_exit case
                    if event.type == pygame.QUIT:
                        return False
                clock.tick(30)
            
            return True  # Continue game on error for non-force_exit case
    
    return True  # Default to continue

def run_game():
    global screen, ball_dx, ball_dy, left_score, right_score, winner, game_over
    global game_mode, current_user, opponent_user, ai_difficulty, pvc_difficulty_selected
    global last_gc_time, performance_issue_detected, consecutive_defeats, consecutive_ai_scores, displayed_thresholds
    global current_deception_effect, deception_effect_start_time, deception_balls, original_paddle_height, is_reverse_controls
    
    try:
        # Set up display in fullscreen mode
        if FULLSCREEN:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        pygame.display.set_caption("Ping Pong Game")
        
        # Pre-render text for better performance
        pre_render_text()
        
        # Main game loop with login screen handling
        while True:
            # Login screen
            game_mode, current_user = start_login_interface()
            
            if not game_mode or not current_user:
                break  # User quit during login
            
            # Initialize game objects
            reset_game()
            
            # Set opponent name and show difficulty selection for PVC mode
            if game_mode == "PVC":
                opponent_user = "Computer"
                ai_difficulty = "Normie"  # Default AI difficulty for PVC mode
                pvc_difficulty_selected = False
                
                # Show difficulty selection and check if user wants to go back
                if not difficulty_selection_screen():
                    print("DEBUG: User chose to go back to login from difficulty selection")
                    continue  # Go back to login screen
            else:
                if game_mode == "PVP":
                    opponent_user = "Player 2"
                else:  # DECEPTION mode
                    opponent_user = "Computer"
                    ai_difficulty = "Deception"  # Set for deception mode
                pvc_difficulty_selected = True  # Skip difficulty selection for other modes
            
            # Create animated background for game
            background = AnimatedBackground(WIDTH, HEIGHT)
            
            # Force garbage collection before starting game loop
            gc.collect()
            last_gc_time = time.time()
            
            # Game loop
            clock = pygame.time.Clock()
            running = True
            current_time = 0
            
            print(f"Starting game. defeat_quotes keys: {sorted(defeat_quotes.keys())}")
            
            while running:
                frame_start_time = time.time()
                current_time += 0.02
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        return  # Exit the entire game
                    
                    # Add ESC key to exit fullscreen
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            return  # Exit the entire game
                        # For testing, force display a quote when T is pressed
                        elif event.key == pygame.K_t:
                            print("TEST: Forcing quote display")
                            consecutive_ai_scores = 5
                            displayed_thresholds = set()  # Reset displayed thresholds for testing
                            continue_game = display_defeat_quote(screen, defeat_quotes[5], consecutive_ai_scores)
                            displayed_thresholds.add(5)  # Mark this threshold as displayed
                            if not continue_game:
                                running = False
                                return  # Exit the entire game
                        # Handle restart on game over
                        elif game_over and event.key == pygame.K_r:
                            # Reset the game and either restart or go back to difficulty selection
                            reset_game()
                            if game_mode == "PVC":
                                pvc_difficulty_selected = False  # Allow re-selecting difficulty
                                # Show difficulty selection and check if user wants to go back
                                if not difficulty_selection_screen():
                                    break  # Break out of game loop to go back to login screen
                            # If not PVC or difficulty was selected, continue with the reset game
                
                if not game_over and pvc_difficulty_selected:
                    # Key Presses for player 1 (left paddle)
                    keys = pygame.key.get_pressed()
                    
                    # Handle regular or reversed controls
                    if not is_reverse_controls:
                        if keys[pygame.K_w] and left_paddle.top > 0:
                            left_paddle.y -= PADDLE_SPEED
                        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
                            left_paddle.y += PADDLE_SPEED
                    else:
                        # Reversed controls in deception mode
                        if keys[pygame.K_s] and left_paddle.top > 0:
                            left_paddle.y -= PADDLE_SPEED
                        if keys[pygame.K_w] and left_paddle.bottom < HEIGHT:
                            left_paddle.y += PADDLE_SPEED
                    
                    # Controls for player 2 (right paddle) in PVP mode
                    if game_mode == "PVP":
                        if keys[pygame.K_UP] and right_paddle.top > 0:
                            right_paddle.y -= PADDLE_SPEED
                        if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
                            right_paddle.y += PADDLE_SPEED
                    else:
                        # Computer controls right paddle in PVC and DECEPTION modes
                        computer_ai()
                    
                    # Move Ball
                    ball.x += ball_dx
                    ball.y += ball_dy
                    
                    # Special effects for different modes
                    if game_mode == "DECEPTION":
                        handle_deception_effects()
                    elif game_mode == "PVC" and ai_difficulty == "Knight of Hell":
                        handle_knight_of_hell_effects()
                    
                    # Collisions with top and bottom walls
                    if ball.top <= 0 or ball.bottom >= HEIGHT:
                        ball_dy *= -1
                        # Keep ball within bounds to prevent getting stuck
                        if ball.top < 0:
                            ball.y = 0
                        elif ball.bottom > HEIGHT:
                            ball.y = HEIGHT - BALL_SIZE
                        play_other_sound()
                    
                    # Paddle collisions
                    if ball.colliderect(left_paddle):
                        # Calculate collision point for angle
                        relative_intersect_y = (left_paddle.centery - ball.centery) / (PADDLE_HEIGHT / 2)
                        
                        # Ensure ball moves right
                        ball_dx = abs(ball_dx)
                        
                        # Add a small increase to speed with each hit, up to a max
                        ball_dx = min(ball_dx * 1.05, MAX_BALL_SPEED)
                        
                        # Adjust angle based on where the ball hits the paddle
                        ball_dy = -relative_intersect_y * BALL_SPEED_Y
                        
                        # Ensure ball doesn't get stuck in paddle
                        ball.x = left_paddle.right
                        
                        play_paddle_hit_sound()
                    
                    if ball.colliderect(right_paddle):
                        # Calculate collision point for angle
                        relative_intersect_y = (right_paddle.centery - ball.centery) / (PADDLE_HEIGHT / 2)
                        
                        # Ensure ball moves left
                        ball_dx = -abs(ball_dx)
                        
                        # Add a small increase to speed with each hit, up to a max
                        ball_dx = max(ball_dx * 1.05, -MAX_BALL_SPEED)
                        
                        # Adjust angle based on where the ball hits the paddle
                        ball_dy = -relative_intersect_y * BALL_SPEED_Y
                        
                        # Ensure ball doesn't get stuck in paddle
                        ball.x = right_paddle.left - BALL_SIZE
                        
                        play_paddle_hit_sound()
                    
                    # Ensure ball speed in Y direction is capped
                    ball_dy = max(min(ball_dy, MAX_BALL_SPEED), -MAX_BALL_SPEED)
                    
                    # Score
                    if ball.left <= 0:
                        right_score += 1
                        play_other_sound()
                        
                        # For Knight of Hell mode, track consecutive AI scores
                        if game_mode == "PVC" and ai_difficulty == "Knight of Hell":
                            consecutive_ai_scores += 1
                            print(f"DEBUG: AI scored! Consecutive AI scores: {consecutive_ai_scores}")
                            
                            # Find the highest threshold that has been reached but not yet displayed
                            reached_threshold = None
                            quote_text = ""
                            force_exit = False
                            
                            # Check thresholds in descending order
                            for threshold in sorted(defeat_quotes.keys(), reverse=True):
                                if consecutive_ai_scores >= threshold and threshold not in displayed_thresholds:
                                    reached_threshold = threshold
                                    quote_text = defeat_quotes[threshold]
                                    
                                    # Force exit only at 30th score
                                    if threshold >= 30:
                                        force_exit = True
                                        print("DEBUG: Force exit enabled at 30+ consecutive scores")
                                    
                                    break
                            
                            # Display quote if a new threshold has been reached
                            if reached_threshold is not None:
                                print(f"DEBUG: New threshold {reached_threshold} reached with {consecutive_ai_scores} consecutive AI scores")
                                # Pause and display the quote
                                continue_game = display_defeat_quote(screen, quote_text, consecutive_ai_scores, force_exit)
                                # Mark this threshold as displayed
                                displayed_thresholds.add(reached_threshold)
                                print(f"DEBUG: Displayed thresholds now: {sorted(displayed_thresholds)}")
                                
                                if not continue_game:
                                    print("DEBUG: User chose to exit")
                                    running = False
                                    continue  # Skip rest of loop
                        
                        reset_ball()
                    
                    if ball.right >= WIDTH:
                        left_score += 1
                        play_other_sound()
                        
                        # Reset consecutive AI scores and displayed thresholds when player scores
                        if game_mode == "PVC" and ai_difficulty == "Knight of Hell":
                            consecutive_ai_scores = 0
                            displayed_thresholds = set()  # Reset displayed thresholds
                            print(f"DEBUG: Player scored! Reset consecutive AI scores to 0 and cleared displayed thresholds")
                        
                        reset_ball()
                    
                    # Check for winner based on difficulty level
                    if game_mode == "PVC":
                        # Different win scores based on difficulty
                        if ai_difficulty == "New Born":
                            win_score = 10
                        elif ai_difficulty == "Normie":
                            win_score = 20
                        else:  # Knight of Hell
                            win_score = 50
                    else:
                        # Default win score for PVP and DECEPTION modes
                        win_score = 5
                    
                    # Check for winner
                    if left_score >= win_score:
                        winner = current_user
                        game_over = True
                        print(f"DEBUG: Player won")
                        # Reset consecutive defeats if player wins against Knight of Hell
                        if game_mode == "PVC" and ai_difficulty == "Knight of Hell":
                            consecutive_defeats = 0
                            consecutive_ai_scores = 0
                            displayed_thresholds = set()  # Reset displayed thresholds
                            print(f"DEBUG: Reset consecutive_defeats, consecutive_ai_scores to 0, and cleared displayed thresholds")
                        # Update user stats
                        try:
                            update_stats(current_user, win=True)
                        except:
                            pass  # Continue even if stats update fails
                    elif right_score >= win_score:
                        if game_mode == "PVP":
                            winner = opponent_user
                        elif game_mode == "DECEPTION":
                            winner = "DECEPTION AI"  # Custom name for deception mode
                        else:
                            winner = f"{ai_difficulty} AI"  # Only use difficulty name in PVC mode
                        
                        game_over = True
                        print(f"DEBUG: AI/Opponent won")
                        
                        # Check for consecutive defeats in Knight of Hell mode
                        if game_mode == "PVC" and ai_difficulty == "Knight of Hell":
                            consecutive_defeats += 1
                            print(f"DEBUG: Increased consecutive_defeats to {consecutive_defeats}")
                            
                            # Find the highest threshold that has been reached but not yet displayed
                            reached_threshold = None
                            quote_text = ""
                            force_exit = False
                            
                            # Check thresholds in descending order
                            for threshold in sorted(defeat_quotes.keys(), reverse=True):
                                if consecutive_defeats >= threshold and threshold not in displayed_thresholds:
                                    reached_threshold = threshold
                                    quote_text = defeat_quotes[threshold]
                                    
                                    # Force exit only at 30th defeat
                                    if threshold >= 30:
                                        force_exit = True
                                        print("DEBUG: Force exit enabled at 30+ consecutive defeats")
                                    
                                    break
                            
                            # Display quote if a new threshold has been reached
                            if reached_threshold is not None:
                                print(f"DEBUG: New threshold {reached_threshold} reached with {consecutive_defeats} consecutive defeats")
                                # Pause and display the quote
                                continue_game = display_defeat_quote(screen, quote_text, consecutive_defeats, force_exit)
                                # Mark this threshold as displayed
                                displayed_thresholds.add(reached_threshold)
                                print(f"DEBUG: Displayed thresholds now: {sorted(displayed_thresholds)}")
                                
                                if not continue_game:
                                    print("DEBUG: User chose to exit")
                                    running = False
                                    continue  # Skip rest of loop
                            else:
                                print(f"DEBUG: No quote found for {consecutive_defeats} defeats")
                        else:
                            print(f"DEBUG: Not Knight of Hell mode, no quote shown")
                        
                        # Update user stats
                        try:
                            update_stats(current_user, win=False)
                        except Exception as e:
                            print(f"DEBUG: Failed to update stats: {e}")
                
                # Update background
                background.update()
                
                # Drawing
                try:
                    # Clear screen with background
                    screen.fill(BLACK)
                    
                    # Draw the animated background
                    background.update()
                    background.draw(screen)
                    
                    # Draw center line
                    draw_dashed_line()
                    
                    # Draw borders
                    draw_borders()
                    
                    # Apply color chaos effect if active
                    if current_deception_effect == "COLOR_CHAOS" and not game_over:
                        # Draw random colored overlay with low opacity
                        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        chaos_color = (
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255),
                            50  # Low opacity
                        )
                        overlay.fill(chaos_color)
                        screen.blit(overlay, (0, 0))
                    
                    # Draw paddles (unless invisible in deception mode)
                    if not (current_deception_effect == "INVISIBLE_PLAYER"):
                        pygame.draw.rect(screen, GREEN, left_paddle)
                    if not (current_deception_effect == "INVISIBLE_ENEMY"):
                        pygame.draw.rect(screen, RED, right_paddle)
                    
                    # Draw ball (unless invisible in deception mode)
                    if not (current_deception_effect == "INVISIBLE_BALL"):
                        pygame.draw.circle(screen, WHITE, ball.center, BALL_SIZE // 2)
                    
                    # Draw additional balls for multiplier effect
                    if current_deception_effect == "BALL_MULTIPLY" and not game_over:
                        for ball_data in deception_balls:
                            fake_ball = ball_data["ball"]
                            # Draw with varying colors, sizes, and alpha to make it more disorienting
                            ball_color = ball_data.get("color", (200, 200, 255))
                            ball_alpha = ball_data.get("alpha", 200)
                            ball_radius = ball_data.get("size", BALL_SIZE) // 2
                            
                            # Create surface for the fake ball with alpha
                            fake_ball_surface = pygame.Surface((fake_ball.width + 4, fake_ball.height + 4), pygame.SRCALPHA)
                            pygame.draw.circle(fake_ball_surface, (*ball_color, ball_alpha), 
                                            (fake_ball.width//2 + 2, fake_ball.height//2 + 2), ball_radius)
                            
                            # Add some glow to fake balls
                            glow_radius = ball_radius + 2
                            pygame.draw.circle(fake_ball_surface, (*ball_color, ball_alpha//2), 
                                            (fake_ball.width//2 + 2, fake_ball.height//2 + 2), glow_radius)
                            
                            screen.blit(fake_ball_surface, (fake_ball.x - 2, fake_ball.y - 2))
                    
                    # Draw scores
                    left_score_text = FONT_LARGE.render(str(left_score), True, WHITE)
                    right_score_text = FONT_LARGE.render(str(right_score), True, WHITE)
                    screen.blit(left_score_text, (WIDTH//4, 20))
                    screen.blit(right_score_text, (WIDTH - WIDTH//4 - right_score_text.get_width(), 20))
                    
                    # Draw player names
                    left_name_text = FONT_SMALL.render(current_user, True, GREEN)
                    right_name_text = FONT_SMALL.render(opponent_user, True, RED)
                    screen.blit(left_name_text, (WIDTH//4, 80))
                    screen.blit(right_name_text, (WIDTH - WIDTH//4 - right_name_text.get_width(), 80))
                    
                    # Display current deception effect if in deception mode
                    if game_mode == "DECEPTION" and not game_over:
                        # Don't show the active effect name to player
                        effect_text = "DECEPTION MODE ACTIVE"
                        effect_surface = FONT_SMALL.render(effect_text, True, NEON_PURPLE)
                        screen.blit(effect_surface, (WIDTH // 2 - effect_surface.get_width() // 2, 10))
                        
                        # Show effect timer without naming the effect
                        time_left = int(DECEPTION_EFFECT_DURATION - (time.time() - deception_effect_start_time))
                        timer_text = f"Effect changes in: {time_left}s"
                        timer_surface = FONT_TINY.render(timer_text, True, NEON_BLUE)
                        screen.blit(timer_surface, (WIDTH // 2 - timer_surface.get_width() // 2, 50))
                        
                        # Show visual indicator for reversed controls only (player needs to know this)
                        if current_deception_effect == "REVERSE_CONTROLS":
                            controls_text = "CONTROLS REVERSED!"
                            controls_surface = FONT_TINY.render(controls_text, True, NEON_RED)
                            screen.blit(controls_surface, (20, HEIGHT - 50))
                    
                    # Draw debug info
                    debug_surf = FONT_TINY.render(f"Mode: {game_mode}, AI Scores: {consecutive_ai_scores}, Displayed: {sorted(displayed_thresholds) if displayed_thresholds else 'None'}", True, WHITE)
                    screen.blit(debug_surf, (10, 10))
                    
                    # Draw game over screen with AAA styling
                    if game_over:
                        # Create animated overlay with scan lines effect
                        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, 150))
                        
                        # Add scan lines
                        for y in range(0, HEIGHT, 4):
                            scan_alpha = 30 + int(20 * math.sin(current_time * 2 + y * 0.01))
                            pygame.draw.line(overlay, (255, 255, 255, scan_alpha), (0, y), (WIDTH, y), 1)
                        
                        screen.blit(overlay, (0, 0))
                        
                        # Create central panel
                        panel_width = int(WIDTH * 0.5)
                        panel_height = int(HEIGHT * 0.4)
                        panel_x = WIDTH//2 - panel_width//2
                        panel_y = HEIGHT//2 - panel_height//2
                        
                        # Draw panel background
                        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                        pygame.draw.rect(panel_surface, (20, 20, 30, 220), pygame.Rect(0, 0, panel_width, panel_height))
                        
                        # Add panel border with glow
                        border_alpha = 150 + int(50 * math.sin(current_time * 3))
                        for i in range(3):
                            border_width = 2 - i
                            alpha = border_alpha - (i * 40)
                            if alpha > 0:
                                pygame.draw.rect(panel_surface, (NEON_RED[0], NEON_RED[1], NEON_RED[2], alpha), 
                                              pygame.Rect(i, i, panel_width-i*2, panel_height-i*2), border_width)
                        
                        # Add diagonal corner accents to panel
                        accent_length = 20
                        pygame.draw.line(panel_surface, NEON_RED, (0, 0), (accent_length, 0), 2)
                        pygame.draw.line(panel_surface, NEON_RED, (0, 0), (0, accent_length), 2)
                        pygame.draw.line(panel_surface, NEON_RED, (panel_width, 0), (panel_width-accent_length, 0), 2)
                        pygame.draw.line(panel_surface, NEON_RED, (panel_width, 0), (panel_width, accent_length), 2)
                        pygame.draw.line(panel_surface, NEON_RED, (0, panel_height), (accent_length, panel_height), 2)
                        pygame.draw.line(panel_surface, NEON_RED, (0, panel_height), (0, panel_height-accent_length), 2)
                        pygame.draw.line(panel_surface, NEON_RED, (panel_width, panel_height), (panel_width-accent_length, panel_height), 2)
                        pygame.draw.line(panel_surface, NEON_RED, (panel_width, panel_height), (panel_width, panel_height-accent_length), 2)
                        
                        screen.blit(panel_surface, (panel_x, panel_y))
                        
                        # Draw "GAME OVER" text
                        game_over_text = FONT.render("GAME OVER", True, NEON_RED)
                        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, panel_y + 50))
                        
                        # Add glow effect to game over text
                        for i in range(3):
                            glow_surf = FONT.render("GAME OVER", True, (*NEON_RED, 150 - i*40))
                            glow_rect = glow_surf.get_rect(center=game_over_rect.center)
                            glow_rect.x += i
                            glow_rect.y += i
                            screen.blit(glow_surf, glow_rect)
                        
                        screen.blit(game_over_text, game_over_rect)
                        
                        # Draw winner text
                        if winner == current_user:
                            winner_color = NEON_BLUE
                        elif winner == opponent_user:
                            winner_color = NEON_GREEN
                        else:  # AI winner
                            winner_color = NEON_RED
                            # Consecutive defeats only count for Knight of Hell
                            if not (game_mode == "PVC" and ai_difficulty == "Knight of Hell"):
                                consecutive_defeats = 0
                        
                        winner_text = FONT_MEDIUM.render(f"{winner} WINS!", True, winner_color)
                        winner_rect = winner_text.get_rect(center=(WIDTH//2, panel_y + panel_height//2))
                        
                        # Add glow to winner text
                        for i in range(3):
                            glow_surf = FONT_MEDIUM.render(f"{winner} WINS!", True, (*winner_color, 150 - i*40))
                            glow_rect = glow_surf.get_rect(center=winner_rect.center)
                            glow_rect.x += i
                            glow_rect.y += i
                            screen.blit(glow_surf, glow_rect)
                        
                        screen.blit(winner_text, winner_rect)
                        
                        # Draw restart prompt with button styling
                        restart_button = AAA_Button(WIDTH//2 - 100, panel_y + panel_height - 60, 
                                                 200, 40, "PRESS 'R' TO RESTART", NEON_BLUE)
                        restart_button.update(current_time)
                        restart_button.draw(screen)
                    
                    pygame.display.flip()
                    clock.tick(60)
                    
                except Exception as e:
                    print(f"Error in game loop: {e}")
                    # Try to recover
                    try:
                        # Simplified fallback rendering
                        screen.fill(BLACK)
                        pygame.draw.rect(screen, WHITE, left_paddle)
                        pygame.draw.rect(screen, WHITE, right_paddle)
                        pygame.draw.ellipse(screen, WHITE, ball)
                        pygame.display.flip()
                        clock.tick(30)  # Slower framerate for recovery
                    except:
                        # If even fallback rendering fails, try to exit gracefully
                        running = False
                
                # Check performance
                check_performance()
            
            # End of game loop
        
    except Exception as e:
        print(f"Critical error: {e}")
    
    finally:
        # Clean up resources
        try:
            pygame.quit()
        except:
            pass

def draw_aaa_text(screen, text, x, y, color=NEON_BLUE, font=FONT_LARGE, glow=True, align='center'):
    """Draw text with AAA-style glow effect"""
    text_surf = font.render(text, True, color)
    
    if align == 'center':
        text_rect = text_surf.get_rect(center=(x, y))
    elif align == 'left':
        text_rect = text_surf.get_rect(midleft=(x, y))
    elif align == 'right':
        text_rect = text_surf.get_rect(midright=(x, y))
    
    if glow:
        # Draw glow layers
        for i in range(3):
            glow_surf = font.render(text, True, (*color, 100 - i*30))
            glow_rect = glow_surf.get_rect(center=text_rect.center)
            glow_rect.x += i
            glow_rect.y += i
            screen.blit(glow_surf, glow_rect)
    
    # Draw main text
    screen.blit(text_surf, text_rect)
    
    return text_rect

class AAA_Button:
    def __init__(self, x, y, width, height, text, color=NEON_BLUE, hover_color=None, text_color=WHITE, border_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color or (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.active_color = color
        self.text_color = text_color
        self.border_color = border_color or color
        self.animation = 0
        self.hovered = False
        self.selected = False
        self.alpha = 200
        self.time_offset = random.random() * 10  # For animation effects

    def update(self, time_val):
        # Animated effects
        self.alpha = 180 + int(20 * math.sin(time_val + self.time_offset))
        
        if self.selected:
            self.animation = min(1.0, self.animation + 0.1)
        elif self.hovered:
            self.animation = min(0.8, self.animation + 0.1)
        else:
            self.animation = max(0.0, self.animation - 0.1)

    def draw(self, screen):
        try:
            # Check if mouse is over button
            mouse_pos = pygame.mouse.get_pos()
            was_hovered = self.hovered
            self.hovered = self.rect.collidepoint(mouse_pos)
            
            # Animated button effect
            hover_offset = int(self.animation * 4)
            
            # Draw button with cyberpunk style
            # Main button background - semi-transparent
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*DARKEST_GRAY, 150), s.get_rect(), border_radius=0)
            screen.blit(s, self.rect)
            
            # Border with glow effect
            if self.animation > 0:
                for i in range(3):
                    border_width = 2 - i
                    alpha = int(self.alpha * (1 - i/3) * self.animation)
                    glow_rect = self.rect.inflate(i*2, i*2)
                    pygame.draw.rect(screen, (*self.border_color, alpha), glow_rect, border_width, border_radius=0)
            
            # Always draw at least the main border
            pygame.draw.rect(screen, self.border_color, self.rect, 1, border_radius=0)
            
            # Left edge accent
            accent_rect = pygame.Rect(self.rect.x, self.rect.y, 4, self.rect.height)
            pygame.draw.rect(screen, self.color, accent_rect)
            
            # Draw text with shadow
            text_surf = FONT_MEDIUM.render(self.text, True, self.text_color)
            
            # Shadow
            shadow_surf = FONT_MEDIUM.render(self.text, True, (30, 30, 30))
            shadow_rect = shadow_surf.get_rect(center=(self.rect.center[0] + 2, self.rect.center[1] + 2))
            screen.blit(shadow_surf, shadow_rect)
            
            # Main text
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
        except Exception as e:
            print(f"Error drawing button: {e}")
            # Fallback to simple button
            try:
                pygame.draw.rect(screen, self.color, self.rect, 2)
                text_surf = FONT_SMALL.render(self.text, True, WHITE)
                text_rect = text_surf.get_rect(center=self.rect.center)
                screen.blit(text_surf, text_rect)
            except:
                pass

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_difficulty_card(screen, difficulty, x, y, width, height, selected=False, hovered=False, time_val=0):
    """Draw a difficulty card with AAA styling"""
    # Card colors based on difficulty
    if difficulty == "New Born":
        color = NEON_BLUE
        border_color = NEON_BLUE
    elif difficulty == "Normie":
        color = NEON_GREEN
        border_color = NEON_GREEN
    else:  # Knight of Hell
        color = NEON_RED
        border_color = NEON_RED
    
    # Animation effects
    animation = 0
    if selected:
        animation = 1.0
    elif hovered:
        animation = 0.7
    
    # Background with border
    card_rect = pygame.Rect(x, y, width, height)
    
    # Semi-transparent background
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(s, (20, 20, 25, 200), s.get_rect(), border_radius=0)
    screen.blit(s, card_rect)
    
    # Border with glow effect
    if animation > 0:
        for i in range(3):
            border_width = 2 - i
            alpha = int(200 * (1 - i/3) * animation)
            glow_rect = card_rect.inflate(i*4, i*4)
            pygame.draw.rect(screen, (*border_color, alpha), glow_rect, border_width, border_radius=0)
    
    # Always draw at least the main border
    pygame.draw.rect(screen, border_color, card_rect, 1, border_radius=0)
    
    # Top accent bar
    accent_rect = pygame.Rect(x, y, width, 4)
    pygame.draw.rect(screen, color, accent_rect)
    
    # Draw difficulty name
    draw_aaa_text(screen, difficulty, x + width//2, y + 30, color, FONT_MEDIUM)
    
    # Draw difficulty description
    desc_text = FONT_TINY.render(difficulty_descriptions[difficulty], True, WHITE)
    screen.blit(desc_text, (x + width//2 - desc_text.get_width()//2, y + height - 40))
    
    # Draw difficulty logo if available
    if difficulty_logos[difficulty]:
        logo = difficulty_logos[difficulty]
        # Scale logo to fit card
        max_logo_width = width * 0.7
        max_logo_height = height * 0.5
        
        logo_ratio = logo.get_width() / logo.get_height()
        if logo.get_width() > max_logo_width:
            new_width = max_logo_width
            new_height = new_width / logo_ratio
            scaled_logo = pygame.transform.scale(logo, (int(new_width), int(new_height)))
        elif logo.get_height() > max_logo_height:
            new_height = max_logo_height
            new_width = new_height * logo_ratio
            scaled_logo = pygame.transform.scale(logo, (int(new_width), int(new_height)))
        else:
            scaled_logo = logo
        
        # Position logo in center of card
        logo_rect = scaled_logo.get_rect(center=(x + width//2, y + height//2))
        screen.blit(scaled_logo, logo_rect)
    
    return card_rect

if __name__ == "__main__":
    try:
        run_game()
    except Exception as e:
        print(f"Critical error in main: {e}")
        try:
            pygame.quit()
        except:
            pass
        sys.exit(1) 