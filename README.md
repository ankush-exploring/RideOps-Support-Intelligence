# RideOps Support Intelligence Dashboard

## Quick Start

```bash
pip install pandas streamlit plotly openpyxl
streamlit run app.py
```

The app will open at `http://localhost:8501`. All data is loaded from `rideops_support_tickets.csv` in the same directory.

## What This Is

A working internal tool built for the **Support Lead** and **Head of Operations** at RideOps. It answers one question: *why are open tickets rising, and what can we do about it without hiring?*

## What It Does

| Page | Who It's For | What It Shows |
|------|-------------|---------------|
| **Executive Summary** | Ritika (Head of Ops) | Top-line metrics, volume trends, escalation breakdown |
| **Root Cause Deep-Dive** | Ritika + Meera | The three reinforcing loops driving the backlog |
| **Agent Performance** | Meera (Support Lead) | Per-agent escalation rates, response times, CSAT |
| **Client Health** | Meera / Account Managers | At-risk clients ranked by composite risk score |
| **Escalation Triage Helper** | L1 Agents | Before escalating: see similar past tickets and outcomes |
| **Open Tickets Queue** | Meera / L1 Agents | Prioritized action queue with urgency scoring |

## Key Finding

**57% of escalations are avoidable.** Each unnecessary escalation adds ~87 hours (median) to resolution vs 13 hours for non-escalated tickets. The fix is not more people — it's fewer bad escalations.

## Files

- `app.py` — Streamlit dashboard (the v0 build)
- `analysis.py` — Data analysis script (generates diagnostic numbers)
- `rideops_support_tickets.csv` — Raw ticket data (1,444 tickets)
- `rideops_data_dictionary.csv` — Column definitions
- `writeup.md` — 4-page case study write-up

## Built With

Python · Pandas · Streamlit · Plotly
