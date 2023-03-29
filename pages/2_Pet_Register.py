import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

st.title("Register new NFT Pet")
accounts = w3.eth.accounts

address = st.selectbox("Select Pet Owner", options=accounts)

nft_uri = st.text_input("The URI to the Pets")

if st.button("Register NFT Pet"):
    tx_hash = contract.functions.registerPet(
        'petName',
        'ownerName',
        1000,
        nft_uri
    ).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))

st.markdown("---")