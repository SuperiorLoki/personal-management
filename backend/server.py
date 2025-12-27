from urllib.error import HTTPError

from fastapi import FastAPI, HTTPException
from datetime import date
from backend import db_helper
from typing import List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI()

class Expense(BaseModel):
    amount: float
    category: str
    notes: str

class Task(BaseModel):
    task_name: str
    notes: str
    task_status: bool

class DateRange(BaseModel):
    start_date: date
    end_date: date

#the response model will ensure that we only get a response of what we want that is stated in the Expense class
@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expense(expense_date: date):
    expenses = db_helper.fetch_expenses_for_date(expense_date)

    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expenses(expense_date: date, expenses:List[Expense]):
    try:
        db_helper.delete_tasks_for_date(expense_date)
        for expense in expenses:
            db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)
        return {"message": "Expenses updated successfully"}
    except Exception as e:
        logger.exception("POST /tasks failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve summary from the database.")

    data = [dict(row) for row in data]

    total = 0
    for section in data:
        total += section['total']

    breakdown = {}


    for section in data:
        percentage = (section['total']/total)*100 if total != 0 else 0
        breakdown[section["category"]] = {
            "total": section['total'],
            "percentage": round(percentage, 2)
        }

    return breakdown

@app.get("/month_breakdown/")
def get_analytics_month():
    data = db_helper.fetch_month()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve data.")
    return data

@app.get("/report/")
def get_reports():
    data = db_helper.fetch_all_records()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve data.")
    return data

@app.get("/tasks/{task_date}", response_model=List[Task])
def get_task(task_date: date):
    tasks = db_helper.fetch_tasks_for_date(task_date)
    if tasks is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks from the database.")
    return tasks

@app.post("/tasks/{task_date}")
def add_or_update_tasks(task_date: date, tasks:List[Task]):
    db_helper.delete_tasks_for_date(task_date)
    for task in tasks:
       db_helper.insert_task(task_date, task.task_name, task.task_status, task.notes)

    return {"message": "Tasks updated successfully"}

@app.get("/tasks/")
def get_all_tasks():
    data = db_helper.fetch_all_tasks()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve data.")
    return data


'''
@app.get("/user_breakdown/")
def get_analytics_user():
    data = db_helper.fetch_user()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve data.")
    return data
'''
