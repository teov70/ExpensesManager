# app.py
import sqlite3
import datetime
from models import User, ExpenseGroup, Expense, ExpenseShare
import database as db

db.initialize_db()

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

def create_group(name, description=None, created_by=None):
    """Create a new expense group

    Returns:
        The ID of the newly created group, or None if creation failed
    """
    conn = get_db_connection()
    try:
        if created_by is None:
            raise ValueError("created_by (user ID) is required to create a group.")

        group = ExpenseGroup(name=name, description=description, created_by=created_by)
        group_id = db.insert_expense_group(conn, group)
        return group_id
    except Exception as e:
        print(f"Error creating group: {e}")
        return None
    finally:
        conn.close()

def add_member(user_id, group_id):
    """Add a user to an expense group
    
    Returns:
        True if the user was added successfully, False otherwise
    """
    conn = get_db_connection()
    try:
        existing_user = db.get_user_by_id(conn, user_id)
        if not existing_user:
            print(f"User with ID {user_id} not found")
            return False

        db.add_group_member(conn, user_id, group_id)
        return True
    except Exception as e:
        print(f"Error adding user to group: {e}")
        return False
    finally:
        conn.close()

def get_group_members(group_id):
    """Fetch all users who are members of a specific group"""
    conn = get_db_connection()
    try:
        return db.get_group_members(conn, group_id)
    except Exception as e:
        print(f"Error retrieving group members: {e}")
        return []
    finally:
        conn.close()

def get_all_groups():
    """Fetch all expense groups in the system"""
    conn = get_db_connection()
    try:
        return db.get_all_expense_groups(conn)
    except Exception as e:
        print(f"Error retrieving groups: {e}")
        return []
    finally:
        conn.close()

def delete_group(group_id):
    """Delete a group by group ID
    Returns:
        True if deletion was successful, False otherwise
    """
    conn = get_db_connection()
    try:
        existing_group = db.get_expense_group(conn, group_id)
        if not existing_group:
            print(f"Group with ID {group_id} not found")
            return False
        
        db.delete_expense_group(conn, group_id)
        return True
    except Exception as e:
        print(f"Error deleting group: {e}")
        return False
    finally:
        conn.close()

# Expense Management Functions

def create_expense_with_shares(description, amount, paid_by, group_id, shares_dict=None):
    """Create a new expense with shares

    Returns:
        The ID of the newly created expense, or None if creation failed
    """
    conn = get_db_connection()

    try:
        if group_id is None:
            raise ValueError("group_id is required to create an expense.")
        
        if not shares_dict:
            raise ValueError("At least one user must be assigned a share for this expense.")

        members = db.get_group_members(conn, group_id)
        valid_user_ids = {user.id for user in members}

        expense = Expense(description=description, amount=amount, paid_by=paid_by, group_id=group_id)
        expense_id = db.insert_expense(conn, expense)
    
        total_input_share = sum(shares_dict.values())
        if total_input_share != amount:
            raise ValueError("Shares must sum up to the total amount.")

        for user_id, share in shares_dict.items():
            if user_id not in valid_user_ids:
                raise ValueError(f"User ID {user_id} is not a member of group {group_id}")
        
            is_paid = (user_id == paid_by)
            
            if total_input_share == 100:
                share = amount * share / 100
            
            elif total_input_share == 0:
                share = amount/len(shares_dict)
            
            expense_share = ExpenseShare(expense_id, user_id, share, is_paid)
            db.insert_expense_share(conn, expense_share)
        return expense_id

    except Exception as e:
        print(f"Error creating shares: {e}")
        return None
    finally:
        conn.close()

def get_group_expenses(group_id):
    """Fetch all expenses for a specific group"""
    conn = get_db_connection()
    try:
        return db.get_group_expenses(conn, group_id)
    except Exception as e:
        print(f"Error retrieving expenses: {e}")
        return None
    finally:
        conn.close()
# Balance and Settlement Functions
def get_user_balance_summary(group_id, user_id):
    """Get the balance of a user in a group."""
    conn = get_db_connection()
    try:
        return db.get_user_owes_whom(conn, group_id, user_id)
    
    except Exception as e:
        print(f"Error retrieving user's balance: {e}")
        return None

    finally:
        conn.close()

def get_user_debts(group_id, user_id):
    """Get debts of a user in a group."""
    conn = get_db_connection
    try:
        return db.get_user_owes_whom(conn, group_id, user_id)
    
    except Exception as e:
        print(f"Error retrieving user's debts: {e}")
        return None
    
    finally:
        conn.close()

#...need to add
