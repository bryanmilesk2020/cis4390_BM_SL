### Block Structure

##### Hash

1. SHA-256
2. hash of previous block's header
3. created when block's contents (index, ts, transaction data, previous block hash) are finalized but before block is added to chain, and compute hashes over all the fields
4.  

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

##### Previous_hash
