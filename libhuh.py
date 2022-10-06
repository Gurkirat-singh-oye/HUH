import argparse, collections, configparser, hashlib, os, re, sys, zlib
import struct
from utility import *

argp = argparse.ArgumentParser()
argsubp = argp.add_subparsers(title="Commands", dest="command")
argsubp.required = True

def main(argv=sys.argv[1:]):
    # args = argp.parse_args(argv)
    if   argv[0] == "init"        : init("." if len(argv) == 1 else argv[1])
    elif argv[0] == "cat-file"    : cat_file(hash=argv[1]) # need to add parameters

IndexEntry = collections.namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode',
    'uid', 'gid', 'size', 'sha1', 'flags', 'path',
])

def init (repo):
    if not os.path.isdir(repo):
        os.mkdir(repo)

    if not os.path.isdir(os.path.join(repo, ".git")):
        os.mkdir(os.path.join(repo, ".git"))
        for a in ["objects", "refs", "refs/heads"]:
            os.mkdir( os.path.join(repo, ".git", a) )

        write_file(os.path.join(repo, '.git', 'HEAD'),
                b'ref: refs/heads/master')
        
        print(f"lets go!!!, repo initialized in {repo}")
    else:
        print("This is already a git repository: .git/ already exists")


def read_index():
    try:
        data = read_file(os.path.join(".git", "index"))
    except Exception as e:
        return e
    
    # digest = hashlib.sha1(data[:-20]).digest()
    # sign, vers, ents = struct.unpack( "!4sLL", data[:12])

    entry_data = data[12:-20]
    entries = []

    i = 0
    while i + 62 < len(entry_data):
        fields_end = i + 62
        fields = struct.unpack('!LLLLLLLLLL20sH', entry_data[i:fields_end])
        path_end = entry_data.index(b'\x00', fields_end)
        path = entry_data[fields_end:path_end]
        entry = IndexEntry(*(fields + (path.decode(),)))
        entries.append(entry)
        entry_len = ((62 + len(path) + 8) // 8) * 8
        i += entry_len
    return entries


def ls_files(details=False):
    for entry in read_index():
        if details:
            stage = (entry.flags >> 12) & 3
            print(f'? {entry.sha1.hex()} ?{stage}?\t{entry.path}')
        else:
            print(entry.path)


def hash_object(data, obj_type, write=True):
    header = (f"{obj_type} {len(data)}").encode()
    full_data = header + b'\x00' + data
    sha1 = hashlib.sha1(full_data).hexdigest()
    if write:
        path = os.path.join('.git', 'objects', sha1[:2], sha1[2:])
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, zlib.compress(full_data))
    return sha1



def find_object(given_hash, dir=""):
    dir = os.path.join(dir, ".git", "objects")
    tmp = []
    for hash_prefix in os.listdir(dir):
        tmp.append(hash_prefix)
        if given_hash[:2] == hash_prefix:
            for two_hashes_end in os.listdir(os.path.join(dir, hash_prefix)):
                if given_hash[2:len(given_hash)] == two_hashes_end[:len(given_hash)-2]:
                    return os.path.join(dir, hash_prefix, two_hashes_end)
    return ""


def read_object(object_file_path):
    z_comp_data = read_file(object_file_path)
    obj_data = zlib.decompress(z_comp_data)
    tmp_tuple = tuple(obj_data.split(b'\x00', 1))
    header, data = tmp_tuple[0], tmp_tuple[1]
    header = header.decode()
    return header, data


def cat_file( hash):
    obj_file = find_object(hash) #dir parameter?
    if obj_file == "":
        print("Object does not exist or invalid hash")
        return
    # if param != "-p":
    #     print("'-p' was not used, use it next time")
    data_list = read_object(obj_file)
    # print(data_list[0])
    print(data_list[1].decode(errors='ignore'))


def add():
    pass