#CRUD (Create, Read, Update, Delete)

import mysql.connector
import psycopg2
from contextlib import contextmanager
from backend.logging_setup import setup_logger
import streamlit as st
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")

logger = setup_logger('db_helper')

@contextmanager
def get_db_cursor(commit=False):
    try:
        conn = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            sslmode = 'require'
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass




def fetch_all_records(user_id):
    logger.info("fetch_all_records called for user {user_id}")
    #This means that the rest of the get_db_cursor() function will run (after the yield statement) after the with
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (user_id,))
        expenses = cursor.fetchall()
        return expenses



def fetch_expenses_for_date(expense_date, user_id):
    logger.info(f"fetch_expenses_for_date called with {expense_date}, for user {user_id}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s AND user_id = %s", (expense_date, user_id))
        expenses = cursor.fetchall()
        return expenses

def insert_expense(expense_date, amount, category, notes, user_id):
    logger.info(f"insert_expense called for {expense_date} with price: {amount}, category: {category}, notes: {notes}. Called for user {user_id}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("INSERT INTO expenses (expense_date, amount, category, notes, user_id) VALUES (%s, %s, %s, %s, %s)",
                       (expense_date, amount, category, notes, user_id)
                       )

def delete_expense(ident):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE id = %s",
                       (ident,))

def delete_expenses_for_date(expense_date, user_id):
    logger.info(f"delete_expenses_for_date called with {expense_date}.")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s AND user_id = %s",
                       (expense_date, user_id))


def update_expense(expense_date, amount, category, notes, user_id):
    logger.info(f"update_expenses called for {expense_date} with price: {amount}, category: {category}, notes: {notes}. Called for user {user_id}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("UPDATE expenses SET amount = %s, category = %s, notes = %s WHERE expense_date = %s AND user_id = %s",
                       (amount, category, notes, expense_date, user_id)
                       )

def fetch_expense_summary(start_date, end_date, user_id):
    logger.info(f"fetching expense summary for user {user_id} called between dates {start_date} and {end_date}.")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT category, SUM(amount) as Total FROM expenses WHERE user_id = %s AND expense_date BETWEEN %s AND %s GROUP BY category;",
        (user_id, start_date, end_date))
        data = cursor.fetchall()
        return data

def fetch_month(user_id):
    logger.info(f"fetching month by month summary")
    with get_db_cursor() as cursor:
        cursor.execute(f"SELECT TO_CHAR(expense_date, 'YYYY-MM') AS month, SUM(amount) AS total_expenses FROM expenses WHERE user_id = %s GROUP BY TO_CHAR(expense_date, 'YYYY-MM') ORDER BY month;", 
                       (user_id,))
        data = cursor.fetchall()
        return data

def fetch_all_tasks():
    logger.info(f"fetching all tasks")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM tasks")
        data = cursor.fetchall()
        return data

def fetch_tasks_for_date(task_date):
    logger.info(f"fetch_expenses_for_date called with {task_date}.")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM tasks WHERE task_date = %s", (task_date,))
        tasks = cursor.fetchall()
        return tasks

def update_tasks(task_date, task_name, notes, task_status):
    logger.info(f"update_tasks called for {task_date} with name: {task_name}, notes: {notes}, status: {task_status}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("UPDATE tasks SET task_name = %s, notes = %s, task_status = %s WHERE task_date = %s",
                       (task_name, notes, task_status, task_date)
                       )

def delete_tasks_for_date(task_date):
    logger.info(f"delete_tasks_for_date called with {task_date}.")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM tasks WHERE task_date = %s",
                       (task_date,))

def insert_task(task_date, task_name, task_status, notes):
    logger.info(f"insert_expense called for {task_date} with name: {task_name}, notes: {notes}.")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("INSERT INTO tasks (task_date, task_name, task_status, notes) VALUES (%s, %s, %s, %s)",
                       (task_date, task_name, task_status, notes)
                       )
        
def create_user(email, hashed_password):
    logger.info(f"Creating new user in database: {email}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id;",
            (email, hashed_password)
        )
        new_id = cursor.fetchone()['id']
        return new_id
    
def get_user_by_email(email):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
        return cursor.fetchone()
    

'''
def fetch_user():
    logger.info(f"fetching user data")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT `User`, SUM(amount) AS total_expense FROM expenses GROUP BY `User` ORDER BY total_expense DESC;")
        data = cursor.fetchall()
        return data
'''


if __name__ == "__main__":
    expenses = fetch_expenses_for_date("2024-08-01")
    print("Expenses for 2024-08-01:", expenses)
    summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    print("Expense summary between 2024-08-01 and 2024-08-05:")
    print(summary)
    data = [dict(row) for row in summary]
    for d in data:
        print(d)
    # for record in summary:
    #     print(record)
    #     print("Monthly summary:")
    #     print(fetch_month())


