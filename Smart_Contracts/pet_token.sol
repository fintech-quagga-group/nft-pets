pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

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
        require(_isApprovedOrOwner(msg.sender, tokenId), "caller is not owner nor approved");

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
}

