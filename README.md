# TNEA Backend API

Express.js backend for TNEA college admission data.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create .env file:
```bash
cp .env.example .env
```

3. Update .env with your database credentials

4. Start server:
```bash
npm start
```

For development:
```bash
npm run dev
```

## API Endpoints

- POST /api/fetch_data
- POST /api/districts
- GET /api/college_type
- GET /api/get_branch_category
- GET /api/get_branch
- GET /api/get_year
- GET /api/get_region
- GET /api/get_category

## Environment Variables

- DATABASE_HOST
- DATABASE_USER
- DATABASE_PASSWORD
- DATABASE_NAME
- DATABASE_PORT
- CACHE_URL
- PORT
