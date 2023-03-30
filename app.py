import os
import json
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from pathlib import Path
from dotenv import load_dotenv

import streamlit as st

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

################################################################################
# Contract Helper function:
################################################################################
@st.cache_resource
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
# login sidebar
################################################################################

w3.eth.default_account = w3.eth.accounts[5]  # replace with the address of your account

st.write(w3.eth.accounts[5])

# Sign the message with the account private key
private_key = "0x73fb6116ac8818aad7e761ec77940ccc5a335c9dc5474282420e412b16092897"  # replace with the private key of the Ganache account that you want to log in
account = Account.privateKeyToAccount(private_key)
message = encode_defunct(text='login')
signature = account.sign_message(message)

# extract the v, r, s values from the signature
v, r, s = signature.v, signature.r, signature.s

# get the address that signed the message
signer_address = Account.recover_message(message, vrs=(v, r, s))

st.write(signer_address)

# Call the login function to log in a user
tx_hash = contract.functions.login(signature.signature).transact({'from': w3.eth.accounts[2], 'gas': 1000000})
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)


st.write(tx_receipt)



def test():
    def login():
        session = st.session_state
        session.logged_in = True

    session = st.session_state
    if not hasattr(session, "logged_in"):
        session.logged_in = False

    st.sidebar.title("Login")

    if not session.logged_in:
        username = st.sidebar.text_input("Username")

        if st.sidebar.button("Login"):
            # You can add authentication logic here to check the credentials
            login()
            st.sidebar.success("Logged in as {}".format(username))
    else:
        st.sidebar.write("Logged in")

test()

################################################################################
# Drowdown Menu for Pet Generation
################################################################################

st.title("Pet Selector")

with open("Resources/Animals.txt") as file:
    all_animals = file.read().splitlines()

animal = st.selectbox('Select an animal', all_animals) 

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

st.markdown("---")

################################################################################
# View all tokens available for sale
################################################################################

st.markdown('## NFT Pet Marketplace')

pets_for_sale = contract.functions.getPetsForSale().call()

for pet in pets_for_sale:
    st.image(contract.functions.tokenURI(pet).call())
