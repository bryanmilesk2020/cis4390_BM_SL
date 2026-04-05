import streamlit as st
import time
import json
import csv
import io
import base64
from blockchain import Blockchain, Transaction
from auth import authenticate, ROLE_PERMISSIONS

st.set_page_config(
    page_title="LedgerCore v2 · Document Chain",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# Aesthetic: Palantir / Chainalysis / CrowdStrike — dense, terminal-adjacent,
# zero decoration, every pixel earns its place. Neutral near-black base with
# a single cold cyan accent (#00d4ff) and amber alert states.
# Fonts: IBM Plex Mono (data / IDs) + IBM Plex Sans (UI copy)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* ── tokens ── */
:root {
  --bg0:     #080b10;
  --bg1:     #0d1117;
  --bg2:     #111820;
  --bg3:     #17202e;
  --border:  #1c2b3a;
  --border2: #243447;
  --text0:   #e8edf3;
  --text1:   #8fa3b8;
  --text2:   #4d6478;
  --text3:   #2d3f52;
  --cyan:    #00d4ff;
  --cyan-dim:#004d5e;
  --cyan-bg: #001a22;
  --green:   #00e676;
  --green-bg:#001a0a;
  --amber:   #ffab00;
  --amber-bg:#1a1000;
  --red:     #ff4444;
  --red-bg:  #1a0505;
  --purple:  #9c6bff;
  --mono:    'IBM Plex Mono', monospace;
  --sans:    'IBM Plex Sans', sans-serif;
}

/* ── base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp { font-family: var(--sans); background: var(--bg0); color: var(--text0); }
.main .block-container { padding: 0 2rem 3rem 2rem; max-width: 1440px; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg1); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ══════════════════════════════════════════════════
   LOGIN
══════════════════════════════════════════════════ */
.lc-login-stage {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 1fr 480px 1fr;
    grid-template-rows: 1fr auto 1fr;
    align-items: center;
}
.lc-login-panel {
    grid-column: 2;
    grid-row: 2;
    background: var(--bg1);
    border: 1px solid var(--border);
    border-top: 2px solid var(--cyan);
}
.lc-login-header {
    padding: 2rem 2rem 1.5rem 2rem;
    border-bottom: 1px solid var(--border);
}
.lc-login-wordmark {
    display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 1.5rem;
}
.lc-login-wordmark .wm-name {
    font-family: var(--mono); font-size: 1rem; font-weight: 600;
    color: var(--text0); letter-spacing: 0.08em; text-transform: uppercase;
}
.lc-login-wordmark .wm-ver {
    font-family: var(--mono); font-size: 0.65rem; color: var(--cyan);
    letter-spacing: 0.06em;
}
.lc-login-heading { font-size: 0.8rem; font-weight: 600; color: var(--text1); text-transform: uppercase; letter-spacing: 0.1em; }
.lc-login-body { padding: 1.75rem 2rem; }
.lc-login-footer {
    padding: 1.25rem 2rem;
    border-top: 1px solid var(--border);
    background: var(--bg0);
}
.lc-login-footer-label {
    font-family: var(--mono); font-size: 0.62rem; color: var(--text3);
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem;
}
.lc-cred-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.45rem 0;
    border-bottom: 1px solid var(--bg2);
    font-family: var(--mono); font-size: 0.72rem;
}
.lc-cred-row:last-child { border-bottom: none; }
.lc-cred-id   { color: var(--text0); }
.lc-cred-pass { color: var(--text2); margin-left: 0.5rem; }
.lc-role-chip {
    font-size: 0.6rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; padding: 0.1rem 0.5rem;
    border: 1px solid; line-height: 1.6;
}
.chip-admin   { color: var(--cyan);   border-color: var(--cyan-dim);   background: var(--cyan-bg); }
.chip-auditor { color: var(--purple); border-color: #3d2a66;           background: #100a1f; }
.chip-viewer  { color: var(--text1);  border-color: var(--border2);    background: var(--bg2); }

/* ══════════════════════════════════════════════════
   TOPBAR
══════════════════════════════════════════════════ */
.lc-topbar {
    position: sticky; top: 0; z-index: 100;
    background: var(--bg1);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center;
    padding: 0 2rem;
    height: 52px;
    gap: 2rem;
    margin: 0 -2rem 1.75rem -2rem;
}
.lc-topbar-brand {
    display: flex; align-items: baseline; gap: 0.45rem;
    flex-shrink: 0;
}
.lc-topbar-brand .tb-name {
    font-family: var(--mono); font-size: 0.78rem; font-weight: 600;
    color: var(--text0); letter-spacing: 0.12em; text-transform: uppercase;
}
.lc-topbar-brand .tb-ver {
    font-family: var(--mono); font-size: 0.58rem; color: var(--cyan); letter-spacing: 0.06em;
}
.lc-topbar-sep { width: 1px; height: 24px; background: var(--border); flex-shrink: 0; }
.lc-topbar-route {
    font-family: var(--mono); font-size: 0.68rem; color: var(--text2);
    letter-spacing: 0.06em; text-transform: uppercase;
}
.lc-topbar-right { margin-left: auto; display: flex; align-items: center; gap: 1.25rem; }
.lc-node-indicator {
    display: flex; align-items: center; gap: 0.4rem;
    font-family: var(--mono); font-size: 0.62rem; color: var(--text2);
}
.lc-node-indicator .ni-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green); box-shadow: 0 0 5px var(--green);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
.lc-session-info {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.3rem 0.75rem;
    border: 1px solid var(--border);
    font-family: var(--mono); font-size: 0.65rem; color: var(--text1);
}
.lc-session-info .si-user { color: var(--text0); font-weight: 500; }
.lc-session-info .si-sep  { color: var(--text3); }

/* ══════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg1) !important;
    border-right: 1px solid var(--border) !important;
    width: 220px !important;
}
[data-testid="stSidebar"] .block-container { padding: 0 !important; }
[data-testid="stSidebar"] > div { padding: 0 !important; }

.lc-sidebar-inner { padding: 1.25rem 1rem; }

.lc-sidebar-section {
    font-family: var(--mono); font-size: 0.58rem; font-weight: 600;
    color: var(--text3); text-transform: uppercase; letter-spacing: 0.14em;
    padding: 0.5rem 0 0.4rem 0;
    margin-top: 1rem;
    border-top: 1px solid var(--border);
}
.lc-sidebar-section:first-child { border-top: none; margin-top: 0; }

.lc-nav-item {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.45rem 0.6rem;
    font-size: 0.8rem; color: var(--text1);
    cursor: pointer;
    border-left: 2px solid transparent;
    transition: color 0.1s, border-color 0.1s;
    margin-bottom: 0.1rem;
}
.lc-nav-item.active { color: var(--cyan); border-left-color: var(--cyan); background: var(--cyan-bg); }
.lc-nav-item.locked { color: var(--text3); cursor: not-allowed; }
.lc-nav-item .ni-icon { font-size: 0.75rem; width: 14px; text-align: center; }
.lc-nav-item .ni-lock { margin-left: auto; font-size: 0.6rem; color: var(--text3); }

.lc-user-block {
    padding: 0.75rem;
    background: var(--bg2);
    border: 1px solid var(--border);
    margin-bottom: 0.75rem;
}
.lc-user-block .ub-handle { font-family: var(--mono); font-size: 0.72rem; color: var(--text0); font-weight: 500; }
.lc-user-block .ub-role   { font-size: 0.68rem; color: var(--text2); margin-top: 0.2rem; }

.lc-stat-line {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.35rem 0;
    border-bottom: 1px solid var(--bg2);
    font-size: 0.72rem;
}
.lc-stat-line:last-child { border-bottom: none; }
.lc-stat-line .sl-label { color: var(--text2); }
.lc-stat-line .sl-value { font-family: var(--mono); color: var(--text0); font-size: 0.7rem; }

/* ══════════════════════════════════════════════════
   KPI STRIP
══════════════════════════════════════════════════ */
.lc-kpi-strip {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    border: 1px solid var(--border);
    margin-bottom: 1.75rem;
}
.lc-kpi-cell {
    padding: 1rem 1.25rem;
    border-right: 1px solid var(--border);
    position: relative;
}
.lc-kpi-cell:last-child { border-right: none; }
.lc-kpi-cell::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: var(--cyan);
    opacity: 0;
    transition: opacity 0.2s;
}
.lc-kpi-cell:hover::after { opacity: 1; }
.lc-kpi-label {
    font-family: var(--mono); font-size: 0.58rem; color: var(--text2);
    text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.6rem;
}
.lc-kpi-value {
    font-family: var(--mono); font-size: 1.65rem; font-weight: 600;
    color: var(--text0); letter-spacing: -0.02em; line-height: 1;
}
.lc-kpi-value.dim { font-size: 1.2rem; }
.lc-kpi-sub {
    font-size: 0.65rem; color: var(--text2); margin-top: 0.3rem;
}

/* ══════════════════════════════════════════════════
   SECTION HEADER
══════════════════════════════════════════════════ */
.lc-sh {
    display: flex; align-items: center; gap: 0.75rem;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}
.lc-sh-label {
    font-family: var(--mono); font-size: 0.65rem; font-weight: 600;
    color: var(--text2); text-transform: uppercase; letter-spacing: 0.12em;
    white-space: nowrap;
}
.lc-sh-count {
    font-family: var(--mono); font-size: 0.6rem; color: var(--cyan);
    background: var(--cyan-bg); border: 1px solid var(--cyan-dim);
    padding: 0 0.4rem; line-height: 1.7;
}

/* ══════════════════════════════════════════════════
   DATA TABLE / TX LIST
══════════════════════════════════════════════════ */
.lc-tx-table { width: 100%; border-collapse: collapse; }
.lc-tx-table th {
    font-family: var(--mono); font-size: 0.58rem; color: var(--text3);
    text-transform: uppercase; letter-spacing: 0.1em; font-weight: 500;
    padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--border);
    text-align: left; background: var(--bg1); white-space: nowrap;
}
.lc-tx-table td {
    padding: 0.55rem 0.75rem;
    border-bottom: 1px solid var(--bg2);
    font-size: 0.78rem; color: var(--text1);
    vertical-align: middle;
}
.lc-tx-table tr:hover td { background: var(--bg2); color: var(--text0); }
.lc-tx-table td.mono { font-family: var(--mono); font-size: 0.72rem; }
.lc-tx-table td.bright { color: var(--text0); font-weight: 500; }

.lc-type-pill {
    font-family: var(--mono); font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    padding: 0.15rem 0.5rem; border: 1px solid; line-height: 1.6;
    white-space: nowrap; display: inline-block;
}
.pill-invoice  { color: var(--green);  border-color: #00602d; background: var(--green-bg); }
.pill-contract { color: var(--purple); border-color: #3d2a66; background: #100a1f; }
.pill-att      { color: var(--cyan);   border-color: var(--cyan-dim); background: var(--cyan-bg); }

/* ══════════════════════════════════════════════════
   BLOCK CARDS
══════════════════════════════════════════════════ */
.lc-block-card {
    border: 1px solid var(--border);
    background: var(--bg1);
    margin-bottom: 0.5rem;
    transition: border-color 0.15s;
}
.lc-block-card:hover { border-color: var(--border2); }
.lc-block-header {
    display: flex; align-items: center; gap: 1rem;
    padding: 0.7rem 1rem;
    background: var(--bg1);
    border-bottom: 1px solid var(--border);
    font-family: var(--mono); font-size: 0.7rem;
}
.lc-block-index {
    color: var(--cyan); font-weight: 600; font-size: 0.75rem; flex-shrink: 0;
}
.lc-block-hash {
    color: var(--text2); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1;
}
.lc-block-meta { color: var(--text2); flex-shrink: 0; margin-left: auto; }
.lc-block-body { padding: 0.75rem 1rem; }

/* ══════════════════════════════════════════════════
   HASH DISPLAY
══════════════════════════════════════════════════ */
.lc-hash-block {
    background: var(--bg0);
    border: 1px solid var(--border);
    padding: 0.6rem 0.9rem;
    margin: 0.35rem 0;
    font-family: var(--mono); font-size: 0.66rem;
    word-break: break-all; line-height: 1.7;
}
.lc-hash-block .hb-key {
    color: var(--text3); font-size: 0.58rem; text-transform: uppercase;
    letter-spacing: 0.1em; display: block; margin-bottom: 0.2rem;
}
.lc-hash-block .hb-val { color: var(--cyan); }
.lc-hash-block .hb-prev{ color: var(--text1); }

/* ══════════════════════════════════════════════════
   FILE PREVIEW
══════════════════════════════════════════════════ */
.lc-file-card {
    background: var(--bg0);
    border: 1px solid var(--border);
    padding: 1rem;
    display: flex; align-items: flex-start; gap: 1rem; margin: 0.75rem 0;
}
.lc-file-card .fc-icon  { font-size: 1.6rem; flex-shrink: 0; }
.lc-file-card .fc-body  { flex: 1; min-width: 0; }
.lc-file-card .fc-name  { font-size: 0.82rem; font-weight: 600; color: var(--text0); word-break: break-all; }
.lc-file-card .fc-meta  { font-family: var(--mono); font-size: 0.65rem; color: var(--text2); margin-top: 0.25rem; }
.lc-file-card .fc-hlabel{ font-family: var(--mono); font-size: 0.56rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.6rem; display: block; }
.lc-file-card .fc-hash  { font-family: var(--mono); font-size: 0.63rem; color: var(--cyan); word-break: break-all; margin-top: 0.15rem; }

/* ══════════════════════════════════════════════════
   ACCESS DENIED
══════════════════════════════════════════════════ */
.lc-denied {
    border: 1px solid var(--border);
    background: var(--bg1);
    padding: 3.5rem 2rem;
    text-align: center;
}
.lc-denied-code {
    font-family: var(--mono); font-size: 0.62rem; color: var(--red);
    text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 1rem;
}
.lc-denied h3 { font-size: 0.95rem; font-weight: 600; color: var(--text0); margin-bottom: 0.5rem; }
.lc-denied p  { font-size: 0.8rem; color: var(--text2); }
.lc-denied-role {
    display: inline-block; margin-top: 1.25rem;
    font-family: var(--mono); font-size: 0.65rem;
    color: var(--text3); background: var(--bg2);
    border: 1px solid var(--border); padding: 0.3rem 0.75rem;
}

/* ══════════════════════════════════════════════════
   INTEGRITY STATES
══════════════════════════════════════════════════ */
.lc-ok   { background: var(--green-bg); border: 1px solid #00602d; padding: 0.75rem 1rem; font-family: var(--mono); font-size: 0.72rem; color: var(--green); }
.lc-fail { background: var(--red-bg);   border: 1px solid #600000; padding: 0.75rem 1rem; font-family: var(--mono); font-size: 0.72rem; color: var(--red);   }
.lc-ok .ih, .lc-fail .ih { font-size: 0.62rem; opacity: 0.7; margin-top: 0.4rem; word-break: break-all; }

/* ══════════════════════════════════════════════════
   FORM ELEMENTS
══════════════════════════════════════════════════ */
.lc-field-group { margin-bottom: 1.1rem; }
.lc-field-group .lc-label {
    font-family: var(--mono); font-size: 0.6rem; color: var(--text2);
    text-transform: uppercase; letter-spacing: 0.1em;
    display: block; margin-bottom: 0.4rem;
}
.lc-panel {
    background: var(--bg1);
    border: 1px solid var(--border);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.lc-panel-title {
    font-family: var(--mono); font-size: 0.6rem; color: var(--text3);
    text-transform: uppercase; letter-spacing: 0.12em;
    padding-bottom: 0.75rem; margin-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

/* ══════════════════════════════════════════════════
   MEMPOOL
══════════════════════════════════════════════════ */
.lc-pool-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    background: var(--bg0);
    border: 1px solid var(--border);
    border-left: 2px solid var(--amber);
    margin-bottom: 0.35rem;
    font-size: 0.75rem;
}
.lc-pool-row .pr-id { font-family: var(--mono); color: var(--text0); font-weight: 500; }
.lc-pool-row .pr-sender { color: var(--text2); font-size: 0.68rem; margin-left: auto; }

.lc-empty {
    padding: 2.5rem 1.5rem; text-align: center;
    border: 1px dashed var(--border); background: var(--bg0);
    font-family: var(--mono); font-size: 0.7rem; color: var(--text3);
    letter-spacing: 0.06em;
}

/* ══════════════════════════════════════════════════
   SEARCH TOOLBAR
══════════════════════════════════════════════════ */
.lc-toolbar {
    display: flex; align-items: center; gap: 0;
    border: 1px solid var(--border);
    background: var(--bg1);
    margin-bottom: 1rem;
}
.lc-toolbar-item {
    padding: 0 1rem;
    border-right: 1px solid var(--border);
    height: 38px; display: flex; align-items: center;
    font-family: var(--mono); font-size: 0.68rem; color: var(--text2);
}
.lc-toolbar-item:last-child { border-right: none; margin-left: auto; }

/* ══════════════════════════════════════════════════
   SECURITY PAGE
══════════════════════════════════════════════════ */
.lc-verify-box {
    border: 1px solid var(--border);
    background: var(--bg1);
    padding: 2rem;
}
.lc-verify-box .vb-title {
    font-family: var(--mono); font-size: 0.78rem; font-weight: 600;
    color: var(--text0); text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.lc-verify-box .vb-desc {
    font-size: 0.8rem; color: var(--text2); line-height: 1.7;
    margin-bottom: 1.5rem;
}
.lc-chain-ok   { display:flex;align-items:center;gap:0.75rem;padding:1rem 1.25rem;background:var(--green-bg);border:1px solid #00602d;font-family:var(--mono);font-size:0.75rem;color:var(--green);margin-top:1rem; }
.lc-chain-fail { display:flex;align-items:center;gap:0.75rem;padding:1rem 1.25rem;background:var(--red-bg);border:1px solid #600000;font-family:var(--mono);font-size:0.75rem;color:var(--red);margin-top:1rem; }

/* ══════════════════════════════════════════════════
   STREAMLIT WIDGET OVERRIDES
══════════════════════════════════════════════════ */
div[data-testid="metric-container"] { display: none !important; }

[data-testid="stTextInput"] > label,
[data-testid="stNumberInput"] > label,
[data-testid="stSelectbox"] > label,
[data-testid="stFileUploader"] > label {
    font-family: var(--mono) !important;
    font-size: 0.6rem !important; font-weight: 500 !important;
    color: var(--text2) !important;
    text-transform: uppercase !important; letter-spacing: 0.1em !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: var(--bg0) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 0 !important;
    color: var(--text0) !important;
    font-family: var(--mono) !important; font-size: 0.78rem !important;
    padding: 0.55rem 0.75rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 1px var(--cyan-dim) !important;
    outline: none !important;
}
[data-testid="stSelectbox"] > div > div {
    background: var(--bg0) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 0 !important;
    color: var(--text0) !important;
    font-family: var(--mono) !important; font-size: 0.78rem !important;
}

.stButton > button[kind="primary"] {
    background: transparent !important;
    color: var(--cyan) !important;
    border: 1px solid var(--cyan) !important;
    border-radius: 0 !important;
    font-family: var(--mono) !important; font-weight: 500 !important;
    font-size: 0.72rem !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.25rem !important;
    transition: background 0.15s !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--cyan-bg) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text1) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 0 !important;
    font-family: var(--mono) !important; font-size: 0.7rem !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--cyan) !important; color: var(--cyan) !important;
}
.stDownloadButton > button {
    background: transparent !important;
    color: var(--text1) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 0 !important;
    font-family: var(--mono) !important; font-size: 0.68rem !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
}
.stDownloadButton > button:hover { border-color: var(--cyan) !important; color: var(--cyan) !important; }

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important; padding: 0 !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    font-family: var(--mono) !important; font-size: 0.65rem !important;
    font-weight: 500 !important; text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    border: none !important; border-bottom: 1px solid transparent !important;
    border-radius: 0 !important; padding: 0.75rem 1.5rem !important;
    transition: color 0.1s !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover { color: var(--text1) !important; }
[data-testid="stTabs"] button[aria-selected="true"][data-baseweb="tab"] {
    color: var(--cyan) !important; border-bottom-color: var(--cyan) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }

[data-testid="stExpander"] {
    background: var(--bg1) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    margin-bottom: 0.4rem !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background: var(--bg1) !important;
    font-family: var(--mono) !important; font-size: 0.7rem !important;
    color: var(--text1) !important; padding: 0.65rem 0.9rem !important;
}
[data-testid="stExpander"] summary:hover { background: var(--bg2) !important; color: var(--text0) !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: var(--bg0) !important;
    border-top: 1px solid var(--border) !important;
    padding: 0.9rem 1rem !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important; border-radius: 0 !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg1) !important; color: var(--text3) !important;
    font-family: var(--mono) !important; font-size: 0.6rem !important;
    text-transform: uppercase !important; letter-spacing: 0.08em !important;
}
[data-testid="stDataFrame"] td {
    font-family: var(--mono) !important; color: var(--text1) !important; font-size: 0.72rem !important;
}

[data-testid="stFileUploader"] {
    background: var(--bg0) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 0 !important;
}

.stSuccess > div { background: var(--green-bg) !important; border: 1px solid #00602d !important; border-radius: 0 !important; color: var(--green) !important; font-family: var(--mono) !important; font-size: 0.72rem !important; }
.stError   > div { background: var(--red-bg)   !important; border: 1px solid #600000 !important; border-radius: 0 !important; color: var(--red)   !important; font-family: var(--mono) !important; font-size: 0.72rem !important; }
.stWarning > div { background: var(--amber-bg) !important; border: 1px solid #604000 !important; border-radius: 0 !important; color: var(--amber) !important; font-family: var(--mono) !important; font-size: 0.72rem !important; }
.stInfo    > div { background: var(--cyan-bg)  !important; border: 1px solid var(--cyan-dim) !important; border-radius: 0 !important; color: var(--cyan) !important; font-family: var(--mono) !important; font-size: 0.72rem !important; }

hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Session ────────────────────────────────────────────────────────────────────
if "blockchain"    not in st.session_state: st.session_state.blockchain    = Blockchain()
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user"          not in st.session_state: st.session_state.user          = None
if "login_error"   not in st.session_state: st.session_state.login_error   = ""

bc = st.session_state.blockchain

# ── Utility ────────────────────────────────────────────────────────────────────
def file_icon(fn):
    ext = fn.rsplit(".",1)[-1].lower() if "." in fn else ""
    return {"pdf":"▣","png":"▣","jpg":"▣","jpeg":"▣","txt":"≡","docx":"≡"}.get(ext,"◈")

def fmt_size(n):
    if n < 1024:    return f"{n}B"
    if n < 1048576: return f"{n/1024:.1f}KB"
    return f"{n/1048576:.1f}MB"

def ts(t): return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
def ts_short(t): return time.strftime('%m/%d %H:%M', time.localtime(t))

def pill(doc_type):
    cls = "pill-invoice" if doc_type == "Invoice" else "pill-contract"
    return f'<span class="lc-type-pill {cls}">{doc_type}</span>'

def render_file_card(att):
    mime = att.get("mime_type","")
    if mime.startswith("image/"):
        st.image(base64.b64decode(att["data"]), caption=att["filename"], width=260)
    st.markdown(f"""
    <div class="lc-file-card">
      <div class="fc-icon">{file_icon(att['filename'])}</div>
      <div class="fc-body">
        <div class="fc-name">{att['filename']}</div>
        <div class="fc-meta">{fmt_size(att['size'])} · {mime or 'unknown'}</div>
        <span class="fc-hlabel">sha-256</span>
        <div class="fc-hash">{att.get('sha256','—')}</div>
      </div>
    </div>""", unsafe_allow_html=True)

def access_denied(area="this resource"):
    role = st.session_state.user["role"] if st.session_state.user else "—"
    st.markdown(f"""
    <div class="lc-denied">
      <div class="lc-denied-code">ERR_ACCESS_DENIED · HTTP 403</div>
      <h3>Insufficient Privileges</h3>
      <p>Your session does not have permission to access {area}.<br>Contact your system administrator to request elevated access.</p>
      <div class="lc-denied-role">session.role = "{role}"</div>
    </div>""", unsafe_allow_html=True)

def can(p):   return st.session_state.user and st.session_state.user.get(p, False)
def has_tab(k): return st.session_state.user and k in st.session_state.user.get("tabs", [])

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    _, center, _ = st.columns([1, 1.1, 1])
    with center:
        st.markdown("""
        <div style="padding-top:8vh;">
        <div class="lc-login-panel">
          <div class="lc-login-header">
            <div class="lc-login-wordmark">
              <span class="wm-name">LedgerCore</span>
              <span class="wm-ver">v2.0.0</span>
            </div>
            <div class="lc-login-heading">Authentication Required</div>
          </div>
          <div class="lc-login-body">
        """, unsafe_allow_html=True)

        with st.form("lc_login"):
            st.text_input("Identifier", placeholder="username", key="li_user")
            st.text_input("Secret", type="password", placeholder="••••••••••", key="li_pass")
            st.form_submit_button("AUTHENTICATE →", use_container_width=True, type="primary")

        if st.session_state.get("FormSubmitter:lc_login-AUTHENTICATE →"):
            ok, user = authenticate(
                st.session_state.get("li_user",""),
                st.session_state.get("li_pass","")
            )
            if ok:
                st.session_state.authenticated = True
                st.session_state.user          = user
                st.session_state.login_error   = ""
                st.rerun()
            else:
                st.session_state.login_error = "AUTHENTICATION FAILED — invalid credentials"

        if st.session_state.login_error:
            st.error(st.session_state.login_error)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="lc-login-footer">
          <div class="lc-login-footer-label">Demo Credentials</div>
          <div class="lc-cred-row">
            <span><span class="lc-cred-id">admin</span><span class="lc-cred-pass">/ admin123</span></span>
            <span class="lc-role-chip chip-admin">Admin</span>
          </div>
          <div class="lc-cred-row">
            <span><span class="lc-cred-id">auditor</span><span class="lc-cred-pass">/ audit456</span></span>
            <span class="lc-role-chip chip-auditor">Auditor</span>
          </div>
          <div class="lc-cred-row">
            <span><span class="lc-cred-id">viewer</span><span class="lc-cred-pass">/ view789</span></span>
            <span class="lc-role-chip chip-viewer">Viewer</span>
          </div>
        </div>
        </div></div>
        """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATED
# ══════════════════════════════════════════════════════════════════════════════
user  = st.session_state.user
stats = bc.stats()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="lc-sidebar-inner">
      <div class="lc-sidebar-section" style="border-top:none;margin-top:0;">System</div>
      <div class="lc-user-block">
        <div class="ub-handle">◉ {user['username']}</div>
        <div class="ub-role">{ROLE_PERMISSIONS[user['role']]['label']} · Private Node</div>
      </div>
      <div class="lc-sidebar-section">Navigation</div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("overview", "▦", "Overview"),
        ("submit",   "⊕", "Submit Record"),
        ("ledger",   "≣", "Ledger"),
        ("security", "⊛", "Security"),
    ]
    nav_html = ""
    for key, icon, label in nav_items:
        granted = key in user["tabs"]
        cls     = "active" if key == "overview" else ("lc-nav-item" if granted else "locked")
        lock    = "" if granted else '<span class="ni-lock">🔒</span>'
        nav_html += f'<div class="lc-nav-item {cls}"><span class="ni-icon">{icon}</span>{label}{lock}</div>'
    st.markdown(nav_html, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="lc-sidebar-section">Chain Metrics</div>
      <div class="lc-stat-line"><span class="sl-label">Blocks</span><span class="sl-value">{stats['total_blocks']}</span></div>
      <div class="lc-stat-line"><span class="sl-label">Records</span><span class="sl-value">{stats['total_transactions']}</span></div>
      <div class="lc-stat-line"><span class="sl-label">Pending</span><span class="sl-value">{stats['pending']}</span></div>
      <div class="lc-stat-line"><span class="sl-label">Attachments</span><span class="sl-value">{stats['with_attachments']}</span></div>
      <div class="lc-stat-line"><span class="sl-label">Invoice Vol.</span><span class="sl-value">${stats['total_invoice_value']:,.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("SIGN OUT", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user          = None
        st.rerun()

# ── Topbar ─────────────────────────────────────────────────────────────────────
role_cfg = ROLE_PERMISSIONS[user["role"]]
chip_cls = {"admin":"chip-admin","auditor":"chip-auditor","viewer":"chip-viewer"}.get(user["role"],"chip-viewer")
st.markdown(f"""
<div class="lc-topbar">
  <div class="lc-topbar-brand">
    <span class="tb-name">LedgerCore</span>
    <span class="tb-ver">v2.0</span>
  </div>
  <div class="lc-topbar-sep"></div>
  <div class="lc-topbar-route">Document Chain · Private Network</div>
  <div class="lc-topbar-right">
    <div class="lc-node-indicator">
      <div class="ni-dot"></div>
      NODE ONLINE
    </div>
    <div class="lc-topbar-sep"></div>
    <div class="lc-session-info">
      <span class="si-user">{user['username'].upper()}</span>
      <span class="si-sep">/</span>
      <span class="lc-role-chip {chip_cls}">{role_cfg['label']}</span>
      <span class="si-sep">·</span>
      <span>{ts_short(time.time())}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(["  OVERVIEW  ", "  SUBMIT RECORD  ", "  LEDGER  ", "  SECURITY  "])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    inv_val = f"${stats['total_invoice_value']:,.2f}"
    st.markdown(f"""
    <div class="lc-kpi-strip">
      <div class="lc-kpi-cell">
        <div class="lc-kpi-label">Blocks Minted</div>
        <div class="lc-kpi-value">{stats['total_blocks']}</div>
        <div class="lc-kpi-sub">chain height</div>
      </div>
      <div class="lc-kpi-cell">
        <div class="lc-kpi-label">Total Records</div>
        <div class="lc-kpi-value">{stats['total_transactions']}</div>
        <div class="lc-kpi-sub">committed txns</div>
      </div>
      <div class="lc-kpi-cell">
        <div class="lc-kpi-label">Invoices</div>
        <div class="lc-kpi-value">{stats['total_invoices']}</div>
        <div class="lc-kpi-sub">doc type</div>
      </div>
      <div class="lc-kpi-cell">
        <div class="lc-kpi-label">Contracts</div>
        <div class="lc-kpi-value">{stats['total_contracts']}</div>
        <div class="lc-kpi-sub">doc type</div>
      </div>
      <div class="lc-kpi-cell">
        <div class="lc-kpi-label">Invoice Volume</div>
        <div class="lc-kpi-value dim">{inv_val}</div>
        <div class="lc-kpi-sub">usd · committed</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    all_tx = bc.all_transactions()
    if not all_tx:
        st.markdown('<div class="lc-empty">// NO COMMITTED TRANSACTIONS — SUBMIT AND MINT RECORDS TO POPULATE THE LEDGER</div>', unsafe_allow_html=True)
    else:
        import pandas as pd

        col_a, col_b = st.columns(2, gap="medium")
        block_counts, block_values = {}, {}
        for tx in all_tx:
            idx = f"BLK-{tx['_block_index']:04d}"
            block_counts[idx] = block_counts.get(idx, 0) + 1
            block_values[idx] = block_values.get(idx, 0) + float(tx["details"].get("amount", 0))

        with col_a:
            st.markdown('<div class="lc-sh"><span class="lc-sh-label">Transactions / Block</span></div>', unsafe_allow_html=True)
            st.bar_chart(pd.DataFrame({"Block": list(block_counts), "Count": list(block_counts.values())}).set_index("Block"), color="#00d4ff", height=200)

        with col_b:
            st.markdown('<div class="lc-sh"><span class="lc-sh-label">Invoice Volume / Block (USD)</span></div>', unsafe_allow_html=True)
            st.bar_chart(pd.DataFrame({"Block": list(block_values), "Value": list(block_values.values())}).set_index("Block"), color="#00e676", height=200)

        # Recent tx table
        recent = list(reversed(all_tx[-12:]))
        st.markdown(f'<div class="lc-sh" style="margin-top:1.5rem;"><span class="lc-sh-label">Recent Transactions</span><span class="lc-sh-count">{len(recent)}</span></div>', unsafe_allow_html=True)

        rows_html = ""
        for tx in recent:
            att    = tx.get("attachment")
            att_td = f'<span class="lc-type-pill pill-att">ATT</span>' if att else "—"
            det    = json.dumps(tx["details"])
            rows_html += f"""
            <tr>
              <td class="mono">{ts_short(tx['timestamp'])}</td>
              <td>{pill(tx['doc_type'])}</td>
              <td class="mono bright">{tx['doc_id']}</td>
              <td class="mono">{tx['sender']}</td>
              <td class="mono">BLK-{tx['_block_index']:04d}</td>
              <td class="mono" style="color:var(--text2);font-size:0.65rem;">{det}</td>
              <td>{att_td}</td>
            </tr>"""
        st.markdown(f"""
        <table class="lc-tx-table">
          <thead><tr>
            <th>Timestamp</th><th>Type</th><th>Document ID</th>
            <th>Operator</th><th>Block</th><th>Details</th><th>Att</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SUBMIT RECORD
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    if not has_tab("submit"):
        access_denied("submit_record · write permission required")
    else:
        left_col, right_col = st.columns([1.05, 1], gap="large")

        with left_col:
            st.markdown('<div class="lc-sh"><span class="lc-sh-label">New Transaction</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="lc-panel"><div class="lc-panel-title">// DOCUMENT PARAMETERS</div>', unsafe_allow_html=True)

            doc_type = st.selectbox("Doc Type", ["Invoice", "Contract"])
            if doc_type == "Invoice":
                doc_id  = st.text_input("Invoice ID", placeholder="INV-2025-001")
                amt     = st.number_input("Amount (USD)", min_value=0.0, format="%.2f")
                details = {"amount": amt}
            else:
                doc_id  = st.text_input("Contract ID", placeholder="CTR-2025-001")
                parties = st.text_input("Counterparties", placeholder="Entity A, Entity B")
                details = {"parties": parties}
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="lc-sh"><span class="lc-sh-label">File Attachment</span></div>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Drag file or click to browse · PDF PNG JPG TXT DOCX",
                type=["pdf","png","jpg","jpeg","txt","docx"],
            )
            attachment_ready = None
            if uploaded_file:
                fb = uploaded_file.read()
                attachment_ready = {
                    "filename":  uploaded_file.name,
                    "data":      base64.b64encode(fb).decode(),
                    "size":      len(fb),
                    "mime_type": uploaded_file.type,
                    "sha256":    Blockchain.hash_file(fb),
                }

            with st.form("submit_form", clear_on_submit=True):
                go = st.form_submit_button("SUBMIT TO MEMPOOL →", use_container_width=True, type="primary")
                if go:
                    tx = Transaction(doc_type, doc_id, details, user["username"], attachment=attachment_ready)
                    ok, msg = bc.add_transaction(tx)
                    if ok:
                        extra = f" · attachment={attachment_ready['filename']}" if attachment_ready else ""
                        st.success(f"OK · {msg}{extra}")
                    else:
                        st.error(f"REJECTED · {msg}")

        with right_col:
            st.markdown('<div class="lc-sh"><span class="lc-sh-label">File Preview</span></div>', unsafe_allow_html=True)
            if attachment_ready:
                render_file_card(attachment_ready)
            else:
                st.markdown('<div class="lc-empty">// NO ATTACHMENT STAGED</div>', unsafe_allow_html=True)

            # Mempool
            pending_count = len(bc.pending_transactions)
            st.markdown(f'<div class="lc-sh" style="margin-top:1.5rem;"><span class="lc-sh-label">Mempool</span><span class="lc-sh-count">{pending_count}</span></div>', unsafe_allow_html=True)

            if bc.pending_transactions:
                for tx in bc.pending_transactions:
                    att   = tx.get("attachment")
                    att_s = '<span class="lc-type-pill pill-att" style="font-size:0.55rem;">ATT</span>' if att else ""
                    st.markdown(f"""
                    <div class="lc-pool-row">
                      {pill(tx['doc_type'])}
                      <span class="pr-id">{tx['doc_id']}</span>
                      {att_s}
                      <span class="pr-sender">{tx['sender']} · {ts_short(tx['timestamp'])}</span>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if can("can_mint"):
                    if st.button(f"MINT BLOCK · {pending_count} RECORD{'S' if pending_count!=1 else ''} →", type="primary", use_container_width=True):
                        ok, msg = bc.mint_pending_transactions(user["username"])
                        if ok:
                            st.success(f"OK · {msg}")
                            st.rerun()
                else:
                    st.markdown("""
                    <div class="lc-denied" style="padding:1.25rem;">
                      <div class="lc-denied-code" style="font-size:0.58rem;">MINT_BLOCKED · ROLE_INSUFFICIENT</div>
                      <p style="font-size:0.75rem;margin-top:0.4rem;">Minting requires <strong>admin</strong> role.</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="lc-empty">// MEMPOOL EMPTY · NO PENDING TRANSACTIONS</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LEDGER
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    if not has_tab("ledger"):
        access_denied("ledger · read_ledger permission required")
    else:
        # Toolbar
        tc1, tc2, tc3, tc4 = st.columns([3, 1.5, 0.8, 0.9])
        with tc1:
            search_query = st.text_input("_", placeholder="Search by Document ID, operator, counterparties…", label_visibility="collapsed")
        with tc2:
            filter_type = st.selectbox("_", ["All","Invoice","Contract"], label_visibility="collapsed")
        with tc3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("FILTER", use_container_width=True)
        with tc4:
            all_committed = bc.all_transactions()
            if all_committed:
                def build_csv(txs):
                    out = io.StringIO()
                    w   = csv.DictWriter(out, fieldnames=["block","doc_type","doc_id","sender","timestamp","details","has_attachment","sha256"])
                    w.writeheader()
                    for tx in txs:
                        att = tx.get("attachment") or {}
                        w.writerow({"block":tx["_block_index"],"doc_type":tx["doc_type"],"doc_id":tx["doc_id"],
                                    "sender":tx["sender"],"timestamp":ts(tx["timestamp"]),
                                    "details":json.dumps(tx["details"]),"has_attachment":bool(att),"sha256":att.get("sha256","")})
                    return out.getvalue()
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("EXPORT CSV", build_csv(all_committed), f"ledger_{int(time.time())}.csv", "text/csv", use_container_width=True)

        if search_query or filter_type != "All":
            import pandas as pd
            results = bc.search_transactions(search_query, filter_type)
            st.markdown(f'<div style="font-family:var(--mono);font-size:0.62rem;color:var(--text2);margin:0.5rem 0 0.75rem 0;letter-spacing:0.06em;">> {len(results)} RECORD(S) MATCHED</div>', unsafe_allow_html=True)
            if results:
                rows = [{"Block":f"BLK-{tx['_block_index']:04d}","Type":tx["doc_type"],
                         "Document ID":tx["doc_id"],"Operator":tx["sender"],
                         "Attachment":"YES" if tx.get("attachment") else "—",
                         "Timestamp":ts(tx["timestamp"])} for tx in results]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.warning("NO RECORDS MATCHED")
            st.markdown("<hr>", unsafe_allow_html=True)

        # Block Explorer
        total_blocks = len(bc.chain)
        st.markdown(f'<div class="lc-sh"><span class="lc-sh-label">Block Explorer</span><span class="lc-sh-count">{total_blocks}</span></div>', unsafe_allow_html=True)

        for block in reversed(bc.chain):
            tx_count  = len(block.transactions)
            att_count = sum(1 for tx in block.transactions if tx.get("attachment"))

            if block.index == 0:
                header = f"BLK-0000  ·  GENESIS  ·  {ts(block.timestamp)}  ·  {block.creator_handle}"
            else:
                att_tag = f"  ·  ATT:{att_count}" if att_count else ""
                header  = f"BLK-{block.index:04d}  ·  TXN:{tx_count}{att_tag}  ·  {ts(block.timestamp)}  ·  {block.creator_handle}"

            with st.expander(header, expanded=False):
                st.markdown(f"""
                <div class="lc-hash-block">
                  <span class="hb-key">block_hash</span>
                  <span class="hb-val">{block.hash}</span>
                </div>
                <div class="lc-hash-block">
                  <span class="hb-key">prev_hash</span>
                  <span class="hb-prev">{block.previous_hash}</span>
                </div>""", unsafe_allow_html=True)

                if block.index > 0:
                    st.markdown(f'<div style="font-family:var(--mono);font-size:0.58rem;color:var(--text3);text-transform:uppercase;letter-spacing:0.12em;margin:0.9rem 0 0.5rem 0;">// TRANSACTIONS [{tx_count}]</div>', unsafe_allow_html=True)
                    for i, tx in enumerate(block.transactions):
                        attachment = tx.get("attachment")
                        att_tag    = f"  ·  ATT:{attachment['filename']}" if attachment else ""
                        inner_lbl  = f"TXN-{i+1:03d}  ·  {tx['doc_type'].upper()}  ·  {tx['doc_id']}  ·  {tx['sender']}{att_tag}"

                        with st.expander(inner_lbl, expanded=False):
                            st.json({k:v for k,v in tx.items() if k != "attachment"})
                            if attachment:
                                st.markdown(f'<div style="font-family:var(--mono);font-size:0.58rem;color:var(--text3);text-transform:uppercase;letter-spacing:0.1em;margin:0.75rem 0 0.4rem 0;">// ATTACHMENT</div>', unsafe_allow_html=True)
                                render_file_card(attachment)
                                dl_col, vfy_col = st.columns(2)
                                with dl_col:
                                    st.download_button(
                                        f"DOWNLOAD FILE",
                                        data=base64.b64decode(attachment["data"]),
                                        file_name=attachment["filename"],
                                        mime=attachment.get("mime_type","application/octet-stream"),
                                        key=f"dl_{block.index}_{i}",
                                        use_container_width=True,
                                    )
                                with vfy_col:
                                    if st.button("VERIFY SHA-256", key=f"vfy_{block.index}_{i}", use_container_width=True):
                                        ok, detail = Blockchain.verify_attachment(attachment)
                                        if ok:
                                            st.markdown(f'<div class="lc-ok">✓ INTEGRITY VERIFIED<div class="ih">{detail}</div></div>', unsafe_allow_html=True)
                                        else:
                                            st.markdown(f'<div class="lc-fail">✗ INTEGRITY FAILURE<div class="ih">{detail}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SECURITY
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    if not has_tab("security"):
        access_denied("security · admin_role required")
    else:
        sec_l, sec_m, sec_r = st.columns([0.8, 2.4, 0.8])
        with sec_m:
            st.markdown("""
            <div class="lc-verify-box">
              <div class="vb-title">// Chain Integrity Verification</div>
              <div class="vb-desc">
                Re-derives every block hash from its raw payload and validates the
                cryptographic linkage (prev_hash → hash) across the full chain.
                Any mutation — including a single bit flip — will produce a hash
                mismatch and trigger a CRITICAL alert.
              </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("RUN VERIFICATION →", type="primary", use_container_width=True):
                with st.spinner("Computing hashes…"):
                    time.sleep(1)
                    is_valid = bc.is_chain_valid()
                if is_valid:
                    st.markdown('<div class="lc-chain-ok">✓ &nbsp; CHAIN VALID — ALL BLOCK HASHES VERIFIED — NO TAMPERING DETECTED</div>', unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.markdown('<div class="lc-chain-fail">✗ &nbsp; CRITICAL ALERT — HASH MISMATCH DETECTED — CHAIN INTEGRITY COMPROMISED</div>', unsafe_allow_html=True)

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(f'<div class="lc-sh"><span class="lc-sh-label">Chain Manifest</span><span class="lc-sh-count">{len(bc.chain)}</span></div>', unsafe_allow_html=True)

            import pandas as pd
            manifest = []
            for blk in bc.chain:
                att_c = sum(1 for tx in blk.transactions if isinstance(tx,dict) and tx.get("attachment"))
                manifest.append({
                    "Block":       f"BLK-{blk.index:04d}",
                    "TXN Count":   len(blk.transactions),
                    "Attachments": att_c,
                    "Operator":    blk.creator_handle,
                    "Timestamp":   ts(blk.timestamp),
                    "Hash":        blk.hash[:24]+"…",
                    "Prev Hash":   blk.previous_hash[:16]+"…",
                })
            st.dataframe(pd.DataFrame(manifest), use_container_width=True, hide_index=True)