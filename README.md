# MarketFlow

MarketFlow is a cash-flow tracker for Nigerian market traders. The repo contains a Django backend API and a React/Vite frontend.

## Project Documentation

- [Project knowledge base](docs/PROJECT_KNOWLEDGE_BASE.md)
- [Backend reconstruction blueprint](docs/BACKEND_RECONSTRUCTION_BLUEPRINT.md)
- [Authentication implementation plan](docs/AUTHENTICATION_IMPLEMENTATION_PLAN.md)

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Optional environment variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_DATABASE_NAME`

## Frontend

```bash
cd cashflow_frontend
npm install
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000` in development.
MarketFlow uses `http://127.0.0.1:5174` for the frontend so it does not
silently attach to another Vite app already running on the default port.

Create or reset the local demo account and its sample grocery data with:

```bash
cd backend
python manage.py seed_demo
```

## Checks

```bash
cd backend
python manage.py test

cd ..\cashflow_frontend
npm run lint
npm run build
```
