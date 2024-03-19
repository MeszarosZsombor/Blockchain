import merkletools
import tools
import random


def test_SPV(full_blockchain, light_blockchain, stack_of_TXs):
    block_num, TX = randomly_select_TX(full_blockchain)
    MP, is_valid = merkletools.request_merkle_path(TX, full_blockchain, stack_of_TXs)
    if is_valid:
        print('Merkle Path is : ')
        tools.print_list_or_dict(MP)
        print('Light node is using the Merkle Path to validate..')
        TX_is_valid = merkletools.SPV(MP, TX['TX_Double_Hash'], light_blockchain[block_num]['MR'])
        print('TX was found valid by light-node: ' + str(TX_is_valid))
    else:
        print('Full node responded to light-node that the TX is invalid. Thus, TX should be ignored.')


def randomly_select_TX(full_blockchain):
    block = random.choice(full_blockchain)
    while len(block['Body']) == 0:
        block = random.choice(full_blockchain)
    TX = random.choice(block['Body'])
    print('Randomly selected Block is number: ' + str(block['Header']['block_no']))
    print('Randomly selected TX is: ' + str(TX))
    return block['Header']['block_no'], TX