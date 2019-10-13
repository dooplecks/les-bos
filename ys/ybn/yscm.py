from collections import namedtuple
from ys.utils import make_reader

YscmHeader = namedtuple("YscmHeader", "version count")
CommandInfo = namedtuple("CommandInfo", "name args")
ArgumentInfo = namedtuple("ArgumentInfo", "name unknown")

read_header = make_reader(YscmHeader, "II4x")


def read_cstring(f):
    return b"".join(iter(lambda: f.read(1), b"\0"))


def read_cstring_sjis(f):
    return read_cstring(f).decode("cp932")


class Yscm:
    def __init__(self, table):
        self.table = table

    @classmethod
    def from_stream(cls, f):
        magic = f.read(4)

        if magic != b"YSCM":
            raise Exception(f"bad YSCM magic, got {magic}")

        header = read_header(f)
        table = []

        for _ in range(header.count):
            cmd_name = read_cstring_sjis(f)
            arity = ord(f.read(1))
            args = []

            for _ in range(arity):
                arg_name = read_cstring_sjis(f)
                unknown = f.read(2)
                args.append(ArgumentInfo(arg_name, unknown))

            table.append(CommandInfo(cmd_name, tuple(args)))

        return cls(table)
