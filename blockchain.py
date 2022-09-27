import hashlib
import json
import random
import time


# initiate the chain of blocks
blockchain = []
# define number of TXs per block
TXs_per_block = int(input('How many TXs per block would you like to generate?\n'))


def get_empty_block():
    new_block = {'Header': {'Timestamp': 0.0,
                            'MR': '',
                            'Hash': '',
                            'previous_hash': '',
                            'proof': '',
                            'block_no': ""},
                 'Body': get_transactions(TXs_per_block)}
    return new_block


def get_transactions(num_txs):
    # randomly generate and return some simulated TXs
    list_of_txs = []
    for i in range(num_txs):
        list_of_txs.append(random.randint(1, 1000000))
    return list_of_txs


def hash_object(entity):
    # hash something
    h = hashlib.sha256()
    h.update(str(entity).encode(encoding='UTF-8'))
    return h.hexdigest()


def hash_twice(entity):
    # hash something twice as for the merkle tree
    return hash_object(hash_object(entity))


def get_next_level_MT(list_of_TXs):
    i = 0
    concatenations = []
    while i < len(list_of_TXs):
        TX1 = list_of_TXs[i]
        try:
            TX2 = list_of_TXs[i + 1]
        except Exception as e:
            TX2 = list_of_TXs[i]
        hash_TX1 = hash_twice(TX1)
        hash_TX2 = hash_twice(TX2)
        concatenations.append(hash_TX1 + hash_TX2)
        i += 2
    return concatenations


def print_list_or_dict(to_be_printed):
    # function to nicely print a dictionary or a list
    if type(to_be_printed) == dict:
        print(json.dumps(to_be_printed, indent=4))
    elif type(to_be_printed) == list:
        for i in range(len(to_be_printed)):
            print(str(i + 1) + '-')
            print(to_be_printed[i])
    print('==========================================')


def get_new_block():
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
    return new_block


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


if __name__ == '__main__':
    # run the simulation
    genesis_block = get_new_block()
    append_block_to_chain(genesis_block)
    for i in range(int(input('How many blocks would you like to generate?\n'))):
        append_block_to_chain(get_new_block())




