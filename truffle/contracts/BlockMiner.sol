pragma solidity ^0.4.19;

// used to "waste" blocks for truffle tests
contract BlockMiner {
    uint blocksMined;

    function BlockMiner(){
        blocksMined = 0;
    }

    function mine() {
       blocksMined += 1;
    }
}
