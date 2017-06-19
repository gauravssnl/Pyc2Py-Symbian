import struct
__all__ = ['magics', 'versions']
def __build_magic(magic):
    return struct.pack('Hcc', magic, '\r', '\n')
def __by_version(magics):
    by_version = {}
    for m, v in magics.items():
        by_version[v] = m
    return by_version
versions = {
    __build_magic(20121): '1.5',
    __build_magic(50428): '1.6',
    __build_magic(50823): '2.0',
    __build_magic(60202): '2.1',
    __build_magic(60717): '2.2',
    __build_magic(62011): '2.3',
}
magics = __by_version(versions)
def __show(text, magic):
    print text, struct.unpack('BBBB', magic), struct.unpack('HBB', magic)
