import time
import hashlib
import json
import base64


class Transaction:
    def __init__(self, doc_type, doc_id, details, sender, attachment=None):
        self.doc_type = doc_type
        self.doc_id = doc_id
        self.details = details
        self.sender = sender
        self.timestamp = time.time()
        # attachment: {"filename": str, "data": base64_str, "size": int}
        self.attachment = attachment

    def to_dict(self):
        return {
            "doc_type": self.doc_type,
            "doc_id": self.doc_id,
            "details": self.details,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "attachment": self.attachment,
        }


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, creator_handle):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.creator_handle = creator_handle
        self.hash = self.compute_hash()

    def compute_hash(self):
        # Exclude attachment binary data from hash to keep it deterministic & fast
        tx_for_hash = []
        for tx in self.transactions:
            tx_copy = dict(tx)
            if tx_copy.get("attachment"):
                tx_copy["attachment"] = {
                    "filename": tx_copy["attachment"].get("filename"),
                    "size": tx_copy["attachment"].get("size"),
                }
            tx_for_hash.append(tx_copy)

        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": tx_for_hash,
                "previous_hash": self.previous_hash,
                "creator_handle": self.creator_handle,
            },
            sort_keys=True,
        ).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0",
            creator_handle="System",
        )
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def validate_transaction(self, tx: Transaction):
        if not tx.doc_id or not str(tx.doc_id).strip():
            return False, "Validation Failed: Document ID cannot be empty."

        if tx.doc_type == "Invoice":
            amount = tx.details.get("amount", 0)
            if float(amount) <= 0:
                return False, "Validation Failed: Invoice amount must be greater than $0.00."

        elif tx.doc_type == "Contract":
            parties = tx.details.get("parties", "")
            if len(parties.split(",")) < 2:
                return False, "Validation Failed: Contracts require at least 2 parties (separated by a comma)."

        return True, "Valid"

    def add_transaction(self, transaction: Transaction):
        is_valid, message = self.validate_transaction(transaction)
        if is_valid:
            self.pending_transactions.append(transaction.to_dict())
            return True, "Transaction securely added to the pending pool."
        else:
            return False, message

    def mint_pending_transactions(self, creator_handle):
        if len(self.pending_transactions) == 0:
            return False, "No pending transactions to mint."

        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            timestamp=time.time(),
            previous_hash=self.get_latest_block().hash,
            creator_handle=creator_handle,
        )
        self.chain.append(new_block)
        self.pending_transactions = []
        return True, f"Block #{new_block.index} successfully minted with {len(new_block.transactions)} records."

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.compute_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    # ── Helpers for new features ──────────────────────────────────────────────

    def all_transactions(self):
        """Return every committed transaction across all blocks (flat list)."""
        txs = []
        for block in self.chain[1:]:  # skip genesis
            for tx in block.transactions:
                txs.append({**tx, "_block_index": block.index, "_block_hash": block.hash})
        return txs

    def search_transactions(self, query: str = "", doc_type: str = "All"):
        """Filter committed transactions by free-text query and/or doc type."""
        query = query.lower().strip()
        results = []
        for tx in self.all_transactions():
            if doc_type != "All" and tx.get("doc_type") != doc_type:
                continue
            if query:
                haystack = json.dumps(tx).lower()
                if query not in haystack:
                    continue
            results.append(tx)
        return results

    def stats(self):
        """Return aggregate metrics for the dashboard."""
        all_tx = self.all_transactions()
        invoices = [t for t in all_tx if t["doc_type"] == "Invoice"]
        contracts = [t for t in all_tx if t["doc_type"] == "Contract"]
        total_value = sum(float(t["details"].get("amount", 0)) for t in invoices)
        return {
            "total_blocks": len(self.chain),
            "total_transactions": len(all_tx),
            "total_invoices": len(invoices),
            "total_contracts": len(contracts),
            "total_invoice_value": total_value,
            "pending": len(self.pending_transactions),
        }
