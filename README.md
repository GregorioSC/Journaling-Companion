# Journaling Companion
## Video link https://youtu.be/h-cVkfm81J8
A lightweight journaling app with an AI coach.  
Frontend: React + Vite + Tailwind + shadcn/ui  
Backend: FastAPI + SQLite + Hugging Face models (sentiment, embeddings) + KeyBERT/YAKE for themes.

---


## Quick Start

### Prereqs
- **Python 3.11** recommended
- **Node.js 20+** and **npm 10+**

> Tip: Create a Python virtual environment so your global site-packages don’t conflict:
> ```bash
> python -m venv .venv
> .\.venv\Scripts\activate   # Windows
> # source .venv/bin/activate  # macOS/Linux
> ```

---

## Backend

### 1) Install deps
From the **Palo Alto** folder:
```bash
pip install -r requirements.txt
```

### 2) Environment
Create a `.env` file in the backend root:

```
JWT_SECRET=replace-with-a-long-random-string
JWT_ALG=HS256
DB_PATH=./my_db.sqlite
```

### 3) Run the API
```bash
uvicorn main:app --reload
```

API: **http://localhost:8000**  
Docs: **http://localhost:8000/docs**

---

## Frontend

### 1) Install deps
From the **journal-frontend** folder:
```bash
npm install
```

### 2) Environment
Create `./journal-frontend/.env`:

```
VITE_API_BASE=http://localhost:8000
```

### 3) Run the frontend
```bash
npm run dev
```

Dev server: **http://localhost:5173**

---


## Running the Full App

1. **Start backend**:
   ```bash
   cd Palo Alto
   uvicorn main:app --reload
   ```
2. **Start frontend**:
   ```bash
   cd journal-frontend
   npm run dev
   ```
3. Visit **http://localhost:5173** and log in / register.  
   Create entries, click **Analyze with AI**, try **Ask AI** and **Summarize week**.

---



