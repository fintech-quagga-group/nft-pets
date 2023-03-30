pragma solidity ^0.5.5;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/cryptography/ECDSA.sol";

contract PetToken is ERC721Full {
    constructor() public ERC721Full("PetToken", "PET") {}

    // define struct for a Pet token, and a mapping to have all minted pets
    struct Pet {
        string name;
        string ownerName;
        uint256 price;
    }

    mapping (uint256 => Pet) public pets;

    // events to track minting a pet, changing the price of a pet, and the sale of a pet
    event PetRegistered(uint256 tokenId, string name, string ownerName, uint256 price);
    event PetPriceChanged(uint256 tokenId, uint256 price);
    event PetSold(uint256 tokenId, address oldOwner, address newOwner, uint256 price);

    // function similar to ArtToken registerArtwork; emits PetRegistered event
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
        // caputure previous owner and new owner to complete ERC721 _transferFrom() call
        address payable oldOwner = address(uint160(ownerOf(tokenId)));
        address payable newOwner = msg.sender;
        uint256 price = pets[tokenId].price;

        require(oldOwner != address(0), "Token does not exist");
        require(oldOwner != newOwner, "You already own this token");
        require(msg.value == price, "Incorrect value sent");

        _transferFrom(oldOwner, newOwner, tokenId);

        // change owner name within Pet struct
        pets[tokenId].ownerName = ERC721Metadata(address(this)).name();

        oldOwner.transfer(msg.value);

        emit PetSold(tokenId, oldOwner, newOwner, price);
    }

    function getPetsForSale() public view returns (uint256[] memory) {
        // count how many pets of all the minted pets are up for sale 
        uint256 count = 0;
        for (uint256 i = 0; i < totalSupply(); i++) {
            if (ownerOf(i) != address(0) && pets[i].price > 0) {
                count++;
            }
        }

        uint256[] memory result = new uint256[](count);
        uint256 index = 0;

        // loop through buyable pets and return array of all the tokenIds
        for (uint256 i = 0; i < totalSupply(); i++) {
            if (ownerOf(i) != address(0) && pets[i].price > 0) {
                result[index] = i;
                index++;
            }
        }

        return result;
    }

    // uses balanceOf() to loop through and return all of the given address' pets
    function getOwnedPets(address owner) public view returns (uint256[] memory) {
        uint256 tokenCount = balanceOf(owner);
        uint256[] memory tokenIds = new uint256[](tokenCount);

        for (uint256 i = 0; i < tokenCount; i++) {
            tokenIds[i] = tokenOfOwnerByIndex(owner, i);
        }

        return tokenIds;
    }

    // mapping to hold currently logged in users
    mapping (address => bool) private loggedInUsers;

    // events to be sent on log in and log out
    event UserLoggedIn(address indexed user);
    event UserLoggedOut(address indexed user);

    function login() public {
        require(!loggedInUsers[msg.sender], "User is already logged in");

        // mark user as logged in
        loggedInUsers[msg.sender] = true;

        emit UserLoggedIn(msg.sender);
    }

    function logout() public {
        require(loggedInUsers[msg.sender], "User is already logged out");

        // mark user as logged out
        loggedInUsers[msg.sender] = false;

        emit UserLoggedOut(msg.sender);
    }
}


