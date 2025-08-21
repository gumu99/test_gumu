# AI-Powered Expense Tracker

## Overview

This is a Streamlit-based expense tracking application that leverages AI features for intelligent expense categorization and analysis. The application provides a comprehensive dashboard for managing personal finances with automated categorization, spending insights, and natural language query capabilities. Built with Python, it combines traditional expense tracking functionality with modern AI-powered features to help users better understand and manage their spending patterns.

## User Preferences

Preferred communication style: Simple, everyday language.
UI Preference: Enhanced visual styling with modern design elements, gradient backgrounds, and better user experience.

## System Architecture

### Frontend Architecture
- **Streamlit Framework**: Web-based interface providing an interactive dashboard with multiple pages for different functionalities
- **Multi-page Navigation**: Sidebar-based navigation system with dedicated pages for Dashboard, Add Expense, Manage Expenses, AI Insights, and Natural Language Query
- **Plotly Visualizations**: Interactive charts and graphs for expense analysis and trend visualization
- **Session State Management**: Persistent database and AI service instances across user interactions

### Backend Architecture
- **Modular Design**: Separated concerns with dedicated modules for database operations, AI features, and utility functions
- **Database Layer**: SQLite-based storage with a dedicated `ExpenseDatabase` class handling all data operations
- **AI Service Layer**: `ExpenseAI` class providing intelligent categorization and analysis capabilities
- **Utility Layer**: Common functions for data validation, formatting, and date handling

### Data Storage
- **SQLite Database**: Local file-based database (`expenses.db`) storing expense records
- **Schema Design**: Simple table structure with fields for ID, description, amount, category, date, and creation timestamp
- **Pandas Integration**: DataFrame-based data manipulation for analysis and visualization

### AI and Machine Learning
- **Keyword-Based Categorization**: Rule-based expense categorization using predefined keyword dictionaries
- **Category Prediction**: Automated expense classification across 8 main categories (Food, Transportation, Shopping, Entertainment, Bills, Healthcare, Education, Travel)
- **Scikit-learn Integration**: Linear regression and label encoding for advanced analytics and predictions
- **Natural Language Processing**: Basic text analysis for expense description processing

### Data Processing Pipeline
- **Input Validation**: Comprehensive validation for expense data including amount, description, and date formats
- **Currency Formatting**: Standardized money display formatting throughout the application
- **Date Handling**: Flexible date processing and validation with proper format checking

## External Dependencies

### Core Frameworks
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis library
- **NumPy**: Numerical computing support

### Visualization
- **Plotly Express**: High-level plotting interface for interactive charts
- **Plotly Graph Objects**: Low-level plotting for custom visualizations

### Machine Learning
- **Scikit-learn**: Machine learning library providing LinearRegression and LabelEncoder
- **Warnings**: Python standard library for managing ML-related warnings

### Database
- **SQLite3**: Built-in Python database interface for local data storage

### Utilities
- **datetime**: Python standard library for date and time operations
- **calendar**: Date/time utilities for calendar operations
- **re**: Regular expressions for text processing
- **os**: Operating system interface for file operations

### Development Tools
- **warnings**: Suppression of sklearn deprecation warnings for cleaner output