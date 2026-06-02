# ⚡ JARVIS — Innovation Intelligence

> *Your personal AI innovation companion. Input an idea, get a full business report.*

Built with Python + FastAPI backend and a single-file HTML frontend. No frameworks, no complex setup — just API keys and go.

---

## What It Does

You type an idea. Jarvis runs 7 automated stages:

| Stage | What happens |
|-------|-------------|
| 1 · Score | Claude scores your idea 1-10. If unclear, asks 3 follow-up questions |
| 2 · Originality | Checks against your past ideas for similarity |
| 3 · Market Research | Market landscape, competitors, TAM/SAM/SOM, strategic fit |
| 4 · Validation | Business Model Canvas, validation scorecard, improvement suggestions |
| 5 · Deep Dive | JTBD, Blue Ocean, gap analysis, risk assessment |
| 6 · Summary | Full evaluation summary + co-founder profile recommendations |
| 7 · Action Plan | 30/60/90-day roadmap, prototype recommendation, next steps |

Report is saved to your Idea Vault with a unique ID you can revisit anytime.

---

## Quick Start (5 steps)

### Step 1 — Get your Anthropic API key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Click **API Keys → Create Key**
3. Copy the key (starts with `sk-ant-...`)

### Step 2 — Set up the backend
Open your terminal and run:

```bash
# Navigate to the backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Copy the environment file
cp .env.example .env
```

Then open `.env` in any text editor and paste your Anthropic key:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3 — Start the backend
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4 — Open the frontend
Open `frontend/index.html` in your browser (just double-click the file).

### Step 5 — Submit your first idea
Type your name, describe your idea, click **⚡ Launch Analysis**. Done.

---

## Optional: Supabase (persistent storage)

By default Jarvis saves everything to local JSON files in `backend/data/`. This is fine for personal use.

If you want cloud storage (so reports survive restarts and sync across devices):

1. Go to [supabase.com](https://supabase.com) and create a free project
2. In the SQL Editor, run this to create the tables:

```sql
create table ideas (
  id uuid primary key default gen_random_uuid(),
  user_id text,
  user_name text,
  idea_title text,
  idea_description text,
  score int,
  date_submitted timestamptz default now()
);

create table reports (
  report_id text primary key,
  user_id text,
  idea_title text,
  idea_raw text,
  user_name text,
  idea_score int,
  final_score int,
  stage1 text,
  stage2 text,
  bmc text,
  validation text,
  suggestions text,
  deep_dive text,
  summary text,
  cofounder text,
  action_plan text,
  verdict text,
  created_at timestamptz default now()
);

create table improvements (
  id uuid primary key default gen_random_uuid(),
  report_id text,
  user_id text,
  improvements text,
  assessment text,
  created_at timestamptz default now()
);
```

3. Copy your project URL and anon key into `.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

---

## Deploy to Railway (so it runs 24/7)

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select the `backend` folder as the root
4. Add environment variables: `ANTHROPIC_API_KEY`, and optionally Supabase keys
5. Railway auto-detects the `Procfile` and deploys

Once deployed, update the API URL in `frontend/index.html`:
```js
const API = 'https://your-project.railway.app';
```

---

## File Structure

```
Jarvis/
├── backend/
│   ├── main.py           ← FastAPI app, all routes
│   ├── pipeline.py       ← 7-stage orchestrator
│   ├── database.py       ← Supabase + local JSON storage
│   ├── config.py         ← API keys + Anthropic client
│   ├── requirements.txt
│   ├── .env.example      ← Copy to .env and fill in keys
│   ├── Procfile          ← Railway deployment
│   └── agents/
│       ├── scorer.py     ← Stage 1: Idea scoring (Haiku)
│       ├── researcher.py ← Stage 3: Market research (Sonnet)
│       ├── validator.py  ← Stage 4: BMC + Scorecard + Suggestions
│       ├── deep_dive.py  ← Stage 5: Innovation frameworks
│       ├── summary.py    ← Stage 6a: Evaluation summary
│       ├── cofounder.py  ← Stage 6b: Co-founder profiles
│       ├── action_plan.py← Stage 7: 30/60/90 plan
│       └── improvement.py← Bonus: Progress assessment
└── frontend/
    └── index.html        ← Full Iron Man UI (single file)
```

---

## API Endpoints

| Method | Path | What it does |
|--------|------|-------------|
| POST | `/api/submit` | Submit a new idea → returns `job_id` |
| POST | `/api/submit/refined` | Submit refined idea with Q&A answers |
| POST | `/api/submit/proceed` | Proceed past similarity warning |
| GET | `/api/status/{job_id}` | Poll pipeline progress |
| GET | `/api/reports` | List all your past reports |
| GET | `/api/reports/{id}` | Fetch a specific report |
| POST | `/api/improve` | Submit improvements for re-evaluation |

---

## Models Used

| Agent | Model | Why |
|-------|-------|-----|
| Idea Scorer | claude-haiku-4-5 | Fast + cheap for scoring |
| All other agents | claude-sonnet-4-6 | Best quality for research & analysis |

---

*Built by Zuyu · Inspired by Tony Stark's JARVIS*
