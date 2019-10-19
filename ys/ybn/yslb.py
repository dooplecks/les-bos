import binascii
import itertools
import collections
from dataclasses import dataclass
from ys.utils import StructIO

header_struct = StructIO("4sII")
label_struct = StructIO("IIHxx")


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = self.func(obj)
        obj.__dict__[self.func.__name__] = value
        return value


@dataclass(frozen=True)
class Label:
    name: str
    offset: int
    yst_index: int

    @cached_property
    def name_encoded(self):
        return self.name.encode("cp932")

    @cached_property
    def name_hash(self):
        return binascii.crc32(self.name_encoded)


class Yslb:
    def __init__(self, labels):
        self.labels = labels

    @classmethod
    def from_stream(cls, f):
        magic, version, count = header_struct.read(f)

        if magic != b"YSLB":
            raise Exception(f"bad YSLB magic, got {magic}")

        f.seek(1024, 1)  # crc first-byte index

        labels = []

        for _ in range(count):
            name_len = ord(f.read(1))
            name = f.read(name_len).decode("cp932")
            _, offset, yst_index = label_struct.read(f)

            label = Label(name, offset, yst_index)
            labels.append(label)

        return cls(labels)

    def to_stream(self, f):
        header_struct.write(f, b"YSLB", 454, len(self.labels))

        sorted_labels = sorted(self.labels, key=lambda x: x.name_hash)
        bucket_sizes = collections.Counter(x.name_hash >> 24 for x in sorted_labels)
        search_table = itertools.accumulate(bucket_sizes[x - 1] for x in range(256))

        for x in search_table:
            f.write(x.to_bytes(4, byteorder="little"))

        for label in sorted_labels:
            name = label.name_encoded
            f.write(bytes((len(name), *name)))
            label_struct.write(f, label.name_hash, label.offset, label.yst_index)
