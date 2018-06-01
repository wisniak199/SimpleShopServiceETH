export default class MerkleTree {

  constructor(numbers, number_hasher, byte_hasher) {
    if (numbers.length == 0) {
      return;
    }
    this.number_hasher = number_hasher;
    this.byte_hasher = byte_hasher;
    this.hash_to_parent_hash = new Map();
    this.nodes = new Map()
    let hashes = [];
    for (let i = 0; i < numbers.length; ++i) {
      let hash = this.number_hasher(numbers[i]);
      hashes.push(hash);
      this.nodes.set(hash, {hash: hash, left: null, right: null});
    }

    while (hashes.length > 1) {
      let new_hashes = [];
      for (let i = 0; i < hashes.length; i += 2) {
        if (i + 1 < hashes.length) {
          let parent_hash = this.byte_hasher(hashes[i], hashes[i + 1]);
          new_hashes.push(parent_hash);
          this.hash_to_parent_hash.set(hashes[i], parent_hash);
          this.hash_to_parent_hash.set(hashes[i + 1], parent_hash);
          this.nodes.set(parent_hash, {hash: parent_hash, left: hashes[i], right: hashes[i + 1]});

        } else {
          new_hashes.push(hashes[i]);
        }
      }
      hashes = new_hashes;
    }
    this.rootHash = hashes[0]
  }

  getRootHash() {
    return this.rootHash;
  }

  getProof(number) {
    let hash = this.number_hasher(number);
    let proofHashes = [];
    let isLeftChild = [];
    if (!this.nodes.has(hash)) {
      return null;
    }
    while (hash != this.rootHash) {
      let parentHash = this.hash_to_parent_hash.get(hash);
      let parentNode = this.nodes.get(parentHash);
      if (hash == parentNode.left) {
        proofHashes.push(parentNode.right);
        isLeftChild.push(false);
      } else {
        proofHashes.push(parentNode.left);
        isLeftChild.push(true);
      }
      hash = parentHash;
    }
    return {
      proofHashes: proofHashes,
      isLeftChild: isLeftChild
    };
  }
}
