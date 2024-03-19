import encryption_module


def get_Merkle_Tree(dict_of_txs):
    nodes_of_merkle_tree = []
    list_of_txs = []
    for tx in dict_of_txs:
        list_of_txs.append(dict_of_txs[tx]['TX_Double_Hash'])
        nodes_of_merkle_tree.append(dict_of_txs[tx]['TX_Double_Hash'])
    if len(nodes_of_merkle_tree) % 2 != 0:
        nodes_of_merkle_tree.append(nodes_of_merkle_tree[-1])
        list_of_txs.append(nodes_of_merkle_tree[-1])
    list_of_concatenations = get_concatenations(list_of_txs)
    while len(list_of_concatenations) > 1:
        next_level = []
        for concatenated_hashes in list_of_concatenations:
            new_value = encryption_module.hash_twice(concatenated_hashes)
            next_level.append(new_value)
            nodes_of_merkle_tree.append(new_value)
        if len(nodes_of_merkle_tree) % 2 != 0:
            nodes_of_merkle_tree.append(nodes_of_merkle_tree[-1])
            next_level.append(nodes_of_merkle_tree[-1])
        list_of_concatenations = get_concatenations(next_level)
    nodes_of_merkle_tree.append(encryption_module.hash_twice(list_of_concatenations[0]))
    return nodes_of_merkle_tree


def get_concatenations(lst_of_TXs):
    concatenations = []
    counter = 0
    while counter < len(lst_of_TXs):
        TX1 = lst_of_TXs[counter]
        try:
            TX2 = lst_of_TXs[counter + 1]
        except Exception as e1:
            TX2 = lst_of_TXs[counter]
        try:
            concatenations.append(TX1['TX_Double_Hash'] + TX2['TX_Double_Hash'])
        except Exception as e2:
            concatenations.append(TX1 + TX2)
        counter += 2
    return concatenations


def request_merkle_path(tx, full_blockchain, stack_of_txs):
    # step1: check if tx data is correct
    path = None
    tx_is_valid = False
    print('Full node is checking if the TX is valid..')
    for element in stack_of_txs:
        if element == tx['Data']:
            tx_is_valid = True
            # step2: build the path of the valid TX
            print('TX is found valid, Full node is building the Merkle Path for the light-node..')
            for block in full_blockchain:
                for TX_num in block['Body']:
                    if block['Body'][TX_num]['Data'] == tx['Data']:
                        path = get_path(block['Merkle_tree'], block['Body'][TX_num]['TX_Double_Hash'])
    return path, tx_is_valid


def get_path(nodes_of_merkel_tree_reversed, tx_hash):
    path = []
    for index in range(len(nodes_of_merkel_tree_reversed) - 1):
        if nodes_of_merkel_tree_reversed[index] == tx_hash:
            if (index % 2) == 0:
                sibling = nodes_of_merkel_tree_reversed[index + 1]
                next_to_hash = tx_hash + sibling
            else:
                sibling = nodes_of_merkel_tree_reversed[index - 1]
                next_to_hash = sibling + tx_hash
            path.append([sibling, index])
            tx_hash = encryption_module.hash_twice(next_to_hash)
    path.append(nodes_of_merkel_tree_reversed[-1])
    return path


def SPV(path, target_hash, merkle_root):
    if len(path) == 0:
        return target_hash == merkle_root
    else:
        for sibling in path:
            if type(sibling) != list:
                return sibling == merkle_root
            else:
                sibling_hash = sibling[0]
                sibling_index = sibling[1]

                if (sibling_index % 2) == 0:
                    target_hash = encryption_module.hash_twice(sibling_hash + target_hash)
                else:
                    target_hash = encryption_module.hash_twice(target_hash + sibling_hash)
