import {createWeb3, deployContract, expectThrow, increaseTimeTo, durationInit, latestTime} from 'ethworks-solidity';
import merkleGameJson from '../../build/contracts/MerkleGame.json';
import blockMinerJson from '../../build/contracts/BlockMiner.json';
import Web3 from 'web3';
import chai from 'chai';
import bnChai from 'bn-chai';
import MerkleTree from '../../src/js/merkleTree.js';

const {expect} = chai;
const web3 = createWeb3(Web3);
chai.use(bnChai(web3.utils.BN));

xdescribe('MerkleGame', async() => {
  let contract;
  let blockMiner;
  let accounts;
  let owner;
  let player1;
  let player2;
  let number_hasher = n => web3.utils.soliditySha3({t: 'uint16', v: n.toString()});
  let byte_hasher = (bytes1, bytes2) => web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii(web3.utils.toAscii(bytes1) + web3.utils.toAscii(bytes2))});

  async function mineBlocks(n) {
    let promises = []
    for (let i = 0; i < n; ++i) {
      promises.push(blockMiner.methods.mine().send({from: owner}));
    }
    for (let i = 0; i < n; ++i) {
      await promises[i];
    }
  }

  before(async () => {
    accounts = await web3.eth.getAccounts();
    [, owner, player1, player2] = accounts;
  });

  beforeEach(async() => {
    blockMiner = await deployContract(web3, blockMinerJson, owner, [])
    contract = await deployContract(web3, merkleGameJson, owner, [])
  });

  it("player2 wins game", async function () {
    let tree = new MerkleTree([1, 2, 3, 4, 5, 6], number_hasher, byte_hasher);
    let proof = tree.getProof(4);
    await contract.methods.bet().send({from: player1, value: web3.utils.toWei("2", "ether")});
    await contract.methods.provideMerkleTree(tree.getRootHash()).send({from: player2});
    await contract.methods.provideNumber(4).send({from: player1});
    await contract.methods.provideProof(proof.proofHashes, proof.isLeftChild).send({from: player2});
    await contract.methods.withdraw().send({from: player2});
  });

  it("player1 wins game", async function () {
    this.timeout(10000);
    let tree = new MerkleTree([1, 2, 3, 4, 5, 6], number_hasher, byte_hasher);
    await contract.methods.bet().send({from: player1, value: web3.utils.toWei("2", "ether")});
    await contract.methods.provideMerkleTree(tree.getRootHash()).send({from: player2});
    await contract.methods.provideNumber(4).send({from: player1});
    await mineBlocks(256);
    await contract.methods.withdraw().send({from: player1});
  });

  it("wrong proof", async function () {
    let tree = new MerkleTree([1, 2, 3, 4, 5, 6], number_hasher, byte_hasher);
    let proof = tree.getProof(4);
    await contract.methods.bet().send({from: player1, value: web3.utils.toWei("2", "ether")});
    await contract.methods.provideMerkleTree(tree.getRootHash()).send({from: player2});
    await contract.methods.provideNumber(100).send({from: player1});
    await contract.methods.provideProof(proof.proofHashes, proof.isLeftChild).send({from: player2});
    await expectThrow(contract.methods.withdraw().send({from: player2}));
  });

  it("player 1 wants withdraw erlier", async function () {
    let tree = new MerkleTree([1, 2, 3, 4, 5, 6], number_hasher, byte_hasher);
    await contract.methods.bet().send({from: player1, value: web3.utils.toWei("2", "ether")});
    await contract.methods.provideMerkleTree(tree.getRootHash()).send({from: player2});
    await contract.methods.provideNumber(100).send({from: player1});
    await expectThrow(contract.methods.withdraw().send({from: player1}));
  });

  it("wrong amount of ether", async function () {
    await expectThrow(contract.methods.bet().send({from: player1, value: web3.utils.toWei("3", "ether")}));
  });

});
