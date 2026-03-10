### 1. Business Record Schema 
(Fields strictly contained within the raw business document itself)

This represents the raw business data (e.g., the JSON payload or uploaded file) 
before it is hashed and embedded into a block.

##### Common Business Fields for all document types

1. business_id / company_name: The identifier for the entity filing the record.
2. date_of_transaction: The real-world date the business event occurred.
3. amount: The financial value associated with the record (if applicable).
4. currency: The currency used for the amount (e.g., USD).
5. counterparty: The vendor, client, or employee involved in the transaction.
6. description: A plain-text memo or summary of the business event.
7. authorizing_user: The employee or account that submitted the record to the dashboard.

##### Gross Receipts Records

(following show **incoming business revenue**)
1. receipt_source     //source of revenue (customer payment, invoice payment, etc)
2. receipt_amount     //total revenue received
3. payment_method     //payment typed (cash, credit, bank transfer, etc.)
4. invoice_number           // associated invoice number if applicable
5. mdeposit_reference        // bank deposit ID or deposit slip reference
6. receipt_document_type    // type of supporting document (invoice, receipt book entry, Form 1099-MISC)
7. customer_name            // name of customer who paid
8. transaction_date         // date revenue was received
9. income_category          // classification of revenue source

##### Purchase Record 

(following document **business purchases and supplier transactions**)
1. vendor_name              // business or person paid for the purchase
2. purchase_amount          // amount paid for the purchase
3. payment_method           // payment type (cash, credit card, check, etc.)
4. purchase_date            // date the purchase occurred
5. item_description         // description of purchased goods or materials
6. proof_of_payment_type    // type of document used as proof (invoice, receipt, canceled check)
7. invoice_reference        // invoice number from vendor
8. purchase_category        // category of purchase (inventory, equipment, supplies, etc.)

##### Expense Record

(documents **operational business expenses**)
1. payee_name               // individual or company receiving payment
2. expense_amount           // total cost of the expense
3. expense_category         // category of expense (utilities, office supplies, rent, etc.)
4. expense_date             // date the expense occurred
5. payment_method           // payment method used
6. service_or_item_description // explanation of service received or item purchased
7. proof_of_payment_type    // receipt, bank statement, credit card receipt, etc.
8. business_purpose         // explanation of why the expense was necessary for business

##### Travel/Transportation/Entertainment/Gift Expense Record

(documents **special tax-deductible travel and entertainment expenses** that require additional justification)
1. payee_name               // individual or company receiving payment
2. expense_amount           // total cost of the expense
3. expense_category         // category of expense (utilities, office supplies, rent, etc.)
4. expense_date             // date the expense occurred
5. payment_method           // payment method used
6. service_or_item_description // explanation of service received or item purchased
7. proof_of_payment_type    // receipt, bank statement, credit card receipt, etc.
8. business_purpose         // explanation of why the expense was necessary for business
9. attendees                // individuals involved in entertainment expenses
10. gift_recipient           // person receiving business gift (if applicable)
11. gift_value               // value of gift provided

##### Asset Record

(tracks **long-term business assets and depreciation calculations**)
1. asset_name               // name of the business asset
2. asset_category           // equipment, vehicle, property, etc.
3. acquisition_date         // date the asset was purchased or acquired
4. purchase_price           // original cost of the asset
5. improvement_costs        // cost of improvements made to the asset
6. section179_deduction     // Section 179 tax deduction taken for the asset
7. depreciation_method      // depreciation method applied
8. annual_depreciation      // yearly depreciation amount
9. casualty_loss_deductions // losses due to disasters such as fire or storm
10. usage_description        // explanation of how the asset is used in the business
11. disposal_date            // date the asset was sold or disposed of
12. selling_price            // sale price of the asset
13. sale_expenses            // costs incurred when selling the asset

##### Employment Tax Record

(track **payroll tax information and compliance documentation**)
1. employee_id_number       // unique identifier for employee
2. employee_name            // employee full name
3. employee_address         // employee mailing address
4. employee_ssn             // employee Social Security Number
5. employment_start_date    // employee hire date
6. employment_end_date      // termination date if applicable
7. pay_period               // payroll period covered
8. wage_payment_amount      // wages paid during pay period
9. annuity_or_pension_paid  // annuity or pension payment amount
10. tips_reported            // tips reported by employee
11. tax_withheld_amount      // amount of employment taxes withheld
12. tax_deposit_date         // date tax deposit was made to the government
13. tax_deposit_amount       // amount deposited
14. paid_sick_leave_period   // dates employee took paid sick leave
15. fringe_benefits_provided // description of benefits given (healthcare, etc.)
16. allocated_tips           // tips allocated by employer
17. tax_return_reference     // reference to employment tax return filed
18. withholding_certificate_reference // reference to employee tax withholding form

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
