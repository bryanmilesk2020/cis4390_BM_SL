import streamlit as st
import time
from blockchain import Blockchain, Transaction

st.set_page_config(page_title="Blockchain Tracker", page_icon="🔗", layout="centered")

if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

bc = st.session_state.blockchain # shorthand reference

st.title("🔗 Document Tracking Blockchain")
st.markdown("A private, immutable ledger for verifying business documents.")

with st.sidebar:
    st.header("⚙️ Node Configuration")
    current_user = st.text_input("Current User Handle", value="admin_user_01")
    st.divider()
    st.metric("Pending Transactions", len(bc.pending_transactions))
    st.metric("Total Blocks", len(bc.chain))

tab1, tab2, tab3 = st.tabs(["📝 Process Records", "📖 View Ledger", "🛡️ Verify Integrity"])

# --- TAB 1: Add Records & Mint ---
with tab1:
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
            
        submitted = st.form_submit_button("Submit Transaction", use_container_width=True)
        
        if submitted:
            new_tx = Transaction(doc_type, doc_id, details, current_user)
            success, msg = bc.add_transaction(new_tx)
            
            if success:
                st.success(msg)
            else:
                st.error(f"🚨 {msg}")

    st.divider()
    
    st.header("2. Pending Transaction Pool")
    if bc.pending_transactions:
        st.json(bc.pending_transactions)
        if st.button("🔨 Mint Block (Process Pool)", type="primary", use_container_width=True):
            success, msg = bc.mint_pending_transactions(current_user)
            if success:
                st.success(msg)
                st.rerun() # Refresh the page to clear the pool visually
    else:
        st.info("The transaction pool is currently empty.")

# --- TAB 2: View the Blockchain ---
with tab2:
    st.header("Immutable Blockchain Ledger")
    
    for block in reversed(bc.chain):
        tx_count = len(block.transactions)
        
        with st.expander(f"📦 Block #{block.index} | Records: {tx_count} | Minted By: {block.creator_handle}"):
            st.write(f"**Timestamp:** {time.ctime(block.timestamp)}")
            st.write(f"**Block Hash:** `{block.hash}`")
            st.write(f"**Previous Hash:** `{block.previous_hash}`")
            
            if block.index > 0: 
                st.write("**Stored Transactions:**")
                st.json(block.transactions)

# --- TAB 3: Validate the Chain ---
with tab3:
    st.header("System Health & Security")
    
    if st.button("Validate Blockchain", use_container_width=True):
        with st.spinner('Running cryptographic hash verification...'):
            time.sleep(1)
            is_valid = bc.is_chain_valid()
            
        if is_valid:
            st.success("🛡️ Cryptographic Validation Passed: The blockchain is secure!")
            st.balloons()
        else:
            st.error("🚨 CRITICAL WARNING: Blockchain integrity compromised!")