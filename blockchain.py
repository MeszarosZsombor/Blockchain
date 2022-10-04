import hashlib
import pathlib
import pprint
import random
import time
import rsa


# initiate the chain of blocks
blockchain = []

# define number of TXs per block
TXs_per_block = int(input('How many TXs per block would you like to generate?\n'))


def generate_keys():
    (pub_key, pri_key) = rsa.newkeys(512)
    string_pub_key = pub_key.save_pkcs1('PEM')
    string_pri_key = pri_key.save_pkcs1('PEM')
    with open("Private_key.key", 'wb') as f1:
        f1.write(string_pri_key)
    with open("Public_key.key", 'wb') as f2:
        f2.write(string_pub_key)
    return string_pri_key, string_pub_key


# generate asymmetric keys
public_key, private_key = generate_keys()


def sign(object_to_be_used_for_signature):
    hashed_object = hash_object(object_to_be_used_for_signature)
    encoded_hashed_object = hashed_object.encode('UTF-8')
    serialized_key = retrieve_key_from_saved_file('Private')
    return rsa.sign(encoded_hashed_object, serialized_key, 'SHA-256')


def retrieve_key_from_saved_file(private_or_public):
    path = private_or_public + "_key.key"
    file_path = pathlib.Path(path)
    with open(file_path, 'rb') as f:
        if private_or_public == 'Private':
            return rsa.PrivateKey.load_pkcs1(f.read())
        if private_or_public == "Public":
            return rsa.PublicKey.load_pkcs1(f.read())
        return None


def verify_signature(hashed_object, deserialized_signature, key):
    encoded_hashed_object = hashed_object.encode('UTF-8')
    serialized_signature = deserialized_signature
    return verify(encoded_hashed_object, serialized_signature, key)


def verify(hashed_credential, signature, pub_key):
    valid = False
    try:
        rsa.verify(hashed_credential, signature, pub_key)
        valid = True
    except Exception as e:
        print('a signature is found invalid!')
        print(e)
    return valid


def get_empty_block():
    new_block = {'Header': {'Timestamp': 0.0,
                            'MR': '',
                            'Hash': '',
                            'previous_hash': '',
                            'proof': None,
                            'block_no': 0},
                 'Body': get_transactions(TXs_per_block)}
    return new_block


# define the used consensus
def define_consensus_algo():
    num_of_consensus = int(input('Please select the consensus algorithm to be simulated: 1-PoW, 2-PoS, 3-PoA:\n'))
    if num_of_consensus == 1:
        # define PoW difficulty
        difficulty = int(input('Please input the difficulty of the PoW puzzle:\n'))
        targeted_hash = get_target(difficulty)
        return num_of_consensus, targeted_hash
    elif num_of_consensus == 2:
        owned_crypto = 100
        staked_crypto = random.randrange(32, owned_crypto)
        return num_of_consensus, staked_crypto
    elif num_of_consensus == 3:
        return num_of_consensus, None


def get_transactions(num_txs):
    # randomly generate and return some simulated TXs
    list_of_txs = []
    for entity in range(num_txs):
        list_of_txs.append(get_new_transaction())
    return list_of_txs


def get_new_transaction():
    return random.randint(1, 1000000)


def hash_object(entity):
    # hash something
    h = hashlib.sha256()
    h.update(str(entity).encode(encoding='UTF-8'))
    return h.hexdigest()


def hash_twice(entity):
    # hash something twice as for the merkle tree
    return hash_object(hash_object(entity))


def print_list_or_dict(to_be_printed):
    # function to nicely print a dictionary or a list
    if type(to_be_printed) == dict:
        pprint.pprint(to_be_printed, sort_dicts=False)
    elif type(to_be_printed) == list:
        for element in range(len(to_be_printed)):
            print(str(i + 1) + '-')
            print(to_be_printed[i])
    print('==========================================')


def get_new_block(consensus, parameter):
    # fill in a new block
    new_block = get_empty_block()
    new_block['Header']['Timestamp'] = time.time()
    new_block['Header']['block_no'] = len(blockchain)
    if len(blockchain) == 0:
        new_block['Body'] = []
        new_block['Header']['MR'] = '0'
        new_block['Header']['previous_hash'] = '0'
    else:
        new_block['Header']['MR'] = get_MR(new_block['Body'])
        new_block['Header']['previous_hash'] = blockchain[-1]['Header']['Hash']
    to_be_hashed = [new_block['Header']['Timestamp'], new_block['Header']['previous_hash'], new_block['Body']]
    new_block['Header']['Hash'] = hash_object(to_be_hashed)
    new_block = get_proof(new_block, consensus, parameter)
    return new_block


def get_next_level_MT(list_of_TXs):
    counter = 0
    concatenations = []
    while counter < len(list_of_TXs):
        TX1 = list_of_TXs[counter]
        try:
            TX2 = list_of_TXs[counter + 1]
        except Exception as e:
            TX2 = list_of_TXs[counter]
        hash_TX1 = hash_twice(TX1)
        hash_TX2 = hash_twice(TX2)
        concatenations.append(hash_TX1 + hash_TX2)
        counter += 2
    return concatenations


def get_MR(list_of_txs):
    # retreive the merkle root of a body
    MR = None
    while not MR:
        concatenations = get_next_level_MT(list_of_txs)
        if len(concatenations) == 1:
            return hash_twice(concatenations[0])
        else:
            list_of_txs = concatenations


def append_block_to_chain(new_block):
    blockchain.append(new_block)
    print('New block is added to the chain:\n')
    print_list_or_dict(new_block)


def get_PoW_proof(block, targeted_hash):
    for nonce in range(1, 4000000000):
        hash_of_block = hash_object([nonce, block['Header']['Timestamp'], block['Header']['previous_hash'], block['Body']])
        if pow_block_is_valid(hash_of_block, targeted_hash):
            block['Header']['Hash'] = hash_of_block
            block['Header']['proof'] = nonce
            return block
    return None


def get_PoS_proof(block, staked_crypto):
    block['Header']['proof'] = [staked_crypto, 'Miner_1']
    return block


def get_PoA_proof(block):

    signature_bytes = sign(block['Body'])
    if verify_signature(hash_object(block['Body']), signature_bytes, retrieve_key_from_saved_file('Public')):
        print('Signature is valid')
        block['Header']['proof'] = signature_bytes
        print('Signature added to the block')

    return block


def get_target(difficulty):
    string_target = ''
    for zeros in range(int(difficulty)):
        string_target += '0'
    for non_zeros in range(64 - int(difficulty)):
        string_target += 'f'
    return string_target


def pow_block_is_valid(hash_of_block, targeted_hash):
    return int(hash_of_block, 16) <= int(targeted_hash, 16)


def get_proof(block, consensus, parameter):
    if consensus == 1:
        return get_PoW_proof(block, parameter)
    elif consensus == 2:
        return get_PoS_proof(block, parameter)
    elif consensus == 3:
        return get_PoA_proof(block)


if __name__ == '__main__':
    # run the simulation
    consensus_type, second_parameter = define_consensus_algo()
    genesis_block = get_new_block(consensus_type, second_parameter)
    append_block_to_chain(genesis_block)

    for i in range(int(input('How many blocks would you like to generate?\n'))):
        append_block_to_chain(get_new_block(consensus_type, second_parameter))
