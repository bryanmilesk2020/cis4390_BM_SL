import time
import hashlib
import json

# --- 1. NEW: Transaction Class ---
class Transaction:
    def __init__(self, doc_type, doc_id, details, sender):
        self.doc_type = doc_type
        self.doc_id = doc_id
        self.details = details
        self.sender = sender
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "doc_type": self.doc_type,
            "doc_id": self.doc_id,
            "details": self.details,
            "sender": self.sender,
            "timestamp": self.timestamp
        }

# --- 2. UPDATED: Unified Block Class ---
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, creator_handle):
        self.index = index
        self.transactions = transactions # Now holds a LIST of transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.creator_handle = creator_handle
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "creator_handle": self.creator_handle
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

# --- 3. UPDATED: Blockchain Engine ---
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = [] # NEW: The waiting room for records
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0, 
            transactions=[], 
            timestamp=time.time(), 
            previous_hash="0", 
            creator_handle="System"
        )
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    # --- NEW: Validation Logic ---
    def validate_transaction(self, tx: Transaction):
        # Rule 1: Document ID cannot be blank
        if not tx.doc_id or not str(tx.doc_id).strip():
            return False, "Validation Failed: Document ID cannot be empty."
        
        # Rule 2: Invoice specific rules
        if tx.doc_type == "Invoice":
            amount = tx.details.get("amount", 0)
            if float(amount) <= 0:
                return False, "Validation Failed: Invoice amount must be greater than $0.00."
                
        # Rule 3: Contract specific rules
        elif tx.doc_type == "Contract":
            parties = tx.details.get("parties", "")
            if len(parties.split(",")) < 2:
                return False, "Validation Failed: Contracts require at least 2 parties (separated by a comma)."
                
        return True, "Valid"

    # --- NEW: Transaction Processing ---
    def add_transaction(self, transaction: Transaction):
        is_valid, message = self.validate_transaction(transaction)
        
        if is_valid:
            self.pending_transactions.append(transaction.to_dict())
            return True, "Transaction securely added to the pending pool."
        else:
            return False, message

    # --- UPDATED: Minting batches transactions ---
    def mint_pending_transactions(self, creator_handle):
        if len(self.pending_transactions) == 0:
            return False, "No pending transactions to mint."

        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions, # Bundle all waiting records
            timestamp=time.time(),
            previous_hash=self.get_latest_block().hash,
            creator_handle=creator_handle
        )
        
        self.chain.append(new_block)
        self.pending_transactions = [] # Empty the pool after minting
        return True, f"Block #{new_block.index} successfully minted with {len(new_block.transactions)} records."

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.compute_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True
