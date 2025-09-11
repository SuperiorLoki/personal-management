import pytest
from backend import db_helper


def test_fetch_expenses_for_date_for_aug_1():

    expenses = db_helper.fetch_expenses_for_date("2024-08-01")

    assert expenses[0]['amount'] == 1227.0
    assert expenses[0]['category'] == "Rent"
    assert expenses[0]['notes'] == "Monthly rent payment"


def test_fetch_expenses_for_date_for_invalid_date():

    expenses = db_helper.fetch_expenses_for_date("9999-08-01")

    assert len(expenses) == 0

def test_fetch_expense_summary_invalid_range():

    expenses = db_helper.fetch_expense_summary("2099-01-01", "2099-12-31")

    assert len(expenses) == 0



