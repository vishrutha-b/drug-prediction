# 🚀 How to Run — IntelliInteraction DDI Platform

> **Good news:** The ML models are already trained and saved in `ml/models/`.  
> You **do not** need to retrain anything — just start the backend and frontend.

---

## ✅ Prerequisites

Make sure you have these installed on your machine:

| Tool | Version | Check Command |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

---

## ▶️ Option 1 — Run Locally (Recommended for Development)

### Step 1 — Open Terminal in Project Root

```powershell
cd "c:\Users\vishr\OneDrive\Documents\vishu backend\drug prediction"
```

---

### Step 2 — Set Up the Backend (FastAPI)

**Open a new terminal window and run:**

```powershell
# Go into the backend folder
cd backend

# Create a virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt
```

> ⚠️ If you get a script execution error, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### Step 3 — Seed the Database (First Time Only)

```powershell
# Still inside the backend folder with .venv active
python seed_db.py
```

This creates the SQLite database and a default test user:
- **Email:** `admin@example.com`
- **Password:** `password123`

---

### Step 4 — Start the Backend Server

```powershell
# Still inside the backend folder
uvicorn app.main:app --reload --port 8000
```

✅ Backend is now running at: **http://localhost:8000**  
📖 Swagger API Docs at: **http://localhost:8000/docs**

---

### Step 5 — Set Up and Start the Frontend (Next.js)

**Open a second terminal window:**

```powershell
# Go to the frontend folder
cd "c:\Users\vishr\OneDrive\Documents\vishu backend\drug prediction\frontend"

# Install Node.js dependencies (only first time)
npm install

# Start the development server
npm run dev
```

✅ Frontend is now running at: **http://localhost:3000**

---

### Step 6 — Open the App

Open your browser and go to:

```
http://localhost:3000
```

Login with:
- **Email:** `admin@example.com`
- **Password:** `password123`

---

## 🐳 Option 2 — Run with Docker (One Command)

If you have **Docker Desktop** installed and running:

```powershell
cd "c:\Users\vishr\OneDrive\Documents\vishu backend\drug prediction"

# Build and start the full platform
docker compose up --build -d
```

✅ Everything runs at: **http://localhost:8080**

To stop:
```powershell
docker compose down
```

---

## 🧪 Option 3 — Run a Quick API Test

With the backend running on port 8000, open a new terminal:

```powershell
cd "c:\Users\vishr\OneDrive\Documents\vishu backend\drug prediction"

# Run the test script
python scratch\test_api.py
```

Or test manually with curl:

```powershell
# Step 1: Login to get a token
curl -X POST http://localhost:8000/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email": "admin@example.com", "password": "password123"}'

# Step 2: Use the token to check a drug interaction
curl -X POST http://localhost:8000/predict/check-interaction `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <your_token_here>" `
  -d '{"drug_a": "Warfarin", "drug_b": "Aspirin"}'
```

---

## 📂 What's Already Ready (No Retraining Needed)

All ML model files are pre-trained and stored in `ml/models/`:

| File | Size | Description |
|---|---|---|
| `pairs_lookup.pkl` | 4.4 MB | 75,537 FAERS drug pair lookup dictionary |
| `xgb_model.pkl` | 4.9 MB | Trained XGBoost classifier |
| `catboost_model.pkl` | 1.3 MB | Trained CatBoost classifier |
| `drug_embeddings.pkl` | 1.6 MB | 64-dim GAT embeddings for ~14,000 drugs |
| `ddi_model.pkl` | 34 MB | Full DDI model artifact |
| `gat_weights.pt` | 0.5 MB | Best GAT checkpoint |
| `tfidf_vectorizer.pkl` | 6.5 KB | Fitted TF-IDF char n-gram vectorizer |
| `label_encoder.pkl` | 0.3 KB | Severity label encoder |
| `drug_node_map.pkl` | 116 KB | Drug name → graph node index map |

---

## 🔁 (Optional) Retrain the ML Models from Scratch

Only needed if you want to refresh the dataset from FDA FAERS:

```powershell
cd "c:\Users\vishr\OneDrive\Documents\vishu backend\drug prediction"

# Step 1: Fetch fresh FAERS data (needs internet)
python ml\pipeline\faers_fetcher.py

# Step 2: Run the full training pipeline
python ml\pipeline\run_full_pipeline.py
```

> ⏱️ Takes approximately **5–15 minutes** depending on network speed.  
> After retraining, restart the backend for new models to load.

---

## ❓ Common Issues & Fixes

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` on backend start | Make sure `.venv` is activated: `.venv\Scripts\Activate.ps1` |
| Port 8000 already in use | Change port: `uvicorn app.main:app --reload --port 8001` |
| Port 3000 already in use | Change port: `npm run dev -- --port 3001` |
| `pip install` fails on `torch_geometric` | Install manually: `pip install torch-geometric` |
| Frontend shows blank page | Make sure backend is running on port 8000 first |
| `seed_db.py` error | Run from inside the `backend/` folder with `.venv` active |
| Docker build fails | Make sure Docker Desktop is running and you have enough disk space |

---

## 📋 Quick Reference — All URLs

| Service | URL |
|---|---|
| Frontend (Dev) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Docker (Full Stack) | http://localhost:8080 |
