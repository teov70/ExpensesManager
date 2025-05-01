# models.py
import datetime

class User:
    def __init__(self, id=None, username=None, first_name=None, last_name=None, email=None, created_at=None):
        self.id = id  # Primary key
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.created_at = created_at if created_at else datetime.datetime.now()
    
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', name='{self.first_name} {self.last_name}')"

class ExpenseGroup:
    def __init__(self, id=None, name=None, description=None, created_by=None, created_at=None):
        self.id = id  # Primary key
        self.name = name
        self.description = description
        self.created_by = created_by  # User ID of creator
        self.created_at = created_at if created_at else datetime.datetime.now()
    
    def __repr__(self):
        return f"ExpenseGroup(id={self.id}, name='{self.name}')"

class Expense:
    def __init__(self, id=None, description=None, amount=None, date=None, paid_by=None, group_id=None, created_at=None):
        self.id = id  # Primary key
        self.description = description
        self.amount = amount  # Total amount of the expense
        self.date = date if date else datetime.datetime.now().date()
        self.paid_by = paid_by  # User ID who paid
        self.group_id = group_id  # ExpenseGroup ID
        self.created_at = created_at if created_at else datetime.datetime.now()
    
    def __repr__(self):
        return f"Expense(id={self.id}, description='{self.description}', amount={self.amount})"

class ExpenseShare:
    def __init__(self, id=None, expense_id=None, user_id=None, amount=None, is_paid=False, created_at=None):
        self.id = id  # Primary key
        self.expense_id = expense_id
        self.user_id = user_id
        self.amount = amount  # Amount this user owes for this expense
        self.is_paid = is_paid  # Whether this share has been paid
        self.created_at = created_at if created_at else datetime.datetime.now()
    
    def __repr__(self):
        return f"ExpenseShare(expense_id={self.expense_id}, user_id={self.user_id}, amount={self.amount}, paid={self.is_paid})"
