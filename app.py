import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

from database import ExpenseDatabase
from ai_features import ExpenseAI
from utils import format_currency, validate_expense_input

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = ExpenseDatabase()
    st.session_state.ai = ExpenseAI()

def main():
    st.set_page_config(
        page_title="AI Expense Tracker",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 AI-Powered Expense Tracker")
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Dashboard", "Add Expense", "Manage Expenses", "AI Insights", "Natural Language Query"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Add Expense":
        show_add_expense()
    elif page == "Manage Expenses":
        show_manage_expenses()
    elif page == "AI Insights":
        show_ai_insights()
    elif page == "Natural Language Query":
        show_nl_query()

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Get all expenses
    expenses_df = st.session_state.db.get_all_expenses()
    
    if expenses_df.empty:
        st.info("No expenses recorded yet. Add your first expense to get started!")
        return
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_expenses = expenses_df['amount'].sum()
        st.metric("Total Expenses", format_currency(total_expenses))
    
    with col2:
        avg_expense = expenses_df['amount'].mean()
        st.metric("Average Expense", format_currency(avg_expense))
    
    with col3:
        total_transactions = len(expenses_df)
        st.metric("Total Transactions", total_transactions)
    
    with col4:
        current_month = datetime.now().strftime('%Y-%m')
        monthly_expenses = expenses_df[expenses_df['date'].str.startswith(current_month)]['amount'].sum()
        st.metric("This Month", format_currency(monthly_expenses))
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Expenses by Category")
        category_summary = expenses_df.groupby('category')['amount'].sum().reset_index()
        fig_pie = px.pie(category_summary, values='amount', names='category', 
                        title="Spending Distribution by Category")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Monthly Spending Trend")
        expenses_df['month'] = pd.to_datetime(expenses_df['date']).dt.to_period('M')
        monthly_trend = expenses_df.groupby('month')['amount'].sum().reset_index()
        monthly_trend['month'] = monthly_trend['month'].astype(str)
        
        fig_line = px.line(monthly_trend, x='month', y='amount', 
                          title="Monthly Spending Trend",
                          markers=True)
        fig_line.update_layout(xaxis_title="Month", yaxis_title="Amount ($)")
        st.plotly_chart(fig_line, use_container_width=True)
    
    # Recent transactions
    st.subheader("Recent Transactions")
    recent_expenses = expenses_df.head(10)
    st.dataframe(recent_expenses, use_container_width=True)

def show_add_expense():
    st.header("➕ Add New Expense")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_input("Description*", placeholder="e.g., Lunch at McDonald's")
            amount = st.number_input("Amount*", min_value=0.01, format="%.2f", step=0.01)
        
        with col2:
            # Get suggested category using AI
            suggested_category = ""
            if description:
                suggested_category = st.session_state.ai.categorize_expense(description)
            
            categories = ["Food", "Transportation", "Shopping", "Entertainment", "Bills", 
                         "Healthcare", "Education", "Travel", "Other"]
            
            # Set default category to suggested one if available
            default_index = 0
            if suggested_category in categories:
                default_index = categories.index(suggested_category)
            
            category = st.selectbox("Category", categories, index=default_index)
            
            if suggested_category and suggested_category != category:
                st.info(f"💡 AI suggests: {suggested_category}")
            
            date = st.date_input("Date", value=datetime.now().date())
        
        submitted = st.form_submit_button("Add Expense")
        
        if submitted:
            if validate_expense_input(description, amount):
                try:
                    st.session_state.db.add_expense(description, amount, category, date.isoformat())
                    st.success(f"✅ Expense added successfully! Amount: {format_currency(amount)}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding expense: {str(e)}")
            else:
                st.error("❌ Please fill in all required fields correctly.")

def show_manage_expenses():
    st.header("📝 Manage Expenses")
    
    expenses_df = st.session_state.db.get_all_expenses()
    
    if expenses_df.empty:
        st.info("No expenses to manage yet.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ["All"] + list(expenses_df['category'].unique())
        selected_category = st.selectbox("Filter by Category", categories)
    
    with col2:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
    
    with col3:
        end_date = st.date_input("End Date", value=datetime.now().date())
    
    # Apply filters
    filtered_df = expenses_df.copy()
    
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    filtered_df = filtered_df[
        (pd.to_datetime(filtered_df['date']).dt.date >= start_date) &
        (pd.to_datetime(filtered_df['date']).dt.date <= end_date)
    ]
    
    st.markdown(f"**Showing {len(filtered_df)} expenses**")
    
    # Display expenses with edit/delete options
    for idx, row in filtered_df.iterrows():
        with st.expander(f"{row['date']} - {row['description']} - {format_currency(row['amount'])}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Category:** {row['category']}")
                st.write(f"**Amount:** {format_currency(row['amount'])}")
                st.write(f"**Date:** {row['date']}")
            
            with col2:
                if st.button(f"Edit", key=f"edit_{row['id']}"):
                    st.session_state[f"editing_{row['id']}"] = True
                    st.rerun()
            
            with col3:
                if st.button(f"Delete", key=f"delete_{row['id']}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{row['id']}", False):
                        st.session_state.db.delete_expense(row['id'])
                        st.success("Expense deleted!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{row['id']}"] = True
                        st.warning("Click again to confirm deletion")
            
            # Edit form
            if st.session_state.get(f"editing_{row['id']}", False):
                with st.form(f"edit_form_{row['id']}"):
                    new_description = st.text_input("Description", value=row['description'])
                    new_amount = st.number_input("Amount", value=float(row['amount']), min_value=0.01, format="%.2f")
                    categories = ["Food", "Transportation", "Shopping", "Entertainment", "Bills", 
                                 "Healthcare", "Education", "Travel", "Other"]
                    new_category = st.selectbox("Category", categories, 
                                              index=categories.index(row['category']) if row['category'] in categories else 0)
                    new_date = st.date_input("Date", value=pd.to_datetime(row['date']).date())
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save Changes"):
                            st.session_state.db.update_expense(
                                row['id'], new_description, new_amount, new_category, new_date.isoformat()
                            )
                            st.session_state[f"editing_{row['id']}"] = False
                            st.success("Expense updated!")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"editing_{row['id']}"] = False
                            st.rerun()

def show_ai_insights():
    st.header("🤖 AI Insights")
    
    expenses_df = st.session_state.db.get_all_expenses()
    
    if expenses_df.empty:
        st.info("No expenses available for analysis yet.")
        return
    
    # Monthly spending comparison
    st.subheader("📈 Monthly Spending Analysis")
    monthly_analysis = st.session_state.ai.analyze_monthly_spending(expenses_df)
    
    if monthly_analysis:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Current Month", format_currency(monthly_analysis['current_month']))
            st.metric("Previous Month", format_currency(monthly_analysis['previous_month']))
        
        with col2:
            change = monthly_analysis['percentage_change']
            if change > 20:
                st.warning(f"⚠️ Spending increased by {change:.1f}% compared to last month!")
            elif change > 0:
                st.info(f"📊 Spending increased by {change:.1f}% compared to last month")
            else:
                st.success(f"📉 Spending decreased by {abs(change):.1f}% compared to last month")
    
    # Spending prediction
    st.subheader("🔮 Next Month Prediction")
    prediction = st.session_state.ai.predict_next_month_spending(expenses_df)
    
    if prediction:
        st.metric("Predicted Next Month Spending", format_currency(prediction))
        
        # Show prediction accuracy info
        st.info("💡 Prediction is based on historical spending patterns and trends.")
    
    # Category insights
    st.subheader("📊 Category Insights")
    category_insights = st.session_state.ai.get_category_insights(expenses_df)
    
    for insight in category_insights:
        if insight['type'] == 'high_spending':
            st.warning(f"💸 High spending in {insight['category']}: {format_currency(insight['amount'])} this month")
        elif insight['type'] == 'increasing_trend':
            st.info(f"📈 {insight['category']} spending is trending upward")

def show_nl_query():
    st.header("🗣️ Natural Language Query")
    st.markdown("Ask questions about your expenses in plain English!")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        - "How much did I spend on food last month?"
        - "What's my average spending on transportation?"
        - "Show me my highest expense this year"
        - "How much did I spend last week?"
        - "What's my total spending on entertainment?"
        """)
    
    query = st.text_input("Enter your question:", placeholder="e.g., How much did I spend on food last month?")
    
    if query:
        expenses_df = st.session_state.db.get_all_expenses()
        
        if expenses_df.empty:
            st.info("No expenses available to query.")
            return
        
        try:
            result = st.session_state.ai.process_natural_language_query(query, expenses_df)
            
            if result:
                st.success("📊 Query Result:")
                if isinstance(result, dict):
                    if 'amount' in result:
                        st.metric("Amount", format_currency(result['amount']))
                    if 'details' in result:
                        st.write(result['details'])
                    if 'data' in result and not result['data'].empty:
                        st.dataframe(result['data'])
                else:
                    st.write(result)
            else:
                st.warning("🤔 I couldn't understand your query. Please try rephrasing it or use one of the example queries.")
        
        except Exception as e:
            st.error(f"❌ Error processing query: {str(e)}")

if __name__ == "__main__":
    main()
