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
private_key = os.get_env("PRIVATE_KEY")
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

def login_form():
    def login():
        session = st.session_state
        session.logged_in = True
        session.login_dummy = not session.login_dummy  # Change dummy variable to trigger rerun

    def logout():
        session = st.session_state
        session.logged_in = False
        session.form_hidden = False
        session.logout_dummy = not session.logout_dummy  # Change dummy variable to trigger rerun

    session = st.session_state
    if not "logged_in" in session:
        session.logged_in = False
    if not "form_hidden" in session:
        session.form_hidden = False
    if not "username" in session:
        session.username = ""
    if not "password" in session:
        session.password = ""
    if not "login_dummy" in session:
        session.login_dummy = False
    if not "logout_dummy" in session:
        session.logout_dummy = False

    st.sidebar.title("Login")

    if not session.logged_in:
        if st.sidebar.button("Login", key="login", on_click=login):

            if session.username == "admin" and session.password == "1234":
                login()
                st.sidebar.success("Logged in as {}".format(session.username))
                session.form_hidden = True  # Hide the form after attempting to log in
            else:
                st.sidebar.error("Incorrect username or password")

        if not session.form_hidden:
            session.username = st.sidebar.text_input("Username", value=session.username)
            session.password = st.sidebar.text_input("Password", type="password", value=session.password)

    if session.logged_in:
        st.sidebar.write("Logged in")
        if st.sidebar.button("Logout", key="logout", on_click=logout):
            logout()

login_form()

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
