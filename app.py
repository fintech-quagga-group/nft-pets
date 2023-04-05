import os
import time
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
# Load contract helper function
################################################################################
@st.cache_resource
def load_contract():
    """Loads the deployed smart contract address from Remix"""

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
# Login sidebar to login with the provided private key in .env file
################################################################################
def login_form():
    """Code to port the login sidebar for each page"""

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
    if not "login_dummy" in session:         # create dummy login variables to trigger "double" page reload
        session.login_dummy = False
    if not "logout_dummy" in session:
        session.logout_dummy = False

    def login():
        """Function to verify that the stored private address is accurate and call the contract login function"""

        session = st.session_state

        # reload the env file
        env = dotenv_values()

        if session.username in w3.eth.accounts:
            account = Account.privateKeyToAccount(session.password)

            # verify that the stored private key is correct for the provided address
            if Web3.toChecksumAddress(session.username) == account.address:
                session.logged_in = True

                # change dummy variable to trigger rerun
                session.login_dummy = not session.login_dummy

                st.sidebar.success(f'Logged into account with address: {session.username}')
                w3.eth.default_account = session.username

                # call the contract login function to login the user
                contract.functions.login().transact({'from': session.username, 'gas': 1000000})

                return True
            else:
                return False

        return False

    def logout():
        """Update session variables and calls smart contract logout function"""

        # update session variables 
        session = st.session_state
        session.logged_in = False
        session.form_hidden = False
        session.logout_dummy = not session.logout_dummy

        # call contract logout function to verify addresses
        contract.functions.logout().transact({'from': session.username, 'gas': 1000000})
        w3.eth.default_account = None
    
    st.sidebar.title('Login')

    # display login form to accept public address
    if not session.logged_in:
        if not session.form_hidden:
            session.username = st.sidebar.text_input('Account ID', value=session.username)
            session.password = st.sidebar.text_input('Private Key', type='password')
        if st.sidebar.button('Login', key='login', on_click=login):
            # call the login function to verify that the address is accurate to the stored private key
            if login():
                st.sidebar.success(f'Logged in as {session.username}')
                session.form_hidden = True
            else:
                st.sidebar.error('Incorrect Account ID or stored private key.')

    # don't show form if user is already logged in; display logout button
    if session.logged_in:
        st.sidebar.write('Logged in')
        if st.sidebar.button('Logout', key='logout', on_click=logout):
            logout()

login_form()

################################################################################
# Use session.logged_in to hide/show all content depending on login status
################################################################################
session = st.session_state

if session.logged_in:

    register_tab, chat_tab, your_pets_tab, marketplace_tab = st.tabs(["Register New Pet", "Chat", "Your Pets", "Marketplace"])

    with register_tab:
        ################################################################################
        # Register new NFT Pet
        ################################################################################
        st.title("Register New NFT Pet")

        # load list of animals that can be created as NFT pets
        with open("Resources/Animals.txt") as file:
            all_animals = file.read().splitlines()
            selection = st.selectbox('Select animal', all_animals) 
        
        # create DALLE prompt based on chosen animal - ex: "pixel art dog"
        animal = str(selection.lower().replace('','_'))
        PROMPT = (f"pixel art {animal}")

        # call openai dalle api to generate image
        def generate_nft_pet():
            response = openai.Image.create(
            prompt=PROMPT,
            n=1,
            size="256x256")
            return response

        # use form inputs to fill in Pet smart contract struct attributes
        pet_name = st.text_input('Name')
        price = st.text_input('Price in Wei')
        is_buyable = st.radio(
            "List Pet on Marketplace?",
            ('Yes', 'No')
        )

        if st.button("Register NFT Pet"):
            nft_uri = generate_nft_pet()['data'][0]['url']

            # call the registerPet smart contract function with the provided Pet info
            tx_hash = contract.functions.registerPet(
                pet_name,
                session.username,
                int(price),
                nft_uri,
                True if is_buyable == 'Yes' else False
            ).transact({'from': session.username, 'gas': 1000000})

            # display transaction receipt if user wants to verify
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Transaction receipt mined:")
            with st.expander('View Transaction Receipt', expanded=False):
                st.write(dict(receipt))

            st.write('New NFT pet created:')
            st.image(nft_uri)

    with chat_tab:
        ################################################################################
        # Chat with your NFT pet 
        ################################################################################
        st.markdown("## Chat With Your NFT Pets")

        # session variables to reset chat history if user selects a new pet
        if not "displayed_pet" in session:
            session.displayed_pet = None
        if not "chat_history" in session:
            session.chat_history = []

        def clear_chat():
            """Helper function to clear the openai chat history for chatgpt call"""

            session.chat_history = []
            output_container.empty()

        # display a selectbox for all of the currently logged in user's pets
        token_id = st.selectbox("Select a Pet", contract.functions.getOwnedPets(session.username).call(), on_change=clear_chat)

        # load the selected NFT pet
        if token_id is not None:
            token_uri = contract.functions.tokenURI(token_id).call()
            st.image(token_uri)

        def get_chatgpt_response(text, pet_name):
            """
            Calls the openai chatgpt function to generate text responses between users and their NFT pets

            Parameters
            ----------
            text : string
                Prompt to ask the NFT pet
            pet_name : string
                The stored name of the NFT pet

            Returns
            -------
            string
                Chatgpt response based on text input
            """

            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are a NFT pet."},
                    {"role": "user", "content": text},
                ]
            )

            # modify the response to replace "system" with the pet name
            message = response.choices[0]['message']
            return f'{pet_name}: {message["content"]}'

        # use session.chat_history to keep a running conversation with the selected NFT pet
        text = st.text_input('Use the text box to send a message to your pet:')
        if text:
            session.chat_history.append({"role": "user", "content": text})
            response = get_chatgpt_response(text, contract.functions.getPet(token_id).call()[0])
            session.chat_history.append({"role": "system", "content": response})

        # use a container so that we can clear the output on pet switch
        output_container = st.container()

        # inside the container, use st.write() to display the messages
        with output_container:
            for message in session.chat_history:
                st.write(f'{message["content"]}')

    with your_pets_tab:
        ################################################################################
        # Displays all of the NFT pets that the current user owns
        ################################################################################
        st.markdown('## Your NFT Pets')

        owned_pets = contract.functions.getOwnedPets(session.username).call()

        for pet in owned_pets:
            st.image(contract.functions.tokenURI(pet).call())

    with marketplace_tab:
        ################################################################################
        # View all pets currently available for sale
        ################################################################################
        st.markdown('## NFT Pet Marketplace')

        pets_for_sale = contract.functions.getPetsForSale().call()

        for pet in pets_for_sale:
            pet_info = contract.functions.getPet(pet).call()

            # for each pet, display its image, name, and price in wei
            st.image(contract.functions.tokenURI(pet).call())
            st.write(f'Name: {pet_info[0]}')
            st.write(f'Price: {pet_info[2]} Wei')

            # whne the buy pet button is called, use the smart contract buyPet function to complete the transaction
            if st.button('Buy Pet', key=f'{pet}:{pet_info[0]}'):
                try: 
                    contract.functions.buyPet(pet).transact({'from': session.username, 'value': int(pet_info[2]), 'gas': 1000000})
                    st.success('Pet purchased!')
                    time.sleep(2)
                    st.experimental_rerun()
                except ValueError as e:
                    error = str(e)

                    if 'insufficient funds' in error:
                        st.write('You have insufficient funds to buy this pet.')
                    elif 'You already own this token' in error:
                        st.write('You alread own this pet!')
else:
    # when the user is not logged in, direct them to use the sidebar and login
    st.markdown("# :arrow_left:")
    st.title('Please use the sidebar to login with a connected Ethereum address.')