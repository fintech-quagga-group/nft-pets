import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st


st.markdown('## NFT Pet Marketplace')

pets_for_sale = contract.functions.getPetsForSale().call()

for pet in pets_for_sale:
    st.image(contract.functions.tokenURI(pet).call())