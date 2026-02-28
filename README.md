# DataShadow — Personal Data Exposure Auditor

DataShadow lets you enter your email or username and see how much of your personal data is exposed online: breach databases (HaveIBeenPwned), data broker opt-out hints, and pastes. An AI agent generates a **prioritized action plan** (sites to opt out of, passwords to change, accounts to delete). Your **exposure score** is tracked over time in the dashboard.

- **Backend:** FastAPI, PostgreSQL (scan history + remediation progress)
- **Frontend:** React (Vite) dashboard with exposure score chart
- **APIs:** HaveIBeenPwned (optional API key), rule-based or OpenAI action plans

## Quick start (localhost)

### 1. PostgreSQL

```bash
cd DataShadow
docker compose up -d
```

If Docker fails (e.g. image pull issues), install [PostgreSQL](https://www.postgresql.org/download/) locally, create a database named `datashadow`, and set `DATABASE_URL` in `backend/.env` accordingly.

### 2. Backend

Use **Python 3.11 or 3.12** (3.14 may have compatibility issues with asyncpg/pydantic).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add HIBP_API_KEY and/or OPENAI_API_KEY (optional)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

- **App:** http://localhost:5173  
- **API:** http://localhost:8000  
- **API docs:** http://localhost:8000/docs  

## Environment (backend)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL URL, e.g. `postgresql+asyncpg://postgres:postgres@localhost:5432/datashadow` |
| `HIBP_API_KEY` | [HaveIBeenPwned API key](https://haveibeenpwned.com/API/Key) for real breach/paste lookups (optional; demo data used if missing) |
| `OPENAI_API_KEY` | OpenAI API key for AI-generated action plans (optional; rule-based plan if missing) |
| `DATA_SHADOW_USER_AGENT` | User-Agent for HIBP requests (optional) |

## Features

- **Run scan:** Enter email/username → backend checks HIBP breaches/pastes and attaches data broker opt-out list.
- **Exposure score:** 0–100 from breach count, paste count, and broker count; stored per scan.
- **Exposure over time:** Dashboard chart of exposure score history for the account you’ve scanned.
- **Action plan:** AI (OpenAI) or rule-based list of actions (opt-out, password change, delete account, monitor).
- **Remediation progress:** Mark actions complete in the UI; stored in PostgreSQL.

## Project layout

```
DataShadow/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   └── scans.py
│   │   └── services/
│   │       ├── hibp.py
│   │       ├── data_brokers.py
│   │       └── action_plan.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.ts
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── docker-compose.yml
└── README.md
```
