# app.py
import sqlite3
import datetime
from models import User, ExpenseGroup, Expense, ExpenseShare
import database as db

# Constants
DB_PATH = 'expenses.db'

def get_db_connection():
    """Get a connection to the database"""
    return db.connect_db(DB_PATH)

# User Management Functions
def create_user(username, first_name=None, last_name=None, email=None):
    """Create a new user
    
    Returns:
        The ID of the newly created user, or None if creation failed
    """
    conn = get_db_connection()
    try:
        user = User(username=username, first_name=first_name, 
                   last_name=last_name, email=email)
        user_id = db.insert_user(conn, user)
        return user_id
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists")
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        conn.close()

# Group Management Functions

# Expense Management Functions

# Balance and Settlement Functions