import re
from datetime import datetime

def format_currency(amount):
    """
    Format a number as currency with proper formatting.
    
    Args:
        amount (float): The amount to format
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "$0.00"
    
    return f"${amount:,.2f}"

def validate_expense_input(description, amount):
    """
    Validate expense input data.
    
    Args:
        description (str): Expense description
        amount (float): Expense amount
        
    Returns:
        bool: True if input is valid, False otherwise
    """
    # Check if description is provided and not empty
    if not description or description.strip() == "":
        return False
    
    # Check if amount is positive
    if amount is None or amount <= 0:
        return False
    
    # Check if description is reasonable length
    if len(description.strip()) > 200:
        return False
    
    return True

def validate_date_format(date_string):
    """
    Validate if a date string is in the correct format (YYYY-MM-DD).
    
    Args:
        date_string (str): Date string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def parse_date_input(date_input):
    """
    Parse various date input formats and return a standardized date string.
    
    Args:
        date_input (str or datetime): Date input in various formats
        
    Returns:
        str: Standardized date string (YYYY-MM-DD) or None if invalid
    """
    if isinstance(date_input, datetime):
        return date_input.strftime('%Y-%m-%d')
    
    if isinstance(date_input, str):
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_input, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
    
    return None

def sanitize_input(text):
    """
    Sanitize text input to prevent potential security issues.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove or escape potentially dangerous characters
    # For expense descriptions, we mainly want to prevent SQL injection
    # and XSS, but since we're using parameterized queries and Streamlit
    # handles output escaping, basic cleaning should suffice
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove any null bytes
    text = text.replace('\x00', '')
    
    return text

def categorize_amount(amount):
    """
    Categorize expense amount into ranges for analysis.
    
    Args:
        amount (float): Expense amount
        
    Returns:
        str: Amount category
    """
    if amount <= 10:
        return "Small (≤$10)"
    elif amount <= 50:
        return "Medium ($10-$50)"
    elif amount <= 200:
        return "Large ($50-$200)"
    else:
        return "Very Large (>$200)"

def get_month_name(month_number):
    """
    Get the full month name from month number.
    
    Args:
        month_number (int): Month number (1-12)
        
    Returns:
        str: Full month name
    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    if 1 <= month_number <= 12:
        return months[month_number - 1]
    else:
        return "Unknown"

def calculate_percentage_change(current, previous):
    """
    Calculate percentage change between two values.
    
    Args:
        current (float): Current value
        previous (float): Previous value
        
    Returns:
        float: Percentage change
    """
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return ((current - previous) / previous) * 100

def format_percentage(percentage):
    """
    Format percentage for display.
    
    Args:
        percentage (float): Percentage value
        
    Returns:
        str: Formatted percentage string
    """
    return f"{percentage:+.1f}%"

def truncate_text(text, max_length=50):
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def is_valid_category(category):
    """
    Check if a category is valid.
    
    Args:
        category (str): Category to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_categories = [
        "Food", "Transportation", "Shopping", "Entertainment", 
        "Bills", "Healthcare", "Education", "Travel", "Other"
    ]
    
    return category in valid_categories
