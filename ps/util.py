import numpy as np
from ps import g
import copy


def pack(cmd, key, src, dest, tag):
    return {
        'cmd': cmd,
        'key': key,
        'src': src,
        'dest': dest,
        'tag': tag
    }


class Unpack:
    def __init__(self, pack, value=None, vc=None):
        if isinstance(pack, dict):
            self.cmd = pack.get('cmd')
            self.key = pack.get('key')
            self.src = pack.get('src')
            self.dest = pack.get('dest')
            self.tag = pack.get('tag')
            self.value = value
            self.vc = vc


class VectorClock:
    def __init__(self, clock=None):
        if clock is None:
            self.clock = np.zeros(g.client_num)
        else:
            self.clock = np.array(copy.deepcopy(clock))

    def tick(self, rank):
        self.clock[rank] += 1

    def __getitem__(self, item):
        return self.clock[item]

    def __setitem__(self, key, value):
        self.clock[key] = value

    def get_min(self):
        return min(self.clock)

    @property
    def inner(self):
        return self.clock


def merge(vc1, vc2):
    if isinstance(vc1, VectorClock) and isinstance(vc2, VectorClock):
        return VectorClock(vc1.inner + vc2.inner)


class Store:
    class __row:
        def __init__(self, value, vc):
            self.value = value
            self.vc = vc

    def __init__(self):
        self.store = dict()

    def insert(self, key, value, vc):
        self.store[key] = Store.__row(value, vc)

    def query(self, key):
        return self.store.get(key)

