### 1. Business Record Schema 
(Fields strictly contained within the raw business document itself)

This represents the raw business data (e.g., the JSON payload or uploaded file) 
before it is hashed and embedded into a block.

1. business_id / company_name: The identifier for the entity filing the record.
2. date_of_transaction: The real-world date the business event occurred.
3. amount: The financial value associated with the record (if applicable).
4. currency: The currency used for the amount (e.g., USD).
5. counterparty: The vendor, client, or employee involved in the transaction.
6. description: A plain-text memo or summary of the business event.
7. authorizing_user: The employee or account that submitted the record to the dashboard.

##### Gross Receipts Records

1. receipt_source     //source of revenu (customer payment, invoice payment, etc)

--------------------------------------------------------------------------------

### 2. Transaction Data Format 
(Metadata included in the block alongside the business data)

1. transaction_id: The unique transaction number in the blockchain.
2. document_hash: The SHA-256 hash that uniquely identifies the document itself and serves as proof of integrity.
3. record_type: The category of the filed record (e.g., gross receipts, employment taxes, expenses).
4. timestamp: The exact Unix epoch time when the block was created.
5. digital_signature (Optional): A cryptographic signature from the authorizing_user to prove non-repudiation.

--------------------------------------------------------------------------------

### 3. How the Dashboard Reads Ledger Data

To ensure the dashboard displays only valid, tamper-proof data, it follows a strict read-and-verify process.



STEP 1: Chain Synchronization & Validation
* Upon initialization, the dashboard backend fetches the entire blockchain.
* It immediately runs the `is_chain_valid()` function. 
* If the chain is broken or tampered with, the dashboard locks down and displays an "Integrity Compromised" alert.

STEP 2: Data Extraction & Parsing
* If the chain is valid, the backend iterates through every block (from Block 1 to the latest).
* It extracts the transactions array from each block, pulling the metadata (e.g., record_type, document_hash).

STEP 3: Cross-Referencing Raw Documents
* The dashboard fetches the raw business records (from local storage or a standard database) using the transaction_id.
* **CRITICAL SECURITY CHECK:** Before displaying the document, the backend re-hashes the raw document and compares it to the document_hash stored in the blockchain block. If they match, the document is verified as untampered.

STEP 4: Aggregation & Visualization
* The verified data is grouped by record_type and sorted by date_of_transaction.
* This aggregated data is passed to the frontend UI to populate the charts, graphs, and tables.
