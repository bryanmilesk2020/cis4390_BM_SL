### Block Structure

##### Hash

1. SHA-256
2. created when block's contents (index, ts, transaction data, previous block hash) are finalized but before block is added to chain, and compute hashes over all the fields
3. takes the hash of everything in the block, including the previous hash  

##### Timestamp

1. Timestamp will mark when the block was added to the blockchain.
2. Timestamp will be in human-readable format
3. used to help filter records, be used as part of hash, & support auditing

##### Index

1. needed to quickly retrieve specific information rather than looking through the whole blockchain history which would be too time-consuming
2. extract data, process it into a readable format, store it in a database, index it based on a feature (such as transaction type or address), have the indexed data be accessed through a API for ease of use
3. data extraction component needs to be able to **1)establish a connection to a blockchain node, 2)capture data real-time as new blocks and transactions are being validated.**
4. database management component that **can handle large volumes of data**
5. **index engine** that can index data **based on certain features**
6. Search API that provides the ability to **query** indexed data, and supporting many **filters and search criteria**
7. Indexer that possibly offers **dashboards or graphical interfaces** to visualize data for users. (See if this is necessary or not when using StreamLit)

##### Data

1. Details of important documents
2. features that improve queryability: document_type, created_by, transaction_id,
3. maybe leave out very private information such as SSNs???

##### Previous_hash

1. hash of the previous block


### How will a business record become a transaction?

##### Turn the record or event into a structured object...

1. The object will contain features from the business event such as transaction_id, record_type, business_data, ts, created_by.
2. Run hash of document and store it in "document_hash"
3. Variable "business_data" will contain the hash of the document, document's location, time it was approved, record type, and possibly contract id and who it was approved by.

##### Validate block

1. System should verify if the user is authorized (such as looking through the AD or list of created users). 
2. Check if the amount being inputted for the field is the right amount (not below the minimum or above the max).
3. Check if all required fields are filled.
4. If it violates, if any, business rules.
5. Once it passes all these steps, it is clear to enter the blockchain.

##### One transaction per block

##### Block gets hashed and added to ledger

1. add business_data to block
2. Compute hash of all fields (including previous_hash field_)
3. append block to blockchain


### Chain integrity rules

1. If the hash of a document in a block is recomputed, it must equal the hash already stored in the document_hash variable located in the business data of the block.
2. The previous_hash must be equal to the hash of all the contents in the previous block, with the exception of the genesis block.
3. Genesis block will have a hard-coded value for the "previous_hash" field/variable of 0.
4. Timestamp cannot be less than the timestamp of the previous block. Nor can it have a value that would be in the future at that point in time when the block is created.
5. Business/block validation. All required fields must be filled, no negative transactions, all documents must have a document hash and all blocks must have a block hash before being appended to the chain.
6. Corrections must be a new block since previous blocks that are already appended cannot be edited.
7. ** Any user that is logged in as a business-owner or manager is allowed to append blocks/upload documents. Though, business-owners will approve the upload.


