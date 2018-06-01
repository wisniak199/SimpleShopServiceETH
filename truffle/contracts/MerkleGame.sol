pragma solidity ^0.4.19;

contract MerkleGame {
    uint constant betPrice = 2 ether;
    uint constant blocksToProvideProof = 256;

    enum GameState {
      Bet,
      ProvidingMerkleTree,
      ProvidingNumber,
      ProvidingProof
    }

    GameState state;
    address player1;
    address player2;
    bytes32 merkleRoot;
    uint16 number;
    uint startBlockNumber;
    bool proofVerified;

    function MerkleGame() public {
      state = GameState.Bet;
    }

    function bet() public payable {
      require(state == GameState.Bet);
      require(msg.value == betPrice);
      player1 = msg.sender;
      state = GameState.ProvidingMerkleTree;
    }

    function provideMerkleTree(bytes32 _merkleRoot) public {
      require(state == GameState.ProvidingMerkleTree);
      require(msg.sender != player1);
      player2 = msg.sender;
      merkleRoot = _merkleRoot;
      state = GameState.ProvidingNumber;
    }

    function provideNumber(uint16 _number) public {
      require(state == GameState.ProvidingNumber);
      require(msg.sender == player1);
      require(_number <= 2048);
      number = _number;
      startBlockNumber = block.number;
      state = GameState.ProvidingProof;
    }

    function provideProof(bytes32[] proofHashes, bool[] whichChild) public {
      require(state == GameState.ProvidingProof);
      require(msg.sender == player2);
      require(block.number <= startBlockNumber + blocksToProvideProof);
      require(proofHashes.length == whichChild.length);
      // assumes binary tree with at most 1024 leafs
      require(proofHashes.length <= 10);
      if (verifyProof(proofHashes, whichChild, merkleRoot, number)) {
        proofVerified = true;
      }
    }

    function withdraw() public {
      require(msg.sender == player1 || msg.sender == player2);
      if (msg.sender == player1) {
        require(block.number > startBlockNumber + 256);
      } else {
        require(proofVerified);
      }
      msg.sender.transfer(betPrice);
    }

    function verifyProof(bytes32[] _proofHashes, bool[] _whichChild, bytes32 _root, uint16 _number) private pure returns (bool) {
      bytes32 accumulatedHash = sha3(_number);
      for (uint i = 0; i < _proofHashes.length; ++i) {
        if (_whichChild[i]) {
          accumulatedHash = sha3(concat(_proofHashes[i], accumulatedHash));
        } else {
          accumulatedHash = sha3(concat(accumulatedHash, _proofHashes[i]));
        }
      }
      bool result = true;
      for (uint j = 0; j < 32; j++) {
        if (accumulatedHash[j] != _root[j]) {
          result = false;
          break;
        }
      }
      return result;
    }

    // probably inefficient
    function concat(bytes32 self, bytes32 other) private pure returns (bytes) {
      bytes memory ret = new bytes(self.length + other.length);
      for (uint i = 0; i < ret.length; ++i) {
        if (i < self.length) {
          ret[i] = self[i];
        } else {
          ret[i] = other[i - self.length];
        }
      }
      return ret;
     }
}
