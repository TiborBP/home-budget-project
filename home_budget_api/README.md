# Home Budget API
Simple backend REST API for managing a personal/home budget, built with FastAPI and PostgreSQL.

## Features
- User registration and login (JWT authentication)
- Preset and user-created categories
- Add, view, and delete expenses and categories
- Filter expenses by category, amount, and date
- Budget summary with total spent, remaining balance, and spending by category
- Summary of spending over the last month, quarter, and year

## Tech Stack
- Python 3.10+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Swagger/OpenAPI documentation

## Setup

1. Clone the repository:

git clone <repo-url>
cd home_budget_api

2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate #venv\Scripts\activate for windows

3. Install dependencies:
pip install -r requirements.txt

4. Database setup:
CREATE DATABASE home_budget;
CREATE USER home_budget_user WITH PASSWORD 'home_budget';
GRANT ALL PRIVILEGES ON DATABASE home_budget TO home_budget_user;

5. Run the app:
uvicorn home_budget_api.main:app --reload

Swagger UI is available at: http://127.0.0.1:8000/docs




cd home_budget_project
python -m venv venv
source venv/bin/activate #venv\Scripts\activate for windows

cd home_budget_api
pip install -r requirements.txt

in home_budget_api> python setup_db.py admin

cd..
uvicorn home_budget_api.main:app --reload --log-level debug