import argparse, collections, configparser, hashlib, os, re, sys, zlib
import struct
from utility import *

argp = argparse.ArgumentParser()
argsubp = argp.add_subparsers(title="Commands", dest="command")
argsubp.required = True

def main(argv=sys.argv[1:]):
    # args = argp.parse_args(argv)
    if argv[0] == "init"        : init(argv[1])

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


def hash_object():
    pass

def add():
    pass