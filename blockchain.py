import copy
import random
import time
import merkletools
import encryption_module
import tools
import SPV_methods


# initiate the chain of blocks
full_blockchain = []
light_blockchain = []
stack_of_TXs = []

# define number of TXs per block
TXs_per_block = int(input('How many TXs per block would you like to generate?\n'))


# generate asymmetric keys
public_key, private_key = encryption_module.generate_keys()


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

    num_of_consensus = 1
    # num_of_consensus = int(input('Please select the consensus algorithm to be simulated: 1-PoW, 2-PoS, 3-PoA:\n'))
    if num_of_consensus == 1:
        # define PoW difficulty
        difficulty = int(input('Please input the difficulty of the PoW puzzle:\n'))
        targeted_hash = get_target(difficulty)
        return num_of_consensus, targeted_hash
    # elif num_of_consensus == 2:
    #     owned_crypto = 100
    #     staked_crypto = random.randrange(32, owned_crypto)
    #     return num_of_consensus, staked_crypto
    # elif num_of_consensus == 3:
    #     return num_of_consensus, None


def get_transactions(num_txs):
    # randomly generate and return some simulated TXs
    txs = {}
    txs_set = set()
    for entity in range(num_txs):
        new_tx = get_new_transaction()
        while new_tx in txs_set:
            new_tx = get_new_transaction()
        txs_set.add(new_tx)
        stack_of_TXs.append(new_tx)
        txs[entity] = {'TX_Double_Hash': encryption_module.hash_twice(new_tx),
                       'Data': new_tx}
    return txs


def get_new_transaction():
    return random.randint(1, 1000000)


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
    to_be_hashed = [new_block['Header']['Timestamp'], new_block['Header']['previous_hash'], new_block['Header']['MR']]
    new_block['Header']['Hash'] = encryption_module.hash_object(to_be_hashed)
    new_block = encryption_module.get_proof(new_block, consensus, parameter)
    return new_block


def append_block_to_chain(new_block):
    full_blockchain.append(new_block)
    light_blockchain.append(new_block['Header'])
    print('New block is added to the chain:\n')
    tools.print_list_or_dict(new_block)


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
    SPV_methods.test_SPV(copy.deepcopy(full_blockchain), copy.deepcopy(light_blockchain), copy.deepcopy(stack_of_TXs))
