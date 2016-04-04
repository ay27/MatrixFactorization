import numpy as np

import g


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
            self.clock = np.zeros(g.client_num, dtype=np.int32)
        else:
            self.clock = np.array(clock)

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
    if isinstance(vc1, VectorClock):
        tmp1 = vc1.inner
    else:
        tmp1 = vc1
    if isinstance(vc2, VectorClock):
        tmp2 = vc2.inner
    else:
        tmp2 = vc2
    tmp = VectorClock()
    for ii in range(len(tmp1)):
        tmp[ii] = max(tmp1[ii], tmp2[ii])
    return tmp


class Store(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

