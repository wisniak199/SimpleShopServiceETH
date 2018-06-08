import {createWeb3, deployContract, expectThrow, increaseTimeTo, durationInit, latestTime} from 'ethworks-solidity';
import testStateChannelJson from '../../build/contracts/TestStateChannel.json';
import Web3 from 'web3';
import chai from 'chai';
import bnChai from 'bn-chai';

const {expect} = chai;
const web3 = createWeb3(Web3);
chai.use(bnChai(web3.utils.BN));
const EthUtil = require('ethereumjs-util');

describe('TestStateChannel', async() => {
  let contract;
  let accounts;
  let owner;
  let client1;
  let client2;

  function transaction_hasher(value, session_id) {
    let value_hash = web3.utils.toAscii(web3.utils.soliditySha3({t: 'uint', v: value.toString()}));
    return web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii(value_hash + session_id)});
  }

  async function sign_transaction(transaction_hash, address) {
    let transaction_hash_ascii  = web3.utils.toAscii(transaction_hash);
    let signature = await web3.eth.sign(transaction_hash, address);
    signature = signature.substr(2);
    let r = '0x' + signature.slice(0, 64);
    let s = '0x' + signature.slice(64, 128);
    let v = '0x' + signature.slice(128, 130);
    let v_decimal = web3.utils.toDecimal(v)
    if(v_decimal != 27 || v_decimal != 28) {
      v_decimal += 27
    }
    const fixed_msg = `\x19Ethereum Signed Message:\n${transaction_hash_ascii.length}${transaction_hash_ascii}`
    const fixed_msg_sha = web3.utils.soliditySha3({t: "bytes", v: web3.utils.fromAscii(fixed_msg)});
    return {
      h: fixed_msg_sha,
      v: v_decimal,
      r: r,
      s: s
    }
  }

  before(async () => {
    accounts = await web3.eth.getAccounts();
    [, owner, client1, client2] = accounts;
  });

  beforeEach(async() => {
    contract = await deployContract(web3, testStateChannelJson, owner, [])
  });

  it("simple transaction", async function () {
    let session_id = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja')});
    await contract.methods.startSession(session_id).send({from: client1, value: web3.utils.toWei("2", "ether")});
    let transaction_confirmation = transaction_hasher(web3.utils.toWei("1", "ether"), web3.utils.toAscii(session_id));
    let transaction_signature = await sign_transaction(transaction_confirmation, client1);
    await contract.methods.endSession(
      transaction_signature.h, transaction_signature.v, transaction_signature.r,
      transaction_signature.s, web3.utils.toWei("1", "ether"), session_id).send({from: owner});
  });

  it("user cannot cancel session whenever he wants", async function () {
    let session_id = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja')});
    await contract.methods.startSession(session_id).send({from: client1, value: web3.utils.toWei("2", "ether")});
    let transaction_confirmation = transaction_hasher(1, web3.utils.toAscii(session_id));
    let transaction_signature = await sign_transaction(transaction_confirmation, client1);
    await expectThrow(contract.methods.cancelSession(session_id).send({from: client1}));
  });

  it("double signature usage", async function () {
    let session_id1 = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja')});
    let session_id2 = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja2')});
    await contract.methods.startSession(session_id1).send({from: client1, value: web3.utils.toWei("2", "ether")});
    let transaction_confirmation = transaction_hasher(1, web3.utils.toAscii(session_id1));
    let transaction_signature = await sign_transaction(transaction_confirmation, client1);
    await contract.methods.endSession(
      transaction_signature.h, transaction_signature.v, transaction_signature.r,
      transaction_signature.s, 1, session_id1).send({from: owner});
    await contract.methods.startSession(session_id2).send({from: client1, value: web3.utils.toWei("2", "ether")});
    await expectThrow(contract.methods.endSession(
      transaction_signature.h, transaction_signature.v, transaction_signature.r,
      transaction_signature.s, 1, session_id1).send({from: owner}));
  });

  it("double signature usage", async function () {
    let session_id1 = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja')});
    let session_id2 = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja2')});
    await contract.methods.startSession(session_id1).send({from: client1, value: web3.utils.toWei("2", "ether")});
    let transaction_confirmation = transaction_hasher(1, web3.utils.toAscii(session_id1));
    let transaction_signature = await sign_transaction(transaction_confirmation, client1);
    await contract.methods.endSession(
      transaction_signature.h, transaction_signature.v, transaction_signature.r,
      transaction_signature.s, 1, session_id1).send({from: owner});
    await contract.methods.startSession(session_id2).send({from: client1, value: web3.utils.toWei("2", "ether")});
    await expectThrow(contract.methods.endSession(
      transaction_signature.h, transaction_signature.v, transaction_signature.r,
      transaction_signature.s, 1, session_id1).send({from: owner}));
  });

  it("cancel session", async function () {
    let session_id = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja')});
    await contract.methods.setSessionLength(-1).send({from: client1});
    await contract.methods.startSession(session_id).send({from: client1, value: web3.utils.toWei("2", "ether")});
    await contract.methods.cancelSession(session_id).send({from: client1});
  });

  it("user cannot cancel not his session", async function () {
    let session_id1 = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja')});
    let session_id2 = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii('sesja2')});
    await contract.methods.setSessionLength(-1).send({from: client1});
    await contract.methods.startSession(session_id1).send({from: client1, value: web3.utils.toWei("2", "ether")});
    await contract.methods.startSession(session_id2).send({from: client2, value: web3.utils.toWei("2", "ether")});
    await expectThrow(contract.methods.cancelSession(session_id2).send({from: client1}));
  });
});
