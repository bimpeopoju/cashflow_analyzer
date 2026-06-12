# MarketFlow

MarketFlow is a cash-flow tracker for Nigerian market traders. The repo contains a Django backend API and a React/Vite frontend.

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
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

## Checks

```bash
cd backend
python manage.py test

cd ..\cashflow_frontend
npm run lint
npm run build
```
