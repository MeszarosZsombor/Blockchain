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


def get_concatenations(list_of_TXs):
    concatenations = []
    counter = 0
    while counter < len(list_of_TXs):
        TX1 = list_of_TXs[counter]
        try:
            TX2 = list_of_TXs[counter + 1]
        except Exception as e1:
            TX2 = list_of_TXs[counter]
        try:
            concatenations.append(TX1['TX_Double_Hash'] + TX2['TX_Double_Hash'])
        except Exception as e2:
            concatenations.append(TX1 + TX2)
        counter += 2
    return concatenations


def request_merkle_path(tx, full_blockchain):
    for block in full_blockchain:
        for TX_num in block['Body']:
            if block['Body'][TX_num]['Data'] == tx['Data']:
                return get_path(block['Merkle_tree'], block['Body'][TX_num]['TX_Double_Hash'])


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



def get_next_level_MT(list_of_TXs, nodes_of_Merkel_Tree_reversed):
    counter = 0
    concatenations = []
    while counter < len(list_of_TXs):
        TX1 = list_of_TXs[counter]
        try:
            TX2 = list_of_TXs[counter + 1]
        except Exception as e1:
            TX2 = list_of_TXs[counter]

        try:
            TX1_double_hash = TX1['TX_Double_Hash']
        except:
            TX1_double_hash = encryption_module.hash_twice(TX1)
        try:
            TX2_double_hash = TX2['TX_Double_Hash']
        except Exception as e2:
            TX2_double_hash = encryption_module.hash_twice(TX2)
        nodes_of_Merkel_Tree_reversed.append(TX1_double_hash)
        nodes_of_Merkel_Tree_reversed.append(TX2_double_hash)
        concatenated = TX1_double_hash + TX2_double_hash
        concatenations.append(concatenated)
        counter += 2
    return concatenations, nodes_of_Merkel_Tree_reversed
