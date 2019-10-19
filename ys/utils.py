from struct import Struct


def make_reader(cls, fmt):
    s = Struct(fmt)

    def fn(f):
        return cls(*s.unpack(f.read(s.size)))

    return fn


class StructIO(Struct):
    def read(self, f):
        return self.unpack(f.read(self.size))

    def write(self, f, *args):
        f.write(self.pack(*args))
