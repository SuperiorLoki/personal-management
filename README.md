# Expense Tracking System

An easy-to-use web application for tracking expenses and visualizing spending habits.  
Built with **Streamlit**, it allows you to log your expenses, view them by date, and explore analytics such as category percentages, bar charts, and pie charts.

## Project Structure

- **frontend/**: Contains the Streamlit application code.
- **backend/**: Contains the FastAPI backend server code.
- **tests/**: Contains the test cases for both frontend and backend.
- **requirements.txt**: Lists the required Python packages
- **README.md**: Provides an overview and instructions for the project.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/yourusername/expense-management-system](https://github.com/yourusername/expense-management-system)
   cd expense-management-system
    ```

2. **Install Dependencies:**:
    ```commandline
       pip install -r requirements.txt 
    ```

3. **Run the FastAPI server:**:
    ```commandline
   uvicorn server.servap:app --reload
   ```

4. **Run the Streamlit app:**:
    ```commandline
   streamlit run frontend/app.py
   ```



## Features

### 1. Expense Management
- Add new expenses with:
  - **Amount** (numeric)
  - **Category** (e.g., Rent, Food, Travel)
  - **Notes** (optional description)
  - **Date** (select from a date picker)
- Update or delete existing expenses
- View a filtered list of expenses based on selected date range

### 2. Analytics
- **Bar Chart** – Visualize total spending per category
- **Pie Chart** – See category-wise percentage distribution
- **Summary Table** – Displays each category, total amount spent, and its percentage of total spending

## How It Works
1. Navigate to the **Manage Expenses** tab to add, edit, or view your transactions.
2. Switch to the **Analytics** tab to see a breakdown of your spending habits.
3. All visualizations update automatically based on your stored expense data.

