import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

################################################################################
# Contract Helper function:
################################################################################
@st.cache(allow_output_mutation=True)
def load_contract():
    with open(Path('./Smart_Contracts/Compiled/pet_token_abi.json')) as f:
        pet_token_abi = json.load(f)

    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    contract = w3.eth.contract(
        address=contract_address,
        abi=pet_token_abi
    )

    return contract

contract = load_contract()

################################################################################
# Register new NFT Pet
################################################################################
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

################################################################################
# Display a Token
################################################################################
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
