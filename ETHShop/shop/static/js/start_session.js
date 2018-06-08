const contract_abi = [{"stateMutability": "nonpayable", "inputs": [], "type": "constructor", "payable": false}, {"inputs": [{"type": "bytes32", "name": "session_id"}], "constant": false, "name": "startSession", "outputs": [], "stateMutability": "payable", "payable": true, "type": "function"}, {"inputs": [{"type": "bytes32", "name": "h"}, {"type": "uint8", "name": "v"}, {"type": "bytes32", "name": "r"}, {"type": "bytes32", "name": "s"}, {"type": "uint256", "name": "value"}, {"type": "bytes32", "name": "session_id"}], "constant": false, "name": "endSession", "outputs": [], "stateMutability": "nonpayable", "payable": false, "type": "function"}, {"inputs": [{"type": "bytes32", "name": "session_id"}], "constant": false, "name": "cancelSession", "outputs": [], "stateMutability": "nonpayable", "payable": false, "type": "function"}];

function getSessionId() {
  var session_id = "";
  for (var i = 0; i < 6; ++i) {
    session_id += Math.random().toString(16).substr(2);
  }
  session_id = "0x" + session_id.substr(0, 64);
  return session_id;
}

async function lockFunds(contract, session_id, my_address){
  var tx = await contract.methods.startSession(session_id).send({from: my_address, value: web3.utils.toWei("2", "ether")});;
  return tx.transactionHash;
}

async function start_session() {
  var contract_address = $('input[name=contract_address]').val();
  var contract = new web3.eth.Contract(contract_abi, contract_address)
  var session_id = getSessionId();
  var etherum_address = await getEtherumAddress();
  var tx_hash = await lockFunds(contract, session_id, etherum_address);
  var receipt = await getReceipt(session_id, 0, etherum_address);
  $('input[name=etherum_address]').val(etherum_address);
  $('input[name=receipt]').val(receipt);
  $('input[name=session_id]').val(session_id);
  $('input[name=transaction_hash]').val(tx_hash);

}

$( document ).ready(function() {
    $('.start_session_form').submit(function() {
        var form = $(this);
        start_session().then(result => {
          form[0].submit();
        });
        return false;
    })
});
