# MarketFlow Frontend

React, TypeScript, Vite, and Tailwind frontend for MarketFlow.

## Setup

```bash
npm install
npm run dev
```

The Vite dev server runs on `http://127.0.0.1:5174` and proxies `/api` to
`http://127.0.0.1:8000`, so run the Django backend alongside it.

## Scripts

```bash
npm run dev
npm run build
npm run lint
npm run preview
```

## Environment

Set `VITE_API_BASE_URL` only when the API is not served from `/api`.
