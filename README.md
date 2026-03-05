CIS 4390 Capstone: Business Blockchain Dashboard
This project is a secure, tamper-proof business dashboard developed for the CIS 4390 Capstone course. It leverages blockchain technology to ensure that business data remains immutable and verifiable, providing a high level of integrity for corporate reporting and data storage.

Features
Immutable Ledger: Utilizes a custom blockchain implementation to store business data securely.

Tamper-Proof Verification: Ensures that once data is recorded, any alteration is detectable.

Business Insights: A centralized dashboard for visualizing and managing secure data entries.

Python-Based Architecture: Built entirely in Python for modularity and ease of testing.

Project Structure
src/blockchain: Core logic for block creation, cryptographic hashing, and chain validation.

scripts: Automation scripts for deployment, environment setup, and data migration.

data: Local storage for ledger state and business records.

assets: UI components and static files for the dashboard interface.

tests: Comprehensive unit tests to ensure blockchain integrity and system stability.

docs: Detailed project documentation and technical specifications.

Getting Started
Prerequisites
Python 3.8 or higher

pip (Python package manager)

Installation
Clone the repository:

Bash
git clone https://github.com/bryanmilesk2020/cis4390_BM_SL.git
cd cis4390_BM_SL
Set up a virtual environment (optional but recommended):

Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:
(Ensure you have a requirements.txt file in the root)

Bash
pip install -r requirements.txt
Usage
To launch the dashboard or run the blockchain node:

Bash
python scripts/start_dashboard.py
Testing
To run the automated test suite and verify the blockchain logic:

Bash
pytest tests/
Acknowledgments
Course: CIS 4390 (Capstone)

Developer: Bryan Mileski (bryanmilesk2020)
