import json
import os
from datetime import datetime

DB_FILE = "user_projects.json"

def init_db():
    """Creates the database file if it doesn't exist"""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)

def save_project(name, data):
    """Saves a design to the JSON database"""
    init_db()
    try:
        with open(DB_FILE, 'r') as f:
            db = json.load(f)
    except:
        db = {}
    
    # Add metadata
    data['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    db[name] = data
    
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)
    return True

def load_project(name):
    """Loads a specific project"""
    init_db()
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    return db.get(name, {})

def get_project_list():
    """Returns list of all saved project names"""
    init_db()
    try:
        with open(DB_FILE, 'r') as f:
            db = json.load(f)
        return list(db.keys())
    except:
        return []

