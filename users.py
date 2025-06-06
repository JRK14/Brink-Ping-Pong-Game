import json
import os
import hashlib
import time

# File to store user data
USER_DB_FILE = "user_database.json"

def hash_password(password):
    """Hash a password for security."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from database file."""
    if not os.path.exists(USER_DB_FILE):
        return {}
    
    try:
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users to database file."""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)

def create_user(username, password):
    """Create a new user. Returns True if successful, False if username already exists."""
    success, _ = register_user(username, password)
    return success

def authenticate_user(username, password):
    """Authenticate a user. Returns True if credentials are valid, False otherwise."""
    success, _ = verify_user(username, password)
    return success

def get_top_scores(limit=10):
    """Get top scoring players based on win/loss ratio.
    Returns a list of tuples (username, score) sorted by score in descending order.
    """
    users = load_users()
    
    # Calculate scores (win/loss ratio with minimum games played)
    scores = []
    for username, data in users.items():
        stats = data.get("stats", {})
        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        games = stats.get("games", 0)
        
        # Calculate score (use wins as the primary score metric)
        # Add a small fraction based on win ratio to break ties
        if games > 0:
            win_ratio = wins / games
            score = wins + (win_ratio * 0.1)
        else:
            score = 0
        
        scores.append((username, int(score * 100)))
    
    # Sort by score (descending)
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N scores
    return scores[:limit]

def register_user(username, password):
    """Register a new user."""
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists"
    
    # Hash the password before storing
    hashed_password = hash_password(password)
    
    # Add new user
    users[username] = {
        "password": hashed_password,
        "stats": {
            "wins": 0,
            "losses": 0,
            "games": 0
        },
        "last_login": time.time()
    }
    
    # Save updated users
    save_users(users)
    return True, "Registration successful"

def verify_user(username, password):
    """Verify user credentials."""
    users = load_users()
    
    # Check if username exists
    if username not in users:
        return False, "Username not found"
    
    # Check if password matches
    if users[username]["password"] != hash_password(password):
        return False, "Incorrect password"
    
    # Update last login time
    users[username]["last_login"] = time.time()
    save_users(users)
    
    return True, "Login successful"

def update_stats(username, win=False):
    """Update user statistics."""
    users = load_users()
    
    if username in users:
        users[username]["stats"]["games"] += 1
        if win:
            users[username]["stats"]["wins"] += 1
        else:
            users[username]["stats"]["losses"] += 1
        save_users(users)
        return True
    
    return False

def get_user_stats(username):
    """Get user statistics."""
    users = load_users()
    
    if username in users:
        return users[username]["stats"]
    
    return None

def get_all_users():
    """Get all users from the database."""
    return load_users() 