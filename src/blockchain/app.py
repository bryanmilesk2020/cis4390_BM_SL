import streamlit as st
import time
from blocks import InvoiceBlock, ContractBlock
from blockchain import Blockchain

# --- 1. Page Configuration MUST BE FIRST ---
st.set_page_config(page_title="Blockchain Tracker", page_icon="🔗", layout="centered")

# --- 2. Initialize Blockchain in Session State ---
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

# --- 3. UI Header ---
st.title("🔗 Document Tracking Blockchain")
st.markdown("A private, immutable ledger for verifying business documents.")

# --- 4. Sidebar for User Settings ---
with st.sidebar:
    st.header("⚙️ Node Configuration")
    current_user = st.text_input("Current User Handle", value="admin_user_01")
    
    st.divider()
    
    st.write("### About This Network")
    st.info(
        "This is a permissioned blockchain tracking "
        "business documents (Invoices & Contracts). Every document "
        "is cryptographically hashed to ensure immutability and provenance."
    )
    st.success("Network Status: Online 🟢")

# --- 5. Main Application Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add Document", "📖 View Ledger", "🛡️ Verify Integrity"])

# --- TAB 1: Add a New Block ---
with tab1:
    st.header("Mint a New Document Block")
    doc_type = st.selectbox("Select Document Type", ["Invoice", "Contract"])
    
    with st.form("add_doc_form", clear_on_submit=True):
        # Using columns to make the form look cleaner and professional
        col1, col2 = st.columns(2)
        
        if doc_type == "Invoice":
            with col1:
                inv_num = st.text_input("Invoice Number (e.g., INV-001)")
            with col2:
                amt = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
        else:
            with col1:
                contract_id = st.text_input("Contract ID (e.g., CTR-999)")
            with col2:
                parties = st.text_input("Parties Involved (e.g., Corp A, Corp B)")
            
        # Submit button for the form
        submitted = st.form_submit_button("Mint Block", use_container_width=True)
        
        if submitted:
            chain_length = len(st.session_state.blockchain.chain)
            
            if doc_type == "Invoice":
                new_block = InvoiceBlock(
                    index=chain_length,
                    transactions=[], 
                    timestamp=time.time(),
                    previous_hash="", 
                    creator_handle=current_user,
                    invoice_number=inv_num,
                    amount=amt
                )
            elif doc_type == "Contract":
                new_block = ContractBlock(
                    index=chain_length,
                    transactions=[],
                    timestamp=time.time(),
                    previous_hash="",
                    creator_handle=current_user,
                    contract_id=contract_id,
                    parties_involved=parties
                )
                
            # Add block and show a sleek toast notification
            st.session_state.blockchain.add_block(new_block)
            st.toast(f"{doc_type} Block #{chain_length} successfully minted!", icon="✅")

# --- TAB 2: View the Blockchain ---
with tab2:
    st.header("Immutable Blockchain Ledger")
    
    # --- Metrics Dashboard ---
    total_blocks = len(st.session_state.blockchain.chain)
    latest_type = st.session_state.blockchain.get_latest_block().document_type
    
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Total Blocks", value=total_blocks)
    m2.metric(label="Latest Minted", value=latest_type)
    m3.metric(label="Tamper Status", value="Secure 🔒")
    
    st.divider() 
    
    # Loop through the chain in reverse to see the newest blocks first
    for block in reversed(st.session_state.blockchain.chain):
        # Create a visually distinct dropdown for each block
        with st.expander(f"📦 Block #{block.index} | Type: {block.document_type} | By: {block.creator_handle}"):
            st.write(f"**Timestamp:** {time.ctime(block.timestamp)}")
            st.write(f"**Block Hash:** `{block.hash}`")
            st.write(f"**Previous Hash:** `{block.previous_hash}`")
            
            if block.index > 0: # Genesis block has no business data
                st.write("**Business Data:**")
                st.json(block.business_data)

# --- TAB 3: Validate the Chain ---
with tab3:
    st.header("System Health & Security")
    st.write("Run a cryptographic check on the entire chain to ensure no data has been tampered with.")
    
    if st.button("Validate Blockchain", use_container_width=True):
        # Add a tiny loading spinner for dramatic effect
        with st.spinner('Running cryptographic hash verification...'):
            time.sleep(1) # Artificial delay to make it feel like it's calculating heavily
            is_valid = st.session_state.blockchain.is_chain_valid()
            
        if is_valid:
            st.success("🛡️ Cryptographic Validation Passed: The blockchain is valid and secure!")
            st.balloons()
        else:
            st.error("🚨 CRITICAL WARNING: Blockchain integrity compromised! Hashes do not match.")
