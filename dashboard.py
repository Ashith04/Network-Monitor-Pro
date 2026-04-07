import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import textwrap
import threading
import ping3
import config
from health_score import calculate_health_score

st.set_page_config(page_title="Network Monitor Pro", page_icon="[NM]", layout="wide", initial_sidebar_state="expanded")

COLORS = {
    'primary': '#00FFC2', 'secondary': '#00D2FF', 'success': '#00FFC2',
    'warning': '#f59e0b', 'danger': '#ef4444', 'critical': '#ff0055',
    'info': '#00D2FF', 'light_bg': '#000000', 'text_dark': '#00FFC2', 'text_light': '#FFFFFF',
    'panel_bg': '#000000', 'glass_border': '#00FFC2'
}

# Global state for monitoring (accessed by thread)
if "ENABLED_IPS" not in st.session_state:
    st.session_state.ENABLED_IPS = {ip: True for ip in config.DEVICES}

st.markdown(f"""<style>
/* Matrix Neo (Neon Performance) System */
@keyframes neonPulse {{ 0% {{ opacity: 0.8; text-shadow: 0 0 5px #00FFC2; }} 50% {{ opacity: 1; text-shadow: 0 0 15px #00FFC2; }} 100% {{ opacity: 0.8; text-shadow: 0 0 5px #00FFC2; }} }}
@keyframes scanline {{ 0% {{ transform: translateY(-100%); }} 100% {{ transform: translateY(100%); }} }}

.stApp {{ background: #000000; color: #00FFC2; }}
.stApp p, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp span {{ font-family: 'JetBrains Mono', 'Monaco', monospace; letter-spacing: -0.5px; }}
[data-testid="stSidebar"] {{ background-color: #000000 !important; border-right: 1px solid #1f2937; padding-top: 1rem; color: #FFFFFF !important; }}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] small {{ color: #FFFFFF !important; }}
[data-testid="stWidgetLabel"] p {{ color: #FFFFFF !important; }}

/* Structured Matrix Cards */
.matrix-card {{
    background: #000000;
    border: 1px solid #1f2937;
    border-radius: 4px;
    padding: 18px 24px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
}}
.matrix-card:hover {{
    border-color: #00FFC2;
    box-shadow: 0 0 15px rgba(0, 255, 194, 0.1);
    transform: translateX(4px);
}}

/* Top Matrix Headers with Neon Scanline */
.header-container {{ 
    background: #000000;
    padding: 2rem 0; border-bottom: 2px solid #00FFC2; margin-bottom: 3rem;
    position: relative; overflow: hidden;
}}
.header-container::after {{
    content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(0deg, transparent 0%, rgba(0,255,194,0.05) 50%, transparent 100%);
    animation: scanline 4s linear infinite; pointer-events: none;
}}
.header-title {{ 
    font-size: 2.8rem; font-weight: 800; color: #00FFC2; margin: 0; 
    text-shadow: 0 0 10px rgba(0,255,194,0.5); text-transform: uppercase;
}}

/* Metric Overrides - Structured & Monospaced */
[data-testid="stMetricValue"] {{ font-size: 1.8rem !important; font-weight: 700 !important; color: #00FFC2 !important; }}
[data-testid="stMetricLabel"] {{ color: #FFFFFF !important; text-transform: uppercase; font-size: 0.75rem !important; letter-spacing: 1px; }}
[data-testid="stMetric"] {{ border-left: 2px solid #1f2937; padding-left: 20px !important; }}

/* Toggles & Buttons - Strictly Structured */
.stButton > button {{ 
    background: transparent !important; color: #FFFFFF !important; 
    border: 1px solid #1f2937 !important; border-radius: 0 !important;
    text-transform: uppercase; font-size: 0.7rem !important; padding: 4px 12px !important;
    transition: all 0.2s;
}}
.stButton > button:hover {{ 
    color: #00FFC2 !important; border-color: #00FFC2 !important; 
    box-shadow: 0 0 8px rgba(0, 255, 194, 0.2) !important;
}}

/* Navigation Radio Styling - Matrix Neo */
div[role="radiogroup"] {{ 
    background: transparent !important; 
    padding: 0 !important; 
}}
div[role="radiogroup"] label {{
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 10px 15px !important;
    margin-bottom: 5px !important;
    border-radius: 4px !important;
    transition: all 0.3s;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
div[role="radiogroup"] label:hover {{
    color: #00FFC2 !important;
    background: rgba(0, 255, 194, 0.05) !important;
}}
div[role="radiogroup"] label[data-selected="true"] {{
    color: #00FFC2 !important;
    border: 1px solid #00FFC2 !important;
    background: rgba(0, 255, 194, 0.1) !important;
    box-shadow: 0 0 10px rgba(0, 255, 194, 0.1);
}}

/* Status Pills */
.status-tag {{ 
    font-weight: 700; font-size: 0.7rem; text-transform: uppercase; 
    padding: 2px 8px; border-radius: 2px; letter-spacing: 1px;
}}
.tag-online {{ color: #00FFC2; border: 1px solid #00FFC2; animation: neonPulse 2s infinite; }}
.tag-offline {{ color: #ff0055; border: 1px solid #ff0055; }}
.tag-disabled {{ color: #FFFFFF; border: 1px solid #FFFFFF; }}

/* Sidebar collapse/expand button - Fix "keyboard_double" text & restore navy style */
[data-testid="stSidebar"] button[kind="headerNoPadding"],
[data-testid="stSidebar"] button[kind="header"],
[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] {{ 
    font-size: 0px !important; 
    color: transparent !important;
    background: #0f2a3d !important; 
    border: 2px solid #0ea5e9 !important;
    border-radius: 6px !important; 
    width: 32px !important; height: 32px !important; 
    min-height: 32px !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    position: relative !important;
    overflow: hidden !important;
}}
[data-testid="stSidebar"] button[kind="headerNoPadding"] span,
[data-testid="stSidebar"] button[kind="header"] span,
[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] span {{ 
    font-size: 0px !important; color: transparent !important; display: none !important;
}}
[data-testid="stSidebar"] button[kind="headerNoPadding"]::after,
[data-testid="stSidebar"] button[kind="header"]::after,
[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"]::after {{ 
    content: "◀" !important; font-size: 16px !important; color: #38bdf8 !important; 
    position: absolute !important;
}}
[data-testid="stSidebar"] button[kind="headerNoPadding"]:hover,
[data-testid="stSidebar"] button[kind="header"]:hover {{ 
    background: #0ea5e9 !important; 
}}
/* Collapsed sidebar expand button - AGGRESSIVE Restoration */
[data-testid="collapsedControl"] {{ 
    background: transparent !important;
    z-index: 9999 !important;
}}
[data-testid="collapsedControl"] button,
[data-testid="collapsedControl"] button[kind="headerNoPadding"],
[data-testid="collapsedControl"] [data-testid="stBaseButton-headerNoPadding"],
header button,
header [data-testid="stBaseButton-headerNoPadding"] {{ 
    font-size: 0px !important;
    color: transparent !important;
    background: #0f2a3d !important;
    border: 2px solid #0ea5e9 !important;
    border-radius: 8px !important;
    width: 38px !important; height: 38px !important;
    min-width: 38px !important; min-height: 38px !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    overflow: hidden !important;
    position: relative !important;
    box-shadow: 0 2px 8px rgba(14,165,233,0.3) !important;
    z-index: 9999 !important;
    margin: 4px !important;
}}
[data-testid="collapsedControl"] button::after,
header button[kind="headerNoPadding"]::after,
header [data-testid="stBaseButton-headerNoPadding"]::after {{ 
    content: "▶" !important; font-size: 16px !important; color: #38bdf8 !important;
    position: absolute !important; display: block !important; visibility: visible !important;
}}
[data-testid="collapsedControl"] button:hover,
header button[kind="headerNoPadding"]:hover,
header [data-testid="stBaseButton-headerNoPadding"]:hover {{ 
    background: #0ea5e9 !important;
    box-shadow: 0 4px 16px rgba(14,165,233,0.5) !important;
}}
/* Hide the header bar background when collapsed */
header[data-testid="stHeader"] {{ background: transparent !important; }}

/* Scrollbar styling for NOC Wall */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: #000000; }}
::-webkit-scrollbar-thumb {{ background: #1f2937; }}
::-webkit-scrollbar-thumb:hover {{ background: #00FFC2; }}
</style>""", unsafe_allow_html=True)

st.markdown(f"""<div class="header-container">
    <div class="header-title">Network Monitor Pro</div>
    <div style="font-size: 0.9rem; color: #FFFFFF; margin-top: 5px; letter-spacing: 2px;">
        <span style="color: #00FFC2;">&gt;</span> ENTERPRISE GLOBAL OPERATIONS CENTER
    </div>
</div>""", unsafe_allow_html=True)

try:
    from database import (get_latest_ping_status, get_ping_history, get_database_stats,
                         get_top_talkers, get_protocol_distribution, get_flow_summary, log_ping_result)
    from advanced_alerts import get_alert_history
except ImportError as e:
    st.error(f"Database module error: {e}")
    st.stop()

# --- LIVE MONITORING THREAD ---
def background_monitoring():
    """Background thread to perform pings at regular intervals"""
    while True:
        try:
            # We use the list from config but check the session state for activity
            for ip in config.DEVICES:
                # Check status from global session-like object (actually using session_state is tricky in threads, 
                # but in local dev streamlit handles it via the session reference)
                is_enabled = st.session_state.ENABLED_IPS.get(ip, True)
                
                if not is_enabled:
                    # Log as 'Disabled' if we want, or just skip
                    continue
                    
                # Use ping3 for live status
                latency = ping3.ping(ip, timeout=2)
                status = "Online" if latency is not None else "Offline"
                if latency is not None:
                    latency = round(latency * 1000, 1)
                
                h_score = calculate_health_score(latency, 0, status)
                log_ping_result(ip, status, latency, h_score)
            
            time.sleep(getattr(config, 'CHECK_INTERVAL', 10))
        except Exception:
            time.sleep(5)

if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = True
    monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()

with st.sidebar:
    st.markdown(f'<div style="color: #FFFFFF; font-size: 0.75rem; letter-spacing: 2px; margin-bottom: 10px;">[NAV_LINK] SELECT_NODE</div>', unsafe_allow_html=True)
    view_mode = st.radio("Select View", 
                         ["SYSTEM MATRIX", "FLEET NODES", "ALARM CENTER", "BANDWIDTH DPI", "INTELLIGENCE", "INTERCEPTION"], 
                         index=0, label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### System Telemetry")
    if st.button("🔄 Sync Live Metrics"):
        with st.status("Fetching live device status...", expanded=False):
            for ip in config.DEVICES:
                latency = ping3.ping(ip, timeout=1)
                status = "Online" if latency is not None else "Offline"
                if latency is not None: latency = round(latency * 1000, 1)
                h_score = calculate_health_score(latency, 0, status)
                log_ping_result(ip, status, latency, h_score)
        st.success("Network state synchronized!")
        st.rerun()

    stats = get_database_stats()
    if stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Devices", stats.get('devices', 0))
            st.metric("Records", f"{stats.get('ping_records', 0):,}")
        with col2:
            st.metric("DB Size", f"{stats.get('db_size_mb', 0)} MB")
            st.metric("Flows", f"{stats.get('flow_records', 0):,}")

latest_df = pd.DataFrame()
history_df = pd.DataFrame()
alerts_df = pd.DataFrame()

try:
    latest = get_latest_ping_status()
    if latest:
        latest_df = pd.DataFrame([dict(row) for row in latest])
    history = get_ping_history(hours=24)
    if history:
        history_df = pd.DataFrame([dict(row) for row in history])
    alerts = get_alert_history(hours=24)
    if alerts:
        alerts_df = pd.DataFrame([dict(row) for row in alerts])
except Exception as e:
    st.error(f"Error loading data: {e}")

if view_mode == "SYSTEM MATRIX":
    if not latest_df.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        total = len(latest_df)
        online = len(latest_df[latest_df['status'] == 'Online'])
        offline = total - online
        avg_latency = latest_df[latest_df['status'] == 'Online']['latency'].mean()
        avg_health = latest_df['health_score'].mean()
        
        with col1:
            st.metric("Total Devices", total)
        with col2:
            st.metric("Online", online)
        with col3:
            st.metric("Offline", offline)
        with col4:
            st.metric("Avg Latency", f"{avg_latency:.0f}ms")
        with col5:
            st.metric("Health Score", f"{avg_health:.0f}")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Alerts", "Traffic", "Trends"])
        
        with tab1:
            st.markdown(f'<div style="color: #FFFFFF; font-size: 0.75rem; margin-bottom: 20px;">[SYS_MONITOR] DEVICE_FLEET_STATUS</div>', unsafe_allow_html=True)
            
            # Helper to toggle IP status
            def toggle_ip(ip):
                st.session_state.ENABLED_IPS[ip] = not st.session_state.ENABLED_IPS.get(ip, True)
                if st.session_state.ENABLED_IPS[ip]:
                    latency = ping3.ping(ip, timeout=1)
                    status = "Online" if latency is not None else "Offline"
                    if latency: latency = round(latency * 1000, 1)
                    log_ping_result(ip, status, latency, calculate_health_score(latency, 0, status))

            for idx, row in latest_df.iterrows():
                ip = row['ip']
                is_enabled = st.session_state.ENABLED_IPS.get(ip, True)
                status = row['status'] if is_enabled else "Disabled"
                
                with st.container():
                    st.markdown(f'<div class="matrix-card">', unsafe_allow_html=True)
                    # Strict 4-column structured layout
                    col_ip, col_lat, col_health, col_action = st.columns([3, 2, 2, 2])
                    
                    with col_ip:
                        st.markdown(f"""<div style="font-size: 1.1rem; font-weight: 700; color: #00FFC2;">{ip}</div>
                        <div style="font-size: 0.65rem; color: #FFFFFF;">NODE_IDENTIFIER</div>""", unsafe_allow_html=True)
                    
                    with col_lat:
                        latency = f"{row['latency']:.1f} MS" if (pd.notna(row['latency']) and is_enabled) else "---"
                        st.markdown(f"""<div style="font-size: 0.9rem; color: #00FFC2;">{latency}</div>
                        <div style="font-size: 0.65rem; color: #FFFFFF;">LATENCY</div>""", unsafe_allow_html=True)
                    
                    with col_health:
                        st.markdown(f"""<div style="font-size: 0.9rem; color: #00FFC2;">{row['health_score']:.0f}%</div>
                        <div style="font-size: 0.65rem; color: #FFFFFF;">HEALTH_INDEX</div>""", unsafe_allow_html=True)
                    
                    with col_action:
                        # Standardized Toggle Position
                        tag_class = "online" if status == "Online" else ("offline" if status == "Offline" else "disabled")
                        if st.button(f"TOGGLE_{ip}", key=f"btn_{ip}", use_container_width=True):
                            toggle_ip(ip)
                            st.rerun()
                        st.markdown(f'<div style="margin-top:-38px; pointer-events:none; text-align:center;"><span class="status-tag tag-{tag_class}">{status}</span></div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="section-title">Critical Events Log</div>', unsafe_allow_html=True)
            if not alerts_df.empty:
                for idx, alert in alerts_df.head(10).iterrows():
                    severity = alert.get('severity', 3)
                    severity_map = {1: 'CRITICAL', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW', 5: 'INFO'}
                    severity_name = severity_map.get(severity, 'UNKNOWN')
                    color_border = COLORS['critical'] if severity == 1 else (COLORS['warning'] if severity == 2 else COLORS['info'])
                    
                    st.markdown(f"""<div class="alert-box" style="border-left-color: {color_border};">
                        <strong style="color: {color_border};">[{severity_name}]</strong> {alert.get('alert_type', 'Unknown')} - {alert.get('device_ip', 'N/A')}<br>
                        <span style="display: block; margin-top: 5px; font-size: 0.95em;">{alert.get('message', '')}</span>
                        <small style="color: {COLORS['text_light']}; display: block; margin-top: 8px;">{alert.get('timestamp', '')}</small>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("System Normal: No critical alerts")
        
        with tab3:
            st.markdown('<div class="section-title">Core Traffic Analysis</div>', unsafe_allow_html=True)
            try:
                flow_summary = get_flow_summary(hours=1)
                if flow_summary and dict(flow_summary).get('total_flows', 0) > 0:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Flows", f"{flow_summary['total_flows']:,}")
                    with col2:
                        total_mb = flow_summary['total_bytes'] / (1024 * 1024) if flow_summary['total_bytes'] else 0
                        st.metric("Traffic", f"{total_mb:.2f} MB")
                    with col3:
                        st.metric("Packets", f"{flow_summary['total_packets']:,}")
                else:
                    st.info("No flow data captured yet.")
            except:
                st.info("Flow data not available")
        
        with tab4:
            st.markdown('<div class="section-title">Holographic Latency 3D Surface</div>', unsafe_allow_html=True)
            if not history_df.empty:
                chart_df = history_df[pd.notna(history_df['latency'])].copy()
                if not chart_df.empty:
                    fig = go.Figure()
                    unique_ips = chart_df['ip'].unique()
                    ip_map = {ip: i for i, ip in enumerate(unique_ips)}
                    chart_df['ip_idx'] = chart_df['ip'].map(ip_map)
                    
                    fig.add_trace(go.Scatter3d(
                        x=chart_df['ip_idx'],
                        y=chart_df['timestamp'],
                        z=chart_df['latency'],
                        mode='markers+lines',
                        marker=dict(
                            size=4,
                            color=chart_df['latency'],
                            colorscale=[[0, '#00FFC2'], [1, '#00D2FF']],
                            opacity=0.8
                        ),
                        line=dict(color='#00FFC2', width=1),
                        name="Latency Hub"
                    ))
                    
                    fig.update_layout(
                        scene=dict(
                            xaxis=dict(title='Device Index', tickvals=list(range(len(unique_ips))), ticktext=unique_ips, color='#FFFFFF'),
                            yaxis=dict(title='Timeline', color='#FFFFFF'),
                            zaxis=dict(title='Latency (ms)', color='#FFFFFF'),
                            xaxis_backgroundcolor="black",
                            yaxis_backgroundcolor="black",
                            zaxis_backgroundcolor="black",
                        ),
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=600,
                        paper_bgcolor='black',
                        plot_bgcolor='black',
                        font=dict(color='#00FFC2')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Insufficient latency data for 3D mapping.")

elif view_mode == "FLEET NODES":
    st.markdown(f'<div style="color: #FFFFFF; font-size: 0.75rem; margin-bottom: 20px;">[SYS_ADMIN] FLEET_CONFIGURATION_NODE</div>', unsafe_allow_html=True)
    if not latest_df.empty:
        for idx, row in latest_df.iterrows():
            ip = row['ip']
            is_enabled = st.session_state.ENABLED_IPS.get(ip, True)
            status = row['status'] if is_enabled else "Disabled"
            
            with st.container():
                st.markdown(f'<div class="matrix-card">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    st.markdown(f"""<div style="font-size: 1.1rem; font-weight: 700; color: #00FFC2;">{ip}</div>
                    <div style="font-size: 0.65rem; color: #FFFFFF;">TARGET_IP_ADDRESS</div>""", unsafe_allow_html=True)
                
                with col2:
                    tag_class = "online" if status == "Online" else ("offline" if status == "Offline" else "disabled")
                    if st.button(f"CONFIG_{ip}", key=f"dev_btn_{ip}", use_container_width=True):
                        st.session_state.ENABLED_IPS[ip] = not st.session_state.ENABLED_IPS.get(ip, True)
                        st.rerun()
                    st.markdown(f'<div style="margin-top:-38px; pointer-events:none; text-align:center;"><span class="status-tag tag-{tag_class}">{status}</span></div>', unsafe_allow_html=True)

                with col3:
                    latency = f"{row['latency']:.1f} MS" if (pd.notna(row['latency']) and is_enabled) else "---"
                    st.markdown(f"""<div style="font-size: 0.9rem; color: #00FFC2;">{latency}</div>
                    <div style="font-size: 0.65rem; color: #FFFFFF;">LAST_PING</div>""", unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""<div style="text-align: right;">
                        <span style="display: block; font-size: 1.1rem; font-weight: 700; color: #00FFC2;">{row['health_score']:.0f}%</span>
                        <span style="font-size: 0.65rem; color: #FFFFFF;">HEALTH_INDEX</span>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

elif view_mode == "ALARM CENTER":
    st.markdown(f'<div style="color: #FFFFFF; font-size: 0.75rem; margin-bottom: 20px;">[SYS_SEC] ALARM_PROPAGATION_LOG</div>', unsafe_allow_html=True)
    if not alerts_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("CRITICAL", len(alerts_df[alerts_df['severity'] == 1]))
        col2.metric("HIGH", len(alerts_df[alerts_df['severity'] == 2]))
        col3.metric("MEDIUM", len(alerts_df[alerts_df['severity'] == 3]))
        col4.metric("OPEN", len(alerts_df[alerts_df['status'] == 'OPEN']))
        
        st.markdown(f'<div style="border-bottom: 1px solid #1f2937; margin: 2rem 0;"></div>', unsafe_allow_html=True)
        
        for idx, alert in alerts_df.iterrows():
            severity = alert.get('severity', 3)
            color_border = "#ff0055" if severity == 1 else ("#f59e0b" if severity == 2 else "#00D2FF")
            
            st.markdown(f"""<div class="matrix-card" style="border-left: 3px solid {color_border};">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: {color_border}; font-weight: 800;">[{alert.get('alert_type', 'Unknown')}]</span>
                    <span style="color: #FFFFFF; font-size: 0.7rem;">{alert.get('timestamp', '')}</span>
                </div>
                <div style="margin-top: 10px; font-size: 0.95rem;">
                    <span style="color: #FFFFFF;">TARGET:</span> <span style="color: #00FFC2;">{alert.get('device_ip', 'N/A')}</span>
                </div>
                <div style="margin-top: 5px; color: #00FFC2; font-size: 0.9rem;">
                    {alert.get('message', '')}
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("System Normal: No alerts active")

elif view_mode == "BANDWIDTH DPI":
    st.markdown('<div class="section-title">Deep DPI & Traffic Analysis</div>', unsafe_allow_html=True)
    
    import psutil
    
    # Get real system network stats
    net_io = psutil.net_io_counters()
    net_per_nic = psutil.net_io_counters(pernic=True)
    connections = psutil.net_connections(kind='inet')
    
    # Summary metrics
    sent_mb = net_io.bytes_sent / (1024 * 1024)
    recv_mb = net_io.bytes_recv / (1024 * 1024)
    total_mb = sent_mb + recv_mb
    active_conns = len([c for c in connections if c.status == 'ESTABLISHED'])
    listening = len([c for c in connections if c.status == 'LISTEN'])
    total_conns = len(connections)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Sent", f"{sent_mb:.1f} MB")
    col2.metric("Total Received", f"{recv_mb:.1f} MB")
    col3.metric("Combined Volume", f"{total_mb:.1f} MB")
    col4.metric("Active Connections", active_conns)
    col5.metric("Listening Ports", listening)
    col6.metric("Total Sockets", total_conns)
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### Active Connections")
        conn_data = []
        for c in connections:
            if c.status == 'ESTABLISHED' and c.raddr:
                conn_data.append({
                    'Local IP': f"{c.laddr.ip}:{c.laddr.port}",
                    'Remote IP': f"{c.raddr.ip}:{c.raddr.port}",
                    'Status': c.status,
                    'PID': c.pid if c.pid else '-'
                })
        if conn_data:
            st.dataframe(pd.DataFrame(conn_data[:20]), use_container_width=True, hide_index=True)
        else:
            st.info("No active connections detected.")
    
    with col_right:
        st.markdown("### Network Interfaces")
        nic_data = []
        for nic_name, nic_stats in net_per_nic.items():
            if nic_stats.bytes_sent > 0 or nic_stats.bytes_recv > 0:
                nic_data.append({
                    'Interface': nic_name[:25],
                    'Sent (MB)': round(nic_stats.bytes_sent / (1024 * 1024), 2),
                    'Recv (MB)': round(nic_stats.bytes_recv / (1024 * 1024), 2),
                    'Packets Out': f"{nic_stats.packets_sent:,}",
                    'Packets In': f"{nic_stats.packets_recv:,}",
                    'Errors': nic_stats.errin + nic_stats.errout
                })
        if nic_data:
            st.dataframe(pd.DataFrame(nic_data), use_container_width=True, hide_index=True)
        else:
            st.info("No active interfaces.")
    
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### Protocol Distribution (Connections)")
        # Count connections by status
        status_counts = {}
        for c in connections:
            status_counts[c.status] = status_counts.get(c.status, 0) + 1
        if status_counts:
            fig = go.Figure(data=[go.Pie(
                labels=list(status_counts.keys()),
                values=list(status_counts.values()),
                hole=0.4,
                marker=dict(colors=['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']),
                textfont=dict(color='white', size=12)
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'), height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(font=dict(color='#e2e8f0'))
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        st.markdown("### Bandwidth by Interface")
        if nic_data:
            nic_names = [n['Interface'][:15] for n in nic_data]
            sent_vals = [n['Sent (MB)'] for n in nic_data]
            recv_vals = [n['Recv (MB)'] for n in nic_data]
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name='Sent (MB)', x=nic_names, y=sent_vals, marker_color='#0ea5e9'))
            fig2.add_trace(go.Bar(name='Recv (MB)', x=nic_names, y=recv_vals, marker_color='#10b981'))
            fig2.update_layout(
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'), height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(font=dict(color='#e2e8f0')),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Also try to show NetFlow data if available
    try:
        flow_summary = get_flow_summary(hours=1)
        if flow_summary and dict(flow_summary).get('total_flows', 0) > 0:
            st.markdown("---")
            st.markdown("### NetFlow/sFlow Enterprise Data")
            top_talkers = get_top_talkers(hours=1, limit=20)
            protocols = get_protocol_distribution(hours=1)
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                st.markdown("#### Top Talkers")
                if top_talkers:
                    talker_data = [{'IP Node': row['src_ip'], 'Transferred (MB)': round(row['total_bytes'] / (1024 * 1024), 2),
                        'Sessions': row['flow_count']} for row in top_talkers]
                    st.dataframe(pd.DataFrame(talker_data), use_container_width=True, hide_index=True)
            with fcol2:
                st.markdown("#### Protocol Layers")
                if protocols:
                    protocol_data = [{'Protocol': row['protocol'], 'Transferred (MB)': round(row['total_bytes'] / (1024 * 1024), 2),
                        'Sessions': row['flow_count']} for row in protocols]
                    st.dataframe(pd.DataFrame(protocol_data), use_container_width=True, hide_index=True)
    except Exception:
        pass

elif view_mode == "INTELLIGENCE":
    st.markdown('<div class="section-title">Intelligence Documentation</div>', unsafe_allow_html=True)
    st.markdown("<p style='color: #FFFFFF; margin-bottom: 10px;'>Select a report type from the dropdown below to generate a live intelligence document.</p>", unsafe_allow_html=True)
    report_type = st.selectbox("Report Type (click to expand)", ["Device Summary", "Alert Summary", "Traffic Summary", "Health Report"],
                               index=0, help="Choose which report to generate")
    
    if st.button("Generate Report", type="primary"):
        st.markdown("---")
        
        if report_type == "Device Summary":
            st.markdown("### Device Fleet Report")
            try:
                dev_data = get_latest_ping_status()
                if dev_data:
                    dev_df = pd.DataFrame(dev_data)
                    total = len(dev_df)
                    online = len(dev_df[dev_df['status'] == 'Online']) if 'status' in dev_df.columns else 0
                    offline = total - online
                    avg_lat = dev_df['latency'].mean() if 'latency' in dev_df.columns else 0
                    
                    r1, r2, r3, r4 = st.columns(4)
                    r1.metric("Total Devices", total)
                    r2.metric("Online", online)
                    r3.metric("Offline", offline)
                    r4.metric("Avg Latency", f"{avg_lat:.1f}ms")
                    
                    st.markdown("#### Device Status Table")
                    st.dataframe(dev_df, use_container_width=True, hide_index=True)
                    
                    st.markdown(f"""
                    <div class="report-card">
                        <strong style="color: #38bdf8;">Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                        <strong>Fleet Health:</strong> {online}/{total} devices operational ({(online/total*100) if total > 0 else 0:.0f}% uptime)<br>
                        <strong>Average Response Time:</strong> {avg_lat:.1f}ms
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No device data available yet. Start monitoring first.")
            except Exception as e:
                st.error(f"Error generating device report: {e}")
        
        elif report_type == "Alert Summary":
            st.markdown("### Alert Intelligence Report")
            try:
                alerts = get_alert_history(hours=24)
                if alerts:
                    alert_list = [dict(a) for a in alerts]
                    al_df = pd.DataFrame(alert_list)
                    
                    total_alerts = len(al_df)
                    critical_count = len(al_df[al_df['severity'] == 1]) if 'severity' in al_df.columns else 0
                    open_count = len(al_df[al_df['status'] == 'OPEN']) if 'status' in al_df.columns else 0
                    
                    r1, r2, r3 = st.columns(3)
                    r1.metric("Total Alerts (24h)", total_alerts)
                    r2.metric("Critical", critical_count)
                    r3.metric("Open", open_count)
                    
                    st.markdown("#### Alert History Table")
                    st.dataframe(al_df, use_container_width=True, hide_index=True)
                    
                    st.markdown(f"""
                    <div class="report-card">
                        <strong style="color: #38bdf8;">Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                        <strong>Alert Volume:</strong> {total_alerts} alerts in last 24 hours<br>
                        <strong>Critical Events:</strong> {critical_count} | <strong>Open Issues:</strong> {open_count}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No alerts recorded in the last 24 hours.")
            except Exception as e:
                st.error(f"Error generating alert report: {e}")
        
        elif report_type == "Traffic Summary":
            st.markdown("### Traffic Analysis Report")
            try:
                flow_summary = get_flow_summary(hours=24)
                if flow_summary and dict(flow_summary).get('total_flows', 0) > 0:
                    fs = dict(flow_summary)
                    r1, r2, r3 = st.columns(3)
                    r1.metric("Total Flows", f"{fs.get('total_flows', 0):,}")
                    r2.metric("Total Volume", f"{fs.get('total_bytes', 0) / (1024*1024):.2f} MB")
                    r3.metric("Total Packets", f"{fs.get('total_packets', 0):,}")
                    
                    top_talkers = get_top_talkers(hours=24, limit=10)
                    if top_talkers:
                        st.markdown("#### Top Talkers (24h)")
                        talker_data = [{'IP': r['src_ip'], 'MB': round(r['total_bytes']/(1024*1024), 2), 'Flows': r['flow_count']} for r in top_talkers]
                        st.dataframe(pd.DataFrame(talker_data), use_container_width=True, hide_index=True)
                else:
                    st.info("No traffic flow data captured yet. NetFlow/sFlow sensors pending.")
            except Exception as e:
                st.error(f"Error generating traffic report: {e}")
        
        elif report_type == "Health Report":
            st.markdown("### System Health Report")
            try:
                db_stats = get_database_stats()
                dev_data = get_latest_ping_status()
                
                if db_stats:
                    r1, r2, r3, r4 = st.columns(4)
                    r1.metric("DB Size", f"{db_stats.get('db_size_mb', 0)} MB")
                    r2.metric("Ping Records", f"{db_stats.get('ping_records', 0):,}")
                    r3.metric("Flow Records", f"{db_stats.get('flow_records', 0):,}")
                    r4.metric("Monitored Devices", db_stats.get('devices', 0))
                
                if dev_data:
                    dev_df = pd.DataFrame(dev_data)
                    total = len(dev_df)
                    online = len(dev_df[dev_df['status'] == 'Online']) if 'status' in dev_df.columns else 0
                    health_pct = (online / total * 100) if total > 0 else 0
                    
                    health_color = '#10b981' if health_pct >= 80 else '#f59e0b' if health_pct >= 50 else '#ef4444'
                    health_label = 'HEALTHY' if health_pct >= 80 else 'DEGRADED' if health_pct >= 50 else 'CRITICAL'
                    
                    st.markdown(f"""
                    <div class="report-card" style="border-left-color: {health_color};">
                        <strong style="color: {health_color}; font-size: 1.3em;">System Status: {health_label}</strong><br><br>
                        <strong style="color: #38bdf8;">Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                        <strong>Network Health:</strong> {health_pct:.0f}% ({online}/{total} devices online)<br>
                        <strong>Database:</strong> {db_stats.get('db_size_mb', 0)} MB with {db_stats.get('ping_records', 0):,} records<br>
                        <strong>Uptime Assessment:</strong> {'All systems nominal' if health_pct >= 80 else 'Attention required - some devices offline'}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No device data available. Start monitoring to generate health reports.")
            except Exception as e:
                st.error(f"Error generating health report: {e}")

elif view_mode == "INTERCEPTION":
    st.markdown('<div class="section-title" style="margin-bottom: 5px;">Deep Packet Analytics - Live Interception</div>', unsafe_allow_html=True)
    
    if 'capture_active' not in st.session_state:
        st.session_state.capture_active = False
    if 'capture_instance' not in st.session_state:
        st.session_state.capture_instance = None
    if 'packet_selection_idx' not in st.session_state:
        st.session_state.packet_selection_idx = -1


    capture = st.session_state.get('capture_instance')

    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown("<p style='color: #FFFFFF; font-size: 0.9em; margin-top: 0;'>Monitoring Promiscuous Network Interface</p>", unsafe_allow_html=True)
    with col2:
        if not st.session_state.capture_active:
            if st.button("▶️ Initialize Link"):
                try:
                    from packet_capture import start_packet_capture_thread
                    st.session_state.capture_instance = start_packet_capture_thread(packet_count=0) # run indefinitely
                    st.session_state.capture_active = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error starting capture: {e}")
        else:
            if st.button("⏹️ Terminate Link"):
                if st.session_state.capture_instance:
                    st.session_state.capture_instance.stop_capture()
                    st.session_state.capture_active = False
                st.rerun()

    if capture:
        packets = capture.get_packets(limit=50) # Keep 50 on screen for performance
        stats = capture.get_stats()
        
        # Wireshark Top Bar Overview
        stats_cols = st.columns(6)
        stats_cols[0].metric("Intercepted", stats.get('total_packets', 0))
        stats_cols[1].metric("Payload (MB)", round(stats.get('total_bytes', 0) / (1024 * 1024), 3))
        stats_cols[2].metric("TCP Segs", stats.get('protocol_TCP', 0))
        stats_cols[3].metric("UDP Dgrms", stats.get('protocol_UDP', 0))
        stats_cols[4].metric("DNS Queries", stats.get('protocol_DNS', 0))
        stats_cols[5].metric("ICMP Echos", stats.get('protocol_ICMP', 0))
        
        st.markdown("---")

        if packets:
            packet_df = pd.DataFrame(packets)
            
            # Wireshark Row Coloring (Pandas Styler supports CSS background colors inside Streamlit!)
            def wireshark_colors(row):
                bg_color = 'rgba(240,240,240,1)' # Light gray default
                text_color = '#1e293b' # Dark slate text for readability
                
                p = str(row['Protocol']).upper()
                if 'TCP' in p or 'TLS' in p:
                    bg_color = 'rgba(187, 247, 208, 0.85)' # Solid green tint
                elif 'UDP' in p or 'DNS' in p:
                    bg_color = 'rgba(186, 230, 253, 0.85)' # Solid blue tint
                elif 'ICMP' in p:
                    bg_color = 'rgba(251, 207, 232, 0.85)' # Solid pink tint
                elif 'ARP' in p:
                    bg_color = 'rgba(254, 240, 138, 0.85)' # Solid yellow tint
                    
                style = f'background-color: {bg_color}; color: {text_color}; font-weight: 500;'
                return [style] * len(row)

            # Reordering columns to exact Wireshark layout
            display_cols = ['no', 'timestamp', 'src_ip', 'dst_ip', 'protocol', 'size', 'info']
            view_df = packet_df[display_cols].copy()
            view_df.rename(columns={'no': 'No.', 'timestamp': 'Time', 'src_ip': 'Source', 'dst_ip': 'Destination', 
                                    'protocol': 'Protocol', 'size': 'Length', 'info': 'Info'}, inplace=True)
            
            styled_df = view_df.style.apply(wireshark_colors, axis=1)
            
            # The Main Log List
            st.dataframe(styled_df, use_container_width=True, hide_index=True, height=350)
            
            # The Deep Inspector (Mimics Wireshark's bottom panes)
            st.markdown("### Deep Payload Inspector")
            
            # Because live capture scrolling removes focus, we use a slider to lock onto a frame
            max_p = len(packet_df)
            if max_p > 1:
                slider_val = st.slider("Scrub frame index (Slide back to analyze historical frames)", 
                                       min_value=1, max_value=max_p, value=max_p)
            else:
                slider_val = 1
                st.caption("Awaiting additional frames for scrubber...")
            
            if slider_val > 0:
                selected_p = packet_df.iloc[slider_val - 1] # 0-indexed offset
                
                col_tree, col_hex = st.columns([1, 1.2])
                with col_tree:
                    st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.8); padding: 15px; border-radius: 8px; border-left: 3px solid {COLORS['secondary']}; font-family: monospace;">
                        <span style="color: #FFFFFF;">▶ Frame {selected_p['no']}:</span> {selected_p['size']} bytes on wire ({selected_p['size'] * 8} bits)<br>
                        <span style="color: #FFFFFF;">▶ Ethernet II, Src:</span> 00:00:00:00:00:00, Dst: ff:ff:ff:ff:ff:ff<br>
                        <span style="color: #FFFFFF;">▶ Internet Protocol Version 4,</span> Src: {selected_p['src_ip']}, Dst: {selected_p['dst_ip']}<br>
                        <span style="color: #FFFFFF;">▶ {selected_p['protocol']}:</span> Src Port: {selected_p['src_port']}, Dst Port: {selected_p['dst_port']}<br><br>
                        <span style="color: #38bdf8;">» Info: {selected_p['info']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_hex:
                    hex_data = selected_p.get('hex_dump', 'No payload')
                    # format hex neatly in grid
                    st.markdown(f"""
                    <div style="background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #1e293b; color: #f8fafc; font-family: 'Consolas', 'Courier New', monospace; font-size: 0.85em; white-space: pre-wrap;">{textwrap.fill(hex_data, width=47)}</div>
                    """, unsafe_allow_html=True)
            
        else:
            st.info("Awaiting line hook establishing...")
            
        # Refresh loop
        if st.session_state.capture_active:
            time.sleep(1.0) # Tick
            st.rerun()
