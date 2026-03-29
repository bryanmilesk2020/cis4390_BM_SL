import streamlit as st
import time
from blocks import InvoiceBlock, ContractBlock
from blockchain import Blockchain

# --- 1. Page Configuration MUST BE FIRST ---
# Streamlit requires this to be the very first Streamlit command called
st.set_page_config(page_title="Blockchain Tracker", page_icon="🔗")

# --- 2. Initialize Blockchain in Session State ---
# This ensures our blockchain persists across page reloads
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

# --- 3. UI Header ---
st.title("🔗 Document Tracking Blockchain")

# --- 4. Sidebar for User Settings ---
st.sidebar.header("User Settings")
# This is the "handle" we built earlier!
current_user = st.sidebar.text_input("Current User Handle", value="admin_user_01")
st.sidebar.info("Any blocks created will be stamped with this user handle.")

# --- 5. Main Application Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add Document", "📖 View Ledger", "🛡️ Verify Integrity"])

# --- TAB 1: Add a New Block ---
with tab1:
    st.header("Mint a New Document Block")
    doc_type = st.selectbox("Select Document Type", ["Invoice", "Contract"])
    
    # Create a form so the app doesn't refresh until "Submit" is clicked
    with st.form("add_doc_form", clear_on_submit=True):
        if doc_type == "Invoice":
            inv_num = st.text_input("Invoice Number (e.g., INV-001)")
            amt = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
        else:
            contract_id = st.text_input("Contract ID (e.g., CTR-999)")
            parties = st.text_input("Parties Involved (e.g., Corp A, Corp B)")
            
        submitted = st.form_submit_button("Add to Blockchain")
        
        if submitted:
            chain_length = len(st.session_state.blockchain.chain)
            
            if doc_type == "Invoice":
                new_block = InvoiceBlock(
                    index=chain_length,
                    transactions=[], # Keeping it simple for the UI right now
                    timestamp=time.time(),
                    previous_hash="", # The blockchain class handles this
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
                
            # Add the newly minted block to our session state blockchain
            st.session_state.blockchain.add_block(new_block)
            st.success(f"✅ {doc_type} Block #{chain_length} securely added to the chain!")

# --- TAB 2: View the Blockchain ---
with tab2:
    st.header("Immutable Blockchain Ledger")
    
    # Loop through the chain in reverse to see the newest blocks first
    for block in reversed(st.session_state.blockchain.chain):
        # Create a visually distinct dropdown for each block
        with st.expander(f"Block #{block.index} | Type: {block.document_type} | By: {block.creator_handle}"):
            st.write(f"**Timestamp:** {time.ctime(block.timestamp)}")
            st.write(f"**Block Hash:** `{block.hash}`")
            st.write(f"**Previous Hash:** `{block.previous_hash}`")
            
            if block.index > 0: # Genesis block has no business data
                st.write("**Business Data:**")
                st.json(block.business_data)

# --- TAB 3: Validate the Chain ---
with tab3:
    st.header("System Health & Security")
    st.write("Click below to run a cryptographic check on the entire chain to ensure no data has been tampered with.")
    
    if st.button("Validate Blockchain"):
        is_valid = st.session_state.blockchain.is_chain_valid()
        if is_valid:
            st.success("🛡️ Cryptographic Validation Passed: The blockchain is valid and secure!")
            st.balloons()
        else:
            st.error("🚨 CRITICAL WARNING: Blockchain integrity compromised! Hashes do not match.")
