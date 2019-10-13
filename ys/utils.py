import struct


def make_reader(cls, fmt):
    sz = struct.calcsize(fmt)

    def fn(f):
        return cls(*struct.unpack(fmt, f.read(sz)))

    return fn
