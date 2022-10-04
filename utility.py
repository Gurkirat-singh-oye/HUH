

def write_file (file, data):
    f = open(file, "wb")
    f.write(data)
    f.close()

def read_file (file):
    f = open(file, "r")
    return (f.read())
