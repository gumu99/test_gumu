import sqlite3
import pandas as pd
from datetime import datetime
import os

class ExpenseDatabase:
    def __init__(self, db_path="expenses.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the expenses table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        date TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Database initialization error: {e}")
    
    def add_expense(self, description, amount, category, date):
        """Add a new expense to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO expenses (description, amount, category, date)
                    VALUES (?, ?, ?, ?)
                ''', (description, amount, category, date))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Error adding expense: {e}")
    
    def get_all_expenses(self):
        """Retrieve all expenses from the database as a pandas DataFrame."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT id, description, amount, category, date, created_at
                    FROM expenses
                    ORDER BY date DESC, created_at DESC
                '''
                df = pd.read_sql_query(query, conn)
                return df
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving expenses: {e}")
        except Exception:
            # Return empty DataFrame if no data exists
            return pd.DataFrame({
                'id': [],
                'description': [],
                'amount': [],
                'category': [],
                'date': [],
                'created_at': []
            })
    
    def get_expense_by_id(self, expense_id):
        """Retrieve a specific expense by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, description, amount, category, date, created_at
                    FROM expenses
                    WHERE id = ?
                ''', (expense_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'id': result[0],
                        'description': result[1],
                        'amount': result[2],
                        'category': result[3],
                        'date': result[4],
                        'created_at': result[5]
                    }
                return None
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving expense: {e}")
    
    def update_expense(self, expense_id, description, amount, category, date):
        """Update an existing expense."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE expenses
                    SET description = ?, amount = ?, category = ?, date = ?
                    WHERE id = ?
                ''', (description, amount, category, date, expense_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Error updating expense: {e}")
    
    def delete_expense(self, expense_id):
        """Delete an expense from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Error deleting expense: {e}")
    
    def get_expenses_by_category(self, category):
        """Retrieve expenses filtered by category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT id, description, amount, category, date, created_at
                    FROM expenses
                    WHERE category = ?
                    ORDER BY date DESC
                '''
                df = pd.read_sql_query(query, conn, params=[category])
                return df
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving expenses by category: {e}")
    
    def get_expenses_by_date_range(self, start_date, end_date):
        """Retrieve expenses within a specific date range."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT id, description, amount, category, date, created_at
                    FROM expenses
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                '''
                df = pd.read_sql_query(query, conn, params=[start_date, end_date])
                return df
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving expenses by date range: {e}")
    
    def get_monthly_summary(self, year, month):
        """Get summary statistics for a specific month."""
        try:
            # Format month to ensure leading zero
            month_str = f"{year}-{month:02d}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total amount for the month
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total,
                           COUNT(*) as count,
                           COALESCE(AVG(amount), 0) as average
                    FROM expenses
                    WHERE date LIKE ?
                ''', (f"{month_str}%",))
                
                result = cursor.fetchone()
                
                # Category breakdown
                cursor.execute('''
                    SELECT category, SUM(amount) as amount, COUNT(*) as count
                    FROM expenses
                    WHERE date LIKE ?
                    GROUP BY category
                    ORDER BY amount DESC
                ''', (f"{month_str}%",))
                
                categories = cursor.fetchall()
                
                return {
                    'total': result[0] if result else 0,
                    'count': result[1] if result else 0,
                    'average': result[2] if result else 0,
                    'categories': [{'category': cat[0], 'amount': cat[1], 'count': cat[2]} for cat in categories]
                }
        except sqlite3.Error as e:
            raise Exception(f"Error getting monthly summary: {e}")
    
    def close(self):
        """Close the database connection (if needed for cleanup)."""
        pass  # Using context managers, so no explicit closing needed
