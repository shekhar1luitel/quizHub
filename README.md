# Loksewa Quiz Hub — Starter

## Prerequisites
- Docker & Docker Compose
- Node.js 22 LTS
- Python 3.12+ (the backend `pyproject.toml` requires it)

> ℹ️ **Ubuntu tip:** if your default `python` is still 3.10/3.11, install 3.12 once via:
> ```bash
> sudo apt update
> sudo apt install python3.12 python3.12-venv
> ```
> then run the commands below with `python3.12` (or activate a pyenv/uv environment).

## 1) Start infrastructure
```bash
# ensure the Docker daemon is running first (Docker Desktop, or `sudo systemctl start docker` on Linux)
docker compose up -d
```

If you see an error like `Cannot connect to the Docker daemon`, start the daemon and rerun the command.

## 2) Backend setup

```bash
cd services/api
# copy env and edit secrets
cp .env.example .env
# create venv with Python 3.12 and install deps
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
# run db migrations
alembic upgrade head
# run API
uvicorn app.main:app --reload --port 8000
```

If you accidentally run the install step with an older interpreter and see
`ModuleNotFoundError: No module named 'tomllib'`, exit, ensure the virtual env
is using Python **3.12+**, then rerun the install step.

Open: [http://localhost:8000/health](http://localhost:8000/health)

## 3) Frontend setup

```bash
cd apps/web
cp .env.example .env  # if you create one; or set VITE_API_URL if needed
npm i
npm run dev
```

Open: [http://localhost:5173](http://localhost:5173)

## Next steps

* Implement JWT parsing middleware and `/users/me` using token subject.
* Add Questions, Options, Quizzes, Attempts models & CRUD.
* Wire Quiz flow: start → submit → results with explanations.
* Protect admin routes with role-based guards.
