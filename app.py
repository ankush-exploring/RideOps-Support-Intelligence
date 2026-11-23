"""
RideOps Support Intelligence Dashboard
Built for: Support Lead (Meera) & Head of Ops (Ritika)
Purpose: Surface actionable insights to reduce open tickets by targeting
         avoidable escalations, slow first responses, and multi-handoff loops.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="RideOps Support Intelligence",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .metric-card h2 { margin: 0; font-size: 2rem; }
    .metric-card p { margin: 0; font-size: 0.85rem; opacity: 0.85; }
    .metric-red { background: linear-gradient(135deg, #f85149 0%, #da3633 100%); }
    .metric-green { background: linear-gradient(135deg, #2ea043 0%, #238636 100%); }
    .metric-orange { background: linear-gradient(135deg, #d29922 0%, #e3b341 100%); }
    .metric-blue { background: linear-gradient(135deg, #388bfd 0%, #1f6feb 100%); }
    .insight-box {
        background: rgba(56, 139, 253, 0.12);
        border: 1px solid rgba(56, 139, 253, 0.35);
        border-left: 5px solid #388bfd;
        color: inherit !important;
        padding: 1.1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .insight-box strong {
        color: #1d4ed8;
    }
    .alert-box {
        background: rgba(248, 81, 73, 0.12);
        border: 1px solid rgba(248, 81, 73, 0.35);
        border-left: 5px solid #f85149;
        color: inherit !important;
        padding: 1.1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .alert-box strong {
        color: #b91c1c;
    }
    @media (prefers-color-scheme: dark) {
        .insight-box strong {
            color: #58a6ff !important;
        }
        .alert-box strong {
            color: #ff7b72 !important;
        }
    }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv('rideops_support_tickets.csv')
    date_cols = ['created_at', 'first_response_at', 'first_closed_at', 'final_closed_at']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce')
    
    df['month'] = df['created_at'].dt.to_period('M').astype(str)
    df['week_start'] = df['created_at'].dt.to_period('W').apply(lambda x: x.start_time)
    df['first_response_hrs'] = (df['first_response_at'] - df['created_at']).dt.total_seconds() / 3600
    df['resolution_hrs'] = (df['final_closed_at'] - df['created_at']).dt.total_seconds() / 3600
    df['is_escalated'] = df['escalated_to_eng'] == 'Yes'
    df['is_open'] = df['status'] != 'Closed'
    df['has_reopened'] = df['reopen_count'] > 0
    
    cutoff = pd.Timestamp('2026-09-30')
    df['age_days'] = np.where(df['is_open'], (cutoff - df['created_at']).dt.total_seconds() / 86400, 0)
    
    # Classify escalation outcomes
    df['esc_outcome_type'] = df['eng_outcome'].map({
        'Fixed': 'Needed (Fixed)',
        'Config issue - returned to L1': 'Avoidable (Config)',
        'Not a bug - how-to': 'Avoidable (How-to)',
        'Insufficient info - returned to L1': 'Avoidable (Info gap)',
        'Duplicate of known issue': 'Avoidable (Duplicate)',
        'Not reproducible': 'Avoidable (Not repro)',
    }).fillna('')
    
    df['is_avoidable_esc'] = df['esc_outcome_type'].str.startswith('Avoidable')
    
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.title("🚕 RideOps Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "📊 Executive Summary",
    "🔍 Root Cause Deep-Dive",
    "👤 Agent Performance",
    "🏢 Client Health",
    "⚠️ Escalation Triage Helper",
    "📋 Open Tickets Queue"
])

# Filters
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")
months = sorted(df['month'].unique())
selected_months = st.sidebar.multiselect("Month", months, default=months)
priorities = st.sidebar.multiselect("Priority", ['P1', 'P2', 'P3', 'P4'], default=['P1', 'P2', 'P3', 'P4'])
tiers = st.sidebar.multiselect("Client Tier", df['client_tier'].unique().tolist(), default=df['client_tier'].unique().tolist())

# Apply filters
mask = (df['month'].isin(selected_months)) & (df['priority'].isin(priorities)) & (df['client_tier'].isin(tiers))
fdf = df[mask]


# ===== PAGE: EXECUTIVE SUMMARY =====
if page == "📊 Executive Summary":
    st.title("📊 Executive Summary")
    st.caption("RideOps Support · Jul–Sep 2026 · Data as of 30 Sep 2026")
    
    # Top-level metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total = len(fdf)
    open_count = fdf['is_open'].sum()
    esc_count = fdf['is_escalated'].sum()
    avoidable = fdf['is_avoidable_esc'].sum()
    median_res = fdf['resolution_hrs'].median()
    
    with col1:
        st.markdown(f'<div class="metric-card"><h2>{total:,}</h2><p>Total Tickets</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card metric-red"><h2>{open_count}</h2><p>Still Open</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card metric-orange"><h2>{esc_count}</h2><p>Escalated ({esc_count/total*100:.0f}%)</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card metric-red"><h2>{avoidable}</h2><p>Avoidable Escalations</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card metric-blue"><h2>{median_res:.0f}h</h2><p>Median Resolution</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # KEY INSIGHT BOX
    st.markdown("""
    <div class="alert-box">
        <strong>🔑 The Core Problem:</strong> Open tickets are rising not because volume is unmanageable, 
        but because <strong>57% of escalations are avoidable</strong>. Each unnecessary escalation adds 
        ~3-5 days to resolution. Fix the escalation pipeline → open tickets drop.
    </div>
    """, unsafe_allow_html=True)
    
    # Volume trend
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Weekly Ticket Volume & Open Tickets")
        weekly = fdf.groupby('week_start').agg(
            created=('ticket_id', 'count'),
            escalated=('is_escalated', 'sum')
        ).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weekly['week_start'], y=weekly['created'], 
                                  mode='lines+markers', name='Tickets Created',
                                  line=dict(color='#388bfd', width=2)))
        fig.add_trace(go.Bar(x=weekly['week_start'], y=weekly['escalated'],
                             name='Escalated', marker_color='#f85149', opacity=0.6))
        fig.update_layout(height=350, margin=dict(t=10, b=30))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Escalation Outcomes")
        esc_df = fdf[fdf['is_escalated']]
        outcomes = esc_df['eng_outcome'].value_counts().reset_index()
        outcomes.columns = ['Outcome', 'Count']
        
        colors = {
            'Fixed': '#2ea043',
            'Config issue - returned to L1': '#f85149',
            'Insufficient info - returned to L1': '#d29922',
            'Not a bug - how-to': '#da3633',
            'Duplicate of known issue': '#e3b341',
            'Not reproducible': '#8b949e',
        }
        fig = px.pie(outcomes, values='Count', names='Outcome',
                     color='Outcome', color_discrete_map=colors,
                     hole=0.4)
        fig.update_layout(height=350, margin=dict(t=10, b=30))
        st.plotly_chart(fig, use_container_width=True)
    
    # Resolution comparison
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Resolution Time: Escalated vs Non-Escalated")
        closed = fdf[fdf['status'] == 'Closed'].copy()
        esc_res = closed[closed['is_escalated']]['resolution_hrs']
        non_esc_res = closed[~closed['is_escalated']]['resolution_hrs']
        
        fig = go.Figure()
        fig.add_trace(go.Box(y=non_esc_res, name='Not Escalated', marker_color='#2ea043',
                             boxmean='sd'))
        fig.add_trace(go.Box(y=esc_res, name='Escalated', marker_color='#f85149',
                             boxmean='sd'))
        fig.update_layout(height=350, margin=dict(t=10, b=30), yaxis_title='Hours')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Category Breakdown")
        cat_data = fdf.groupby('category').agg(
            total=('ticket_id', 'count'),
            escalated=('is_escalated', 'sum'),
            open_count=('is_open', 'sum')
        ).reset_index().sort_values('total', ascending=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(y=cat_data['category'], x=cat_data['total'] - cat_data['escalated'],
                             name='Not Escalated', orientation='h', marker_color='#388bfd'))
        fig.add_trace(go.Bar(y=cat_data['category'], x=cat_data['escalated'],
                             name='Escalated', orientation='h', marker_color='#f85149'))
        fig.update_layout(barmode='stack', height=350, margin=dict(t=10, b=30, l=10))
        st.plotly_chart(fig, use_container_width=True)


# ===== PAGE: ROOT CAUSE DEEP-DIVE =====
elif page == "🔍 Root Cause Deep-Dive":
    st.title("🔍 Root Cause Deep-Dive")
    
    st.markdown("""
    <div class="insight-box">
        <strong>Why are open tickets rising?</strong> Three reinforcing loops:<br>
        ① <strong>Avoidable escalations</strong> clog engineering → long wait times<br>
        ② <strong>Insufficient info</strong> in escalations → tickets bounce back → re-escalation<br>
        ③ <strong>Slow first response</strong> → clients chase → agents context-switch → more delays
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Escalation Pipeline", "Response Times", "Handoff Loops", "Reopens & CSAT"])
    
    with tab1:
        st.subheader("The Escalation Funnel")
        esc_data = fdf[fdf['is_escalated']]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Escalated", f"{len(esc_data)}", f"{len(esc_data)/len(fdf)*100:.0f}% of all tickets")
        with col2:
            avoidable = esc_data['is_avoidable_esc'].sum()
            st.metric("Avoidable", f"{avoidable}", f"{avoidable/len(esc_data)*100:.0f}% of escalated", delta_color="inverse")
        with col3:
            needed = len(esc_data) - avoidable
            st.metric("Truly Needed (Fixed)", f"{needed}", f"{needed/len(esc_data)*100:.0f}% of escalated")
        
        # Monthly trend of avoidable vs needed
        monthly_esc = fdf[fdf['is_escalated']].groupby('month').agg(
            avoidable=('is_avoidable_esc', 'sum'),
            needed=('is_avoidable_esc', lambda x: (~x).sum())
        ).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_esc['month'], y=monthly_esc['avoidable'],
                             name='Avoidable', marker_color='#f85149'))
        fig.add_trace(go.Bar(x=monthly_esc['month'], y=monthly_esc['needed'],
                             name='Needed (Fixed)', marker_color='#2ea043'))
        fig.update_layout(barmode='stack', height=350, title='Escalations by Month: Avoidable vs Needed')
        st.plotly_chart(fig, use_container_width=True)
        
        # Avoidable breakdown
        st.subheader("What makes escalations avoidable?")
        avoidable_df = esc_data[esc_data['is_avoidable_esc']]
        col1, col2 = st.columns(2)
        with col1:
            reason_counts = avoidable_df['eng_outcome'].value_counts().reset_index()
            reason_counts.columns = ['Reason', 'Count']
            fig = px.bar(reason_counts, x='Count', y='Reason', orientation='h',
                        color='Reason', color_discrete_sequence=['#f85149', '#d29922', '#da3633', '#e3b341', '#8b949e'])
            fig.update_layout(height=300, showlegend=False, title='Avoidable Escalation Reasons')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Categories driving avoidable escalations
            cat_avoid = avoidable_df['category'].value_counts().reset_index()
            cat_avoid.columns = ['Category', 'Count']
            fig = px.bar(cat_avoid, x='Count', y='Category', orientation='h',
                        color_discrete_sequence=['#d29922'])
            fig.update_layout(height=300, title='Categories with Most Avoidable Escalations')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("First Response Time Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            # Response time by priority
            resp_by_pri = fdf.groupby('priority')['first_response_hrs'].agg(['median', 'mean', lambda x: x.quantile(0.9)]).reset_index()
            resp_by_pri.columns = ['Priority', 'Median', 'Mean', 'P90']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=resp_by_pri['Priority'], y=resp_by_pri['Median'], name='Median', marker_color='#388bfd'))
            fig.add_trace(go.Bar(x=resp_by_pri['Priority'], y=resp_by_pri['P90'], name='90th Percentile', marker_color='#f85149'))
            fig.update_layout(barmode='group', height=350, title='First Response Time by Priority (hrs)')
            
            # Add SLA lines
            fig.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="1hr target (P1)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Response time by agent
            agent_resp = fdf.groupby('assigned_agent')['first_response_hrs'].median().reset_index()
            agent_resp.columns = ['Agent', 'Median Response (hrs)']
            agent_resp = agent_resp.sort_values('Median Response (hrs)', ascending=True)
            
            fig = px.bar(agent_resp, x='Median Response (hrs)', y='Agent', orientation='h',
                        color='Median Response (hrs)',
                        color_continuous_scale=['#2ea043', '#d29922', '#f85149'])
            fig.update_layout(height=350, title='Median Response Time by Agent')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Multi-Handoff Loop Analysis")
        
        esc_data = fdf[fdf['is_escalated']]
        
        col1, col2 = st.columns(2)
        with col1:
            handoff_dist = esc_data['eng_handoffs'].value_counts().sort_index().reset_index()
            handoff_dist.columns = ['Handoffs', 'Count']
            fig = px.bar(handoff_dist, x='Handoffs', y='Count',
                        color='Count', color_continuous_scale=['#2ea043', '#d29922', '#f85149'])
            fig.update_layout(height=300, title='Handoff Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Resolution time by handoffs
            handoff_res = esc_data.groupby('eng_handoffs')['resolution_hrs'].median().reset_index()
            handoff_res.columns = ['Handoffs', 'Median Resolution (hrs)']
            fig = px.bar(handoff_res, x='Handoffs', y='Median Resolution (hrs)',
                        color='Median Resolution (hrs)',
                        color_continuous_scale=['#2ea043', '#d29922', '#f85149'])
            fig.update_layout(height=300, title='Resolution Time Grows with Handoffs')
            st.plotly_chart(fig, use_container_width=True)
        
        # Multi-handoff tickets table
        multi = esc_data[esc_data['eng_handoffs'] >= 2].sort_values('eng_handoffs', ascending=False)
        st.subheader(f"⚠️ Multi-Handoff Tickets ({len(multi)} tickets)")
        st.dataframe(
            multi[['ticket_id', 'client_name', 'category', 'priority', 'eng_handoffs', 'eng_outcome', 'resolution_hrs', 'status']].head(20),
            use_container_width=True, hide_index=True
        )
    
    with tab4:
        st.subheader("Reopens & Customer Satisfaction")
        col1, col2 = st.columns(2)
        
        with col1:
            reopened = fdf[fdf['has_reopened']]
            reopen_by_cat = reopened['category'].value_counts().reset_index()
            reopen_by_cat.columns = ['Category', 'Reopened Tickets']
            fig = px.bar(reopen_by_cat, x='Reopened Tickets', y='Category', orientation='h',
                        color_discrete_sequence=['#d29922'])
            fig.update_layout(height=300, title=f'Reopened Tickets by Category (Total: {len(reopened)})')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            csat = fdf[fdf['csat_score'].notna()]
            csat_by_esc = csat.groupby('is_escalated')['csat_score'].mean().reset_index()
            csat_by_esc['Label'] = csat_by_esc['is_escalated'].map({True: 'Escalated', False: 'Not Escalated'})
            fig = px.bar(csat_by_esc, x='Label', y='csat_score',
                        color='Label', color_discrete_map={'Escalated': '#f85149', 'Not Escalated': '#2ea043'})
            fig.update_layout(height=300, title='CSAT: Escalated vs Non-Escalated', yaxis_range=[0, 5])
            st.plotly_chart(fig, use_container_width=True)


# ===== PAGE: AGENT PERFORMANCE =====
elif page == "👤 Agent Performance":
    st.title("👤 Agent Performance Dashboard")
    
    agent_stats = fdf.groupby('assigned_agent').agg(
        tickets=('ticket_id', 'count'),
        escalated=('is_escalated', 'sum'),
        avoidable_esc=('is_avoidable_esc', 'sum'),
        median_response=('first_response_hrs', 'median'),
        median_resolution=('resolution_hrs', 'median'),
        reopened=('has_reopened', 'sum'),
        avg_csat=('csat_score', 'mean'),
        open_tickets=('is_open', 'sum')
    ).reset_index()
    agent_stats['esc_rate'] = (agent_stats['escalated'] / agent_stats['tickets'] * 100).round(1)
    agent_stats['avoidable_rate'] = (agent_stats['avoidable_esc'] / agent_stats['tickets'] * 100).round(1)
    agent_stats['reopen_rate'] = (agent_stats['reopened'] / agent_stats['tickets'] * 100).round(1)
    
    # Leaderboard
    st.subheader("Agent Leaderboard")
    display_stats = agent_stats[['assigned_agent', 'tickets', 'esc_rate', 'avoidable_rate', 
                                  'median_response', 'median_resolution', 'reopen_rate', 'avg_csat', 'open_tickets']].copy()
    display_stats.columns = ['Agent', 'Tickets', 'Escalation %', 'Avoidable Esc %', 
                              'Median Response (hrs)', 'Median Resolution (hrs)', 'Reopen %', 'Avg CSAT', 'Open']
    display_stats = display_stats.sort_values('Avoidable Esc %', ascending=True)
    
    st.dataframe(display_stats, use_container_width=True, hide_index=True)
    
    # Visual comparisons
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(agent_stats.sort_values('esc_rate'), x='esc_rate', y='assigned_agent',
                    orientation='h', color='esc_rate',
                    color_continuous_scale=['#2ea043', '#d29922', '#f85149'],
                    labels={'esc_rate': 'Escalation Rate %', 'assigned_agent': 'Agent'})
        fig.update_layout(height=400, title='Escalation Rate by Agent')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(agent_stats.sort_values('median_response'), x='median_response', y='assigned_agent',
                    orientation='h', color='median_response',
                    color_continuous_scale=['#2ea043', '#d29922', '#f85149'],
                    labels={'median_response': 'Median Response (hrs)', 'assigned_agent': 'Agent'})
        fig.update_layout(height=400, title='Median First Response Time by Agent')
        st.plotly_chart(fig, use_container_width=True)
    
    # Agent deep-dive
    st.markdown("---")
    selected_agent = st.selectbox("Select agent for deep-dive:", agent_stats['assigned_agent'].tolist())
    
    agent_df = fdf[fdf['assigned_agent'] == selected_agent]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tickets", len(agent_df))
    with col2:
        st.metric("Escalation Rate", f"{agent_df['is_escalated'].mean()*100:.0f}%")
    with col3:
        st.metric("Median Response", f"{agent_df['first_response_hrs'].median():.1f}h")
    with col4:
        csat_val = agent_df['csat_score'].mean()
        st.metric("Avg CSAT", f"{csat_val:.1f}" if not pd.isna(csat_val) else "N/A")
    
    col1, col2 = st.columns(2)
    with col1:
        agent_cat = agent_df['category'].value_counts().reset_index()
        agent_cat.columns = ['Category', 'Count']
        fig = px.pie(agent_cat, values='Count', names='Category', title=f'{selected_agent}: Ticket Categories')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        agent_weekly = agent_df.groupby('week_start').size().reset_index(name='Tickets')
        fig = px.line(agent_weekly, x='week_start', y='Tickets', title=f'{selected_agent}: Weekly Volume',
                     markers=True)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


# ===== PAGE: CLIENT HEALTH =====
elif page == "🏢 Client Health":
    st.title("🏢 Client Health Monitor")
    
    client_stats = fdf.groupby(['client_id', 'client_name', 'client_tier']).agg(
        tickets=('ticket_id', 'count'),
        escalated=('is_escalated', 'sum'),
        reopened=('has_reopened', 'sum'),
        open_count=('is_open', 'sum'),
        avg_csat=('csat_score', 'mean'),
        median_resolution=('resolution_hrs', 'median')
    ).reset_index()
    client_stats['esc_rate'] = (client_stats['escalated'] / client_stats['tickets'] * 100).round(1)
    
    # Risk scoring
    client_stats['risk_score'] = (
        client_stats['open_count'] * 3 +
        client_stats['reopened'] * 2 +
        client_stats['escalated'] * 1 +
        (5 - client_stats['avg_csat'].fillna(3)) * 2
    ).round(1)
    client_stats = client_stats.sort_values('risk_score', ascending=False)
    
    # Tier filter
    tier_filter = st.selectbox("Filter by tier:", ["All"] + sorted(fdf['client_tier'].unique().tolist()))
    if tier_filter != "All":
        client_stats = client_stats[client_stats['client_tier'] == tier_filter]
    
    # Top at-risk clients
    st.subheader("🚨 Top At-Risk Clients")
    top_risk = client_stats.head(15)
    
    fig = px.bar(top_risk, x='risk_score', y='client_name', orientation='h',
                color='client_tier', color_discrete_map={
                    'Enterprise': '#f85149', 'Mid-market': '#d29922', 'SMB': '#388bfd'
                })
    fig.update_layout(height=500, title='Client Risk Score (higher = more at risk)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Client table
    st.subheader("Full Client Health Table")
    display_clients = client_stats[['client_name', 'client_tier', 'tickets', 'escalated', 'esc_rate',
                                     'reopened', 'open_count', 'avg_csat', 'median_resolution', 'risk_score']].copy()
    display_clients.columns = ['Client', 'Tier', 'Tickets', 'Escalated', 'Esc %', 
                                'Reopened', 'Open', 'Avg CSAT', 'Median Res (hrs)', 'Risk Score']
    st.dataframe(display_clients, use_container_width=True, hide_index=True)


# ===== PAGE: ESCALATION TRIAGE HELPER =====
elif page == "⚠️ Escalation Triage Helper":
    st.title("⚠️ Escalation Triage Helper")
    
    st.markdown("""
    <div class="insight-box">
        <strong>Purpose:</strong> This tool helps L1 agents decide whether to escalate or resolve 
        tickets themselves. It surfaces similar past tickets and their outcomes, reducing unnecessary 
        escalations by showing agents that many issues were resolved without engineering.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        input_category = st.selectbox("Ticket Category", sorted(fdf['category'].unique()))
    with col2:
        input_description = st.text_input("Issue description keywords", placeholder="e.g. booking cutoff, roster, GPS")
    
    # Find similar tickets
    similar = fdf[fdf['category'] == input_category].copy()
    
    if input_description:
        keywords = input_description.lower().split()
        similar = similar[similar['description'].str.lower().apply(
            lambda x: any(k in str(x) for k in keywords)
        )]
    
    if len(similar) > 0:
        st.markdown("---")
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Similar Tickets Found", len(similar))
        with col2:
            esc_pct = similar['is_escalated'].mean() * 100
            st.metric("Were Escalated", f"{esc_pct:.0f}%")
        with col3:
            if similar['is_escalated'].sum() > 0:
                avoidable_pct = similar[similar['is_escalated']]['is_avoidable_esc'].mean() * 100
                st.metric("Of Those, Avoidable", f"{avoidable_pct:.0f}%")
            else:
                st.metric("Of Those, Avoidable", "N/A")
        with col4:
            st.metric("Median Resolution", f"{similar['resolution_hrs'].median():.0f}h")
        
        # Recommendation
        esc_similar = similar[similar['is_escalated']]
        if len(esc_similar) > 0:
            avoidable_rate = esc_similar['is_avoidable_esc'].mean()
            if avoidable_rate > 0.5:
                st.markdown("""
                <div class="alert-box">
                    <strong>⚠️ RECOMMENDATION: Try resolving without escalation first.</strong><br>
                    Most similar escalated tickets were returned from engineering as config issues or missing info.
                    Check configuration settings and gather all details before escalating.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-box">
                    <strong>✅ This category typically needs engineering.</strong><br>
                    Most escalations in this category resulted in real fixes. Escalate with complete info.
                </div>
                """, unsafe_allow_html=True)
        
        # Past escalation outcomes for this category
        st.subheader("Past Escalation Outcomes for This Pattern")
        if len(esc_similar) > 0:
            outcome_dist = esc_similar['eng_outcome'].value_counts().reset_index()
            outcome_dist.columns = ['Outcome', 'Count']
            fig = px.pie(outcome_dist, values='Count', names='Outcome', hole=0.4)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Sample tickets
        st.subheader("Sample Similar Tickets")
        st.dataframe(
            similar[['ticket_id', 'description', 'is_escalated', 'eng_outcome', 'resolution_hrs', 'csat_score']].head(15),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No similar tickets found. Try broadening your search.")


# ===== PAGE: OPEN TICKETS QUEUE =====
elif page == "📋 Open Tickets Queue":
    st.title("📋 Open Tickets Queue")
    
    open_df = fdf[fdf['is_open']].copy()
    
    if len(open_df) == 0:
        st.success("🎉 No open tickets matching your filters!")
    else:
        # Sort by urgency
        cutoff = pd.Timestamp('2026-09-30')
        open_df['age_days'] = (cutoff - open_df['created_at']).dt.total_seconds() / 86400
        
        # Urgency score
        priority_weight = {'P1': 10, 'P2': 7, 'P3': 4, 'P4': 2}
        tier_weight = {'Enterprise': 3, 'Mid-market': 2, 'SMB': 1}
        open_df['urgency'] = (
            open_df['priority'].map(priority_weight) * 2 +
            open_df['age_days'] +
            open_df['client_tier'].map(tier_weight) * 3 +
            open_df['eng_handoffs'] * 5
        )
        open_df = open_df.sort_values('urgency', ascending=False)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Open Tickets", len(open_df))
        with col2:
            st.metric("Median Age", f"{open_df['age_days'].median():.0f} days")
        with col3:
            st.metric("P1/P2 Open", len(open_df[open_df['priority'].isin(['P1', 'P2'])]))
        with col4:
            esc_open = open_df['is_escalated'].sum()
            st.metric("Stuck in Escalation", int(esc_open))
        
        # Age distribution
        fig = px.histogram(open_df, x='age_days', nbins=20, color='priority',
                          color_discrete_map={'P1': '#f85149', 'P2': '#d29922', 'P3': '#388bfd', 'P4': '#8b949e'},
                          title='Open Ticket Age Distribution')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Prioritized queue
        st.subheader("Prioritized Action Queue")
        display_cols = ['ticket_id', 'client_name', 'client_tier', 'category', 'priority',
                       'description', 'assigned_agent', 'is_escalated', 'eng_handoffs', 'age_days']
        queue_display = open_df[display_cols].copy()
        queue_display['age_days'] = queue_display['age_days'].round(1)
        queue_display.columns = ['Ticket', 'Client', 'Tier', 'Category', 'Priority',
                                'Description', 'Agent', 'Escalated', 'Handoffs', 'Age (days)']
        st.dataframe(queue_display, use_container_width=True, hide_index=True)


# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("Data: 1,444 tickets · Jul-Sep 2026")
