pragma solidity ^0.4.19;

import "./StateChannel.sol";

contract TestStateChannel is StateChannel {

  function setSessionLength(uint l) {
    sessionLength = l;
  }

}
