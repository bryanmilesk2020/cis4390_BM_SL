import time
# Import the Block class from your blocks.py file
from blocks import Block

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # The very first block needs no previous hash
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
        # Link the new block to the previous one
        new_block.previous_hash = self.get_latest_block().hash
        # Recompute the hash since the previous_hash just changed
        new_block.hash = new_block.compute_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        # Loop through the chain to ensure no blocks have been tampered with
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Check if the current block's hash is still accurate
            if current_block.hash != current_block.compute_hash():
                return False

            # Check if the current block actually links to the previous block
            if current_block.previous_hash != previous_block.hash:
                return False

        return True
