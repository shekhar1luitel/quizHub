# Loksewa Quiz Hub — Starter Monorepo (FastAPI + Vue 3 + Tailwind v4)

A ready-to-run scaffold with pinned, stable tooling for a solo-dev MVP. Copy files into your repo and follow the README steps at the end.

---

## 📁 Project Structure

```
loksewa-quiz-hub/
├─ docker-compose.yml
├─ README.md
├─ .env.example
├─ services/
│  └─ api/
│     ├─ pyproject.toml
│     ├─ .env.example
│     ├─ alembic.ini
│     ├─ alembic/
│     │  ├─ env.py
│     │  └─ versions/  # (empty)
│     └─ app/
│        ├─ main.py
│        ├─ core/
│        │  ├─ config.py
│        │  └─ security.py
│        ├─ db/
│        │  ├─ session.py
│        │  └─ base.py
│        ├─ models/
│        │  ├─ user.py
│        │  └─ __init__.py
│        ├─ schemas/
│        │  ├─ auth.py
│        │  └─ user.py
│        └─ api/
│           ├─ __init__.py
│           ├─ deps.py
│           └─ routes/
│              ├─ __init__.py
│              ├─ health.py
│              ├─ auth.py
│              └─ users.py
└─ apps/
   └─ web/
      ├─ package.json
      ├─ vite.config.ts
      ├─ index.html
      └─ src/
         ├─ main.ts
         ├─ App.vue
         ├─ assets/
         │  └─ main.css
         ├─ api/
         │  └─ http.ts
         ├─ pages/
         │  ├─ Home.vue
         │  ├─ Quiz.vue
         │  ├─ Results.vue
         │  ├─ Dashboard.vue
         │  ├─ auth/
         │  │  ├─ Login.vue
         │  │  └─ Register.vue
         │  └─ admin/
         │     ├─ Admin.vue
         │     └─ QuestionsCRUD.vue
         ├─ stores/
         │  ├─ auth.ts
         │  └─ quiz.ts
         └─ router/
            └─ index.ts
```

---

## 🐘 Docker Compose (Postgres 17 + Redis 7)

**File: `docker-compose.yml`**

```yaml
version: "3.9"
services:
  db:
    image: postgres:17
    container_name: lqh_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: quiz
      POSTGRES_PASSWORD: quiz
      POSTGRES_DB: quizhub
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    container_name: lqh_redis
    restart: unless-stopped
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

**File: `.env.example` (monorepo root)**

```env
# API public URL (for CORS) and Web URL
API_BASE_URL=http://localhost:8000
WEB_BASE_URL=http://localhost:5173
```

---

## 🐍 Backend — FastAPI

**File: `services/api/pyproject.toml`**

```toml
[project]
name = "loksewa_api"
version = "0.1.0"
description = "Loksewa Quiz Hub API (FastAPI)"
requires-python = ">=3.12"
dependencies = [
  "fastapi==0.118.*",
  "uvicorn[standard]==0.30.*",
  "SQLAlchemy==2.0.*",
  "psycopg[binary]==3.2.*",
  "alembic==1.13.*",
  "pydantic==2.*",
  "python-multipart==0.0.*",
  "passlib[bcrypt]==1.7.*",
  "email-validator==2.*",
  "python-dotenv==1.*",
]

[tool.ruff]
line-length = 100
select = ["E","F","I","UP","B","SIM"]

[tool.pytest.ini_options]
addopts = "-q"
```

**File: `services/api/.env.example`**

```env
# Database
DATABASE_URL=postgresql+psycopg://quiz:quiz@localhost:5432/quizhub

# Security
JWT_SECRET=replace-with-a-long-random-string
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14

# CORS
BACKEND_CORS_ORIGINS=http://localhost:5173
```

**File: `services/api/alembic.ini`**

```ini
[alembic]
script_location = alembic
prepend_sys_path = .

env.py = alembic/env.py

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers = console
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

**File: `services/api/alembic/env.py`**

```python
from __future__ import annotations
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
fileConfig(config.config_file_name)

def get_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql+psycopg://quiz:quiz@localhost:5432/quizhub")

# Import metadata from models
from app.db.base import Base  # noqa: E402

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**File: `services/api/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router

app = FastAPI(title="Loksewa Quiz Hub API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
```

**File: `services/api/app/core/config.py`**

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://quiz:quiz@localhost:5432/quizhub"
    jwt_secret: str = "dev-secret"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    backend_cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

settings = Settings()
```

**File: `services/api/app/core/security.py`**

```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_jwt_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)
```

**File: `services/api/app/db/session.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**File: `services/api/app/db/base.py`**

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

**File: `services/api/app/models/user.py`**

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
```

**File: `services/api/app/schemas/user.py`**

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
```

**File: `services/api/app/schemas/auth.py`**

```python
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str
```

**File: `services/api/app/api/deps.py`**

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db

# Placeholder for auth dependency (parse JWT in a real app)
def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db
```

**File: `services/api/app/api/routes/health.py`**

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}
```

**File: `services/api/app/api/routes/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import LoginIn, Token
from app.schemas.user import UserCreate, UserOut
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_jwt_token
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, hashed_password=get_password_hash(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_jwt_token(str(user.id))
    return Token(access_token=token)
```

**File: `services/api/app/api/routes/users.py`**

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def me():
    # Placeholder; in real app parse JWT and fetch user
    return {"id": 1, "email": "demo@example.com", "role": "user"}
```

---

## 🧭 Initial migration (users table)

Run this after you’ve created the DB container.

```bash
# from services/api
alembic revision -m "create users" --autogenerate
alembic upgrade head
```

> If autogenerate doesn’t pick up the model, you can hand-write a simple migration creating `users` (id, email, hashed_password, role).

---

## 🖥️ Frontend — Vue 3 + Vite + Tailwind v4

**File: `apps/web/package.json`**

```json
{
  "name": "loksewa-web",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.2",
    "naive-ui": "^2.39.0",
    "pinia": "^2.1.7",
    "vue": "^3.5.0",
    "vue-router": "^4.3.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.41",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

**File: `apps/web/vite.config.ts`**

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: { port: 5173 },
})
```

**File: `apps/web/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Loksewa Quiz Hub</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

**File: `apps/web/src/assets/main.css`**

```css
@import "tailwindcss";
```

**File: `apps/web/src/main.ts`**

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/main.css'

createApp(App).use(createPinia()).use(router).mount('#app')
```

**File: `apps/web/src/router/index.ts`**

```ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../pages/Home.vue') },
  { path: '/quiz', component: () => import('../pages/Quiz.vue') },
  { path: '/results/:id', component: () => import('../pages/Results.vue') },
  { path: '/dashboard', component: () => import('../pages/Dashboard.vue') },
  { path: '/admin', component: () => import('../pages/admin/Admin.vue') },
  { path: '/login', component: () => import('../pages/auth/Login.vue') },
  { path: '/register', component: () => import('../pages/auth/Register.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
```

**File: `apps/web/src/api/http.ts`**

```ts
import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const http = axios.create({ baseURL })

http.interceptors.response.use(
  (r) => r,
  async (error) => {
    // handle refresh flow later
    return Promise.reject(error)
  }
)
```

**File: `apps/web/src/App.vue`**

```vue
<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="px-6 py-4 shadow bg-white">
      <nav class="flex items-center gap-4">
        <a href="/" class="font-semibold">Loksewa Quiz Hub</a>
        <a href="/quiz">Quiz</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/admin">Admin</a>
      </nav>
    </header>
    <main class="p-6">
      <router-view />
    </main>
  </div>
</template>
```

**File: `apps/web/src/pages/Home.vue`**

```vue
<template>
  <section class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Welcome</h1>
    <p class="mb-4">Start practicing Lok Sewa style quizzes.</p>
    <a class="inline-block px-4 py-2 bg-black text-white rounded" href="/quiz">Start a quiz</a>
  </section>
</template>
```

**File: `apps/web/src/pages/Quiz.vue`**

```vue
<template>
  <div>
    <h2 class="text-xl font-semibold mb-4">Quiz</h2>
    <p class="opacity-70">Placeholder — connect to /attempts API later.</p>
  </div>
</template>
```

**File: `apps/web/src/pages/Results.vue`**

```vue
<template>
  <div>
    <h2 class="text-xl font-semibold mb-4">Results</h2>
    <p class="opacity-70">Your score and explanations will appear here.</p>
  </div>
</template>
```

**File: `apps/web/src/pages/Dashboard.vue`**

```vue
<template>
  <div>
    <h2 class="text-xl font-semibold mb-4">Dashboard</h2>
    <ul class="list-disc pl-6 space-y-1">
      <li>Average score</li>
      <li>Accuracy by subject</li>
      <li>Recent attempts</li>
    </ul>
  </div>
</template>
```

**File: `apps/web/src/pages/auth/Login.vue`**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { http } from '../../api/http'
const email = ref('')
const password = ref('')
const msg = ref('')
const submit = async () => {
  try {
    const { data } = await http.post('/auth/login', { email: email.value, password: password.value })
    msg.value = `Logged in! token: ${data.access_token.substring(0, 12)}...`
  } catch (e: any) {
    msg.value = e?.response?.data?.detail || 'Login failed'
  }
}
</script>
<template>
  <form class="max-w-sm space-y-3" @submit.prevent="submit">
    <input v-model="email" class="w-full border rounded px-3 py-2" placeholder="Email" />
    <input v-model="password" type="password" class="w-full border rounded px-3 py-2" placeholder="Password" />
    <button class="px-4 py-2 bg-black text-white rounded">Login</button>
    <p class="text-sm opacity-75">{{ msg }}</p>
  </form>
</template>
```

**File: `apps/web/src/pages/auth/Register.vue`**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { http } from '../../api/http'
const email = ref('')
const password = ref('')
const msg = ref('')
const submit = async () => {
  try {
    const { data } = await http.post('/auth/register', { email: email.value, password: password.value })
    msg.value = `Registered: ${data.email}`
  } catch (e: any) {
    msg.value = e?.response?.data?.detail || 'Registration failed'
  }
}
</script>
<template>
  <form class="max-w-sm space-y-3" @submit.prevent="submit">
    <input v-model="email" class="w-full border rounded px-3 py-2" placeholder="Email" />
    <input v-model="password" type="password" class="w-full border rounded px-3 py-2" placeholder="Password" />
    <button class="px-4 py-2 bg-black text-white rounded">Register</button>
    <p class="text-sm opacity-75">{{ msg }}</p>
  </form>
</template>
```

**File: `apps/web/src/pages/admin/Admin.vue`**

```vue
<template>
  <div>
    <h2 class="text-xl font-semibold mb-4">Admin</h2>
    <p class="opacity-70">Build Questions CRUD & CSV import here.</p>
  </div>
</template>
```

**File: `apps/web/src/pages/admin/QuestionsCRUD.vue`**

```vue
<template>
  <div>
    <h3 class="text-lg font-semibold mb-2">Questions</h3>
    <p>Table + form will go here.</p>
  </div>
</template>
```

**File: `apps/web/src/stores/auth.ts`**

```ts
import { defineStore } from 'pinia'
export const useAuthStore = defineStore('auth', {
  state: () => ({ accessToken: '', refreshToken: '' }),
  actions: {
    setAccessToken(t: string) { this.accessToken = t },
    logout() { this.accessToken = ''; this.refreshToken = '' }
  }
})
```

**File: `apps/web/src/stores/quiz.ts`**

```ts
import { defineStore } from 'pinia'
export const useQuizStore = defineStore('quiz', {
  state: () => ({ startedAt: 0, answers: {} as Record<number, number> }),
})
```

---

## 📘 README (root)

**File: `README.md`**

````md
# Loksewa Quiz Hub — Starter

## Prerequisites
- Docker & Docker Compose
- Node.js 22 LTS
- Python 3.12+ (optional locally if you prefer `uv`), or just run with `uvicorn` in a venv.

## 1) Start infrastructure
```bash
docker compose up -d
````

## 2) Backend setup

```bash
cd services/api
# copy env and edit secrets
cp .env.example .env
# create venv & install (uv recommended) — or use pip if you prefer
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r <(python - <<'PY'\nfrom pathlib import Path; import tomllib; d=tomllib.loads(Path('pyproject.toml').read_text()); print('\n'.join(d['project']['dependencies']))\nPY)
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

```
```
