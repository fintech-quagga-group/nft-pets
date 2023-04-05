# NFT Pets

---

### Project Goals 


### Outline
1. Generate NFTs based on pixel art generated by OpenAI Dall-E
2. Middleman that will take percentage of all sales
3. Different pages based on Ganache account that is logged in through Metamask
4. Make a marketplace to buy and sell NFTs between accounts
	- have a list of all the minted nft pets
	- add art registry code to be able to set your price for your minted nft pet
5. Image generation code based on list of animal names
        - add st.selectbox for choosing what type of animal you want
        - hard code "pixel art" prefix to whatever animal chosen
6. ChatGPT integration to talk with your selected nft pet

Optional
7. Add Pokemon-like game features (edited) 

### Data Collection 


---

## Technologies

Kaggle handles all code dependencies and we do not advise trying to run our notebooks on your own machine because of high memory usage. 

The following dependencies are used: 
1. [Pandas](https://github.com/pandas-dev/pandas) (1.3.5) - Data analysis
2. [Streamlit](https://streamlit.io/) (1.2.0) - Web app interface
3. [Ganache](https://trufflesuite.com/ganache/) (2.7.0) - Ethereum blockchain
4. [Solidarity](https://soliditylang.org/) (0.8.19) - Language for smart contract
5. [Remix](https://remix-project.org/) - IDE for Web3 developement
6. [ChatGTP](https://openai.com/blog/chatgpt) (3.5) - Chat features
7. [DALL-E](https://labs.openai.com/) - Image creation
8. [Metamask](https://metamask.io/) (10.28.1) - Blockchain Wallet
---

## Usage
-To use this program, download github repository clone in a local environment.  Then you must download Ganache and open a new ethereum workspace.  In Ganache, copy both the RPC server address and the private key to an account from the list and paste them into a .env file in the repository folder.  <br>
-With Ganache open, install the Metamask extension, open Metamask and create a new network using your Ganache RPC server address.  In this network, import accounts from Ganache using their private key. <br>
-Register with OpenAI and copy your API key to the .env file. <br>
-Open your browser and go to (https://remix.ethereum.org/), select "open file" and load the Smart_Contracts folder from the repo.  Select  the pet_token.sol contract and hit "compile" from the left menu and choose the compiler 0.5.5+commit.47171e8f.  Select "compile pet_token.sold" <br>
-Deploy the contract with the button under compile on the left menu. For the environment variable select "Injected Provider - MetaMask".  The orange button will deploy the contract. <br>
-Open the app.py file in the terminal and type "streamlit run app.py" <br>
-Once Streamlit has opened, use login with your account key that matches the private key of one of your Ganache accounts.  At this point you should be logged in and ready to create, talk to, and trade NFT Pets. <br>
### Other Files 


---

## Contributors

[Ethan Silvas](https://github.com/ethansilvas) <br>
[Naomy Velasco](https://github.com/naomynaomy) <br>
[Karim Bouzina](https://github.com/karim985) <br>
[Jeff Crabill](https://github.com/jeffreycrabill) <br>

---

## License

This project uses the [GNU General Public License](https://choosealicense.com/licenses/gpl-3.0/)