import streamlit as st
import time
import json
import csv
import io
import base64
from blockchain import Blockchain, Transaction
from auth import authenticate, ROLE_PERMISSIONS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LedgerCore — Document Chain",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Full design system (login + app) ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #070d1a; }
.main .block-container { padding: 2rem 2.5rem 3rem 2.5rem; max-width: 1400px; }

/* ── LOGIN PAGE ── */
.login-wrap {
    min-height: 85vh;
    display: flex; align-items: center; justify-content: center;
}
.login-card {
    width: 100%; max-width: 420px;
    background: #0b1220;
    border: 1px solid #1a2744;
    border-radius: 18px;
    padding: 2.5rem 2.5rem 2rem 2.5rem;
    box-shadow: 0 24px 80px rgba(0,0,0,0.5);
}
.login-logo {
    display: flex; align-items: center; gap: 0.9rem;
    margin-bottom: 2rem;
}
.login-logo .logo-icon {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #2563eb, #0ea5e9);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
}
.login-logo .logo-text .logo-name {
    font-size: 1.25rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.02em;
}
.login-logo .logo-text .logo-sub {
    font-size: 0.7rem; color: #4b6a9b; text-transform: uppercase;
    letter-spacing: 0.1em; font-weight: 500; margin-top: 0.1rem;
}
.login-title  { font-size: 1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.3rem; }
.login-sub    { font-size: 0.82rem; color: #4b6a9b; margin-bottom: 1.75rem; }

.login-divider {
    height: 1px; background: #1a2744; margin: 1.5rem 0;
}

.role-hint {
    background: #060c18;
    border: 1px solid #1a2744;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin-top: 1.25rem;
}
.role-hint .rh-title {
    font-size: 0.65rem; color: #3b5280; text-transform: uppercase;
    letter-spacing: 0.09em; font-weight: 600; margin-bottom: 0.65rem;
}
.role-row {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.5rem;
}
.role-row:last-child { margin-bottom: 0; }
.role-row .rr-creds { font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #64748b; }
.role-row .rr-creds strong { color: #94a3b8; }
.role-badge {
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; padding: 0.15rem 0.55rem; border-radius: 5px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0b1220 !important;
    border-right: 1px solid #1a2744;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem; }

.sidebar-brand {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid #1a2744;
    margin-bottom: 1.5rem;
}
.sidebar-brand .brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #2563eb, #0ea5e9);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.sidebar-brand .brand-name { font-weight: 700; font-size: 1rem; color: #f1f5f9; letter-spacing: -0.01em; }
.sidebar-brand .brand-sub  { font-size: 0.7rem; color: #4b6a9b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; }

.sidebar-section-label {
    font-size: 0.65rem; font-weight: 600; color: #3b5280;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 1.5rem 0 0.6rem 0;
}
.status-dot {
    display: inline-block; width: 7px; height: 7px;
    background: #22c55e; border-radius: 50%;
    margin-right: 0.4rem; box-shadow: 0 0 6px #22c55e;
}
.sidebar-stat {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.55rem 0.75rem;
    background: #0f1b30; border: 1px solid #1a2744;
    border-radius: 8px; margin-bottom: 0.5rem;
}
.sidebar-stat .s-label { font-size: 0.78rem; color: #64748b; font-weight: 500; }
.sidebar-stat .s-value { font-size: 0.88rem; color: #e2e8f0; font-weight: 700; font-family: 'DM Mono', monospace; }

.user-card {
    background: #0f1b30; border: 1px solid #1e3358;
    border-radius: 10px; padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
}
.user-card .uc-name  { font-size: 0.88rem; font-weight: 600; color: #e2e8f0; }
.user-card .uc-role  { font-size: 0.72rem; color: #4b6a9b; margin-top: 0.15rem; }
.user-card .uc-badge {
    display: inline-block; font-size: 0.63rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
    padding: 0.15rem 0.55rem; border-radius: 5px; margin-top: 0.4rem;
}

.access-row {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.4rem 0; font-size: 0.78rem; color: #4b6a9b;
    border-bottom: 1px solid #101e36;
}
.access-row:last-child { border-bottom: none; }
.access-row .ar-icon { font-size: 0.85rem; }
.access-row.granted { color: #64748b; }
.access-row.denied  { color: #2d3f5a; text-decoration: line-through; }
.access-row .ar-lock { font-size: 0.7rem; margin-left: auto; }

/* ── PAGE HEADER ── */
.page-header {
    display: flex; align-items: flex-end; justify-content: space-between;
    padding-bottom: 1.5rem; border-bottom: 1px solid #1a2744; margin-bottom: 2rem;
}
.page-header h1 { font-size: 1.65rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.03em; margin: 0; }
.page-header p  { font-size: 0.85rem; color: #4b6a9b; margin: 0.3rem 0 0 0; }
.header-badge {
    background: #0f2847; border: 1px solid #1d4ed8; color: #60a5fa;
    font-size: 0.72rem; font-weight: 600; padding: 0.3rem 0.8rem;
    border-radius: 99px; text-transform: uppercase; letter-spacing: 0.06em;
}

/* ── ACCESS DENIED GATE ── */
.access-denied {
    background: #0a0f1e; border: 1px solid #1e2a40;
    border-radius: 14px; padding: 3.5rem 2rem;
    text-align: center; margin: 1rem 0;
}
.access-denied .ad-icon  { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.6; }
.access-denied h3        { font-size: 1rem; font-weight: 600; color: #e2e8f0; margin: 0 0 0.4rem 0; }
.access-denied p         { font-size: 0.83rem; color: #4b6a9b; margin: 0; }
.access-denied .ad-role  {
    display: inline-block; margin-top: 1rem;
    font-size: 0.72rem; color: #3b5280; font-family: 'DM Mono', monospace;
    background: #0b1220; border: 1px solid #1a2744;
    border-radius: 6px; padding: 0.35rem 0.75rem;
}

/* ── KPI CARDS ── */
.kpi-grid {
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 1rem; margin-bottom: 2rem;
}
.kpi-card {
    background: #0b1220; border: 1px solid #1a2744;
    border-radius: 12px; padding: 1.2rem 1.3rem;
    position: relative; overflow: hidden; transition: border-color 0.2s;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #2563eb, #0ea5e9);
}
.kpi-card:hover { border-color: #2563eb; }
.kpi-card .kpi-label { font-size: 0.72rem; color: #4b6a9b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.6rem; }
.kpi-card .kpi-value { font-size: 1.75rem; font-weight: 700; color: #f1f5f9; font-family: 'DM Mono', monospace; letter-spacing: -0.02em; line-height: 1; }
.kpi-card .kpi-icon  { position: absolute; top: 1rem; right: 1rem; font-size: 1.1rem; opacity: 0.4; }

/* ── SECTION HEADERS ── */
.section-header { display: flex; align-items: center; gap: 0.6rem; margin: 0 0 1.25rem 0; }
.section-header h2 { font-size: 1rem; font-weight: 600; color: #e2e8f0; margin: 0; letter-spacing: -0.01em; }
.section-header .section-line { flex: 1; height: 1px; background: #1a2744; }

/* ── FORM ── */
.form-panel {
    background: #0b1220; border: 1px solid #1a2744;
    border-radius: 14px; padding: 1.75rem; margin-bottom: 1.5rem;
}
.form-panel .panel-title {
    font-size: 0.72rem; font-weight: 600; color: #4b6a9b;
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 1.25rem; padding-bottom: 0.75rem; border-bottom: 1px solid #1a2744;
}

/* ── WIDGET OVERRIDES ── */
div[data-testid="metric-container"] { display: none; }

[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] > div > div > input {
    background: #0f1b30 !important; border: 1px solid #1e3358 !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important;
    padding: 0.6rem 0.9rem !important;
}
[data-testid="stTextInput"] > div > div > input:focus,
[data-testid="stNumberInput"] > div > div > input:focus {
    border-color: #2563eb !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #0f1b30 !important; border: 1px solid #1e3358 !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
label[data-testid="stWidgetLabel"] p,
.stTextInput label, .stNumberInput label, .stSelectbox label {
    font-size: 0.78rem !important; font-weight: 600 !important;
    color: #64748b !important; text-transform: uppercase !important; letter-spacing: 0.06em !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #fff !important; border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 0.88rem !important; padding: 0.65rem 1.5rem !important;
    transition: opacity 0.15s !important; letter-spacing: 0.01em !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }
.stButton > button[kind="secondary"] {
    background: #0f1b30 !important; color: #94a3b8 !important;
    border: 1px solid #1e3358 !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; font-size: 0.85rem !important;
}
.stButton > button[kind="secondary"]:hover { border-color: #2563eb !important; color: #e2e8f0 !important; }

.stDownloadButton > button {
    background: #0f1b30 !important; color: #60a5fa !important;
    border: 1px solid #1e3358 !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.82rem !important;
}
.stDownloadButton > button:hover { border-color: #2563eb !important; background: #172035 !important; }

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important; border-bottom: 1px solid #1a2744 !important; gap: 0 !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    background: transparent !important; color: #4b6a9b !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 0.85rem !important; border: none !important;
    border-bottom: 2px solid transparent !important; padding: 0.75rem 1.25rem !important;
    margin-right: 0.25rem !important; border-radius: 0 !important; transition: color 0.15s !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover { color: #94a3b8 !important; }
[data-testid="stTabs"] button[aria-selected="true"][data-baseweb="tab"] { color: #60a5fa !important; border-bottom-color: #2563eb !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }

[data-testid="stExpander"] {
    background: #0b1220 !important; border: 1px solid #1a2744 !important;
    border-radius: 10px !important; margin-bottom: 0.75rem !important; overflow: hidden !important;
}
[data-testid="stExpander"]:hover { border-color: #1e3358 !important; }
[data-testid="stExpander"] summary {
    background: #0b1220 !important; padding: 0.9rem 1.1rem !important;
    font-size: 0.88rem !important; font-weight: 600 !important; color: #cbd5e1 !important;
}
[data-testid="stExpander"] summary:hover { background: #0f1b30 !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: #080f1c !important; padding: 1rem 1.25rem !important; border-top: 1px solid #1a2744 !important;
}

[data-testid="stDataFrame"] { border: 1px solid #1a2744 !important; border-radius: 10px !important; overflow: hidden !important; }
[data-testid="stDataFrame"] th { background: #0b1220 !important; color: #4b6a9b !important; font-size: 0.72rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
[data-testid="stDataFrame"] td { color: #cbd5e1 !important; font-size: 0.83rem !important; }

.stSuccess, .stError, .stInfo, .stWarning { border-radius: 8px !important; font-size: 0.86rem !important; }

[data-testid="stFileUploader"] {
    background: #0b1220 !important; border: 1.5px dashed #1e3358 !important; border-radius: 10px !important;
}
[data-testid="stFileUploader"]:hover { border-color: #2563eb !important; }

hr { border-color: #1a2744 !important; margin: 1.5rem 0 !important; }

/* ── MISC COMPONENTS ── */
.hash-row {
    background: #060c18; border: 1px solid #101e36; border-radius: 8px;
    padding: 0.6rem 0.9rem; margin: 0.4rem 0;
    font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #4b6a9b;
    word-break: break-all; line-height: 1.6;
}
.hash-row .hash-key  { color: #3b5280; text-transform: uppercase; font-size: 0.62rem; letter-spacing: 0.06em; }
.hash-row .hash-val  { color: #60a5fa; }
.hash-row .hash-prev { color: #94a3b8; }

.tx-row {
    background: #080f1c; border: 1px solid #101e36; border-radius: 8px;
    padding: 0.75rem 1rem; margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 1rem;
}
.tx-type-badge { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; padding: 0.2rem 0.55rem; border-radius: 5px; white-space: nowrap; }
.tx-type-invoice  { background: #0c2a0c; color: #4ade80; border: 1px solid #166534; }
.tx-type-contract { background: #1a0e2e; color: #c084fc; border: 1px solid #7e22ce; }
.tx-doc-id { font-family: 'DM Mono', monospace; font-size: 0.82rem; color: #e2e8f0; font-weight: 600; }
.tx-sender { font-size: 0.75rem; color: #4b6a9b; }
.tx-detail { font-size: 0.75rem; color: #64748b; margin-left: auto; }
.att-pill  { background: #0c2040; border: 1px solid #1e40af; color: #60a5fa; font-size: 0.7rem; font-weight: 600; padding: 0.18rem 0.6rem; border-radius: 99px; white-space: nowrap; }

.file-preview-card {
    background: #060c18; border: 1px solid #1a2744; border-radius: 10px;
    padding: 1rem 1.2rem; display: flex; align-items: flex-start; gap: 1rem; margin: 0.75rem 0;
}
.file-preview-card .fp-icon  { font-size: 2rem; line-height: 1; }
.file-preview-card .fp-meta  { flex: 1; min-width: 0; }
.file-preview-card .fp-name  { font-weight: 700; color: #e2e8f0; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.file-preview-card .fp-info  { color: #4b6a9b; font-size: 0.75rem; margin-top: 0.2rem; }
.file-preview-card .fp-hlabel{ color: #3b5280; font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.5rem; }
.file-preview-card .fp-hash  { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #3b82f6; word-break: break-all; margin-top: 0.15rem; }

.integrity-ok   { background:#021a0d; border:1px solid #16a34a; border-radius:8px; padding:0.75rem 1rem; color:#4ade80; font-size:0.85rem; }
.integrity-fail { background:#1a0606; border:1px solid #dc2626; border-radius:8px; padding:0.75rem 1rem; color:#f87171; font-size:0.85rem; }
.integrity-hash { font-family:'DM Mono',monospace; font-size:0.7rem; word-break:break-all; margin-top:0.5rem; opacity:0.75; }

.pool-empty {
    text-align: center; padding: 2.5rem 1rem;
    background: #080f1c; border: 1px dashed #1a2744;
    border-radius: 12px; color: #3b5280; font-size: 0.88rem;
}
.pool-empty .pe-icon { font-size: 2rem; margin-bottom: 0.5rem; }

.verify-panel {
    background: #060c18; border: 1px solid #1a2744;
    border-radius: 14px; padding: 2.5rem; text-align: center;
}
.verify-panel h3 { font-size: 1.1rem; color: #e2e8f0; margin: 0 0 0.5rem 0; }
.verify-panel p  { font-size: 0.85rem; color: #4b6a9b; margin: 0 0 1.5rem 0; }
.chain-status-ok   { display:inline-flex;align-items:center;gap:0.5rem;background:#021a0d;border:1px solid #16a34a;border-radius:10px;padding:1rem 1.5rem;color:#4ade80;font-weight:600;font-size:0.95rem;margin-top:1rem; }
.chain-status-fail { display:inline-flex;align-items:center;gap:0.5rem;background:#1a0606;border:1px solid #dc2626;border-radius:10px;padding:1rem 1.5rem;color:#f87171;font-weight:600;font-size:0.95rem;margin-top:1rem; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "blockchain"    not in st.session_state: st.session_state.blockchain    = Blockchain()
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user"          not in st.session_state: st.session_state.user          = None
if "login_error"   not in st.session_state: st.session_state.login_error   = ""

bc = st.session_state.blockchain

# ── Helpers ───────────────────────────────────────────────────────────────────
def file_icon(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {"pdf":"📄","png":"🖼️","jpg":"🖼️","jpeg":"🖼️","txt":"📃","docx":"📝"}.get(ext,"📎")

def fmt_size(n):
    if n < 1024:    return f"{n} B"
    if n < 1048576: return f"{n/1024:.1f} KB"
    return f"{n/1048576:.1f} MB"

def render_preview_card(att):
    mime = att.get("mime_type","")
    if mime.startswith("image/"):
        st.image(base64.b64decode(att["data"]), caption=att["filename"], width=300)
    st.markdown(f"""
    <div class="file-preview-card">
      <div class="fp-icon">{file_icon(att['filename'])}</div>
      <div class="fp-meta">
        <div class="fp-name">{att['filename']}</div>
        <div class="fp-info">{fmt_size(att['size'])} &nbsp;·&nbsp; {mime or 'unknown'}</div>
        <div class="fp-hlabel">SHA-256 Fingerprint</div>
        <div class="fp-hash">{att.get('sha256','—')}</div>
      </div>
    </div>""", unsafe_allow_html=True)

def tx_type_badge(doc_type):
    cls = "tx-type-invoice" if doc_type == "Invoice" else "tx-type-contract"
    return f'<span class="tx-type-badge {cls}">{doc_type}</span>'

def access_denied(area="this area"):
    role = st.session_state.user["role"] if st.session_state.user else "unknown"
    st.markdown(f"""
    <div class="access-denied">
      <div class="ad-icon">🔒</div>
      <h3>Access Restricted</h3>
      <p>Your account does not have permission to access {area}.</p>
      <div class="ad-role">role: {role}</div>
    </div>""", unsafe_allow_html=True)

def can(permission):
    """Check if logged-in user has a given permission key."""
    return st.session_state.user and st.session_state.user.get(permission, False)

def has_tab(tab_key):
    """Check if logged-in user's role includes a tab."""
    return st.session_state.user and tab_key in st.session_state.user.get("tabs", [])

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:

    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown("""
        <div style="padding-top:6vh;">
        <div class="login-card">
          <div class="login-logo">
            <div class="logo-icon">🔗</div>
            <div class="logo-text">
              <div class="logo-name">LedgerCore</div>
              <div class="logo-sub">Document Chain</div>
            </div>
          </div>
          <div class="login-title">Sign in to your account</div>
          <div class="login-sub">Enter your credentials to access the ledger platform.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit   = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

            if submit:
                ok, user = authenticate(username, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.user          = user
                    st.session_state.login_error   = ""
                    st.rerun()
                else:
                    st.session_state.login_error = "Invalid username or password. Please try again."

        if st.session_state.login_error:
            st.error(st.session_state.login_error)

        # Demo credentials hint
        st.markdown("""
        <div class="role-hint" style="margin-top:1rem;">
          <div class="rh-title">Demo Credentials</div>
          <div class="role-row">
            <span class="rr-creds"><strong>admin</strong> / admin123</span>
            <span class="role-badge" style="background:#0f2847;color:#60a5fa;border:1px solid #1d4ed8;">Admin</span>
          </div>
          <div class="role-row">
            <span class="rr-creds"><strong>auditor</strong> / audit456</span>
            <span class="role-badge" style="background:#1e1040;color:#c084fc;border:1px solid #7e22ce;">Auditor</span>
          </div>
          <div class="role-row">
            <span class="rr-creds"><strong>viewer</strong> / view789</span>
            <span class="role-badge" style="background:#0c2535;color:#38bdf8;border:1px solid #0e7490;">Viewer</span>
          </div>
        </div>
        </div></div>
        """, unsafe_allow_html=True)

    st.stop()  # Don't render anything else until logged in

# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATED APP
# ═══════════════════════════════════════════════════════════════════════════════
user  = st.session_state.user
stats = bc.stats()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="brand-icon">🔗</div>
      <div>
        <div class="brand-name">LedgerCore</div>
        <div class="brand-sub">Document Chain</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # User card
    role_cfg = ROLE_PERMISSIONS[user["role"]]
    st.markdown(f"""
    <div class="user-card">
      <div class="uc-name">👤 {user['display_name']}</div>
      <div class="uc-role">@{user['username']}</div>
      <span class="uc-badge" style="background:{role_cfg['badge_bg']};color:{role_cfg['badge_fg']};border:1px solid {role_cfg['color']}33;">
        {role_cfg['label']}
      </span>
    </div>""", unsafe_allow_html=True)

    # Access summary
    st.markdown('<div class="sidebar-section-label">Access Level</div>', unsafe_allow_html=True)
    access_items = [
        ("overview",  "📊", "Overview"),
        ("submit",    "📝", "Submit Records"),
        ("ledger",    "📖", "View Ledger"),
        ("security",  "🛡️", "Security"),
    ]
    access_html = ""
    for key, icon, label in access_items:
        granted = key in user["tabs"]
        cls     = "granted" if granted else "denied"
        lock    = "" if granted else '<span class="ar-lock">🔒</span>'
        access_html += f'<div class="access-row {cls}"><span class="ar-icon">{icon}</span>{label}{lock}</div>'
    st.markdown(f'<div style="background:#0a0f1e;border:1px solid #1a2744;border-radius:8px;padding:0.5rem 0.75rem;margin-bottom:1rem;">{access_html}</div>', unsafe_allow_html=True)

    # Chain stats
    st.markdown('<div class="sidebar-section-label">Chain Stats</div>', unsafe_allow_html=True)
    for label, val in [("Blocks Minted", stats["total_blocks"]),
                       ("Total Records", stats["total_transactions"]),
                       ("Pending",       stats["pending"]),
                       ("Attachments",   stats["with_attachments"])]:
        st.markdown(f"""
        <div class="sidebar-stat">
          <span class="s-label">{label}</span>
          <span class="s-value">{val}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding:0.75rem;background:#0f1b30;border:1px solid #1a2744;border-radius:8px;text-align:center;margin-top:0.5rem;">
      <div style="font-size:1.3rem;font-weight:700;color:#f1f5f9;font-family:'DM Mono',monospace;">${stats['total_invoice_value']:,.2f}</div>
      <div style="font-size:0.7rem;color:#3b5280;margin-top:0.2rem;text-transform:uppercase;letter-spacing:0.06em;">Total Invoice Volume</div>
    </div>""", unsafe_allow_html=True)

    # Sign out
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user          = None
        st.rerun()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
  <div>
    <h1>Document Tracking Ledger</h1>
    <p>Immutable record-keeping for business documents · Private blockchain network</p>
  </div>
  <span class="header-badge">● Live</span>
</div>
""", unsafe_allow_html=True)

# ── Build tab list based on role ──────────────────────────────────────────────
TAB_DEFS = [
    ("overview",  "  Overview  "),
    ("submit",    "  Submit Record  "),
    ("ledger",    "  Ledger  "),
    ("security",  "  Security  "),
]
# Always show all tab labels (greyed tabs are cleaner than hiding them)
tab_labels = [label for _, label in TAB_DEFS]
tab_keys   = [key   for key, _   in TAB_DEFS]

tabs = st.tabs(tab_labels)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 0 — OVERVIEW  (all roles)
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    inv_val = f"${stats['total_invoice_value']:,.2f}"
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-icon">⛓️</div><div class="kpi-label">Blocks Minted</div><div class="kpi-value">{stats['total_blocks']}</div></div>
      <div class="kpi-card"><div class="kpi-icon">📄</div><div class="kpi-label">Total Records</div><div class="kpi-value">{stats['total_transactions']}</div></div>
      <div class="kpi-card"><div class="kpi-icon">🧾</div><div class="kpi-label">Invoices</div><div class="kpi-value">{stats['total_invoices']}</div></div>
      <div class="kpi-card"><div class="kpi-icon">📑</div><div class="kpi-label">Contracts</div><div class="kpi-value">{stats['total_contracts']}</div></div>
      <div class="kpi-card"><div class="kpi-icon">💰</div><div class="kpi-label">Invoice Volume</div><div class="kpi-value" style="font-size:1.3rem;">{inv_val}</div></div>
    </div>""", unsafe_allow_html=True)

    all_tx = bc.all_transactions()
    if not all_tx:
        st.markdown('<div class="pool-empty" style="padding:3rem;"><div class="pe-icon">📊</div><div>No committed transactions yet.</div></div>', unsafe_allow_html=True)
    else:
        import pandas as pd
        block_counts, block_values = {}, {}
        for tx in all_tx:
            idx = f"#{tx['_block_index']}"
            block_counts[idx] = block_counts.get(idx, 0) + 1
            block_values[idx] = block_values.get(idx, 0) + float(tx["details"].get("amount", 0))

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-header"><h2>Transactions per Block</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
            st.bar_chart(pd.DataFrame({"Block": list(block_counts), "Records": list(block_counts.values())}).set_index("Block"), color="#2563eb")
        with col_b:
            st.markdown('<div class="section-header"><h2>Invoice Value per Block</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
            st.bar_chart(pd.DataFrame({"Block": list(block_values), "Value ($)": list(block_values.values())}).set_index("Block"), color="#0ea5e9")

        st.markdown('<div class="section-header" style="margin-top:1.5rem;"><h2>Recent Activity</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
        for tx in reversed(all_tx[-8:]):
            att   = tx.get("attachment")
            att_s = f'<span class="att-pill">📎 {att["filename"]}</span>' if att else ""
            st.markdown(f"""
            <div class="tx-row">
              {tx_type_badge(tx['doc_type'])}
              <div><div class="tx-doc-id">{tx['doc_id']}</div><div class="tx-sender">{tx['sender']} · Block #{tx['_block_index']}</div></div>
              <div class="tx-detail">{json.dumps(tx['details'])}</div>
              <div style="margin-left:auto;">{att_s}</div>
              <div style="font-size:0.72rem;color:#3b5280;white-space:nowrap;">{time.strftime('%b %d %H:%M', time.localtime(tx['timestamp']))}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SUBMIT RECORD  (admin only)
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    if not has_tab("submit"):
        access_denied("Submit Record — Administrator access required")
    else:
        left_col, right_col = st.columns([1.1, 1], gap="large")

        with left_col:
            st.markdown('<div class="section-header"><h2>New Transaction</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
            st.markdown('<div class="form-panel"><div class="panel-title">Document Details</div>', unsafe_allow_html=True)

            doc_type = st.selectbox("Document Type", ["Invoice", "Contract"])
            if doc_type == "Invoice":
                doc_id  = st.text_input("Invoice Number", placeholder="e.g. INV-2024-001")
                amt     = st.number_input("Amount (USD)", min_value=0.0, format="%.2f")
                details = {"amount": amt}
            else:
                doc_id  = st.text_input("Contract ID", placeholder="e.g. CTR-2024-099")
                parties = st.text_input("Parties Involved", placeholder="Corp A, Corp B")
                details = {"parties": parties}

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:1rem;"><h2>Supporting Document</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Drag & drop or click to browse · PDF, PNG, JPG, TXT, DOCX",
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
                submitted = st.form_submit_button("Submit to Mempool →", use_container_width=True, type="primary")
                if submitted:
                    tx = Transaction(doc_type, doc_id, details, user["username"], attachment=attachment_ready)
                    ok, msg = bc.add_transaction(tx)
                    if ok:
                        extra = f" · `{attachment_ready['filename']}` fingerprinted" if attachment_ready else ""
                        st.success(f"✓ {msg}{extra}")
                    else:
                        st.error(f"✗ {msg}")

        with right_col:
            st.markdown('<div class="section-header"><h2>File Preview</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
            if attachment_ready:
                render_preview_card(attachment_ready)
            else:
                st.markdown('<div class="pool-empty"><div class="pe-icon">📎</div><div>No file attached</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:1.5rem;"><h2>Mempool</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
            if bc.pending_transactions:
                for tx in bc.pending_transactions:
                    att   = tx.get("attachment")
                    att_s = f'<span class="att-pill">📎 {att["filename"]}</span>' if att else ""
                    st.markdown(f"""
                    <div class="tx-row">
                      {tx_type_badge(tx['doc_type'])}
                      <div><div class="tx-doc-id">{tx['doc_id']}</div><div class="tx-sender">{tx['sender']}</div></div>
                      <div style="margin-left:auto;">{att_s}</div>
                    </div>""", unsafe_allow_html=True)

                # Mint is also admin-only
                st.markdown("<br>", unsafe_allow_html=True)
                if can("can_mint"):
                    if st.button(f"🔨  Mint Block  ({len(bc.pending_transactions)} records)", type="primary", use_container_width=True):
                        ok, msg = bc.mint_pending_transactions(user["username"])
                        if ok:
                            st.success(f"✓ {msg}")
                            st.rerun()
                else:
                    st.markdown('<div class="access-denied" style="padding:1.5rem;"><div class="ad-icon" style="font-size:1.5rem;">🔒</div><h3 style="font-size:0.9rem;">Minting requires Admin role</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="pool-empty"><div class="pe-icon">⏳</div><div>Mempool is empty</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LEDGER  (admin + auditor)
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    if not has_tab("ledger"):
        access_denied("the Ledger — Auditor or Administrator access required")
    else:
        tc1, tc2, tc3, tc4 = st.columns([3, 1.5, 1, 1])
        with tc1:
            search_query = st.text_input("Search", placeholder="🔍  Document ID, sender, parties…", label_visibility="collapsed")
        with tc2:
            filter_type = st.selectbox("Type", ["All","Invoice","Contract"], label_visibility="collapsed")
        with tc3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Filter", use_container_width=True)
        with tc4:
            all_committed = bc.all_transactions()
            if all_committed:
                def build_csv(txs):
                    out = io.StringIO()
                    w   = csv.DictWriter(out, fieldnames=["block","doc_type","doc_id","sender","timestamp","details","has_attachment","file_sha256"])
                    w.writeheader()
                    for tx in txs:
                        att = tx.get("attachment") or {}
                        w.writerow({"block":tx["_block_index"],"doc_type":tx["doc_type"],"doc_id":tx["doc_id"],
                                    "sender":tx["sender"],"timestamp":time.ctime(tx["timestamp"]),
                                    "details":json.dumps(tx["details"]),"has_attachment":bool(att),"file_sha256":att.get("sha256","")})
                    return out.getvalue()
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("⬇ Export", build_csv(all_committed), f"ledger_{int(time.time())}.csv", "text/csv", use_container_width=True)

        if search_query or filter_type != "All":
            import pandas as pd
            results = bc.search_transactions(search_query, filter_type)
            st.markdown(f'<div style="font-size:0.8rem;color:#4b6a9b;margin:0.5rem 0 0.75rem 0;">{len(results)} record(s) matched</div>', unsafe_allow_html=True)
            if results:
                rows = [{"Block":f"#{tx['_block_index']}","Type":tx["doc_type"],"Document ID":tx["doc_id"],
                         "Sender":tx["sender"],"Attachment":f"📎 {tx['attachment']['filename']}" if tx.get("attachment") else "—",
                         "Timestamp":time.ctime(tx["timestamp"])} for tx in results]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.warning("No records matched your search criteria.")
            st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-header"><h2>Block Explorer</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
        for block in reversed(bc.chain):
            tx_count  = len(block.transactions)
            att_count = sum(1 for tx in block.transactions if tx.get("attachment"))
            att_str   = f" · 📎 {att_count} file{'s' if att_count>1 else ''}" if att_count else ""
            label     = (f"Genesis Block  ·  System  ·  {time.strftime('%b %d %Y', time.localtime(block.timestamp))}"
                         if block.index == 0 else
                         f"Block #{block.index}  ·  {tx_count} record{'s' if tx_count!=1 else ''}  ·  {block.creator_handle}{att_str}  ·  {time.strftime('%b %d %Y %H:%M', time.localtime(block.timestamp))}")

            with st.expander(label, expanded=False):
                st.markdown(f"""
                <div class="hash-row"><span class="hash-key">Block Hash &nbsp;</span><span class="hash-val">{block.hash}</span></div>
                <div class="hash-row"><span class="hash-key">Previous Hash &nbsp;</span><span class="hash-prev">{block.previous_hash}</span></div>""", unsafe_allow_html=True)

                if block.index > 0:
                    st.markdown('<div style="font-size:0.72rem;color:#3b5280;text-transform:uppercase;letter-spacing:0.07em;margin:1rem 0 0.6rem 0;">Transactions</div>', unsafe_allow_html=True)
                    for i, tx in enumerate(block.transactions):
                        attachment = tx.get("attachment")
                        att_label  = f"  ·  📎 {attachment['filename']}" if attachment else ""
                        with st.expander(f"#{i+1}  ·  {tx['doc_type']}  ·  {tx['doc_id']}  ·  {tx['sender']}{att_label}"):
                            st.json({k:v for k,v in tx.items() if k != "attachment"})
                            if attachment:
                                st.markdown("**Attachment**")
                                render_preview_card(attachment)
                                dl_col, vfy_col = st.columns(2)
                                with dl_col:
                                    st.download_button(f"⬇ Download {attachment['filename']}",
                                                       data=base64.b64decode(attachment["data"]),
                                                       file_name=attachment["filename"],
                                                       mime=attachment.get("mime_type","application/octet-stream"),
                                                       key=f"dl_{block.index}_{i}")
                                with vfy_col:
                                    if st.button("🔍 Verify Integrity", key=f"vfy_{block.index}_{i}"):
                                        ok, detail = Blockchain.verify_attachment(attachment)
                                        css, icon, txt = ("integrity-ok","✅","File intact — SHA-256 verified") if ok else ("integrity-fail","🚨","Integrity check FAILED")
                                        st.markdown(f'<div class="{css}">{icon} <strong>{txt}</strong><div class="integrity-hash">{detail}</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SECURITY  (admin only)
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    if not has_tab("security"):
        access_denied("Security — Administrator access required")
    else:
        left, mid, right = st.columns([1, 2, 1])
        with mid:
            st.markdown("""
            <div class="verify-panel">
              <h3>Chain Integrity Verification</h3>
              <p>Re-computes every block hash and verifies the cryptographic linkage<br>across the entire chain to detect any tampering or corruption.</p>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Run Cryptographic Verification", type="primary", use_container_width=True):
                with st.spinner("Verifying chain…"):
                    time.sleep(1)
                    is_valid = bc.is_chain_valid()
                if is_valid:
                    st.markdown('<div style="text-align:center"><div class="chain-status-ok">✅ &nbsp; Chain is valid — all hashes verified</div></div>', unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.markdown('<div style="text-align:center"><div class="chain-status-fail">🚨 &nbsp; CRITICAL — Blockchain integrity compromised</div></div>', unsafe_allow_html=True)

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h2>Chain Summary</h2><div class="section-line"></div></div>', unsafe_allow_html=True)
            import pandas as pd
            chain_rows = [{"Block": blk.index, "Records": len(blk.transactions),
                           "Attachments": sum(1 for tx in blk.transactions if isinstance(tx,dict) and tx.get("attachment")),
                           "Minted By": blk.creator_handle,
                           "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(blk.timestamp)),
                           "Hash (short)": blk.hash[:20]+"…"} for blk in bc.chain]
            st.dataframe(pd.DataFrame(chain_rows), use_container_width=True, hide_index=True)