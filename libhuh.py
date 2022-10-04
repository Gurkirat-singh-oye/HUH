import argparse, collections, configparser, hashlib, os, re, sys, zlib
from utility import *

argp = argparse.ArgumentParser()
argsubp = argp.add_subparsers(title="Commands", dest="command")
argsubp.required = True

def main(argv=sys.argv[1:]):
    # args = argp.parse_args(argv)
    if argv[0] == "init"        : init(argv[1])


def init (repo):
    if not os.path.isdir(repo):
        os.mkdir(repo)

    os.mkdir(os.path.join(repo, ".git"))
    for a in ["objects", "refs", "refs/heads"]:
        os.mkdir( os.path.join(repo, ".git", a) )

    write_file(os.path.join(repo, '.git', 'HEAD'),
               b'ref: refs/heads/master')
    
    print(f"lets go!!!, repo initialized in {repo}")

