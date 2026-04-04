import streamlit as st
import time
import json
import csv
import io
import base64
import hashlib
from blockchain import Blockchain, Transaction

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Blockchain Tracker", page_icon="🔗", layout="wide")

# ── CSS (drag-and-drop zone + badges + preview card) ─────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; }

    /* KPI cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    div[data-testid="metric-container"] label            { color: #94a3b8 !important; font-size: 0.78rem; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #38bdf8 !important; font-size: 1.7rem !important; font-weight: 700 !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] { font-weight: 600; }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        color: white; border: none; border-radius: 8px;
    }
    .stDownloadButton > button:hover { opacity: 0.9; }

    /* Drag-and-drop upload zone */
    .drop-zone {
        border: 2px dashed #334155;
        border-radius: 12px;
        padding: 2rem 1.5rem;
        text-align: center;
        background: #0f172a;
        transition: border-color 0.2s, background 0.2s;
        cursor: pointer;
        margin-bottom: 0.5rem;
    }
    .drop-zone:hover, .drop-zone.dragover {
        border-color: #38bdf8;
        background: #1e293b;
    }
    .drop-zone .drop-icon { font-size: 2rem; margin-bottom: 0.4rem; }
    .drop-zone p { color: #94a3b8; margin: 0; font-size: 0.9rem; }
    .drop-zone strong { color: #e2e8f0; }

    /* File preview card */
    .file-preview-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-top: 0.75rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    .file-preview-card .file-icon { font-size: 2.2rem; line-height: 1; }
    .file-preview-card .file-meta { flex: 1; }
    .file-preview-card .file-name { font-weight: 700; color: #e2e8f0; font-size: 0.95rem; word-break: break-all; }
    .file-preview-card .file-info { color: #94a3b8; font-size: 0.8rem; margin-top: 0.25rem; }
    .file-preview-card .file-hash { 
        color: #38bdf8; font-size: 0.72rem; font-family: monospace; 
        margin-top: 0.4rem; word-break: break-all;
    }
    .hash-label { color: #64748b; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; }

    /* Attachment badge on block headers */
    .att-badge {
        display: inline-block;
        background: #1e3a5f;
        color: #38bdf8;
        border: 1px solid #1d4ed8;
        border-radius: 99px;
        padding: 0 0.55rem;
        font-size: 0.72rem;
        font-weight: 600;
        margin-left: 0.5rem;
        vertical-align: middle;
    }

    /* Integrity check result */
    .integrity-ok   { background:#052e16; border:1px solid #16a34a; border-radius:8px; padding:0.75rem 1rem; color:#4ade80; }
    .integrity-fail { background:#2d0a0a; border:1px solid #dc2626; border-radius:8px; padding:0.75rem 1rem; color:#f87171; }
    .integrity-hash { font-family:monospace; font-size:0.75rem; word-break:break-all; margin-top:0.4rem; opacity:0.8; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
if "preview_file" not in st.session_state:
    st.session_state.preview_file = None   # holds processed attachment dict before submit

bc = st.session_state.blockchain

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Node Configuration")
    current_user = st.text_input("Current User Handle", value="admin_user_01")
    st.divider()
    stats = bc.stats()
    st.metric("Pending Transactions", stats["pending"])
    st.metric("Total Blocks", stats["total_blocks"])
    st.metric("Total Records", stats["total_transactions"])
    st.metric("📎 With Attachments", stats["with_attachments"])

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🔗 Document Tracking Blockchain")
st.markdown("A private, immutable ledger for verifying business documents.")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📝 Process Records", "📖 View Ledger", "🛡️ Verify Integrity"])

# ─────────────────────────────────────────────────────────────────────────────
# Helper: file-type icon
# ─────────────────────────────────────────────────────────────────────────────
def file_icon(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {"pdf": "📄", "png": "🖼️", "jpg": "🖼️", "jpeg": "🖼️",
            "txt": "📃", "docx": "📝"}.get(ext, "📎")

def fmt_size(n: int) -> str:
    if n < 1024:       return f"{n} B"
    if n < 1024**2:    return f"{n/1024:.1f} KB"
    return f"{n/1024**2:.1f} MB"

# ─────────────────────────────────────────────────────────────────────────────
# Helper: render file preview card
# ─────────────────────────────────────────────────────────────────────────────
def render_preview_card(att: dict):
    icon  = file_icon(att["filename"])
    mime  = att.get("mime_type", "")
    sha   = att.get("sha256", "")

    # Image inline preview
    if mime.startswith("image/"):
        img_bytes = base64.b64decode(att["data"])
        st.image(img_bytes, caption=att["filename"], width=320)

    st.markdown(f"""
    <div class="file-preview-card">
      <div class="file-icon">{icon}</div>
      <div class="file-meta">
        <div class="file-name">{att['filename']}</div>
        <div class="file-info">{fmt_size(att['size'])} &nbsp;·&nbsp; {mime or 'unknown type'}</div>
        <div class="hash-label" style="margin-top:0.5rem;">SHA-256 fingerprint</div>
        <div class="file-hash">{sha}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Network Dashboard")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("⛓️ Blocks",        stats["total_blocks"])
    k2.metric("📄 Total Records", stats["total_transactions"])
    k3.metric("🧾 Invoices",      stats["total_invoices"])
    k4.metric("📑 Contracts",     stats["total_contracts"])
    k5.metric("💰 Invoice Value", f"${stats['total_invoice_value']:,.2f}")

    st.divider()
    all_tx = bc.all_transactions()

    if not all_tx:
        st.info("No committed transactions yet. Submit and mint records to see analytics.")
    else:
        import pandas as pd

        block_counts, block_values = {}, {}
        for tx in all_tx:
            idx = f"Block #{tx['_block_index']}"
            block_counts[idx] = block_counts.get(idx, 0) + 1
            block_values[idx] = block_values.get(idx, 0) + float(tx["details"].get("amount", 0))

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Transactions per Block")
            st.bar_chart(pd.DataFrame({"Block": list(block_counts), "Count": list(block_counts.values())}).set_index("Block"))
        with col_b:
            st.subheader("Invoice Value per Block ($)")
            st.bar_chart(pd.DataFrame({"Block": list(block_values), "Value ($)": list(block_values.values())}).set_index("Block"))

        st.subheader("Document Type Breakdown")
        dc1, dc2 = st.columns(2)
        total = stats["total_transactions"] or 1
        dc1.progress(stats["total_invoices"]  / total, text=f"🧾 Invoices — {stats['total_invoices']} ({stats['total_invoices']/total*100:.0f}%)")
        dc2.progress(stats["total_contracts"] / total, text=f"📑 Contracts — {stats['total_contracts']} ({stats['total_contracts']/total*100:.0f}%)")

        st.divider()
        st.subheader("Recent Transactions")
        rows = [{"Block": f"#{tx['_block_index']}", "Type": tx["doc_type"],
                 "Document ID": tx["doc_id"], "Sender": tx["sender"],
                 "Timestamp": time.ctime(tx["timestamp"]),
                 "Attachment": f"📎 {tx['attachment']['filename']}" if tx.get("attachment") else "—"}
                for tx in reversed(all_tx[-10:])]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PROCESS RECORDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("1. Submit Business Record")
    st.write("Submit documents to the network. They will wait in the mempool until a block is minted.")

    doc_type = st.selectbox("Select Document Type", ["Invoice", "Contract"])

    # ── File uploader (outside form so preview is reactive) ───────────────────
    st.markdown("**📎 Attach Supporting Document** *(optional — drag & drop or click)*")

    uploaded_file = st.file_uploader(
        "Drop a file here or click to browse",
        type=["pdf", "png", "jpg", "jpeg", "txt", "docx"],
        label_visibility="visible",
        key="file_uploader",
    )

    # Process & preview as soon as a file is selected
    attachment_ready = None
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        sha256 = Blockchain.hash_file(file_bytes)
        attachment_ready = {
            "filename":  uploaded_file.name,
            "data":      base64.b64encode(file_bytes).decode("utf-8"),
            "size":      len(file_bytes),
            "mime_type": uploaded_file.type,
            "sha256":    sha256,
        }
        st.markdown("**📋 File Preview**")
        render_preview_card(attachment_ready)

    st.divider()

    # ── Transaction form ──────────────────────────────────────────────────────
    with st.form("add_doc_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        if doc_type == "Invoice":
            with col1:
                doc_id = st.text_input("Invoice Number (e.g., INV-001)")
            with col2:
                amt = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
                details = {"amount": amt}
        else:
            with col1:
                doc_id = st.text_input("Contract ID (e.g., CTR-999)")
            with col2:
                parties = st.text_input("Parties Involved (e.g., Corp A, Corp B)")
                details = {"parties": parties}

        submitted = st.form_submit_button("🔐 Submit Transaction", use_container_width=True, type="primary")

        if submitted:
            new_tx = Transaction(doc_type, doc_id, details, current_user, attachment=attachment_ready)
            success, msg = bc.add_transaction(new_tx)
            if success:
                if attachment_ready:
                    st.success(f"{msg}  📎 `{attachment_ready['filename']}` attached & fingerprinted.")
                else:
                    st.success(msg)
            else:
                st.error(f"🚨 {msg}")

    st.divider()

    # ── Pending pool ──────────────────────────────────────────────────────────
    st.header("2. Pending Transaction Pool")
    if bc.pending_transactions:
        import pandas as pd
        pending_rows = [{"Type": tx["doc_type"], "Document ID": tx["doc_id"],
                         "Sender": tx["sender"], "Details": json.dumps(tx["details"]),
                         "Attachment": f"📎 {tx['attachment']['filename']}" if tx.get("attachment") else "—",
                         "Submitted": time.ctime(tx["timestamp"])}
                        for tx in bc.pending_transactions]
        st.dataframe(pd.DataFrame(pending_rows), use_container_width=True, hide_index=True)

        if st.button("🔨 Mint Block (Process Pool)", type="primary", use_container_width=True):
            success, msg = bc.mint_pending_transactions(current_user)
            if success:
                st.success(msg)
                st.rerun()
    else:
        st.info("The transaction pool is currently empty.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VIEW LEDGER
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Immutable Blockchain Ledger")

    # Search & filter
    sf1, sf2, sf3 = st.columns([3, 1.5, 1.5])
    with sf1:
        search_query = st.text_input("🔍 Search records", placeholder="doc ID, sender, parties…")
    with sf2:
        filter_type = st.selectbox("Filter by type", ["All", "Invoice", "Contract"])
    with sf3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Apply Filter", use_container_width=True)

    st.divider()

    # CSV export
    all_committed = bc.all_transactions()
    if all_committed:
        def build_csv(transactions):
            out = io.StringIO()
            w = csv.DictWriter(out, fieldnames=["block","doc_type","doc_id","sender","timestamp","details","has_attachment","file_sha256"])
            w.writeheader()
            for tx in transactions:
                att = tx.get("attachment") or {}
                w.writerow({"block": tx["_block_index"], "doc_type": tx["doc_type"],
                            "doc_id": tx["doc_id"], "sender": tx["sender"],
                            "timestamp": time.ctime(tx["timestamp"]),
                            "details": json.dumps(tx["details"]),
                            "has_attachment": bool(att),
                            "file_sha256": att.get("sha256", "")})
            return out.getvalue()

        exp1, exp2 = st.columns([4, 1])
        with exp2:
            st.download_button("⬇️ Export CSV", build_csv(all_committed),
                               f"blockchain_export_{int(time.time())}.csv", "text/csv",
                               use_container_width=True)

    # Filtered results
    if search_query or filter_type != "All":
        import pandas as pd
        results = bc.search_transactions(search_query, filter_type)
        st.markdown(f"**{len(results)} record(s) matched**")
        if results:
            rows = [{"Block": f"#{tx['_block_index']}", "Type": tx["doc_type"],
                     "Document ID": tx["doc_id"], "Sender": tx["sender"],
                     "Attachment": f"📎 {tx['attachment']['filename']}" if tx.get("attachment") else "—",
                     "Timestamp": time.ctime(tx["timestamp"])}
                    for tx in results]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.warning("No records matched your search.")
        st.divider()

    # ── Block explorer with attachment badges ─────────────────────────────────
    st.subheader("Block Explorer")
    for block in reversed(bc.chain):
        tx_count  = len(block.transactions)
        att_count = sum(1 for tx in block.transactions if tx.get("attachment"))

        # Build badge HTML
        badge_html = ""
        if att_count:
            badge_html = f'<span class="att-badge">📎 {att_count} file{"s" if att_count > 1 else ""}</span>'

        # Expander label (plain text) + badge injected just below via markdown
        expander_label = (
            f"📦 Block #{block.index} | Records: {tx_count} | Minted By: {block.creator_handle}"
            + (f" | 📎 {att_count} attachment{'s' if att_count > 1 else ''}" if att_count else "")
        )

        with st.expander(expander_label):
            # Coloured badge row
            if badge_html:
                st.markdown(badge_html, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            c1.markdown(f"**Timestamp:** {time.ctime(block.timestamp)}")
            c2.markdown(f"**Creator:** `{block.creator_handle}`")
            st.markdown(f"**Block Hash:** `{block.hash}`")
            st.markdown(f"**Previous Hash:** `{block.previous_hash}`")

            if block.index > 0:
                st.markdown("---")
                for i, tx in enumerate(block.transactions):
                    attachment = tx.get("attachment")
                    att_label  = f"📎 {attachment['filename']}" if attachment else ""
                    label      = f"#{i+1} · {tx['doc_type']} · **{tx['doc_id']}** · {tx['sender']}" + (f" · {att_label}" if att_label else "")

                    with st.expander(label):
                        display_tx = {k: v for k, v in tx.items() if k not in ("attachment",)}
                        st.json(display_tx)

                        if attachment:
                            st.markdown("**📎 Attachment**")
                            render_preview_card(attachment)

                            dl_col, verify_col = st.columns(2)
                            with dl_col:
                                file_data = base64.b64decode(attachment["data"])
                                st.download_button(
                                    f"⬇️ Download {attachment['filename']}",
                                    data=file_data,
                                    file_name=attachment["filename"],
                                    mime=attachment.get("mime_type", "application/octet-stream"),
                                    key=f"dl_{block.index}_{i}",
                                )
                            with verify_col:
                                if st.button("🔍 Verify Integrity", key=f"verify_{block.index}_{i}"):
                                    ok, detail = Blockchain.verify_attachment(attachment)
                                    if ok:
                                        st.markdown(
                                            f'<div class="integrity-ok">✅ <strong>File intact</strong>'
                                            f'<div class="integrity-hash">SHA-256: {detail}</div></div>',
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        st.markdown(
                                            f'<div class="integrity-fail">🚨 <strong>Integrity check FAILED</strong>'
                                            f'<div class="integrity-hash">{detail}</div></div>',
                                            unsafe_allow_html=True,
                                        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — VERIFY INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("System Health & Security")

    if st.button("Validate Blockchain", use_container_width=True):
        with st.spinner("Running cryptographic hash verification…"):
            time.sleep(1)
            is_valid = bc.is_chain_valid()
        if is_valid:
            st.success("🛡️ Cryptographic Validation Passed: The blockchain is secure!")
            st.balloons()
        else:
            st.error("🚨 CRITICAL WARNING: Blockchain integrity compromised!")
