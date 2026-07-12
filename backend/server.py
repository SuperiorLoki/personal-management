from urllib.error import HTTPError

from fastapi import FastAPI, HTTPException, Depends,status
from datetime import date
from backend import db_helper
from typing import List
from pydantic import BaseModel, EmailStr
import logging
import backend import auth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI()

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str 

class Token(BaseModel):
    access_token: str
    token_type: str

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

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    existing_user = db_helper.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    hashed_pw = auth.get_password_hash(user.password)

    user_id = db_helper.create_user(user.email, hashed_pw)
    return {"message": "User created successfully!", "user_id": user_id}

@app.post("/login", response_model=Token)
def login_user(user: UserLogin):
    db_user = db_helper.get_user_by_email(user.email)

    if not db_user or not auth.verify_password(user.password, db_user['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = auth.create_access_token(data={"sub": db_user['email']})
    return {"access_token": access_token, "token_type": "bearer"}

#the response model will ensure that we only get a response of what we want that is stated in the Expense class
@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expense(expense_date: date, current_user: dict = Depends(auth.get_current_user)):
    expenses = db_helper.fetch_expenses_for_date(expense_date, current_user['id'])

    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expenses(expense_date: date, expenses:List[Expense], current_user: dict = Depends(auth.get_current_user)):
    try:
        db_helper.delete_expenses_for_date(expense_date, current_user['id'])
        for expense in expenses:
            db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes, current_user['id'])
        return {"message": "Expenses updated successfully"}
    except Exception as e:
        logger.exception("POST /tasks failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/")
def get_analytics(date_range: DateRange, current_user: dict = Depends(auth.get_current_user)):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date, current_user['id'])
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
def get_analytics_month(current_user: dict = Depends(auth.get_current_user)):
    data = db_helper.fetch_month(current_user['id'])
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve data.")
    return data

@app.get("/report/")
def get_reports(current_user: dict = Depends(auth.get_current_user)):
    data = db_helper.fetch_all_records(current_user['id'])
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
