from bitarray import bitarray

'''
How to use the interface:

from file_encrypt import FileEncrypter, FileDecrypter

file_encrypter = FileEncrypter()
file_encrypter.encrypt_file('path/to/your/file', 'key')

file_decrypter = FileDecrypter()
file_decrypter.decrypt_file('path/to/your/file', 'key')
'''


def gen_permutation(idx_dict: dict, key: str) -> dict:
    key = key.encode('utf-8')
    key_bits = bitarray(endian='big')
    key_bits.frombytes(key)
    key_bits = key_bits.tolist()  # 64-bits
    for i in range(len(key_bits)):
        permute_op(idx_dict, key_bits[i], i % 7 + 1)
    return idx_dict


def permute_op(idx_dict: dict, op_mark, seed):
    sign = 1
    if op_mark:
        sign = -1
    for i in range(64):
        idx1 = i
        idx2 = (i + sign * (i % 11 + 1) * seed + 128) % 64
        temp = idx_dict[idx1]
        idx_dict[idx1] = idx_dict[idx2]
        idx_dict[idx2] = temp


def permute_bytes(permutation_dict: dict, content: bytes) -> bytes:
    new_content = b''
    for i in range(64):
        pos = permutation_dict[i]
        new_content += content[pos: pos + 1]
    return new_content


class FileEncrypter:
    def __init__(self):
        self.permutation_dict = dict([(i, i) for i in range(64)])

    # read original file
    def read_file(self, path) -> str:
        try:
            # using 'rb' & 'wb' is more robust
            # with open(path, 'r+') as file:
            #     content = file.read()
            #     file.write('')  # clear the file
            # file.close()
            with open(path, 'rb') as file:
                content = file.read()
            file.close()
            with open(path, 'wb') as file:
                file.write(b'')
            file.close()
            return content
        except:
            raise FileNotFoundError('The file does not exist.')
    
    # encrypt a file
    def encrypt_file(self, path, key: str):
        # generate new permutation_dict
        assert len(key) == 8, 'The key must be 8 characters long.'
        self.permutation_dict = gen_permutation(self.permutation_dict, key)

        content = self.read_file(path)

        # enlongate the content to 64*x Bytes
        # content = content.encode('utf-8')
        content_len = len(content)
        padded_len = ((content_len + 3) // 64 + 1) * 64
        for i in range(padded_len - 4 - content_len):
            content += int(i).to_bytes(1, byteorder='big')
        content += int(content_len).to_bytes(4, byteorder='big')

        # permutation
        new_content = b''
        for i in range(0, padded_len, 64):
            new_content += permute_bytes(self.permutation_dict, content[i: i + 64])
        
        # XOR
        encrypted_content = b''
        for i in range(0, padded_len, 8):
            # encrypted_content += new_content[i: i + 8] ^ (key.encode('utf-8'))
            encrypted_content += bytes([bit1 ^ bit2 for bit1, bit2 in zip(new_content[i: i + 8], (key.encode('utf-8')))])
        
        with open(path, 'wb') as file:
            file.write(encrypted_content)
        file.close()


class FileDecrypter:
    def __init__(self):
        self.permutation_dict = dict([(i, i) for i in range(64)])
    
    # read encrypted file
    def read_encrypted_file(self, path) -> bytes:
        try:
            with open(path, 'rb') as file:
                encrypted_content = file.read()
            file.close()
            with open(path, 'wb') as file:
                file.write(b'')
            file.close()
            return encrypted_content
        except:
            raise FileNotFoundError('The file does not exist.')
    
    # decrypt a file
    def decrypt_file(self, path, key: str):
        # reconstruct the permutation_dict
        assert len(key) == 8, 'The key must be 8 characters long.'
        self.permutation_dict = gen_permutation(self.permutation_dict, key)

        encrypted_content = self.read_encrypted_file(path)

        # XOR
        permuted_content = b''
        for i in range(0, len(encrypted_content), 8):
            # permuted_content += encrypted_content[i: i + 8] ^ (key.encode('utf-8'))
            permuted_content += bytes([bit1 ^ bit2 for bit1, bit2 in zip(encrypted_content[i: i + 8], (key.encode('utf-8')))])
        
        # reverse permutation
        reverse_dict = dict([(v[1], v[0]) for v in self.permutation_dict.items()])
        decrypted_content = b''
        for i in range(0, len(permuted_content), 64):
            decrypted_content += permute_bytes(reverse_dict, permuted_content[i: i + 64])
        
        # restore original content
        content_len = int.from_bytes(decrypted_content[-4:], byteorder='big')
        # content = decrypted_content[:content_len].decode("utf-8")

        # using 'wb' is more robust
        # with open(path, 'w') as file:
        #     file.write(content)
        with open(path, 'wb') as file:
            file.write(decrypted_content[:content_len])
        file.close()
