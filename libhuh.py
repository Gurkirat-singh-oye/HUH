import argparse, collections, configparser, hashlib, os, re, sys, zlib
import subprocess
import struct
from utility import *

argp = argparse.ArgumentParser()
argsubp = argp.add_subparsers(title="Commands", dest="command")
argsubp.required = True

def main(argv=sys.argv[1:]):
    # args = argp.parse_args(argv)
    if   argv[0] == "init"        : init("." if len(argv) == 1 else argv[1])
    elif argv[0] == "cat-file"    : cat_file(hash=argv[1])  # need to add parameters, just dont use any flags
    elif argv[0] == "ls-files"    : ls_files()              # need to add details flag
    elif argv[0] == "status"      : get_status()

    else :
        print("future me will definetly implement this")

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
    
    # some checks were skipped

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
    return "nah!"

def read_object(sha1_prefix):
    path = find_object(sha1_prefix)
    full_data = zlib.decompress(read_file(path))
    nul_index = full_data.index(b'\x00')
    header = full_data[:nul_index]
    obj_type, size_str = header.decode().split()
    size = int(size_str)
    data = full_data[nul_index + 1:]
    assert size == len(data), 'expected size {}, got {} bytes'.format(
            size, len(data))
    return (obj_type, data)


def read_tree(sha1=None, data=None):
    """
        things were ignored for simplicity - no mention of object type
    """
    if sha1 is not None:
        obj_type, data = read_object(sha1)
        assert obj_type == 'tree'
    elif data is None:
        raise TypeError('must specify "sha1" or "data"')
    i = 0
    entries = []
    for _ in range(1000):
        end = data.find(b'\x00', i)
        if end == -1:
            break
        mode_str, path = data[i:end].decode().split()
        mode = int(mode_str, 8)
        digest = data[end + 1:end + 21]
        entries.append((mode, path, digest.hex()))
        i = end + 1 + 20
    return entries


def cat_file( hash):
    (obj_type, data) = read_object(hash)
    for a in read_tree(data=data):
        print(a[0], obj_type, a[2], a[1])


def get_status():
    commited_files = []
    not_traced = []
    curr_dir = subprocess.run(["ls"], capture_output=True).stdout.decode().splitlines()
    for en in read_index():
        commited_files = {en.path : "y"}
    
    for file in curr_dir:
        try:
            commited_files[file]
        except KeyError:
            not_traced.append(file)

    print("huh have no idea what these files are :")
    for a in not_traced:
        print("\t", a)


def add():
    pass