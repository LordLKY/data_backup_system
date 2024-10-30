import os
# import stat
# from bitarray import bitarray

'''
How to use the interface:

from file_pack import FilePacker, FileUnpacker

file_packer = FilePacker()
file_packer.pack_dir(dir_path, pack_path)

file_unpacker = FileUnpacker()
file_unpacker.unpack_dir(pack_path, dir_path)
'''

class FileWalker:
    def __init__(self) -> None:
        self.dir_path = ''
        self.link_records = {}
    
    def check_name(self, file_name: str):
        if(len(file_name) > 255):
            print("The name of file is longer than 255 bytes")
            exit(-1)
    
    def get_file_info(self, file_name: str) -> bytes:
        file_info = {}

        # structure of file_info:
        # file_name(relative path) - (1(len)+255)B
        # file_type 1bit(is_dir)
        # (not used) file_type 1B(is_reg/is_dir/is_link/is_slink/is_pipe/is_major_link/is_cross_slink/pad with 1 bit)
        # (not used) link_dst - (1+255)B
        # (not used) slink_dst - (1+255)B
        # ...
        # content_len - 4B
        # content

        file_info['file_name'] = file_name
        self.check_name(file_name)
        file_path = os.path.join(self.dir_path, file_name)

# since we don't consider links now, some of this part is not used
#---------------------------
        # file_stat = os.stat(file_path)

        # # get file_type
        # # define that only normal file and non-symbolic major_link-type file are regular
        # # only the content of regular files should be recorded 
        # file_info['is_reg'] = 0
        file_info['is_dir'] = 0
        # is_dir, is_link, is_slink, is_pipe, \
        # is_major_link, is_cross_slink = 0, 0, 0, 0, 0, 0
        # file_info['link_dst'], file_info['slink_dst'] = '', ''
        # if stat.S_ISREG(file_stat.st_mode):
        #     file_info['is_reg'] = 1
        if os.path.isdir(file_path):
            file_info['is_dir'] = 1
        # if stat.S_ISLNK(file_stat.st_mode):
        #     is_slink = 1
        #     slink_dst = os.readlink(file_path)
        #     file_info['is_reg'] = 0
        #     file_info['slink_dst'] = slink_dst
        #     self.check_name(slink_dst)
        #     if slink_dst not in os.listdir(self.dir_path):
        #         is_cross_slink = 1
        # if stat.S_ISFIFO(file_stat.st_mode):
        #     is_pipe = 1
        # if file_stat.st_nlink > 1:
        #     is_link = 1
        #     ino = file_stat.st_ino
        #     if ino in self.link_records.keys():
        #         file_info['link_dst'] = self.link_records[ino]
        #         file_info['is_reg'] = 0
        #         self.check_name(file_info['link_dst'])
        #     else:
        #         is_major_link = 1
        #         self.link_records[ino] = file_name
        # file_info['file_type'] = bitarray(
        #     [file_info['is_reg'], is_dir, is_link, is_slink, is_pipe, is_major_link, is_cross_slink, 0],
        #     endian='big')
        
        # other info
#---------------------------

        return self.file2bytes(file_info)
    
    def file2bytes(self, file_info: dict) -> bytes:
        content = b''

# since we don't consider links now, some of this part is not used
#---------------------------
        # file_name2bytes
        content += self.name2bytes(file_info['file_name'])
        content += int(file_info['is_dir']).to_bytes(1, byteorder='big')
        
        # # file_type2bytes
        # content += file_info['file_type'].tobytes()

        # # link2bytes
        # content += self.name2bytes(file_info['link_dst'])
        # content += self.name2bytes(file_info['slink_dst'])
#---------------------------

        # file_content2bytes
        if file_info['is_dir'] == 0:
            with open(os.path.join(self.dir_path, file_info['file_name']), 'rb') as file:
                file_content = file.read()
                content += int(len(file_content)).to_bytes(4, byteorder='big')
                content += file_content
            file.close()
        else:
            content += int(0).to_bytes(4, byteorder='big')
        
        return content

    def name2bytes(self, name: str) -> bytes:
        content = b''
        name_bytes = name.encode('utf-8')
        name_len = len(name_bytes)
        content += int(name_len).to_bytes(1, byteorder='big')
        content += name_bytes
        if name_len < 255:
            content += int(0).to_bytes(255 - name_len, byteorder='big')
        return content


class FilePacker:
    def __init__(self) -> None:
        self.packed_content = b''
        self.file_walker = FileWalker()

    # pack a dir
    def pack_file(self, dir_path: str, pack_path: str):
        if not os.path.isdir(dir_path):
            raise RuntimeError("The directory does not exist.")
        
        self.file_walker.dir_path = dir_path
        self.dir_tree(dir_path)

        with open(pack_path, 'wb') as file:
            file.write(self.packed_content)
        file.close()
    
    def dir_tree(self, strat_path: str, relative_path: str = ''):
        for file_name in os.listdir(os.path.join(strat_path, relative_path)):
            relative_file_path = os.path.join(relative_path, file_name)
            self.packed_content += self.file_walker.get_file_info(relative_file_path)
            if os.path.isdir(os.path.join(strat_path, relative_file_path)):
                self.dir_tree(strat_path, relative_file_path)
        

class FileUnpacker:
    def __init__(self) -> None:
        self.packed_content = b''
        self.dir_path = ''
    
    # read packed file
    def read_packed_file(self, path) -> bytes:
        try:
            with open(path, 'rb') as file:
                self.packed_content = file.read()
            file.close()
        except:
            raise FileNotFoundError('The file does not exist.')
    
    # unpack
    def unpack_file(self, pack_path: str, dir_path: str):
        if not os.path.isdir(dir_path):
            raise RuntimeError("The directory does not exist.")
        
        self.read_packed_file(pack_path)
        self.dir_path = dir_path

        cur = 0
        while cur != len(self.packed_content):
            file_info = {}

            # get file_name
            name_len = int.from_bytes(self.packed_content[cur: cur + 1], byteorder='big')
            file_info['file_name'] = self.packed_content[cur + 1: cur + 1 + name_len].decode('utf-8')
            cur += 256

# since we don't consider links now, some of this part is not used
#---------------------------
            # # get file_type
            # file_info['file_type'] = bitarray(endian='big')
            # file_info['file_type'].frombytes(self.packed_content[cur: cur + 1])
            file_info['is_dir'] = int.from_bytes(self.packed_content[cur: cur + 1], byteorder='big')
            cur += 1

            # # get link_dst
            # link_len = int.from_bytes(self.packed_content[cur: cur + 1], byteorder='big')
            # file_info['link_dst'] = self.packed_content[cur + 1: cur + 1 + link_len].decode('utf-8')
            # cur += 256
            # slink_len = int.from_bytes(self.packed_content[cur: cur + 1], byteorder='big')
            # file_info['slink_dst'] = self.packed_content[cur + 1: cur + 1 + slink_len].decode('utf-8')
            # cur += 256
#---------------------------

            # get file_content
            content_len = int.from_bytes(self.packed_content[cur: cur + 4], byteorder='big')
            content = self.packed_content[cur + 4: cur + 4 + content_len]
            cur += 4 + content_len

            self.reconstruct_file(file_info, content)
        
        # self.reconstruct_link()
    
    def reconstruct_file(self, file_info: dict, content: bytes):
        path = os.path.join(self.dir_path, file_info['file_name'])
        if file_info['is_dir']:
            os.mkdir(path)
        else:
            with open(path, 'wb') as file:
                file.write(content)
            file.close()

    # def reconstruct_link(self):
    #     pass