# AI Job Recommendation Assistant

Phase 1 provides registration, login, JWT authentication, a protected current-user
API, and a protected React dashboard. Later job and AI features are intentionally
not included yet.

## Local setup

Create the PostgreSQL database:

```sql
CREATE DATABASE job_recommendation_db;
```

Copy `backend/.env.example` to `backend/.env` and replace the database password
and JWT secret. Copy `frontend/.env.example` to `frontend/.env`.

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (in a second terminal):

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. API documentation is at
`http://localhost:8000/docs`.
