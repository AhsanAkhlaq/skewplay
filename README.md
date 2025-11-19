# SkewPlay · Vue + Firebase shell

This `frontend/` workspace implements the first 10 % milestone for the SkewPlay platform:

- Vue 3 + TypeScript + Vite + Pinia + Vue Router
- Firebase Auth + Firestore + Storage bootstrap (modular SDK v10)
- Minimal, modern UI shell (Landing, Auth, Dashboard, Datasets, Workflows, Profile)
- CRUD flows covering UC-01/02/03/05/13 from the SRS

## Setup

```bash
cd frontend
cp env.example .env # fill with your Firebase keys
npm install
npm run dev
```

## Scripts

- `npm run dev` — start Vite dev server
- `npm run build` — type-check + production build
- `npm run preview` — preview built assets

## Firebase

The project expects a Firebase project with Authentication (Email/Password) and Firestore enabled. Firestore collections:

- `users` — created automatically on first register/login
- `datasets` — dataset metadata CRUD
- `workflows` — workflow stage tracker + experiment notes

Update Firestore security rules to restrict access to `request.auth.uid`. See `docs/SRS_analysis.md` for the detailed plan and next milestones.
