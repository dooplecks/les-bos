import itertools
from io import BytesIO
from collections import namedtuple
from ys.utils import make_reader

DEFAULT_KEY = b"\xd3\x6f\xac\x96"

YstbHeader = namedtuple("YstbHeader", "version count arg_section_len res_section_len")
CommandMeta = namedtuple("CommandMeta", "code arg_count")
Argument = namedtuple("Argument", "idx type res_len res_off")
Command = namedtuple("Command", "code args line")

read_header = make_reader(YstbHeader, "II4xII8x")
read_cmd_meta = make_reader(CommandMeta, "BBxx")  # xx = always zero
read_arg = make_reader(Argument, "HHII")


class Ystb:
    def __init__(self, code, res):
        self.code = code
        self.res = res

    @classmethod
    def from_stream(cls, f, key=DEFAULT_KEY):
        magic = f.read(4)

        if magic != b"YSTB":
            raise Exception(f"bad YSTB magic, got {magic}")

        header = read_header(f)
        count = header.count

        def read_obfuscated(size):
            buf = f.read(size)
            keystream = itertools.cycle(key)
            return bytes(x ^ y for x, y in zip(buf, keystream))

        cmd_section = read_obfuscated(count * 4)
        arg_section = read_obfuscated(header.arg_section_len)
        res_section = read_obfuscated(header.res_section_len)
        srcmap_section = read_obfuscated(count * 4)

        cmd_reader = BytesIO(cmd_section)
        arg_reader = BytesIO(arg_section)
        srcmap_reader = BytesIO(srcmap_section)
        code = []

        for _ in range(count):
            meta = read_cmd_meta(cmd_reader)
            args = tuple(read_arg(arg_reader) for _ in range(meta.arg_count))
            line = int.from_bytes(srcmap_reader.read(4), byteorder="little")

            cmd = Command(meta.code, args, line)
            code.append(cmd)

        return cls(code, res_section)
