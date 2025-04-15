# database.py
import sqlite3
import datetime
from models import User, ExpenseGroup, Expense, ExpenseShare

# Database connection and initialization
def connect_db(db_path='expenses.db'):
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def create_tables(conn):
    """Create all necessary tables if they don't exist"""
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        created_at TIMESTAMP
    )
    ''')
    
    # Create ExpenseGroups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expense_groups (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_by INTEGER,
        created_at TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')
    
    # Create Expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        description TEXT,
        amount REAL NOT NULL,
        date TIMESTAMP,
        paid_by INTEGER,
        group_id INTEGER,
        created_at TIMESTAMP,
        FOREIGN KEY (paid_by) REFERENCES users (id),
        FOREIGN KEY (group_id) REFERENCES expense_groups (id)
    )
    ''')
    
    # Create GroupMembers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_members (
        id INTEGER PRIMARY KEY,
        group_id INTEGER,
        user_id INTEGER,
        joined_at TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES expense_groups (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(group_id, user_id)
    )
    ''')
    
    # Create ExpenseShares table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expense_shares (
        id INTEGER PRIMARY KEY,
        expense_id INTEGER,
        user_id INTEGER,
        amount REAL NOT NULL,
        is_paid BOOLEAN DEFAULT 0,
        created_at TIMESTAMP,
        FOREIGN KEY (expense_id) REFERENCES expenses (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()

# User operations
def insert_user(conn, user):
    """Insert a new user into the database"""
    cursor = conn.cursor()
    with conn:
        cursor.execute('''
        INSERT INTO users (username, first_name, last_name, email, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (user.username, user.first_name, user.last_name, user.email, user.created_at))
    return cursor.lastrowid

def get_user_by_id(conn, user_id):
    """Get a user by their ID"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    if row:
        return User(
            id=row['id'],
            username=row['username'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            created_at=row['created_at']
        )
    return None

def get_user_by_username(conn, username):
    """Get a user by their username"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        return User(
            id=row['id'],
            username=row['username'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            created_at=row['created_at']
        )
    return None

def update_user(conn, user):
    """Update a user's information"""
    with conn:
        conn.execute('''
        UPDATE users
        SET username = ?, first_name = ?, last_name = ?, email = ?
        WHERE id = ?
        ''', (user.username, user.first_name, user.last_name, user.email, user.id))

def delete_user(conn, user_id):
    """Delete a user by their ID"""
    with conn:
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))

# ExpenseGroup operations
def insert_expense_group(conn, group):
    """Insert a new expense group"""
    cursor = conn.cursor()
    with conn:
        cursor.execute('''
        INSERT INTO expense_groups (name, description, created_by, created_at)
        VALUES (?, ?, ?, ?)
        ''', (group.name, group.description, group.created_by, group.created_at))
    return cursor.lastrowid

def get_expense_group(conn, group_id):
    """Get an expense group by ID"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expense_groups WHERE id = ?', (group_id,))
    row = cursor.fetchone()
    if row:
        return ExpenseGroup(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            created_by=row['created_by'],
            created_at=row['created_at']
        )
    return None

def get_user_groups(conn, user_id):
    """Get all groups a user is a member of"""
    cursor = conn.cursor()
    cursor.execute('''
    SELECT eg.* FROM expense_groups eg
    JOIN group_members gm ON eg.id = gm.group_id
    WHERE gm.user_id = ?
    ''', (user_id,))
    
    groups = []
    for row in cursor.fetchall():
        groups.append(ExpenseGroup(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            created_by=row['created_by'],
            created_at=row['created_at']
        ))
    return groups

def update_expense_group(conn, group):
    """Update an expense group's information"""
    with conn:
        conn.execute('''
        UPDATE expense_groups
        SET name = ?, description = ?
        WHERE id = ?
        ''', (group.name, group.description, group.id))

def delete_expense_group(conn, group_id):
    """Delete an expense group by ID"""
    with conn:
        conn.execute('DELETE FROM expense_groups WHERE id = ?', (group_id,))

# GroupMember operations
def add_group_member(conn, group_id, user_id):
    """Add a user to an expense group"""
    joined_at = datetime.datetime.now()
    cursor = conn.cursor()
    try:
        with conn:
            cursor.execute('''
            INSERT INTO group_members (group_id, user_id, joined_at)
            VALUES (?, ?, ?)
            ''', (group_id, user_id, joined_at))
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # User is already in the group
        return None

def remove_group_member(conn, group_id, user_id):
    """Remove a user from an expense group"""
    with conn:
        conn.execute('''
        DELETE FROM group_members
        WHERE group_id = ? AND user_id = ?
        ''', (group_id, user_id))

def get_group_members(conn, group_id):
    """Get all members of a group"""
    cursor = conn.cursor()
    cursor.execute('''
    SELECT u.* FROM users u
    JOIN group_members gm ON u.id = gm.user_id
    WHERE gm.group_id = ?
    ''', (group_id,))
    
    members = []
    for row in cursor.fetchall():
        members.append(User(
            id=row['id'],
            username=row['username'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            created_at=row['created_at']
        ))
    return members

# Expense operations
def insert_expense(conn, expense):
    """Insert a new expense"""
    cursor = conn.cursor()
    with conn:
        cursor.execute('''
        INSERT INTO expenses (description, amount, date, paid_by, group_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (expense.description, expense.amount, expense.date, 
              expense.paid_by, expense.group_id, expense.created_at))
    return cursor.lastrowid

def get_expense(conn, expense_id):
    """Get an expense by ID"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
    row = cursor.fetchone()
    if row:
        return Expense(
            id=row['id'],
            description=row['description'],
            amount=row['amount'],
            date=row['date'],
            paid_by=row['paid_by'],
            group_id=row['group_id'],
            created_at=row['created_at']
        )
    return None

def get_group_expenses(conn, group_id):
    """Get all expenses for a group"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE group_id = ?', (group_id,))
    
    expenses = []
    for row in cursor.fetchall():
        expenses.append(Expense(
            id=row['id'],
            description=row['description'],
            amount=row['amount'],
            date=row['date'],
            paid_by=row['paid_by'],
            group_id=row['group_id'],
            created_at=row['created_at']
        ))
    return expenses

def update_expense(conn, expense):
    """Update an expense's information"""
    with conn:
        conn.execute('''
        UPDATE expenses
        SET description = ?, amount = ?, date = ?, paid_by = ?
        WHERE id = ?
        ''', (expense.description, expense.amount, expense.date, 
              expense.paid_by, expense.id))

def delete_expense(conn, expense_id):
    """Delete an expense by ID"""
    with conn:
        conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))

# ExpenseShare operations
def insert_expense_share(conn, share):
    """Insert a new expense share"""
    cursor = conn.cursor()
    with conn:
        cursor.execute('''
        INSERT INTO expense_shares (expense_id, user_id, amount, is_paid, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (share.expense_id, share.user_id, share.amount, 
              share.is_paid, share.created_at))
    return cursor.lastrowid

def get_expense_shares(conn, expense_id):
    """Get all shares for an expense"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expense_shares WHERE expense_id = ?', (expense_id,))
    
    shares = []
    for row in cursor.fetchall():
        shares.append(ExpenseShare(
            id=row['id'],
            expense_id=row['expense_id'],
            user_id=row['user_id'],
            amount=row['amount'],
            is_paid=bool(row['is_paid']),
            created_at=row['created_at']
        ))
    return shares

def mark_share_as_paid(conn, share_id, is_paid=True):
    """Mark an expense share as paid or unpaid"""
    with conn:
        conn.execute('''
        UPDATE expense_shares
        SET is_paid = ?
        WHERE id = ?
        ''', (is_paid, share_id))

def get_user_balances(conn, group_id, user_id):
    """Calculate how much a user owes or is owed in a group"""
    cursor = conn.cursor()
    
    # What the user has paid
    cursor.execute('''
    SELECT SUM(amount) as total_paid
    FROM expenses
    WHERE group_id = ? AND paid_by = ?
    ''', (group_id, user_id))
    paid_row = cursor.fetchone()
    total_paid = paid_row['total_paid'] if paid_row['total_paid'] else 0
    
    # What the user owes
    cursor.execute('''
    SELECT SUM(es.amount) as total_owed
    FROM expense_shares es
    JOIN expenses e ON es.expense_id = e.id
    WHERE e.group_id = ? AND es.user_id = ? AND es.is_paid = 0
    ''', (group_id, user_id))
    owed_row = cursor.fetchone()
    total_owed = owed_row['total_owed'] if owed_row['total_owed'] else 0
    
    return {
        'paid': total_paid,
        'owed': total_owed,
        'balance': total_paid - total_owed
    }

def get_user_owes_whom(conn, group_id, user_id):
    """Calculate how much a user owes to each other user"""
    cursor = conn.cursor()
    cursor.execute('''
    SELECT u.id, u.username, u.first_name, u.last_name, SUM(es.amount) as amount_owed
    FROM expense_shares es
    JOIN expenses e ON es.expense_id = e.id
    JOIN users u ON e.paid_by = u.id
    WHERE e.group_id = ? AND es.user_id = ? AND es.is_paid = 0 AND e.paid_by != ?
    GROUP BY e.paid_by
    ''', (group_id, user_id, user_id))
    
    owes_to = []
    for row in cursor.fetchall():
        owes_to.append({
            'user_id': row['id'],
            'username': row['username'],
            'name': f"{row['first_name']} {row['last_name']}",
            'amount': row['amount_owed']
        })
    return owes_to

def initialize_db(db_path='expenses.db'):
    """Initialize the database with all tables"""
    conn = connect_db(db_path)
    create_tables(conn)
    conn.close()

# Run this if the script is executed directly
if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully!")