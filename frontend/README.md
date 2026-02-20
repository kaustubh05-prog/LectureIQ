# LectureIQ — Frontend

React 18 + Vite + TailwindCSS single-page app for the LectureIQ AI learning platform.

---

## Structure

```
frontend/
├── public/
│   └── logo.svg
│
├── src/
│   ├── main.jsx              # Entry point — React root + Toaster
│   ├── App.jsx               # Router + PrivateRoute + page layout
│   ├── index.css             # Tailwind base + component classes
│   │
│   ├── pages/                # Route-level components
│   │   ├── HomePage.jsx      # Landing page
│   │   ├── LoginPage.jsx     # Email + password login
│   │   ├── SignupPage.jsx    # Registration form
│   │   ├── DashboardPage.jsx # Lecture list + status cards
│   │   ├── UploadPage.jsx    # Drag-and-drop audio upload
│   │   └── LectureDetailPage.jsx  # Notes / Flashcards / Quiz / Resources
│   │
│   ├── components/           # Reusable UI components
│   │   ├── Navbar.jsx
│   │   ├── LectureCard.jsx
│   │   ├── StatusBadge.jsx
│   │   ├── FlashcardViewer.jsx
│   │   ├── QuizRunner.jsx
│   │   ├── ResourceList.jsx
│   │   └── LoadingSkeleton.jsx
│   │
│   ├── services/             # API call functions
│   │   └── api.js            # Axios instance + auth interceptor + 401 handler
│   │
│   ├── store/                # Zustand global state
│   │   └── useAuthStore.js   # user, token, setAuth(), logout() — persisted
│   │
│   └── utils/
│       └── formatters.js     # Duration, date, file size formatters
│
├── .env                      # Local env vars (git-ignored)
├── .env.example              # Template
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

---

## Setup

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env — set VITE_API_URL to backend URL

# Start dev server
npm run dev
# → http://localhost:5173
```

### Environment Variables

| Variable       | Description           | Example                      |
|----------------|-----------------------|------------------------------|
| `VITE_API_URL` | Backend API base URL  | `http://localhost:8000`      |

For production (Vercel), set:

```
VITE_API_URL=https://api.lectureiq.app
```

---

## Pages

| Route           | Page                | Auth Required |
|-----------------|---------------------|---------------|
| `/`             | HomePage            | No            |
| `/login`        | LoginPage           | No            |
| `/signup`       | SignupPage          | No            |
| `/dashboard`    | DashboardPage       | Yes           |
| `/upload`       | UploadPage          | Yes           |
| `/lectures/:id` | LectureDetailPage   | Yes           |

Any unauthenticated access to a protected route redirects to `/login`.

---

## State Management

Zustand store (`useAuthStore`) persists `user` and `token` to `localStorage` under the key `lectureiq-auth`.

```javascript
import useAuthStore from './store/useAuthStore';

// Read
const token = useAuthStore((s) => s.token);
const user  = useAuthStore((s) => s.user);

// Write
const { setAuth, logout } = useAuthStore();
setAuth(user, token);   // after login
logout();               // clears state + localStorage
```

---

## API Client

`src/services/api.js` exports a pre-configured Axios instance:

```javascript
import api from './services/api';

// GET
const res = await api.get('/api/lectures');

// POST with JSON
const res = await api.post('/api/auth/login', { email, password });

// POST with file (multipart)
const form = new FormData();
form.append('file', file);
form.append('title', title);
const res = await api.post('/api/lectures/upload', form, {
  onUploadProgress: (e) => setProgress(Math.round(e.loaded / e.total * 100)),
});
```

JWT token is attached automatically via request interceptor. 401 responses automatically log the user out and redirect to `/login`.

---

## CSS Utility Classes

Custom component classes defined in `src/index.css`:

| Class            | Description                                   |
|------------------|-----------------------------------------------|
| `.btn-primary`   | Blue filled button with hover + disabled      |
| `.btn-secondary` | White outlined button                         |
| `.card`          | White rounded card with shadow                |
| `.input`         | Styled text input with focus ring             |
| `.badge`         | Small rounded status label                    |

---

## Build for Production

```bash
npm run build
# Output in dist/ — deploy to Vercel, Netlify, or any static host
```

---

## Deployment (Vercel)

1. Connect GitHub repo to Vercel
2. Set **Root Directory** → `frontend`
3. Set environment variable: `VITE_API_URL=https://api.lectureiq.app`
4. Vercel auto-detects Vite — no extra config needed
5. Every push to `main` auto-deploys

---

## Key Dependencies

| Package            | Purpose                              |
|--------------------|--------------------------------------|
| `react-router-dom` | Client-side routing                  |
| `zustand`          | Lightweight global state             |
| `axios`            | HTTP client with interceptors        |
| `react-dropzone`   | Drag-and-drop file upload            |
| `react-markdown`   | Render markdown notes                |
| `remark-gfm`       | GitHub Flavored Markdown in notes    |
| `react-hot-toast`  | Toast notifications                  |
| `tailwindcss`      | Utility-first CSS                    |