# Gokul's Astrological Insights — Frontend

The modern, responsive web application for **Gokul's Astrological Insights (GAI)**, built with **Next.js 16 (App Router)**, **React 19**, and **Tailwind CSS v4**.

> For full-system architecture, backend setup, database migrations, and ephemeris details, please refer to the master [Root README.md](../README.md).

---

## Overview & UI Architecture

- **Framework**: Next.js 16.4.2 (App Router with Partial Prerendering and Turbopack)
- **UI Library**: React 19.3.0 with Lucide React 1.59.0 icons
- **Styling**: Tailwind CSS v4 with custom warm astrological color palette (ivory/cream surfaces, antique-gold accents, deep navy typography)
- **Authentication**: `@supabase/ssr` with secure cookie-based session management and middleware route protection
- **Internationalization**: Native bilingual dictionary (English & தமிழ்) supporting full astrological terminology
- **Charts & Visualization**: Interactive vector SVG chart renderers supporting both **South Indian (4x4 square grid)** and **North Indian (Diamond / Bhava-centric)** chart formats

---

## Frontend Setup & Running

### 1. Environment Configuration

Copy the example environment template to `.env.local`:

```bash
cp .env.example .env.local
```

Ensure the following variables are configured in `.env.local`:

```ini
# Public Supabase credentials (used by client & SSR)
NEXT_PUBLIC_SUPABASE_URL=https://<your-project-id>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-anon-publishable-key>

# Server-only credentials (used by API route handlers & admin operations)
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-secret-key>

# Administrator bootstrap variables (used by `npm run bootstrap:admin`)
ADMIN_USERNAME=gokul_admin
ADMIN_EMAIL=admin@your-astrology-domain.com
ADMIN_INITIAL_PASSWORD=YourSecureInitialPassword#2026

# FastAPI backend calculation service
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run Development Server

The development server runs on port `3001` (configured via `package.json`):

```bash
npm run dev
```

Visit [http://127.0.0.1:3001](http://127.0.0.1:3001) in your browser.

---

## Available NPM Scripts

| Script | Command | Purpose |
|---|---|---|
| `npm run dev` | `next dev --hostname 127.0.0.1 --port 3001` | Starts the Next.js local development server with Turbopack. |
| `npm run build` | `next build` | Creates an optimized production build. |
| `npm run start` | `next start --hostname 127.0.0.1 --port 3001` | Starts the production server. |
| `npm run lint` | `eslint` | Runs ESLint diagnostic checks. |
| `npm run type-check` | `tsc --noEmit` | Runs strict TypeScript type checking. |
| `npm run bootstrap:admin` | `node --env-file=.env.local scripts/bootstrap-admin.mjs` | Provisions the initial administrator account in Supabase. |
| `npm test` | Runs core chart correctness, dasa hierarchy, and auth test scripts. | Executes frontend test suite. |
| `npm run test:auth` | Runs auth integration & live Supabase verification scripts. | Validates auth and RLS rules. |
| `npm run test:scenarios` | Runs login and role access scenario tests. | Verifies user journeys. |
| `npm run test:d1-d9` | Tests D1 Rasi and D9 Navamsa rendering pipelines. | Chart transform test. |
| `npm run test:transit-watch` | Tests real-time planetary transit watchers. | Transit timeline test. |
| `npm run test:dosha` | Tests Kuja, Kaal Sarp, and Sadesati UI components. | Dosha UI verification. |
| `npm run test:marriage-prediction`| Tests marriage compatibility and synastry components. | Compatibility test. |
| `npm run test:medical-astrology` | Tests Ayurvedic dosha and anatomical vulnerability tools. | Medical engine test. |

---

## API Proxy & Rewrites

In development and production, the Next.js application automatically proxies calculation requests to the FastAPI backend service via `next.config.ts`:

- `/api/v1/:path*` $\longrightarrow$ `http://127.0.0.1:8000/api/v1/:path*`
- `/health` $\longrightarrow$ `http://127.0.0.1:8000/health`

For more information, see the [Root System Documentation](../README.md).
