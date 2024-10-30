from .file_encrypt import *
from .file_pack import *
from .file_zip import *

'''
all the functions has been wrapped as interface below
use 'from AdditionalFunction.interface import *' to import
'''

def fencrypt(path: str, key: str):
    file_encrypter = FileEncrypter()
    file_encrypter.encrypt_file(path, key)

def fdecrypt(path: str, key: str):
    file_decrypter = FileDecrypter()
    file_decrypter.decrypt_file(path, key)

def fpack(from_path: str, to_path:str):
    file_packer = FilePacker()
    file_packer.pack_file(from_path, to_path)

def funpack(from_path: str, to_path:str):
    file_unpacker = FileUnpacker()
    file_unpacker.unpack_file(from_path, to_path)

def fzip(from_path: str, to_path:str):
    file_zipper = FileZipper()
    file_zipper.zip_file(from_path, to_path)

def funzip(from_path: str, to_path:str):
    file_unzipper = FileUnzipper()
    file_unzipper.unzip_file(from_path, to_path)