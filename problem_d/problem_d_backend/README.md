# Problem D Backend

NestJS backend for the demo SaaS site.

## Scripts

- `npm install`
- `npm run start:dev`
- `npm run build`
- `npm run start`

## API

Base URL: `http://localhost:4000/api`

## Database

The backend reads from a local SQLite file.

- Default path: `../problem_d_database/northwind_signal.sqlite`
- Override with `DB_PATH`

- `GET /health`
- `POST /auth/login`
- `GET /auth/me`
- `GET /projects`
- `POST /projects`
- `GET /organizations`
- `GET /billing/plans`
- `GET /billing/invoices`
- `GET /usage/summary`
- `GET /usage/audit`
