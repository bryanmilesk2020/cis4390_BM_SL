import streamlit as st
import time
import json
import csv
import io
import base64
from blockchain import Blockchain, Transaction

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Blockchain Tracker",
    page_icon="🔗",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Overall dark theme adjustments */
    .main .block-container { padding-top: 1.5rem; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    div[data-testid="metric-container"] label { color: #94a3b8 !important; font-size: 0.78rem; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 1.7rem !important;
        font-weight: 700 !important;
    }

    /* Tab styling */
    button[data-baseweb="tab"] { font-weight: 600; }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        color: white;
        border: none;
        border-radius: 8px;
    }
    .stDownloadButton > button:hover { opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

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

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🔗 Document Tracking Blockchain")
st.markdown("A private, immutable ledger for verifying business documents.")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "📝 Process Records",
    "📖 View Ledger",
    "🛡️ Verify Integrity",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Network Dashboard")

    # ── KPI row ──
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("⛓️ Blocks", stats["total_blocks"])
    k2.metric("📄 Total Records", stats["total_transactions"])
    k3.metric("🧾 Invoices", stats["total_invoices"])
    k4.metric("📑 Contracts", stats["total_contracts"])
    k5.metric("💰 Invoice Value", f"${stats['total_invoice_value']:,.2f}")

    st.divider()

    all_tx = bc.all_transactions()

    if not all_tx:
        st.info("No committed transactions yet. Submit and mint records to see analytics.")
    else:
        # ── Charts ──
        import datetime

        # Build per-block bar data
        block_counts = {}
        block_values = {}
        for tx in all_tx:
            idx = f"Block #{tx['_block_index']}"
            block_counts[idx] = block_counts.get(idx, 0) + 1
            block_values[idx] = block_values.get(idx, 0) + float(tx["details"].get("amount", 0))

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Transactions per Block")
            chart_data = {"Block": list(block_counts.keys()), "Count": list(block_counts.values())}
            import pandas as pd
            st.bar_chart(pd.DataFrame(chart_data).set_index("Block"))

        with col_b:
            st.subheader("Invoice Value per Block ($)")
            val_data = {"Block": list(block_values.keys()), "Value ($)": list(block_values.values())}
            st.bar_chart(pd.DataFrame(val_data).set_index("Block"))

        # ── Doc-type breakdown ──
        st.subheader("Document Type Breakdown")
        dc1, dc2 = st.columns(2)
        total = stats["total_transactions"] or 1
        dc1.progress(
            stats["total_invoices"] / total,
            text=f"🧾 Invoices — {stats['total_invoices']} ({stats['total_invoices']/total*100:.0f}%)",
        )
        dc2.progress(
            stats["total_contracts"] / total,
            text=f"📑 Contracts — {stats['total_contracts']} ({stats['total_contracts']/total*100:.0f}%)",
        )

        # ── Recent activity table ──
        st.divider()
        st.subheader("Recent Transactions")
        rows = []
        for tx in reversed(all_tx[-10:]):
            rows.append({
                "Block": f"#{tx['_block_index']}",
                "Type": tx["doc_type"],
                "Document ID": tx["doc_id"],
                "Sender": tx["sender"],
                "Timestamp": time.ctime(tx["timestamp"]),
                "Has File": "📎" if tx.get("attachment") else "—",
            })
        if rows:
            import pandas as pd
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PROCESS RECORDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("1. Submit Business Record")
    st.write("Submit documents to the network. They will wait in the mempool until a block is minted.")

    doc_type = st.selectbox("Select Document Type", ["Invoice", "Contract"])

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

        # ── File upload ──
        st.markdown("**📎 Attach Supporting Document** *(optional)*")
        uploaded_file = st.file_uploader(
            "Upload PDF, image, or text file",
            type=["pdf", "png", "jpg", "jpeg", "txt", "docx"],
            label_visibility="collapsed",
        )

        submitted = st.form_submit_button("Submit Transaction", use_container_width=True)

        if submitted:
            # Process attachment
            attachment = None
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                attachment = {
                    "filename": uploaded_file.name,
                    "data": base64.b64encode(file_bytes).decode("utf-8"),
                    "size": len(file_bytes),
                    "mime_type": uploaded_file.type,
                }

            new_tx = Transaction(doc_type, doc_id, details, current_user, attachment=attachment)
            success, msg = bc.add_transaction(new_tx)

            if success:
                if attachment:
                    st.success(f"{msg} (📎 {uploaded_file.name} attached)")
                else:
                    st.success(msg)
            else:
                st.error(f"🚨 {msg}")

    st.divider()
    st.header("2. Pending Transaction Pool")

    if bc.pending_transactions:
        # Show clean table instead of raw JSON
        pending_rows = []
        for tx in bc.pending_transactions:
            pending_rows.append({
                "Type": tx["doc_type"],
                "Document ID": tx["doc_id"],
                "Sender": tx["sender"],
                "Details": json.dumps(tx["details"]),
                "Attachment": f"📎 {tx['attachment']['filename']}" if tx.get("attachment") else "—",
                "Submitted": time.ctime(tx["timestamp"]),
            })
        import pandas as pd
        st.dataframe(pd.DataFrame(pending_rows), use_container_width=True, hide_index=True)

        if st.button("🔨 Mint Block (Process Pool)", type="primary", use_container_width=True):
            success, msg = bc.mint_pending_transactions(current_user)
            if success:
                st.success(msg)
                st.rerun()
    else:
        st.info("The transaction pool is currently empty.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VIEW LEDGER  (Search + Filter + Export)
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Immutable Blockchain Ledger")

    # ── Search & filter controls ──
    sf1, sf2, sf3 = st.columns([3, 1.5, 1.5])
    with sf1:
        search_query = st.text_input("🔍 Search records", placeholder="doc ID, sender, parties…")
    with sf2:
        filter_type = st.selectbox("Filter by type", ["All", "Invoice", "Contract"])
    with sf3:
        st.markdown("<br>", unsafe_allow_html=True)
        do_search = st.button("Apply Filter", use_container_width=True)

    st.divider()

    # ── Export to CSV ──
    all_committed = bc.all_transactions()
    if all_committed:
        def build_csv(transactions):
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "block", "doc_type", "doc_id", "sender", "timestamp", "details", "has_attachment"
            ])
            writer.writeheader()
            for tx in transactions:
                writer.writerow({
                    "block": tx["_block_index"],
                    "doc_type": tx["doc_type"],
                    "doc_id": tx["doc_id"],
                    "sender": tx["sender"],
                    "timestamp": time.ctime(tx["timestamp"]),
                    "details": json.dumps(tx["details"]),
                    "has_attachment": bool(tx.get("attachment")),
                })
            return output.getvalue()

        exp1, exp2 = st.columns([4, 1])
        with exp2:
            csv_bytes = build_csv(all_committed)
            st.download_button(
                label="⬇️ Export CSV",
                data=csv_bytes,
                file_name=f"blockchain_export_{int(time.time())}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # ── Filtered results ──
    if search_query or filter_type != "All":
        results = bc.search_transactions(search_query, filter_type)
        st.markdown(f"**{len(results)} record(s) matched**")

        if results:
            rows = []
            for tx in results:
                rows.append({
                    "Block": f"#{tx['_block_index']}",
                    "Type": tx["doc_type"],
                    "Document ID": tx["doc_id"],
                    "Sender": tx["sender"],
                    "Details": json.dumps(tx["details"]),
                    "Attachment": f"📎 {tx['attachment']['filename']}" if tx.get("attachment") else "—",
                    "Timestamp": time.ctime(tx["timestamp"]),
                })
            import pandas as pd
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.warning("No records matched your search.")

        st.divider()

    # ── Full ledger block explorer ──
    st.subheader("Block Explorer")
    for block in reversed(bc.chain):
        tx_count = len(block.transactions)
        with st.expander(
            f"📦 Block #{block.index} | Records: {tx_count} | Minted By: {block.creator_handle}"
        ):
            st.write(f"**Timestamp:** {time.ctime(block.timestamp)}")
            st.write(f"**Block Hash:** `{block.hash}`")
            st.write(f"**Previous Hash:** `{block.previous_hash}`")

            if block.index > 0:
                st.write("**Stored Transactions:**")
                for i, tx in enumerate(block.transactions):
                    attachment = tx.get("attachment")
                    label = (
                        f"#{i+1} · {tx['doc_type']} · {tx['doc_id']} · {tx['sender']}"
                    )
                    with st.expander(label, expanded=False):
                        display_tx = {k: v for k, v in tx.items() if k != "attachment"}
                        st.json(display_tx)

                        # ── Attachment download ──
                        if attachment:
                            file_data = base64.b64decode(attachment["data"])
                            st.download_button(
                                label=f"📎 Download {attachment['filename']} ({attachment['size'] // 1024} KB)",
                                data=file_data,
                                file_name=attachment["filename"],
                                mime=attachment.get("mime_type", "application/octet-stream"),
                                key=f"dl_{block.index}_{i}",
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
