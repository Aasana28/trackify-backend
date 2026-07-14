# JTS Backend — Setup Instructions
# Follow these steps in order. Do not skip any step.

## Step 1 — Install Python
Download Python 3.11 from https://www.python.org/downloads/
During installation, check "Add Python to PATH"
Verify: open CMD and type:  python --version

## Step 2 — Install PostgreSQL
Download PostgreSQL from https://www.postgresql.org/download/windows/
During installation, remember the password you set for the "postgres" user
After installation, open pgAdmin (installed automatically)
Create a new database named: jts_db

## Step 3 — Set up the backend
Open CMD and navigate to the jts-backend folder:
  cd path\to\jts-backend

Create a virtual environment:
  python -m venv venv

Activate it:
  venv\Scripts\activate        (Windows)
  source venv/bin/activate     (Mac/Linux)

Install all dependencies:
  pip install -r requirements.txt

## Step 4 — Configure environment variables
Copy the .env.example file and rename it to .env:
  copy .env.example .env

Open .env and fill in your values:
  SECRET_KEY=any-random-long-string-here
  DB_PASSWORD=your_postgres_password_from_step2

Leave GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET empty for now (Google login will show an alert)

## Step 5 — Create database tables
  python manage.py makemigrations
  python manage.py migrate

## Step 6 — Create admin user (optional, to see data in Django admin)
  python manage.py createsuperuser

## Step 7 — Run the backend server
  python manage.py runserver

Backend is now running at: http://localhost:8000
Django admin panel at: http://localhost:8000/admin

---

## Running the Frontend
Open a NEW CMD window (keep backend running):
  cd path\to\jts
  npm install
  npm start

Frontend opens at: http://localhost:3000

---

## API Endpoints Summary

### Auth
  POST /api/auth/register/      — Create new account
  POST /api/auth/login/         — Login, get JWT token
  POST /api/auth/token/refresh/ — Refresh expired token
  POST /api/auth/google/        — Google login
  GET  /api/auth/me/            — Get logged-in user profile

### Applications
  GET    /api/applications/          — Get all applications
  POST   /api/applications/          — Add new application
  GET    /api/applications/<id>/     — Get one application
  PUT    /api/applications/<id>/     — Update application
  DELETE /api/applications/<id>/     — Delete application
  POST   /api/applications/<id>/timeline/ — Add timeline entry

### Reminders
  GET    /api/reminders/             — Get all reminders
  POST   /api/reminders/             — Add reminder
  PUT    /api/reminders/<id>/        — Update reminder
  DELETE /api/reminders/<id>/        — Delete reminder
  POST   /api/reminders/<id>/toggle/ — Toggle done status

### Brain Dumps
  GET    /api/braindumps/            — Get all brain dumps
  POST   /api/braindumps/            — Save new brain dump
  DELETE /api/braindumps/<id>/       — Delete brain dump

---

## How JWT Authentication Works (simple explanation)
1. User logs in with email + password
2. Backend returns an "access token" (valid 1 day) and "refresh token" (valid 30 days)
3. Frontend stores both tokens in localStorage
4. Every API request sends the access token in the Authorization header
5. Backend checks the token and returns data only if valid
6. If token expires, frontend automatically logs out the user

---

## What Was Changed in Frontend to Connect Backend
Only 2 files were changed:
1. src/services/api.js — NEW FILE — all API calls in one place
2. src/App.jsx — replaced mock data and simulated functions with real API calls

All pages (Dashboard, Applications, Timeline, etc.) were NOT changed.
They receive data as props, same as before — just now the data comes from the database.
