
import streamlit as st
import pandas as pd
import numpy as np
from hashlib import sha256
import json

#more attributes may have to be added inside class Block
#different document types will have different attributes under "business_data", so use inheritance, on child class for each doc type
class Block: 
    def __init__(self, index, transactions, timestamp, document_type, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.document_type = document_type
        self.previous_hash = previous_hash
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexidigest()
    
