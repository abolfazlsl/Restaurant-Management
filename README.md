# Restaurant Management System (OOP)

## Prerequisites
- Python 3.8+
- PostgreSQL
- Virtualenv (recommended)

## Installation
1. Database Setup and Schema Execution:
   - Create the database: Use `createdb restaurant_db` or in `psql`:
     ```sql
     CREATE DATABASE restaurant_db;
     \c restaurant_db
     ```
   - Execute the script: `psql -d restaurant_db -f schema.sql`

2. Package Installation:

python -m venv venv

source `venv/bin/activate` # Windows: `venv\Scripts\activate`

pip install -r requirements.txt

3. Connection Configuration:
- You can set the following environment variables:
  ```
  PG_DB=restaurant_db
  PG_USER=postgres
  PG_PASS=your_password
  PG_HOST=localhost
  PG_PORT=5432
  ```
  (use `.env` file)

4. Running the Application:

python app.py
