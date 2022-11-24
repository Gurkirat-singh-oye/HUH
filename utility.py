import enum

def write_file (file, data):
    f = open(file, "wb")
    f.write(data)
    f.close()

def read_file (file):
    f = open(file, "rb")
    return (f.read())

class ObjectType(enum.Enum):
    commit = 1
    tree = 2
    blob = 3

