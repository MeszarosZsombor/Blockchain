import rsa
from datetime import datetime
import tools


class Node:
    def __init__(self):
        self.private_key, self.public_key = generate_keys()
        self.private_data = ''


def generate_keys():
    try:
        (pub_key, pri_key) = rsa.newkeys(512)
        return pri_key, pub_key
    except Exception as e:
        print(e)


nodeA = Node()
nodeB = Node()


def initiate_contract(public_key, private_key):
    signmsg = public_key.save_pkcs1().decode() + datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

    contract = {
        'public_key': public_key,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f"),
        'sign': rsa.sign(signmsg.encode(), private_key, 'SHA-256'),
        'encrypted_data': None
    }
    return contract


def encrypt_data(data, pub_key):
    data_bytes = data.encode('utf-8')
    encrypted_data = rsa.encrypt(data_bytes, pub_key)
    return encrypted_data


def decrypt_data(encrypted_data, pri_key):
    decrypted_data = rsa.decrypt(encrypted_data, pri_key)
    decrypted_data_str = decrypted_data.decode('utf-8')
    return decrypted_data_str


def upload_data(contract, node_private_data):
    encrypted_data = encrypt_data(node_private_data, contract['public_key'])
    contract['encrypted_data'] = encrypted_data


def verify_contract(contract, public_key):
    message = public_key.save_pkcs1().decode() + contract['timestamp']

    try:
        rsa.verify(message.encode(), contract['sign'], public_key)
        print("The contract is valid.")
    except rsa.VerificationError:
        print("The contract is NOT valid.")


if __name__ == '__main__':
    contractTest = initiate_contract(nodeA.public_key, nodeA.private_key)
    tools.print_list_or_dict(contractTest)
    verify_contract(contractTest, nodeA.public_key)
    msg = input("What message do you want to send?\n")
    upload_data(contractTest, msg)
    tools.print_list_or_dict(contractTest)
    print(decrypt_data(contractTest['encrypted_data'], nodeA.private_key))
