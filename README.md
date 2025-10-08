# Loksewa Quiz Hub — Starter

## Prerequisites
- Docker & Docker Compose
- Node.js 22 LTS
- Python 3.12+ (optional locally if you prefer `uv`), or just run with `uvicorn` in a venv.

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
# create venv & install (uv recommended) — or use pip if you prefer
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r <(python - <<'PY'
from pathlib import Path; import tomllib; d=tomllib.loads(Path('pyproject.toml').read_text()); print('\n'.join(d['project']['dependencies']))
PY)
# run db migrations
alembic upgrade head
# run API
uvicorn app.main:app --reload --port 8000
```

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
