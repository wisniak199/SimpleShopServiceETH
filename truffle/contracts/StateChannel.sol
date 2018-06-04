pragma solidity ^0.4.19;

contract StateChannel {
    uint constant lockAmount = 2 ether;
    uint sessionLength = 1 days;

    struct Session {
      uint start_ts;
      address user;
      bool set;
    }

    event StartSession (
      bytes32 indexed session_id,
      address indexed client
    );

    address owner;
    mapping(bytes32 => Session) sessions;


    function StateChannel() public {
      owner = msg.sender;
    }

    function startSession(bytes32 session_id) public payable {
      require(msg.sender != owner);
      require(msg.value == lockAmount);
      require(sessions[session_id].set == false);
      sessions[session_id].start_ts = now;
      sessions[session_id].user = msg.sender;
      sessions[session_id].set = true;
      StartSession(session_id, msg.sender);
    }

    function endSession(bytes32 h, uint8 v, bytes32 r, bytes32 s, uint value, bytes32 session_id) public {
      require(msg.sender == owner);
      address signer;
  		bytes32 proof;

  		// get signer from signature
  		signer = ecrecover(h, v, r, s);

      require(sessions[session_id].set);
      require(sessions[session_id].user == signer);

  		proof = sha3("\x19Ethereum Signed Message:\n32", sha3(concat(sha3(value), session_id)));
      require(proof == h);

      owner.transfer(value);
      signer.transfer(lockAmount - value);

      delete sessions[session_id];
    }

    function cancelSession(bytes32 session_id) public {
      Session storage session = sessions[session_id];
      require(session.set);
      require(msg.sender == session.user);
      require(session.start_ts + sessionLength < now);
      msg.sender.transfer(lockAmount);
      delete sessions[session_id];
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
