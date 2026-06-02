# ⚡ JARVIS — Product Blueprint
> *"Sometimes you gotta run before you can walk."* — Tony Stark

**Version:** 0.1 — Planning & Framework  
**Date:** May 2026  
**Author:** Zuyu + Claude

---

## 1. What Is Jarvis?

Jarvis is a personal AI-powered innovation companion. You give it a raw idea — as rough or developed as it is — and it walks you through the full innovation process: scoring, researching, validating, stress-testing, and producing a complete business report. Think of it as a co-founder in your pocket, available 24/7, who never gets tired and always challenges your thinking.

**Inspired by:** Tony Stark's JARVIS — conversational, intelligent, proactive, and brutally honest.

**Core Promise:** *From raw idea to investor-ready insight in under 5 minutes.*

---

## 2. Who It's For

| User | Need |
|------|------|
| You (primary) | A thinking partner for every idea, available immediately |
| Future users | Anyone who generates ideas and needs a structured way to evaluate them |

The product is designed as a **personal tool first**, scalable to a product later.

---

## 3. The Full Pipeline (7 Stages)

### Stage 0 — Idea Intake
The user opens Jarvis, types (or speaks) their raw idea. Jarvis acknowledges it in a conversational way. Behind the scenes:
- User is authenticated (Supabase Auth)
- A new session is created and logged (session ID, timestamp)
- The message is saved to the messages table

**Input fields:** Idea text (required), optionally title

---

### Stage 1 — Idea Scoring & Clarification
Jarvis scores the idea on four dimensions using Claude AI:
- **Clarity** — Is the problem and solution well-defined?
- **Relevance** — Does it address a real problem?
- **Feasibility** — Can it realistically be built?
- **Originality** — Does it bring something new?

**Scoring logic:**
- Score 1–10 returned as JSON
- **Score ≥ 5 → PASS** → proceeds to Stage 2
- **Score < 5 → FOLLOWUP** → Jarvis asks 3 specific clarifying questions
- User answers questions → idea is re-scored with enriched context
- Refined submissions almost always score ≥ 5

**Output:** `ideaScore`, `ideaStatus`, `followupQuestions`

---

### Stage 2 — Originality Check
Jarvis checks the new idea against your personal idea vault (all past ideas you've submitted):
- Uses keyword-based similarity matching (NLP, Jaccard similarity)
- **Threshold: 40% overlap = SIMILAR**
- If SIMILAR: Jarvis flags it, shows the previous similar idea, and asks whether to proceed or merge/revise
- If UNIQUE: saves to idea vault and continues

**Why this matters:** Prevents you from re-doing work; surfaces connections between your ideas.

**Output:** `similarityScore`, `similarityStatus`, `matchedIdea`

---

### Stage 3 — Market Research (Stage 1 Report)
Jarvis conducts deep market research using web search + AI synthesis. Runs four parallel threads:

1. **Market Landscape** — What trends are driving this space? What's the macro context?
2. **Market Sizing** — TAM (Total Addressable Market), SAM (Serviceable Available Market), SOM (Serviceable Obtainable Market)
3. **Competitor Map** — Who already exists? What are the gaps? How are they positioned?
4. **Strategic Fit** — Is now the right time? Does this fit the market timing?

**Output:** Stage 1 Report (structured text, 800–1500 words)

---

### Stage 4 — Business Validation (Stage 2 Report)
Jarvis builds a full business validation package:

1. **Business Model Canvas (BMC)** — All 9 blocks (Customer Segments, Value Proposition, Channels, Customer Relationships, Revenue Streams, Key Resources, Key Activities, Key Partners, Cost Structure)
2. **Validation Scorecard** — Scores on: Strategic Fit, Financial Viability, Team Fit, Market Readiness
3. **Improvement Suggestions** — 3–5 specific ways to make the idea stronger

**Output:** Stage 2 Report with BMC, Scorecard, and Suggestions sections

---

### Stage 5 — Innovation Deep Dive *(NEW — not in original n8n flow)*
This is what makes Jarvis more than a scoring tool — it walks you through the innovation process:

1. **Gap Analysis** — What skills, resources, or knowledge is missing to build this?
2. **Innovation Frameworks** — Applies 1–2 relevant frameworks:
   - *Jobs to Be Done (JTBD)* — What job is the customer hiring this to do?
   - *Blue Ocean Strategy* — Is there a way to create uncontested market space?
   - *Design Thinking* — How would a human-centered approach change the solution?
3. **Risk Assessment** — Top 3 risks and mitigation strategies for each

**Output:** Deep Dive Report section (new section added to final report)

---

### Stage 6 — Team Matching & Summary
Two agents run in parallel:

**Summary Agent** — Reads all previous stage outputs and compiles one cohesive evaluation summary:
- Founder info
- One-line idea summary
- Key findings (market, validation, strategic fit, financial viability)
- Skill gaps
- Critical issues
- Verdict

**Co-Founder / Team Match Agent** — Looks at the skill gaps and suggests:
- For now: best roles/profiles to hire or partner with
- In the future: can connect to your contacts/network to suggest real people

---

### Stage 7 — Action Plan & Output *(NEW — not in original n8n flow)*

1. **Action Plan** — A 30/60/90-day roadmap:
   - What to do in the next 30 days to validate the idea
   - What to build in 60 days (MVP or prototype spec)
   - What to achieve by 90 days (traction metrics or decision point)
2. **Full Report** — Saved to Supabase with a unique Report ID (e.g., `RPT-X7K2MN`)
3. **Push Notification** — Mobile app notifies the user when the report is ready
4. **Share Link** — Each report gets a shareable URL

---

## 4. Tech Stack (No-Code Friendly)

Since the goal is to build without deep coding knowledge, here's the recommended stack — each tool either has a visual interface or can be managed by Claude:

| Layer | Tool | Why |
|-------|------|-----|
| **Frontend (Web)** | Lovable.dev or Bolt.new | AI-generated React web app, no code needed |
| **Mobile (iOS + Android)** | Expo / React Native | One codebase for both platforms |
| **Backend API** | Python + FastAPI | Claude writes and maintains this; hosted on Railway |
| **Database** | Supabase | Visual dashboard, no SQL needed, same as n8n flow |
| **AI** | Anthropic Claude API | claude-sonnet-4-5 for agents, claude-haiku-4-5 for scoring |
| **Web Search** | Tavily API or Perplexity API | Real-time research for Stage 3 |
| **Authentication** | Supabase Auth | Built-in, simple email/password or Google login |
| **Hosting (API)** | Railway.app | One-click deploy, no server management |
| **Hosting (Web)** | Vercel | Free tier, instant deploy from GitHub |
| **Notifications** | Expo Push Notifications | Free, cross-platform |

**Total estimated monthly cost (personal use):**
- Supabase: Free tier
- Railway: ~$5/month
- Vercel: Free
- Claude API: ~$10–30/month depending on usage
- Tavily: Free tier (1,000 searches/month)
- **Total: ~$15–35/month**

---

## 5. Database Schema (Supabase)

### `users` table
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | Primary key |
| email | text | Login email |
| name | text | Display name |
| created_at | timestamp | |

### `sessions` table
| Column | Type | Notes |
|--------|------|-------|
| session_id | text | `SES-{timestamp}` |
| user_id | uuid | Foreign key → users |
| started_at | timestamp | |
| idea_raw | text | Original input |

### `ideas` table
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | |
| user_id | uuid | |
| idea_title | text | First 80 chars |
| idea_description | text | Full idea text |
| score | int | 1–10 |
| date_submitted | date | |

### `reports` table
| Column | Type | Notes |
|--------|------|-------|
| report_id | text | `RPT-XXXXXX` |
| user_id | uuid | |
| session_id | text | |
| idea_title | text | |
| stage1 | text | Market research report |
| stage2 | text | Business validation report |
| bmc | text | Business Model Canvas |
| validation | text | Scorecard |
| suggestions | text | Improvement suggestions |
| deep_dive | text | Innovation deep dive (NEW) |
| action_plan | text | 30/60/90 plan (NEW) |
| cofounder | text | Team match analysis |
| final_score | int | |
| verdict | text | |
| created_at | timestamp | |

### `messages` table
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | |
| session_id | text | |
| user_id | uuid | |
| role | text | 'user' or 'assistant' |
| content | text | |
| timestamp | timestamp | |

---

## 6. AI Agent Definitions

### Agent 1: Idea Scorer
- **Model:** claude-haiku-4-5 (fast, cheap)
- **Input:** Raw idea text
- **Output:** JSON `{score, reason, status, questions}`
- **System prompt key points:** Scores on clarity/relevance/feasibility/originality; returns PASS or FOLLOWUP with 3 specific questions

### Agent 2: Market Research Agent
- **Model:** claude-sonnet-4-5
- **Tools:** Web search (Tavily)
- **Input:** Idea text
- **Output:** Stage 1 Report (market landscape, sizing, competitors, strategic fit)

### Agent 3: Business Validation Agent
- **Model:** claude-sonnet-4-5
- **Input:** Idea text + Stage 1 Report
- **Output:** Stage 2 Report (BMC, scorecard, improvement suggestions)

### Agent 4: Innovation Coach Agent *(NEW)*
- **Model:** claude-sonnet-4-5
- **Input:** Idea text + Stage 1 + Stage 2 Reports
- **Output:** Deep Dive (gap analysis, frameworks, risk assessment)

### Agent 5: Summary Agent
- **Model:** claude-sonnet-4-5
- **Input:** All previous stage outputs
- **Output:** Evaluation summary

### Agent 6: Co-Founder Match Agent
- **Model:** claude-sonnet-4-5
- **Input:** Summary (skill gaps section)
- **Output:** Team match analysis with role profiles

### Agent 7: Action Plan Agent *(NEW)*
- **Model:** claude-sonnet-4-5
- **Input:** Full evaluation
- **Output:** 30/60/90-day action plan

---

## 7. Build Phases

### Phase 1 — Core MVP (Web Only) · ~4 weeks
**Goal:** Fully working web app with the complete pipeline

**What gets built:**
- User auth (login/signup)
- Idea input form
- Full 7-stage pipeline (backend API)
- Report view page
- Idea history/vault

**Tools:** Lovable.dev for frontend, Python + FastAPI on Railway for backend, Supabase for data

**Definition of done:** You can input an idea and get a full report in the browser.

---

### Phase 2 — Polish & Memory · ~2 weeks
**Goal:** Make it feel like Jarvis, not just a form

**What gets added:**
- Conversational UI (chat-style interface)
- Idea timeline / history view
- Report comparison (if same idea is re-submitted after improvements)
- Improvement scoring: "Your revised idea scored 2 points higher — here's why"
- Shareable report links

---

### Phase 3 — Mobile Apps · ~3 weeks
**Goal:** iOS and Android app

**What gets built:**
- React Native app using Expo
- Mirrors full web functionality
- Voice-to-text idea input (type OR speak your idea)
- Push notifications when report is ready
- Offline-first idea drafts

**App stores:** Apple App Store + Google Play Store

---

### Phase 4 — Advanced Features · ongoing
**Ideas for later:**
- Connect to your contacts/LinkedIn for real co-founder matching
- Pitch deck generator (auto-generate slides from report)
- Investor match (find relevant investors for your idea)
- Team mode (invite collaborators to work on an idea together)
- Idea tournament (compare two ideas head-to-head)

---

## 8. UI/UX Direction

**Design philosophy:** Dark, sleek, Iron Man-esque. Think JARVIS HUD — deep blues, subtle neon accents, clean typography.

**Key screens:**
1. **Home / Dashboard** — Your recent ideas, quick submit button
2. **Idea Input** — Minimal, single text field, "Tell Jarvis your idea..."
3. **Processing View** — Live progress through the 7 stages (with stage names + indicators)
4. **Report View** — Full report with collapsible sections per stage
5. **Idea Vault** — All past ideas with scores and verdicts
6. **Profile** — Account settings

**Color palette:**
- Background: `#0a0e1a` (deep navy)
- Primary: `#5b8aff` (electric blue)
- Accent: `#fbbf24` (gold/amber)
- Success: `#6ee7b7` (mint green)
- Danger: `#fca5a5` (soft red)

---

## 9. What We're Building vs. The n8n Flow

| n8n Component | Jarvis Equivalent | Change |
|---------------|-------------------|--------|
| Main Webhook | FastAPI POST `/api/ideas` | Same logic, independent |
| Employee Validation | Supabase Auth | Simplified for personal use |
| Google Sheets (ideas) | Supabase `ideas` table | Upgraded to proper DB |
| Google Sheets (employees) | Supabase `contacts` table | User's own network |
| LinkedIn Scraper | Optional: manual input | Simplified |
| Idea Scorer Agent | Same, Agent 1 | Identical |
| Follow-up loop | Same | Identical |
| Similarity Check | Same algorithm | Runs against personal vault |
| Stage 1 Research | Same + web search | Enhanced with Tavily |
| Stage 2 Validation | Same | Identical |
| Summary Agent | Same | Identical |
| Co-Founder Agent | Updated for personal network | Enhanced |
| Report Save | Supabase `reports` table | Upgraded from Google Sheets |
| — | Innovation Deep Dive | **NEW** |
| — | Action Plan (30/60/90) | **NEW** |
| — | Mobile app | **NEW** |
| — | Push notifications | **NEW** |

---

## 10. Next Steps

When you're ready to build, here's the order of operations:

1. **Set up Supabase** — Create project, build tables (Claude can do this with you)
2. **Get API keys** — Anthropic (Claude), Tavily (search), Supabase
3. **Build backend** — Claude writes the Python FastAPI backend
4. **Build web frontend** — Use Lovable.dev with Claude's guidance
5. **Test full pipeline** — Submit a real idea and walk through every stage
6. **Build mobile** — Convert to React Native with Expo
7. **Deploy** — Railway (API) + Vercel (web) + App stores (mobile)

---

*Blueprint prepared by Jarvis Planning Session · May 2026*
