import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings('ignore')

class ExpenseAI:
    def __init__(self):
        """Initialize the AI features for expense analysis."""
        self.category_keywords = {
            'Food': ['restaurant', 'food', 'lunch', 'dinner', 'breakfast', 'snack', 'coffee', 'pizza', 
                    'burger', 'sandwich', 'takeout', 'delivery', 'grocery', 'supermarket', 'cafe',
                    'mcdonalds', 'starbucks', 'subway', 'kfc', 'dominos', 'uber eats', 'doordash'],
            'Transportation': ['gas', 'fuel', 'uber', 'taxi', 'bus', 'train', 'metro', 'parking',
                             'toll', 'car', 'vehicle', 'maintenance', 'repair', 'lyft', 'transport'],
            'Shopping': ['amazon', 'store', 'shop', 'retail', 'clothes', 'clothing', 'shoes',
                        'electronics', 'gadget', 'online', 'purchase', 'buy', 'walmart', 'target'],
            'Entertainment': ['movie', 'cinema', 'theater', 'concert', 'game', 'sport', 'gym',
                            'netflix', 'spotify', 'entertainment', 'subscription', 'hobby'],
            'Bills': ['electric', 'water', 'internet', 'phone', 'rent', 'mortgage', 'insurance',
                     'utility', 'bill', 'payment', 'subscription', 'service'],
            'Healthcare': ['doctor', 'hospital', 'medicine', 'pharmacy', 'medical', 'health',
                          'dentist', 'clinic', 'prescription', 'treatment'],
            'Education': ['school', 'college', 'university', 'course', 'book', 'education',
                         'learning', 'tuition', 'fees', 'class'],
            'Travel': ['hotel', 'flight', 'vacation', 'trip', 'travel', 'booking', 'airbnb',
                      'resort', 'cruise', 'tour']
        }
    
    def categorize_expense(self, description):
        """
        Automatically categorize an expense based on its description using keyword matching.
        
        Args:
            description (str): The expense description
            
        Returns:
            str: The predicted category
        """
        if not description:
            return 'Other'
        
        description_lower = description.lower()
        
        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in description_lower:
                    # Give higher score for exact matches and longer keywords
                    score += len(keyword)
            category_scores[category] = score
        
        # Return category with highest score, or 'Other' if no matches
        if category_scores and max(category_scores.values()) > 0:
            best_category = max(category_scores, key=lambda x: category_scores[x])
            return best_category
        else:
            return 'Other'
    
    def analyze_monthly_spending(self, expenses_df):
        """
        Analyze monthly spending patterns and detect unusual spending.
        
        Args:
            expenses_df (pd.DataFrame): DataFrame containing expense data
            
        Returns:
            dict: Analysis results including current month, previous month, and percentage change
        """
        if expenses_df.empty:
            return None
        
        try:
            # Convert date column to datetime
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            
            # Get current month and previous month data
            current_date = datetime.now()
            current_month_start = current_date.replace(day=1)
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)
            
            # Filter expenses for current and previous month
            current_month_expenses = expenses_df[
                (expenses_df['date'] >= current_month_start) & 
                (expenses_df['date'] <= current_date)
            ]['amount'].sum()
            
            previous_month_expenses = expenses_df[
                (expenses_df['date'] >= previous_month_start) & 
                (expenses_df['date'] <= previous_month_end)
            ]['amount'].sum()
            
            # Calculate percentage change
            if previous_month_expenses > 0:
                percentage_change = ((current_month_expenses - previous_month_expenses) / previous_month_expenses) * 100
            else:
                percentage_change = 0 if current_month_expenses == 0 else 100
            
            return {
                'current_month': current_month_expenses,
                'previous_month': previous_month_expenses,
                'percentage_change': percentage_change
            }
        
        except Exception as e:
            print(f"Error in monthly spending analysis: {e}")
            return None
    
    def predict_next_month_spending(self, expenses_df):
        """
        Predict next month's spending using linear regression on historical data.
        
        Args:
            expenses_df (pd.DataFrame): DataFrame containing expense data
            
        Returns:
            float: Predicted spending amount for next month
        """
        if expenses_df.empty or len(expenses_df) < 3:
            return None
        
        try:
            # Convert date column to datetime and extract monthly totals
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            expenses_df['month_year'] = expenses_df['date'].dt.to_period('M')
            
            # Group by month and calculate total spending
            monthly_spending = expenses_df.groupby('month_year')['amount'].sum().reset_index()
            
            if len(monthly_spending) < 2:
                return None
            
            # Prepare data for linear regression
            monthly_spending['month_numeric'] = range(len(monthly_spending))
            X = monthly_spending[['month_numeric']].values
            y = monthly_spending['amount'].values
            
            # Train linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next month (next numeric value)
            next_month_numeric = len(monthly_spending)
            prediction = model.predict([[next_month_numeric]])[0]
            
            # Ensure prediction is not negative
            return max(0, prediction)
        
        except Exception as e:
            print(f"Error in spending prediction: {e}")
            return None
    
    def get_category_insights(self, expenses_df):
        """
        Generate insights about spending patterns by category.
        
        Args:
            expenses_df (pd.DataFrame): DataFrame containing expense data
            
        Returns:
            list: List of insights about spending patterns
        """
        insights = []
        
        if expenses_df.empty:
            return insights
        
        try:
            # Convert date column to datetime
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            
            # Current month data
            current_month_start = datetime.now().replace(day=1)
            current_month_data = expenses_df[expenses_df['date'] >= current_month_start]
            
            # Category spending for current month
            category_spending = current_month_data.groupby('category')['amount'].sum()
            
            # Find high spending categories (above average)
            if len(category_spending) > 0:
                avg_category_spending = category_spending.mean()
                high_spending_categories = category_spending[category_spending > avg_category_spending * 1.5]
                
                for category, amount in high_spending_categories.items():
                    insights.append({
                        'type': 'high_spending',
                        'category': category,
                        'amount': amount,
                        'message': f"High spending detected in {category}"
                    })
            
            # Check for increasing trends (compare last two months)
            if len(expenses_df) > 30:  # Only if we have enough data
                last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
                last_month_end = current_month_start - timedelta(days=1)
                
                last_month_data = expenses_df[
                    (expenses_df['date'] >= last_month_start) & 
                    (expenses_df['date'] <= last_month_end)
                ]
                
                current_category_spending = current_month_data.groupby('category')['amount'].sum()
                last_category_spending = last_month_data.groupby('category')['amount'].sum()
                
                for category in current_category_spending.index:
                    if category in last_category_spending.index:
                        current_amount = current_category_spending[category]
                        last_amount = last_category_spending[category]
                        
                        if current_amount > last_amount * 1.3:  # 30% increase
                            insights.append({
                                'type': 'increasing_trend',
                                'category': category,
                                'current_amount': current_amount,
                                'last_amount': last_amount,
                                'message': f"Spending in {category} is increasing"
                            })
        
        except Exception as e:
            print(f"Error generating category insights: {e}")
        
        return insights
    
    def process_natural_language_query(self, query, expenses_df):
        """
        Process natural language queries about expenses.
        
        Args:
            query (str): Natural language query
            expenses_df (pd.DataFrame): DataFrame containing expense data
            
        Returns:
            dict or str: Query results
        """
        if expenses_df.empty:
            return "No expense data available to query."
        
        try:
            # Convert date column to datetime
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            query_lower = query.lower()
            
            # Extract time periods
            current_date = datetime.now()
            
            # Define time period filters
            time_filters = {
                'last week': current_date - timedelta(weeks=1),
                'last month': current_date - timedelta(days=30),
                'this month': current_date.replace(day=1),
                'this year': current_date.replace(month=1, day=1),
                'last year': current_date.replace(year=current_date.year-1, month=1, day=1)
            }
            
            # Apply time filter if found in query
            filtered_df = expenses_df.copy()
            time_period = None
            
            for period, start_date in time_filters.items():
                if period in query_lower:
                    if period == 'last week':
                        filtered_df = expenses_df[expenses_df['date'] >= start_date]
                    elif period == 'last month':
                        last_month_start = (current_date.replace(day=1) - timedelta(days=1)).replace(day=1)
                        last_month_end = current_date.replace(day=1) - timedelta(days=1)
                        filtered_df = expenses_df[
                            (expenses_df['date'] >= last_month_start) & 
                            (expenses_df['date'] <= last_month_end)
                        ]
                    elif period == 'this month':
                        filtered_df = expenses_df[expenses_df['date'] >= start_date]
                    elif period == 'this year':
                        filtered_df = expenses_df[expenses_df['date'] >= start_date]
                    time_period = period
                    break
            
            # Extract category if mentioned
            category = None
            for cat in self.category_keywords.keys():
                if cat.lower() in query_lower:
                    category = cat
                    filtered_df = filtered_df[filtered_df['category'] == category]
                    break
            
            # Process different types of queries
            if any(word in query_lower for word in ['how much', 'total', 'spent', 'spending']):
                total_amount = filtered_df['amount'].sum()
                period_text = f" {time_period}" if time_period else ""
                category_text = f" on {category}" if category else ""
                
                return {
                    'amount': total_amount,
                    'details': f"Total spending{category_text}{period_text}: ${total_amount:.2f}",
                    'data': filtered_df[['date', 'description', 'amount', 'category']].head(10)
                }
            
            elif any(word in query_lower for word in ['average', 'avg']):
                avg_amount = filtered_df['amount'].mean()
                period_text = f" {time_period}" if time_period else ""
                category_text = f" on {category}" if category else ""
                
                return {
                    'amount': avg_amount,
                    'details': f"Average spending{category_text}{period_text}: ${avg_amount:.2f}",
                    'data': filtered_df[['date', 'description', 'amount', 'category']].head(10)
                }
            
            elif any(word in query_lower for word in ['highest', 'maximum', 'max', 'most expensive']):
                if not filtered_df.empty:
                    max_expense = filtered_df.loc[filtered_df['amount'].idxmax()]
                    return {
                        'amount': max_expense['amount'],
                        'details': f"Highest expense: {max_expense['description']} - ${max_expense['amount']:.2f} on {max_expense['date'].strftime('%Y-%m-%d')}",
                        'data': filtered_df.nlargest(5, 'amount')[['date', 'description', 'amount', 'category']]
                    }
            
            elif any(word in query_lower for word in ['lowest', 'minimum', 'min', 'cheapest']):
                if not filtered_df.empty:
                    min_expense = filtered_df.loc[filtered_df['amount'].idxmin()]
                    return {
                        'amount': min_expense['amount'],
                        'details': f"Lowest expense: {min_expense['description']} - ${min_expense['amount']:.2f} on {min_expense['date'].strftime('%Y-%m-%d')}",
                        'data': filtered_df.nsmallest(5, 'amount')[['date', 'description', 'amount', 'category']]
                    }
            
            else:
                # General query - return summary
                if not filtered_df.empty:
                    return {
                        'amount': filtered_df['amount'].sum(),
                        'details': f"Found {len(filtered_df)} expenses totaling ${filtered_df['amount'].sum():.2f}",
                        'data': filtered_df[['date', 'description', 'amount', 'category']].head(10)
                    }
            
            return "I couldn't understand your query. Please try rephrasing it."
        
        except Exception as e:
            return f"Error processing query: {str(e)}"
