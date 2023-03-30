import os
import json
from web3 import Web3, Account
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
def login_form():
    # define session variables to manage logged in state
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

    def login():
        session = st.session_state

        if session.username in w3.eth.accounts:
            session.logged_in = True

            # change dummy variable to trigger rerun
            session.login_dummy = not session.login_dummy

            account = Account.privateKeyToAccount(os.getenv('PRIVATE_KEY'))

            # verify that the stored private key is correct for the provided address
            if Web3.toChecksumAddress(session.username) == account.address:
                st.sidebar.success(f'Logged into account with address: {session.username}')
                w3.eth.default_account = session.username

                # call the contract login function to login the user
                contract.functions.login().transact({'from': session.username, 'gas': 1000000})

                return True
            else:
                st.sidebar.error(f'Private key is not correct for address: {session.username}')
                return False

        return False

    def logout():
        session = st.session_state
        session.logged_in = False
        session.form_hidden = False
        session.logout_dummy = not session.logout_dummy

        contract.functions.logout().transact({'from': session.username, 'gas': 1000000})
        w3.eth.default_account = None

    st.sidebar.title('Login')

    if not session.logged_in:
        if st.sidebar.button('Login', key='login', on_click=login):
            if login():
                st.sidebar.success(f'Logged in as {session.username}')
                session.form_hidden = True
            else:
                st.sidebar.error('Incorrect username or password')

        if not session.form_hidden:
            session.username = st.sidebar.text_input('Account ID', value=session.username)

    if session.logged_in:
        st.sidebar.write('Logged in')
        if st.sidebar.button('Logout', key='logout', on_click=logout):
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
