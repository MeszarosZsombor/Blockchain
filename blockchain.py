import pprint
import random
import time
import merkletools
import encryption_module


# initiate the chain of blocks
full_blockchain = []
light_blockchain = []

# define number of TXs per block
TXs_per_block = int(input('How many TXs per block would you like to generate?\n'))


# generate asymmetric keys
public_key, private_key = encryption_module.generate_keys()


def randomly_select_TX():
    block = random.choice(full_blockchain)
    while len(block['Body']) == 0:
        block = random.choice(full_blockchain)
    TX = random.choice(block['Body'])
    print('Randomly selected Block is number: ' + str(block['Header']['block_no']))
    print('Randomly selected TX is: ' + str(TX))
    return block['Header']['block_no'], TX


def get_empty_block():
    new_block = {'Header': {'Timestamp': 0.0,
                            'MR': '',
                            'Hash': '',
                            'previous_hash': '',
                            'proof': None,
                            'block_no': 0},
                 'Body': get_transactions(TXs_per_block)}
    return new_block


def test_SPV():
    block_num, TX = randomly_select_TX()
    MP = merkletools.request_merkle_path(TX, full_blockchain)
    print('Merkle Path is : ')
    print_list_or_dict(MP)
    TX_is_valid = merkletools.SPV(MP, TX['TX_Double_Hash'], light_blockchain[block_num]['MR'])
    print('TX was found valid: ' + str(TX_is_valid))


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
    txs = {}
    txs_set = set()
    for entity in range(num_txs):
        new_tx = get_new_transaction()
        while new_tx in txs_set:
            new_tx = get_new_transaction()
        txs_set.add(new_tx)
        txs[entity] = {'TX_Double_Hash': encryption_module.hash_twice(new_tx),
                       'Data': new_tx}
    return txs


def get_new_transaction():
    return random.randint(1, 1000000)


def print_list_or_dict(to_be_printed):
    # function to nicely print a dictionary or a list
    if type(to_be_printed) == dict:
        pprint.pprint(to_be_printed, sort_dicts=False)
    elif type(to_be_printed) == list:
        for element in to_be_printed:
            print(element)
    print('==========================================')


def get_new_block(consensus, parameter):
    # fill in a new block
    new_block = get_empty_block()
    new_block['Header']['Timestamp'] = time.time()
    new_block['Header']['block_no'] = len(full_blockchain)
    if len(full_blockchain) == 0:
        new_block['Body'] = {}
        new_block['Header']['MR'] = '0'
        new_block['Header']['previous_hash'] = '0'
    else:
        new_block['Merkle_tree'] = merkletools.get_Merkle_Tree(new_block['Body'])
        new_block['Header']['MR'] = new_block['Merkle_tree'][-1]
        new_block['Header']['previous_hash'] = full_blockchain[-1]['Header']['Hash']
    to_be_hashed = [new_block['Header']['Timestamp'], new_block['Header']['previous_hash'], new_block['Body']]
    new_block['Header']['Hash'] = encryption_module.hash_object(to_be_hashed)
    new_block = encryption_module.get_proof(new_block, consensus, parameter)
    return new_block


def append_block_to_chain(new_block):
    full_blockchain.append(new_block)
    light_blockchain.append(new_block['Header'])
    print('New block is added to the chain:\n')
    print_list_or_dict(new_block)


def get_target(difficulty):
    string_target = ''
    for zeros in range(int(difficulty)):
        string_target += '0'
    for non_zeros in range(64 - int(difficulty)):
        string_target += 'f'
    return string_target


if __name__ == '__main__':
    # run the simulation
    consensus_type, second_parameter = define_consensus_algo()
    genesis_block = get_new_block(consensus_type, second_parameter)
    append_block_to_chain(genesis_block)

    for i in range(int(input('How many blocks would you like to generate?\n'))):
        append_block_to_chain(get_new_block(consensus_type, second_parameter))

    input('Now lets test our SPV implementation..?')
    test_SPV()
