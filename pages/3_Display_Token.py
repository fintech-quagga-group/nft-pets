import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

st.markdown("## Display an NFT Pet")

selected_address = st.selectbox("Select Account", options=accounts)

tokens = contract.functions.balanceOf(selected_address).call()

st.write(f"This address owns {tokens} NFT Pets")

token_id = st.selectbox("NFT Pets", list(range(tokens)))

if st.button("Display"):
    owner = contract.functions.ownerOf(token_id).call()

    st.write(f"The NFT Pet is registered to {owner}")

    token_uri = contract.functions.tokenURI(token_id).call()

    st.write(f"The NFT Pet URI is {token_uri}")
    st.image(token_uri)

st.markdown("---")