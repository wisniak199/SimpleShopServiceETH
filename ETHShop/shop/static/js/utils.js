var web3;

const promisify = (inner) =>
  new Promise((resolve, reject) =>
    inner((err, res) => {
      if (err) { reject(err) }

      resolve(res);
    })
  );

function transaction_hasher(value, session_id) {
  let session_id_ascii = web3.utils.toAscii(session_id)
  let value_hash = web3.utils.toAscii(web3.utils.soliditySha3({t: 'uint256', v: web3.utils.toWei(value.toString(), 'Finney').toString()}));
  let transaction_hash = web3.utils.soliditySha3({t: 'bytes', v: web3.utils.fromAscii(value_hash + session_id_ascii)});
  let transaction_hash_ascii  = web3.utils.toAscii(transaction_hash);
  const fixed_msg = `\x19Ethereum Signed Message:\n${transaction_hash_ascii.length}${transaction_hash_ascii}`
  const fixed_msg_sha = web3.utils.soliditySha3({t: "bytes", v: web3.utils.fromAscii(fixed_msg)});
  return fixed_msg_sha;
}

async function sign_transaction(transaction_hash, address) {
  let signature = await web3.eth.sign(transaction_hash, address);
  return signature;
}

async function getEtherumAddress() {
  var etherum_address = (await promisify(cb => web3.eth.getAccounts(cb)))[0];
  return etherum_address;
}

async function getReceipt(session_id, receipt_value, address) {
  var transaction_hash = transaction_hasher(receipt_value, session_id);
  var receipt = await sign_transaction(transaction_hash, address);
  return receipt;
}

$( document ).ready(function() {
    if (typeof web3 !== 'undefined') {
      var web3Provider = web3.currentProvider;
      web3 = new Web3(web3.currentProvider);
    } else {
      // If no injected web3 instance is detected, fallback to Ganache CLI.
      var web3Provider = new web3.providers.HttpProvider('http://127.0.0.1:8545');
      web3 = new Web3(web3Provider);
    }
});
