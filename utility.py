

def write_file (file, data):
    f = open(file, "wb")
    f.write(data)
    f.close()

def read_file (file):
    f = open(file, "rb")
    return (f.read())
