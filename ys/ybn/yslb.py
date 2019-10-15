import struct
from collections import namedtuple
from ys.utils import make_reader

YslbHeader = namedtuple("YslbHeader", "version count")
Label = namedtuple("Label", "name offset yst_index")

read_header = make_reader(YslbHeader, "II")


class Yslb:
    def __init__(self, labels):
        self.labels = labels

    @classmethod
    def from_stream(cls, f):
        magic = f.read(4)

        if magic != b"YSLB":
            raise Exception(f"bad YSLB magic, got {magic}")

        header = read_header(f)
        f.seek(1024, 1)  # crc first-byte index

        labels = []

        for _ in range(header.count):
            name_len = ord(f.read(1))
            name = f.read(name_len).decode("cp932")
            offset, yst_index = struct.unpack(
                "xxxxIHxx", f.read(12)
            )  # xxxx = crc of name, xx = always zero

            label = Label(name, offset, yst_index)
            labels.append(label)

        return cls(labels)
