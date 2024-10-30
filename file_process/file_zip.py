import heapq
from bitarray import bitarray


'''
How to use the interface:

from file_zip import FileZipper, FileUnzipper

file_zipper = FileZipper()
file_zipper.zip_file(source_path, target_path)

file_unzipper = FileUnzipper()
file_unzipper.unzip_file(source_path, target_path)
'''


class HoffmanNode:
    def __init__(self, idx, value, left=-1, right=-1):
        self.idx = idx
        self.value = value
        self.pos = -1
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        if self.value < other.value:
            return True
        elif self.value == other.value:
            return self.idx < other.idx
        else:
            return False


def hoffman_dfs(hoffman_tree: list, pos, cur_code: str, code_dict: dict):
    if pos < 0 or pos >= len(hoffman_tree):
        return
    cur_node = hoffman_tree[pos]
    if cur_node.left == -1 and cur_node.right == -1:
        code_dict[cur_node.idx] = cur_code
    else:
        hoffman_dfs(hoffman_tree, cur_node.left, cur_code + '0', code_dict)
        hoffman_dfs(hoffman_tree, cur_node.right, cur_code + '1', code_dict)


def hoffman_encode(value_dict: dict) -> dict:
    unused_idx = 256
    hoffman_tree = []
    node_heap = [HoffmanNode(v[0], v[1]) for v in value_dict.items()]
    heapq.heapify(node_heap)
    while len(node_heap) > 0:
        node1 = heapq.heappop(node_heap)
        node1.pos = len(hoffman_tree)
        hoffman_tree.append(node1)
        if len(node_heap) == 0:
            break
        node2 = heapq.heappop(node_heap)
        node2.pos = len(hoffman_tree)
        hoffman_tree.append(node2)
        new_node = HoffmanNode(unused_idx,
                               node1.value + node2.value,
                               left=node1.pos,
                               right=node2.pos)
        unused_idx += 1
        heapq.heappush(node_heap, new_node)
    
    code_dict = {}
    hoffman_dfs(hoffman_tree, len(hoffman_tree) - 1, "", code_dict)
    return code_dict


class FileZipper:
    def __init__(self):
        pass

    # read original file
    def read_file(self, path) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            file.close()
            return content
        except:
            raise FileNotFoundError('The file does not exist.')
    
    # calculate freq of each char
    def cal_freq(self, content: str) -> dict:
        char_conut = {}
        for c in content:
            c_i = ord(c)
            if c_i >= 256:
                continue  # assume that all ord(c) <= 255
            if c_i in char_conut:
                char_conut[c_i] += 1
            else:
                char_conut[c_i] = 1
        return char_conut
    
    # zip a file
    def zip_file(self, from_path, to_path):
        content = self.read_file(from_path)
        char_freq_dict = self.cal_freq(content)
        char_code_dict = hoffman_encode(char_freq_dict)
        zipped_content = b''

        '''
        zipped_content:
        num_char(1byte)
        char_freq_dict(num_char * (ord(char) 1byte + freq 4byte))
        encoded content(bit stream)
        end_mark(1byte)
        '''

        # save num_char
        num_char = len(char_freq_dict)
        zipped_content += int(num_char).to_bytes(1, byteorder='big')

        # save char_freq_dict
        for v in char_freq_dict.items():
            zipped_content += int(v[0]).to_bytes(1, byteorder='big')
            zipped_content += int(v[1]).to_bytes(4, byteorder='big')

        # save content
        bit_stream = bitarray('', endian='big')
        for c in content:
            if ord(c) >= 256:
                continue
            bit_stream += bitarray(char_code_dict[ord(c)], endian='big')
        
        # save end_mark
        end_mark = (8 - bit_stream.__len__() % 8) % 8
        zipped_content += bit_stream.tobytes()
        zipped_content += int(end_mark).to_bytes(1, byteorder='big')

        with open(to_path, 'wb') as file:
            file.write(zipped_content)
        file.close()


class FileUnzipper:
    def __init__(self):
        pass

    # read zipped file
    def read_zipped_file(self, path) -> bytes:
        try:
            with open(path, 'rb') as file:
                zipped_content = file.read()
            file.close()
            return zipped_content
        except:
            raise FileNotFoundError('The file does not exist.')
    
    # unzip a file
    def unzip_file(self, from_path, to_path):
        zipped_content = self.read_zipped_file(from_path)
        
        '''
        zipped_content:
        num_char(1byte)
        char_freq_dict(num_char * (ord(char) 1byte + freq 4byte))
        encoded content
        end_mark(1byte)
        '''

        num_char = int.from_bytes(zipped_content[0 : 1], byteorder='big')

        # reconstruct char_freq_dict
        char_freq_dict = {}
        for i in range(num_char):
            c_i = int.from_bytes(zipped_content[i * 5 + 1 : i * 5 + 2], byteorder='big')
            freq = int.from_bytes(zipped_content[i * 5 + 2 : i * 5 + 6], byteorder='big')
            char_freq_dict[c_i] = freq
        
        # re-calculate char_code_dict
        char_code_dict = hoffman_encode(char_freq_dict)

        # decode
        code_char_map = dict([(v[1], v[0]) for v in char_code_dict.items()])
        end_mark = int.from_bytes(zipped_content[-1:], byteorder='big')
        encoded_content = bitarray(endian='big')
        encoded_content.frombytes(zipped_content[num_char * 5 + 1 : -1])
        encoded_content = encoded_content.tolist()
        i, content = 0, ''
        while i < len(encoded_content) - end_mark:
            char_code = ''
            while True:
                if encoded_content[i]:
                    char_code += '1'
                else: 
                    char_code += '0'
                i += 1
                if char_code in code_char_map.keys():
                    content += chr(code_char_map[char_code])
                    break
        
        with open(to_path, 'w') as file:
            file.write(content)
        file.close()
