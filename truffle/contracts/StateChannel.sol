pragma solidity ^0.4.19;

contract StateChannel {
    uint constant lockAmount = 2 ether;
    uint constant sessionLength = 1 days;

    struct Session {
      uint start_ts;
      bytes32 session_id;
      bool set;
    }

    address owner;
    mapping(address => Session) sessions;


    function StateChannel() public {
      owner = msg.sender;
    }

    function startSession(bytes32 session_id) public payable {
      require(msg.sender != owner);
      require(msg.value == lockAmount);
      require(sessions[msg.sender].start_ts == 0);
      sessions[msg.sender].start_ts = now;
      sessions[msg.sender].session_id = session_id;
      sessions[msg.sender].set = true;
    }

    function endSession(bytes32 h, uint8 v, bytes32 r, bytes32 s, uint value, bytes32 session_id) public {
      require(msg.sender == owner);
      address signer;
  		bytes32 proof;

  		// get signer from signature
  		signer = ecrecover(h, v, r, s);

      require(sessions[signer].set);
      require(session_id == sessions[signer].session_id);

  		proof = sha3("\x19Ethereum Signed Message:\n32", sha3(concat(sha3(value), session_id)));
      require(proof == h);

      owner.transfer(value);
      signer.transfer(lockAmount - value);

      delete sessions[signer];
    }

    function cancelSession() public {
      Session storage session = sessions[msg.sender];
      require(session.start_ts != 0);
      require(session.start_ts + sessionLength < now);
      msg.sender.transfer(lockAmount);
      delete sessions[msg.sender];
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
