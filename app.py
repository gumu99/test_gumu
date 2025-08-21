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
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .success-box {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
    }
    
    .expense-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .nav-link {
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        transition: all 0.3s;
    }
    
    .nav-link:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
    .stButton > button {
        border-radius: 8px;
        border: none;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 8px;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced header
    st.markdown("""
    <div class="main-header">
        <h1>💰 AI-Powered Expense Tracker</h1>
        <p>Smart financial management with AI insights and predictions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced sidebar for navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["📊 Dashboard", "➕ Add Expense", "📝 Manage Expenses", "🤖 AI Insights", "🗣️ Natural Language Query"],
            format_func=lambda x: x
        )
        
        st.markdown("---")
        st.markdown("### 💡 Quick Tips")
        st.info("💡 Use descriptive expense names for better AI categorization!")
        st.info("🔍 Try natural language queries like 'How much did I spend on food this month?'")
    
    # Remove the icon from page name for processing
    page_clean = page.split(" ", 1)[1] if " " in page else page
    
    if page_clean == "Dashboard":
        show_dashboard()
    elif page_clean == "Add Expense":
        show_add_expense()
    elif page_clean == "Manage Expenses":
        show_manage_expenses()
    elif page_clean == "AI Insights":
        show_ai_insights()
    elif page_clean == "Natural Language Query":
        show_nl_query()

def show_dashboard():
    # Get all expenses
    expenses_df = st.session_state.db.get_all_expenses()
    
    if expenses_df.empty:
        st.markdown("""
        <div class="info-box">
            <h3>🎯 Welcome to Your Expense Tracker!</h3>
            <p>No expenses recorded yet. Add your first expense to get started with AI-powered financial insights!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Add Your First Expense", type="primary"):
                st.rerun()
        return
    
    # Summary statistics with enhanced styling
    st.markdown("### 📈 Financial Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_expenses = expenses_df['amount'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h4>💰 Total Expenses</h4>
            <h2 style="color: #667eea;">{format_currency(total_expenses)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_expense = expenses_df['amount'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 Average Expense</h4>
            <h2 style="color: #667eea;">{format_currency(avg_expense)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_transactions = len(expenses_df)
        st.markdown(f"""
        <div class="metric-card">
            <h4>🔢 Total Transactions</h4>
            <h2 style="color: #667eea;">{total_transactions}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        current_month = datetime.now().strftime('%Y-%m')
        monthly_expenses = expenses_df[expenses_df['date'].str.startswith(current_month)]['amount'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h4>📅 This Month</h4>
            <h2 style="color: #667eea;">{format_currency(monthly_expenses)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Enhanced Charts Section
    st.markdown("### 📊 Spending Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category_summary = expenses_df.groupby('category')['amount'].sum().reset_index()
        fig_pie = px.pie(category_summary, values='amount', names='category', 
                        title="💳 Spending Distribution by Category",
                        color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_layout(
            font=dict(size=12),
            title_font_size=16,
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        expenses_df['month'] = pd.to_datetime(expenses_df['date']).dt.to_period('M')
        monthly_trend = expenses_df.groupby('month')['amount'].sum().reset_index()
        monthly_trend['month'] = monthly_trend['month'].astype(str)
        
        fig_line = px.line(monthly_trend, x='month', y='amount', 
                          title="📈 Monthly Spending Trend",
                          markers=True,
                          line_shape='spline')
        fig_line.update_traces(
            line_color='#667eea',
            marker_color='#764ba2',
            marker_size=8
        )
        fig_line.update_layout(
            xaxis_title="Month", 
            yaxis_title="Amount ($)",
            font=dict(size=12),
            title_font_size=16,
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    # Enhanced Recent transactions
    st.markdown("### 🕒 Recent Transactions")
    recent_expenses = expenses_df.head(10)[['date', 'description', 'category', 'amount']]
    
    # Style the dataframe
    st.dataframe(
        recent_expenses,
        use_container_width=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
            "description": st.column_config.TextColumn("Description", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "amount": st.column_config.NumberColumn("Amount", format="$%.2f")
        },
        hide_index=True
    )

def show_add_expense():
    st.markdown("### ➕ Add New Expense")
    st.markdown("Add a new expense and let AI automatically categorize it for you!")
    
    # Enhanced form container
    with st.container():
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); margin: 1rem 0;">
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_expense_form", clear_on_submit=True):
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                st.markdown("**💭 Expense Details**")
                description = st.text_input(
                    "Description*", 
                    placeholder="e.g., Lunch at McDonald's, Gas for car, Netflix subscription",
                    help="Be descriptive! AI will categorize based on your description."
                )
                amount = st.number_input(
                    "Amount*", 
                    min_value=0.01, 
                    format="%.2f", 
                    step=0.01,
                    help="Enter the expense amount"
                )
            
            with col2:
                st.markdown("**🏷️ Category & Date**")
                
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
                
                category = st.selectbox(
                    "Category", 
                    categories, 
                    index=default_index,
                    help="Select or let AI suggest the category"
                )
                
                # Show AI suggestion with enhanced styling
                if suggested_category and suggested_category != category:
                    st.markdown(f"""
                    <div class="info-box" style="padding: 0.5rem; margin: 0.5rem 0;">
                        <strong>🤖 AI Suggestion:</strong> {suggested_category}
                    </div>
                    """, unsafe_allow_html=True)
                
                date = st.date_input(
                    "Date", 
                    value=datetime.now().date(),
                    help="When did this expense occur?"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Enhanced submit button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submitted = st.form_submit_button(
                    "💾 Add Expense", 
                    type="primary",
                    use_container_width=True
                )
            
            if submitted:
                if validate_expense_input(description, amount):
                    try:
                        st.session_state.db.add_expense(description, amount, category, date.isoformat())
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>✅ Success!</h4>
                            <p>Expense "{description}" added successfully!</p>
                            <p><strong>Amount:</strong> {format_currency(amount)} | <strong>Category:</strong> {category}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    except Exception as e:
                        st.markdown(f"""
                        <div class="warning-box">
                            <h4>❌ Error</h4>
                            <p>Failed to add expense: {str(e)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        <h4>⚠️ Invalid Input</h4>
                        <p>Please fill in all required fields correctly.</p>
                    </div>
                    """, unsafe_allow_html=True)

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
    st.markdown("### 🤖 AI Insights & Analytics")
    st.markdown("Get intelligent insights about your spending patterns and predictions.")
    
    expenses_df = st.session_state.db.get_all_expenses()
    
    if expenses_df.empty:
        st.markdown("""
        <div class="info-box">
            <h3>📊 No Data Available</h3>
            <p>Add some expenses first to see AI-powered insights and analytics!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Monthly spending comparison with enhanced styling
    st.markdown("### 📈 Monthly Spending Analysis")
    monthly_analysis = st.session_state.ai.analyze_monthly_spending(expenses_df)
    
    if monthly_analysis:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📅 Current Month</h4>
                <h2 style="color: #667eea;">{format_currency(monthly_analysis['current_month'])}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📅 Previous Month</h4>
                <h2 style="color: #667eea;">{format_currency(monthly_analysis['previous_month'])}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            change = monthly_analysis['percentage_change']
            if change > 20:
                st.markdown(f"""
                <div class="warning-box">
                    <h4>⚠️ High Increase Alert</h4>
                    <p>Spending increased by <strong>{change:.1f}%</strong> compared to last month!</p>
                    <p>Consider reviewing your expenses.</p>
                </div>
                """, unsafe_allow_html=True)
            elif change > 0:
                st.markdown(f"""
                <div class="info-box">
                    <h4>📊 Spending Increase</h4>
                    <p>Spending increased by <strong>{change:.1f}%</strong> compared to last month.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-box">
                    <h4>📉 Great Progress!</h4>
                    <p>Spending decreased by <strong>{abs(change):.1f}%</strong> compared to last month!</p>
                    <p>Keep up the good work!</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Enhanced spending prediction
    st.markdown("### 🔮 AI Spending Prediction")
    prediction = st.session_state.ai.predict_next_month_spending(expenses_df)
    
    if prediction:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎯 Next Month Prediction</h4>
                <h2 style="color: #667eea;">{format_currency(prediction)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
                <h4>💡 About This Prediction</h4>
                <p>This prediction is based on your historical spending patterns and trends using machine learning algorithms.</p>
                <p>Use this as a guide for budget planning!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced category insights
    st.markdown("### 📊 Smart Category Insights")
    category_insights = st.session_state.ai.get_category_insights(expenses_df)
    
    if category_insights:
        for insight in category_insights:
            if insight['type'] == 'high_spending':
                st.markdown(f"""
                <div class="warning-box">
                    <h4>💸 High Spending Alert</h4>
                    <p>You've spent <strong>{format_currency(insight['amount'])}</strong> on <strong>{insight['category']}</strong> this month.</p>
                    <p>This is above your average spending for this category.</p>
                </div>
                """, unsafe_allow_html=True)
            elif insight['type'] == 'increasing_trend':
                st.markdown(f"""
                <div class="info-box">
                    <h4>📈 Trending Up</h4>
                    <p><strong>{insight['category']}</strong> spending is showing an upward trend.</p>
                    <p>You might want to monitor this category more closely.</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
            <h4>📊 No Unusual Patterns</h4>
            <p>Your spending patterns look normal! No significant alerts at this time.</p>
        </div>
        """, unsafe_allow_html=True)

def show_nl_query():
    st.markdown("### 🗣️ Natural Language Query")
    st.markdown("Ask questions about your expenses in plain English! Our AI will understand and provide detailed answers.")
    
    # Enhanced example queries section
    with st.expander("💡 Example Queries You Can Try", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **💰 Spending Questions:**
            - "How much did I spend on food last month?"
            - "What's my total spending on entertainment?"
            - "How much did I spend last week?"
            """)
        
        with col2:
            st.markdown("""
            **📊 Analysis Questions:**
            - "What's my average spending on transportation?"
            - "Show me my highest expense this year"
            - "What's my lowest expense in healthcare?"
            """)
    
    # Enhanced query input
    st.markdown("### 🎯 Ask Your Question")
    query = st.text_area(
        "Enter your question:",
        placeholder="e.g., How much did I spend on food last month?",
        help="Ask any question about your expenses in natural language",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        ask_button = st.button("🔍 Ask AI", type="primary", use_container_width=True)
    
    if query and ask_button:
        expenses_df = st.session_state.db.get_all_expenses()
        
        if expenses_df.empty:
            st.markdown("""
            <div class="info-box">
                <h4>📊 No Data Available</h4>
                <p>No expenses available to query. Add some expenses first!</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        with st.spinner("🤖 AI is analyzing your question..."):
            try:
                result = st.session_state.ai.process_natural_language_query(query, expenses_df)
                
                if result:
                    st.markdown("### 📊 Query Results")
                    
                    if isinstance(result, dict):
                        # Enhanced result display
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            if 'amount' in result:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>💰 Amount</h4>
                                    <h2 style="color: #667eea;">{format_currency(result['amount'])}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col2:
                            if 'details' in result:
                                st.markdown(f"""
                                <div class="info-box">
                                    <h4>📋 Details</h4>
                                    <p>{result['details']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if 'data' in result and not result['data'].empty:
                            st.markdown("#### 📄 Related Transactions")
                            st.dataframe(
                                result['data'],
                                use_container_width=True,
                                column_config={
                                    "date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
                                    "description": st.column_config.TextColumn("Description"),
                                    "category": st.column_config.TextColumn("Category"),
                                    "amount": st.column_config.NumberColumn("Amount", format="$%.2f")
                                },
                                hide_index=True
                            )
                    else:
                        st.markdown(f"""
                        <div class="info-box">
                            <h4>📋 Result</h4>
                            <p>{result}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        <h4>🤔 Couldn't Understand</h4>
                        <p>I couldn't understand your query. Please try rephrasing it or use one of the example queries above.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            except Exception as e:
                st.markdown(f"""
                <div class="warning-box">
                    <h4>❌ Error</h4>
                    <p>Error processing query: {str(e)}</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
