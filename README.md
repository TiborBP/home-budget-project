# Home Budget API
Simple backend REST API for managing a personal/home budget.

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
- Alembic

## Setup

1. Clone the repository:
```bash
git clone <repo-url>
cd home_budget_project
```
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate #venv\Scripts\activate for windows
```
3. Install dependencies:
```bash
cd home_budget_api
pip install -r requirements.txt
```
4. Database setup:
```bash
python setup_db.py admin
```
5. Run the app
```bash
cd.. #have to be in home_budget_project\
uvicorn home_budget_api.main:app --reload --log-level debug
```
Swagger UI is available at: http://127.0.0.1:8000/docs



## Functionalities