import time
import hashlib
import json

class Block:
    def __init__(self, index, transactions, timestamp, document_type, previous_hash, creator_handle):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.document_type = document_type
        self.previous_hash = previous_hash
        self.creator_handle = creator_handle
        self.business_data = {}
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "document_type": self.document_type,
            "previous_hash": self.previous_hash,
            "creator_handle": self.creator_handle,
            "business_data": self.business_data
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class InvoiceBlock(Block):
    def __init__(self, index, transactions, timestamp, previous_hash, creator_handle, invoice_number, amount):
        super().__init__(index, transactions, timestamp, "Invoice", previous_hash, creator_handle)
        self.invoice_number = invoice_number
        self.amount = amount
        self.business_data = {
            "invoice_number": self.invoice_number,
            "amount": self.amount
        }
        self.hash = self.compute_hash()

class ContractBlock(Block):
    def __init__(self, index, transactions, timestamp, previous_hash, creator_handle, contract_id, parties_involved):
        super().__init__(index, transactions, timestamp, "Contract", previous_hash, creator_handle)
        self.contract_id = contract_id
        self.parties_involved = parties_involved
        self.business_data = {
            "contract_id": self.contract_id,
            "parties_involved": self.parties_involved
        }
        self.hash = self.compute_hash()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0, 
            transactions=[], 
            timestamp=time.time(), 
            document_type="Genesis", 
            previous_hash="0", 
            creator_handle="System"
        )
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.compute_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.compute_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True