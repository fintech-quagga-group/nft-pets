pragma solidity ^0.5.5;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/cryptography/ECDSA.sol";

contract PetToken is ERC721Full {
    constructor() public ERC721Full("PetToken", "PET") {}

    struct Pet {
        string name;
        string ownerName;
        uint256 price;
    }

    mapping (uint256 => Pet) public pets;

    event PetRegistered(uint256 tokenId, string name, string ownerName, uint256 price);
    event PetPriceChanged(uint256 tokenId, uint256 price);
    event PetSold(uint256 tokenId, address oldOwner, address newOwner, uint256 price);

    function registerPet(string memory name, string memory ownerName, uint256 price, string memory tokenURI) public returns (uint256) {
        uint256 tokenId = totalSupply();
        _mint(msg.sender, tokenId);
        _setTokenURI(tokenId, tokenURI);

        pets[tokenId] = Pet(name, ownerName, price);

        emit PetRegistered(tokenId, name, ownerName, price);

        return tokenId;
    }

    function changePrice(uint256 tokenId, uint256 price) public {
        require(_isApprovedOrOwner(msg.sender, tokenId), "caller is not owner or approved");

        pets[tokenId].price = price;

        emit PetPriceChanged(tokenId, price);
    }

    function buyPet(uint256 tokenId) public payable {
        address payable oldOwner = address(uint160(ownerOf(tokenId)));
        address payable newOwner = msg.sender;
        uint256 price = pets[tokenId].price;

        require(oldOwner != address(0), "token does not exist");
        require(oldOwner != newOwner, "you already own this token");
        require(msg.value == price, "incorrect value sent");

        _transferFrom(oldOwner, newOwner, tokenId);

        pets[tokenId].ownerName = ERC721Metadata(address(this)).name();

        oldOwner.transfer(msg.value);

        emit PetSold(tokenId, oldOwner, newOwner, price);
    }

    function getPetsForSale() public view returns (uint256[] memory) {
        uint256 count = 0;
        for (uint256 i = 0; i < totalSupply(); i++) {
            if (ownerOf(i) != address(0) && pets[i].price > 0) {
                count++;
            }
        }

        uint256[] memory result = new uint256[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < totalSupply(); i++) {
            if (ownerOf(i) != address(0) && pets[i].price > 0) {
                result[index] = i;
                index++;
            }
        }

        return result;
    }

    mapping (address => bool) private loggedInUsers;

    function login(bytes memory _signature) public {
        // Get the address associated with the public key that signed the message
        address signer = ECDSA.recover(keccak256(abi.encodePacked(msg.sender)), _signature);
        
        // Check if the signer is the same as the sender
        require(signer == msg.sender, "Invalid signature");

        // Check if the user is already logged in
        require(!loggedInUsers[msg.sender], "User is already logged in");

        // Mark user as logged in
        loggedInUsers[msg.sender] = true;

        // Emit an event to indicate that the user has logged in
        emit UserLoggedIn(msg.sender);
    }

    function logout() public {
        // Check if the user is already logged out
        require(loggedInUsers[msg.sender], "User is already logged out");

        // Mark user as logged out
        loggedInUsers[msg.sender] = false;

        // Emit an event to indicate that the user has logged out
        emit UserLoggedOut(msg.sender);
    }

    event UserLoggedIn(address indexed user);
    event UserLoggedOut(address indexed user);
}


