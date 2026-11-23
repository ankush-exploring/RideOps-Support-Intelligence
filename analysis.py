"""
RideOps Support Ticket Data Analysis
Generates all diagnostic insights for the case study submission.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Load data
df = pd.read_csv('rideops_support_tickets.csv')

# Parse dates
date_cols = ['created_at', 'first_response_at', 'first_closed_at', 'final_closed_at']
for col in date_cols:
    df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce')

# Derived columns
df['month'] = df['created_at'].dt.to_period('M')
df['week'] = df['created_at'].dt.isocalendar().week
df['year_week'] = df['created_at'].dt.strftime('%Y-W%U')
df['first_response_hrs'] = (df['first_response_at'] - df['created_at']).dt.total_seconds() / 3600
df['resolution_hrs'] = (df['final_closed_at'] - df['created_at']).dt.total_seconds() / 3600
df['is_escalated'] = df['escalated_to_eng'] == 'Yes'
df['is_open'] = df['status'] != 'Closed'
df['has_reopened'] = df['reopen_count'] > 0

print("=" * 70)
print("RIDEOPS SUPPORT TICKET ANALYSIS")
print("=" * 70)

# --- 1. VOLUME TRENDS ---
print("\n1. TICKET VOLUME BY MONTH")
print("-" * 40)
monthly = df.groupby('month').agg(
    total=('ticket_id', 'count'),
    escalated=('is_escalated', 'sum'),
    reopened=('has_reopened', 'sum'),
).reset_index()
print(monthly.to_string(index=False))

# Weekly trend
weekly = df.groupby('year_week').size().reset_index(name='count')
print(f"\nWeekly avg July: {df[df['created_at'].dt.month == 7].groupby('year_week').size().mean():.0f}")
print(f"Weekly avg Aug: {df[df['created_at'].dt.month == 8].groupby('year_week').size().mean():.0f}")
print(f"Weekly avg Sep: {df[df['created_at'].dt.month == 9].groupby('year_week').size().mean():.0f}")

# --- 2. OPEN TICKETS ---
print("\n2. OPEN TICKETS (as of 30 Sep 2026)")
print("-" * 40)
open_tickets = df[df['is_open']]
print(f"Total open: {len(open_tickets)}")
print(f"Open by priority:\n{open_tickets['priority'].value_counts().to_string()}")
print(f"\nOpen by category:\n{open_tickets['category'].value_counts().to_string()}")
print(f"\nOpen by client_tier:\n{open_tickets['client_tier'].value_counts().to_string()}")

# Age of open tickets
cutoff = pd.Timestamp('2026-09-30')
open_tickets = open_tickets.copy()
open_tickets['age_days'] = (cutoff - open_tickets['created_at']).dt.total_seconds() / 86400
print(f"\nOpen ticket age: median={open_tickets['age_days'].median():.1f}d, max={open_tickets['age_days'].max():.1f}d")
print(f"Open > 7 days: {(open_tickets['age_days'] > 7).sum()}")
print(f"Open > 14 days: {(open_tickets['age_days'] > 14).sum()}")

# --- 3. ESCALATION ANALYSIS ---
print("\n3. ESCALATION ANALYSIS")
print("-" * 40)
esc = df[df['is_escalated']]
print(f"Total escalated: {len(esc)} ({len(esc)/len(df)*100:.1f}%)")
print(f"\nEscalation rate by month:")
esc_monthly = df.groupby('month').agg(
    total=('ticket_id', 'count'),
    escalated=('is_escalated', 'sum')
).reset_index()
esc_monthly['esc_rate'] = (esc_monthly['escalated'] / esc_monthly['total'] * 100).round(1)
print(esc_monthly.to_string(index=False))

print(f"\nEng outcome distribution:")
print(esc['eng_outcome'].value_counts().to_string())

# Unnecessary escalations
unnecessary = esc[esc['eng_outcome'].isin(['Config issue - returned to L1', 'Not a bug - how-to', 'Insufficient info - returned to L1', 'Duplicate of known issue', 'Not reproducible'])]
print(f"\nUnnecessary/avoidable escalations: {len(unnecessary)} ({len(unnecessary)/len(esc)*100:.1f}% of all escalations)")
print(f"Breakdown:")
print(unnecessary['eng_outcome'].value_counts().to_string())

# Escalation by category
print(f"\nEscalation rate by category:")
cat_esc = df.groupby('category').agg(
    total=('ticket_id', 'count'),
    escalated=('is_escalated', 'sum')
).reset_index()
cat_esc['esc_rate'] = (cat_esc['escalated'] / cat_esc['total'] * 100).round(1)
cat_esc = cat_esc.sort_values('esc_rate', ascending=False)
print(cat_esc.to_string(index=False))

# --- 4. RESOLUTION TIME ---
print("\n4. RESOLUTION TIME ANALYSIS")
print("-" * 40)
closed = df[df['status'] == 'Closed'].copy()
print(f"Median resolution time: {closed['resolution_hrs'].median():.1f} hrs")
print(f"Mean resolution time: {closed['resolution_hrs'].mean():.1f} hrs")
print(f"90th percentile: {closed['resolution_hrs'].quantile(0.9):.1f} hrs")

print(f"\nResolution time by escalation status:")
print(f"  Non-escalated median: {closed[~closed['is_escalated']]['resolution_hrs'].median():.1f} hrs")
print(f"  Escalated median: {closed[closed['is_escalated']]['resolution_hrs'].median():.1f} hrs")

print(f"\nResolution time by priority (median hrs):")
for p in ['P1', 'P2', 'P3', 'P4']:
    subset = closed[closed['priority'] == p]
    print(f"  {p}: {subset['resolution_hrs'].median():.1f} hrs (n={len(subset)})")

# --- 5. FIRST RESPONSE TIME ---
print("\n5. FIRST RESPONSE TIME ANALYSIS")
print("-" * 40)
print(f"Median first response: {df['first_response_hrs'].median():.1f} hrs")
print(f"Mean first response: {df['first_response_hrs'].mean():.1f} hrs")
print(f"90th percentile: {df['first_response_hrs'].quantile(0.9):.1f} hrs")

print(f"\nFirst response by priority:")
for p in ['P1', 'P2', 'P3', 'P4']:
    subset = df[df['priority'] == p]
    print(f"  {p}: median={subset['first_response_hrs'].median():.1f} hrs, >4hrs={((subset['first_response_hrs'] > 4).sum()/len(subset)*100):.0f}%")

# --- 6. AGENT PERFORMANCE ---
print("\n6. AGENT PERFORMANCE")
print("-" * 40)
agent_stats = df.groupby('assigned_agent').agg(
    tickets=('ticket_id', 'count'),
    escalated=('is_escalated', 'sum'),
    median_response_hrs=('first_response_hrs', 'median'),
    median_resolution_hrs=('resolution_hrs', 'median'),
    reopened=('has_reopened', 'sum'),
    avg_csat=('csat_score', 'mean')
).reset_index()
agent_stats['esc_rate'] = (agent_stats['escalated'] / agent_stats['tickets'] * 100).round(1)
agent_stats['reopen_rate'] = (agent_stats['reopened'] / agent_stats['tickets'] * 100).round(1)
print(agent_stats.to_string(index=False))

# --- 7. MULTI-HANDOFF TICKETS ---
print("\n7. ENGINEERING HANDOFF ANALYSIS")
print("-" * 40)
multi_handoff = esc[esc['eng_handoffs'] > 1]
print(f"Tickets with >1 handoff: {len(multi_handoff)} ({len(multi_handoff)/len(esc)*100:.1f}% of escalated)")
print(f"Handoff distribution:")
print(esc['eng_handoffs'].value_counts().sort_index().to_string())

print(f"\nResolution time by handoffs (median hrs):")
for h in sorted(esc['eng_handoffs'].unique()):
    subset = esc[esc['eng_handoffs'] == h]
    median_res = subset['resolution_hrs'].median()
    print(f"  {h} handoffs: {median_res:.1f} hrs (n={len(subset)})")

# --- 8. REOPEN ANALYSIS ---
print("\n8. REOPEN ANALYSIS")
print("-" * 40)
reopened = df[df['has_reopened']]
print(f"Total reopened: {len(reopened)} ({len(reopened)/len(df)*100:.1f}%)")
print(f"\nReopen by category:")
print(reopened['category'].value_counts().to_string())

# --- 9. CSAT ANALYSIS ---
print("\n9. CSAT ANALYSIS")
print("-" * 40)
csat_df = df[df['csat_score'].notna()]
print(f"Response rate: {len(csat_df)/len(df)*100:.1f}%")
print(f"Mean CSAT: {csat_df['csat_score'].mean():.2f}")
print(f"CSAT by escalation: escalated={csat_df[csat_df['is_escalated']]['csat_score'].mean():.2f}, non-escalated={csat_df[~csat_df['is_escalated']]['csat_score'].mean():.2f}")
print(f"\nCSAT distribution:")
print(csat_df['csat_score'].value_counts().sort_index().to_string())

# --- 10. CATEGORY ANALYSIS ---
print("\n10. CATEGORY BREAKDOWN")
print("-" * 40)
cat_stats = df.groupby('category').agg(
    tickets=('ticket_id', 'count'),
    pct=('ticket_id', lambda x: f"{len(x)/len(df)*100:.1f}%"),
    escalated=('is_escalated', 'sum'),
    median_resolution=('resolution_hrs', 'median'),
    reopened=('has_reopened', 'sum'),
    avg_csat=('csat_score', 'mean'),
    open_count=('is_open', 'sum')
).reset_index()
cat_stats = cat_stats.sort_values('tickets', ascending=False)
print(cat_stats.to_string(index=False))

# --- 11. CHANNEL ANALYSIS ---
print("\n11. CHANNEL ANALYSIS")
print("-" * 40)
print(df['channel'].value_counts().to_string())

# --- 12. CLIENT TIER ANALYSIS ---
print("\n12. CLIENT TIER ANALYSIS")
print("-" * 40)
tier_stats = df.groupby('client_tier').agg(
    tickets=('ticket_id', 'count'),
    escalated=('is_escalated', 'sum'),
    median_resolution=('resolution_hrs', 'median'),
    avg_csat=('csat_score', 'mean')
).reset_index()
print(tier_stats.to_string(index=False))

# --- 13. TOP REPEAT CLIENTS ---
print("\n13. TOP REPEAT CLIENTS")
print("-" * 40)
client_counts = df.groupby(['client_id', 'client_name', 'client_tier']).agg(
    tickets=('ticket_id', 'count'),
    escalated=('is_escalated', 'sum'),
    reopened=('has_reopened', 'sum')
).reset_index().sort_values('tickets', ascending=False).head(15)
print(client_counts.to_string(index=False))

# --- 14. KEY FINDINGS SUMMARY ---
print("\n" + "=" * 70)
print("KEY FINDINGS SUMMARY")
print("=" * 70)

july_count = len(df[df['created_at'].dt.month == 7])
sep_count = len(df[df['created_at'].dt.month == 9])
growth = (sep_count - july_count) / july_count * 100

print(f"""
1. TICKET VOLUME GROWING: {july_count} tickets in July → {sep_count} in September ({growth:.0f}% increase)
2. OPEN TICKETS: {len(open_tickets)} still open as of Sep 30
3. ESCALATION OVERLOAD: {len(esc)}/{len(df)} tickets escalated ({len(esc)/len(df)*100:.0f}%)
4. AVOIDABLE ESCALATIONS: {len(unnecessary)}/{len(esc)} escalations ({len(unnecessary)/len(esc)*100:.0f}%) were returned/unnecessary
5. SLOW RESPONSE: Median first response {df['first_response_hrs'].median():.1f}hrs, P1 tickets at {df[df['priority']=='P1']['first_response_hrs'].median():.1f}hrs
6. ESCALATED = SLOW: Non-escalated resolve in {closed[~closed['is_escalated']]['resolution_hrs'].median():.0f}hrs vs escalated in {closed[closed['is_escalated']]['resolution_hrs'].median():.0f}hrs
7. MULTI-HANDOFFS: {len(multi_handoff)} tickets bounced between L1 and eng multiple times
8. REOPENS: {len(reopened)} tickets ({len(reopened)/len(df)*100:.1f}%) reopened, suggesting premature closure
9. CSAT IMPACT: Escalated tickets get {csat_df[csat_df['is_escalated']]['csat_score'].mean():.1f} CSAT vs {csat_df[~csat_df['is_escalated']]['csat_score'].mean():.1f} non-escalated
""")

print("ANALYSIS COMPLETE")
