# RideOps Support Case Study: Diagnosis, Solution & Plan

---

## 1. Diagnosis: What Is Driving the Problem?

### The headline
Open tickets are rising not because of unmanageable volume, but because **57% of escalations to engineering are avoidable**, and each unnecessary escalation adds 6-7× more resolution time.

### Evidence from the data (1,444 tickets, Jul–Sep 2026)

| Metric | July | August | September | Trend |
|--------|------|--------|-----------|-------|
| Tickets created | 390 | 462 | 592 | **+52%** |
| Escalated to eng | 146 (37%) | 151 (33%) | 189 (32%) | Volume ↑ even as rate ↓ |
| Still open (as of Sep 30) | — | — | 48 | **17 are Roster, 13 are GPS** |

### Three reinforcing loops are creating the backlog:

**Loop 1 — Avoidable Escalations Clog Engineering**
- 486 tickets were escalated (34% of total).
- Of those, **275 (57%) were returned** without a real fix: config issues (84), insufficient info (89), duplicates (56), not-a-bug/how-to (24), not reproducible (22).
- These clog engineering's queue, slowing down the tickets that actually need them.

**Loop 2 — Multi-Handoffs Multiply Delay**
- 229 escalated tickets (47%) bounced between L1 and engineering 2–3 times.
- Median resolution by handoff count: **1 handoff = 59h, 2 handoffs = 110h, 3 handoffs = 170h**.
- Root cause: insufficient information in the initial escalation → eng returns it → agent re-escalates with slightly more info → repeat.

**Loop 3 — Escalation Destroys Resolution Speed**
- Non-escalated tickets resolve in **13 hours median**.
- Escalated tickets take **87 hours median** — a 6.7× multiplier.
- This gap alone explains the growing open-ticket count.

### Supporting signals

- **CSAT tells the story**: Escalated tickets average **3.1/5 CSAT** vs **4.0/5** for non-escalated. Clients notice the difference.
- **10.5% reopen rate** (151 tickets) suggests premature closure — tickets closed without full resolution.
- **Agent variance is real**: Rahul T has a 62% escalation rate; Karan B has 16%. Both handle similar volumes and categories. This signals a training/process gap, not a volume gap.
- **Roster/booking** (24% of tickets, 51% escalation rate) and **GPS/tracking** (16%, 56% escalation rate) are the biggest category drivers.

### What Meera and Sandeep are both right about — and wrong about

- **Meera** says the problem is engineering turnaround. She's right that engineering is slow (87h median), but wrong that the fix is more people. 57% of what she sends to engineering shouldn't go there at all.
- **Sandeep** says support escalates too much without basic checks. He's right — 89 tickets came back as "insufficient info." But engineering could also reduce duplicates by flagging known issues proactively.

---

## 2. Defining Success

### Primary metric: Weekly avoidable escalation count
**Target: Reduce from ~21/week to <10/week within 4 weeks.**

This directly attacks the root cause. Fewer avoidable escalations → faster engineering throughput on real bugs → faster resolution → fewer open tickets → better CSAT.

### Supporting metrics (tracked weekly):

| Metric | Current Baseline | 4-Week Target | Why It Matters |
|--------|-----------------|---------------|----------------|
| Avoidable escalation rate | 57% of escalated | <35% | Core lever |
| Median resolution (escalated) | 87 hrs | <50 hrs | Direct client impact |
| Multi-handoff rate (2+ handoffs) | 47% of escalated | <25% | Eliminates bounce loops |
| Open ticket count | 48 | <30 | Leadership's KPI |
| Reopen rate | 10.5% | <7% | Quality of resolution |
| CSAT (escalated) | 3.1 | >3.5 | Client perception |

### Why this measure over "just reduce open tickets"
"Reduce open tickets" is an outcome, not a lever. You can game it by closing tickets prematurely (which increases reopens and kills CSAT). The avoidable escalation rate is the lever that naturally pulls down open tickets, resolution time, and CSAT all at once.

---

## 3. What I Built (v0)

### Tool: RideOps Support Intelligence Dashboard
**Target user: Support Lead (Meera) and L1 Agents**

A Streamlit-based internal dashboard with 6 pages:

| Page | Purpose |
|------|---------|
| **Executive Summary** | High-level metrics for Ritika's weekly review |
| **Root Cause Deep-Dive** | Escalation pipeline analysis, response time breakdown, handoff loops |
| **Agent Performance** | Per-agent escalation rates, response times, CSAT — surfaces coaching opportunities |
| **Client Health** | Risk-scored client list to prevent churn from at-risk accounts |
| **Escalation Triage Helper** | *The most impactful page.* Before escalating, an agent enters the category and keywords → sees similar past tickets and their outcomes. If 60%+ of similar escalations were returned, the tool warns: "Try resolving without escalation first." |
| **Open Tickets Queue** | Prioritized by urgency score (priority × age × tier × handoffs) |

### Why this tool and this user?
- Meera controls the escalation decision. If her team escalates smarter, the entire pipeline improves.
- The Escalation Triage Helper directly attacks the #1 root cause (avoidable escalations) with zero new hires.
- The Agent Performance page lets Meera coach the right people (Rahul T at 62% escalation rate vs Karan B at 16%).

### What actually runs
- Loads and processes all 1,444 tickets from CSV
- Computes derived metrics (resolution time, first response time, escalation outcomes, risk scores)
- Interactive filters (month, priority, tier)
- All charts are live Plotly visualizations
- Escalation Triage Helper does real keyword matching against historical data

---

## 4. Four-Week Plan

### Week 1: Quick wins + triage tool rollout
- [ ] Deploy the Escalation Triage Helper to L1 agents
- [ ] Create a simple escalation checklist: "Before escalating, confirm: (1) checked config, (2) checked known issues list, (3) gathered logs/screenshots"
- [ ] Share the Known Issues list with L1 (56 escalations were duplicates of known issues — these are immediately preventable)
- [ ] Start tracking avoidable escalation rate weekly

### Week 2: Agent coaching + process change
- [ ] 1:1 coaching for high-escalation agents (Rahul T, Ananya R) using the Agent Performance dashboard
- [ ] Pair high-escalation agents with low-escalation agents (Karan B, Vikram S) for 2 days
- [ ] Add mandatory fields to escalation form: steps to reproduce, config verified (Y/N), screenshots attached (Y/N)
- [ ] Engineering creates a "known issues" status page updated weekly

### Week 3: Structural improvements
- [ ] Build auto-tagging: when a ticket matches a known issue pattern, pre-fill the resolution template
- [ ] Add SLA targets to the dashboard (P1: 1h response, P2: 4h, P3: 8h) with breach alerts
- [ ] Create category-specific resolution guides for top 3 categories (Roster, GPS, Reports)
- [ ] Review and close stale open tickets with client communication

### Week 4: Measure and iterate
- [ ] Measure all KPIs against baseline
- [ ] Run a retrospective with Meera and Sandeep
- [ ] Decide: scale the triage tool to auto-suggest resolutions, or focus on further reducing handoffs?
- [ ] Present results to Ritika with before/after data

### What I would deliberately NOT do:
- **Not hire more agents.** The data shows a process problem, not a capacity problem. Ticket volume per agent (~180/quarter) is manageable if 57% of escalations stop happening.
- **Not build a customer-facing portal.** Internal process fixes have higher ROI right now. A client portal adds complexity without fixing the root cause.
- **Not automate ticket routing.** The problem isn't routing; it's that tickets are escalated that shouldn't be. Fix the decision, not the pipe.
- **Not invest in AI/NLP classification yet.** A simple checklist and historical lookup (the triage helper) captures 80% of the value. ML adds complexity and maintenance burden for marginal gain at this stage.

---

## Assumptions

1. The data is representative of normal operations (no major outages or one-time events skewing the numbers).
2. L1 agents currently have no structured decision support for escalation — they use judgment alone.
3. Engineering's capacity is fixed for the next quarter (no additional headcount).
4. The "config issue" and "not a bug" outcomes mean L1 could have resolved those tickets with better tooling/knowledge.
5. CSAT response rate (45%) is not systematically biased toward unhappy or happy clients.
