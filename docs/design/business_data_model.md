### Business Record Schema - Fields that will be in ONLY THE DOCUMENT ITSELF

1. 

### Transaction Data format - Fields that will be the metadata that is included in the block in addition to the business data defined in Business Record Schema

1. transaction_id: transaction number in blockchain
2. document_hash: SHA-256 hash that uniquely identifies the document itself and will serve as proof of integrity
3. record_type: the type of record that is being filed (e.g. gross receipts, employment taxes, expenses)
4. timestamp: the time when the block was created 


### How the dashboard will read ledger data
