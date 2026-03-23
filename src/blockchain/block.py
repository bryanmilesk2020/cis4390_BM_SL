import time
from blocks import Transaction, InvoiceBlock
from blockchain import Blockchain

# Initialize
my_chain = Blockchain()

# Create a block
new_invoice = InvoiceBlock(
    index=1,
    transactions=[],
    timestamp=time.time(),
    previous_hash="", 
    creator_handle="bryan_m",
    invoice_number="INV-100",
    amount=500.00
)

# Add to chain
my_chain.add_block(new_invoice)
