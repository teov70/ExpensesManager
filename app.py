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

def get_user(user_id):
    """Get user details by user ID
    Returns:
        A User object if found, None otherwise
    """
    conn = get_db_connection()
    try:
        user = db.get_user_by_id(conn, user_id)
        return user
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        conn.close()

def update_user(user_id, username=None, first_name=None, last_name=None, email=None):
    """Update user details by user ID
    Returns:
        True if update was successful, False otherwise
    """
    conn = get_db_connection()
    
    try:
        existing_user = db.get_user_by_id(conn, user_id)
        if not existing_user:
            print(f"User with ID {user_id} not found")
            return False

        if username is not None:
            existing_user.username = username
        if first_name is not None:
            existing_user.first_name = first_name
        if last_name is not None:
            existing_user.last_name = last_name
        if email is not None:
            existing_user.email = email

        db.update_user(conn, existing_user)
        return True
    
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
    finally:
        conn.close()


def delete_user(user_id):
    """Delete a user by user ID
    Returns:
        True if deletion was successful, False otherwise
    """
    conn = get_db_connection()
    try:
        existing_user = db.get_user_by_id(conn, user_id)
        if not existing_user:
            print(f"User with ID {user_id} not found")
            return False
        
        db.delete_user(conn, user_id)
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        conn.close()

def get_all_users():
    """Get all users in the system
    
    Returns:
        A list of User objects
    """
    conn = get_db_connection()
    try:
        users = db.get_all_users(conn)
        return users
    except Exception as e:
        print(f"Error retrieving users: {e}")
        return []
    finally:
        conn.close()

# Group Management Functions

def create_group(name, description=None):
    """Create a new expense group
    
    Returns:
        The ID of the newly created group, or None if creation failed
    """
    conn = get_db_connection()
    try:
        group = ExpenseGroup(name=name, description=description)
        group_id = db.insert_expense_group(conn, group)
        return group_id 
    except Exception as e:
        print(f"Error creating group: {e}")
    finally:
        conn.close()

# Expense Management Functions

#...need to add

# Balance and Settlement Functions

#...need to add
