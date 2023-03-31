import os
import json
from web3 import Web3, Account
from pathlib import Path
from dotenv import dotenv_values
import openai

import streamlit as st

env = dotenv_values()

w3 = Web3(Web3.HTTPProvider(env["WEB3_PROVIDER_URI"]))
openai.api_key = env["OPENAI_API_KEY"]

################################################################################
# Contract Helper function:
################################################################################
@st.cache_resource
def load_contract():
    with open(Path('./Smart_Contracts/Compiled/pet_token_abi.json')) as f:
        pet_token_abi = json.load(f)

    contract_address = env["SMART_CONTRACT_ADDRESS"]

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

            account = Account.privateKeyToAccount(env['PRIVATE_KEY'])

            st.write(session.username)
            st.write(account.address)
            st.write(env['PRIVATE_KEY'])

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
        if not session.form_hidden:
            session.username = st.sidebar.text_input('Account ID', value=session.username)
        if st.sidebar.button('Login', key='login', on_click=login):
            if login():
                st.sidebar.success(f'Logged in as {session.username}')
                session.form_hidden = True
            else:
                st.sidebar.error('Incorrect username or password')

    if session.logged_in:
        st.sidebar.write('Logged in')
        if st.sidebar.button('Logout', key='logout', on_click=logout):
            logout()

login_form()

################################################################################
# Check if user is logged in before displaying the rest of the code
################################################################################
session = st.session_state
if session.logged_in:
    ################################################################################
    # Register new NFT Pet
    ################################################################################

    st.title("Register New NFT Pet")

    with open("Resources/Animals.txt") as file:
        all_animals = file.read().splitlines()
        selection = st.selectbox('Select animal', all_animals) 
    
    animal = str(selection.lower().replace('','_'))
    PROMPT = (f"pixel art {animal}")

    def generate_nft_pet():
        response = openai.Image.create(
        prompt=PROMPT,
        n=1,
        size="256x256")
        return response

    pet_name = st.text_input('Name')
    price = st.text_input('Price in Wei')
    is_buyable = st.radio(
        "List Pet on Marketplace?",
        ('Yes', 'No')
    )

    if st.button("Register NFT Pet"):
        nft_uri = generate_nft_pet()['data'][0]['url']

        tx_hash = contract.functions.registerPet(
            pet_name,
            session.username,
            int(price),
            nft_uri,
            True if is_buyable == 'Yes' else False
        ).transact({'from': session.username, 'gas': 1000000})

        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Transaction receipt mined:")
        with st.expander('View Transaction Receipt', expanded=False):
            st.write(dict(receipt))

        st.write('New NFT pet created:')
        st.image(nft_uri)

    st.markdown("---")

    ################################################################################
    # Display a Token
    ################################################################################
    st.markdown("## Display an NFT Pet")

    tokens = contract.functions.balanceOf(session.username).call()

    token_id = st.selectbox("Select a Pet", list(range(tokens)))

    if st.button("Display"):
        token_uri = contract.functions.tokenURI(token_id).call()
        st.image(token_uri)

    st.markdown("---")

    ################################################################################
    # View tokens that you own
    ################################################################################
    st.markdown('## Your NFT Pets')

    owned_pets = contract.functions.getOwnedPets(session.username).call()

    for pet in owned_pets:
        st.image(contract.functions.tokenURI(pet).call())

    ################################################################################
    # View all tokens available for sale
    ################################################################################
    st.markdown('## NFT Pet Marketplace')

    pets_for_sale = contract.functions.getPetsForSale().call()

    for pet in pets_for_sale:
        st.image(contract.functions.tokenURI(pet).call())
else:
    st.markdown("# :arrow_left:")
    st.title('Please use the sidebar to login with a connected Ethereum address.')