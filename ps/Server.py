# Created by ay27 at 16/3/17

import multiprocessing as mp
from mpi4py import MPI

from ps import g


class QueryCache:
    def __init__(self):
        self.queue = []

    def add(self, ts, key, st):
        self.queue.append([ts, key, st, 0])

    def check(self):
        for row in self.queue:
            if row[3] != 0:
                return row
        return None

    def remove(self, row):
        try:
            self.queue.remove(row)
        except ValueError:
            pass

    def fill(self, ts, key, value):
        for row in self.queue:
            if row[0] == ts and row[1] == key:
                row[3] = value
                return
        raise ValueError('the ts=%d, key=%s is not in QueryCache' % (ts, key))


class DualKeyMap:
    def __init__(self):
        self.store = dict()

    def get(self, key1, key2):
        row = self.store.get(key1)
        if row is None:
            return None
        else:
            return row.get(key2)

    def add(self, key1, key2, value):
        row = self.store.get(key1)
        if row is None:
            self.store[key1] = dict()
            self.store[key1][key2] = value
        else:
            if row.get(key2) is None:
                self.store[key1][key2] = value
            else:
                self.store[key1][key2] += value


class Server(mp.Process):
    # store size default == 16GB
    def __init__(self, comm, store_size=16 * 1024 * 1024 * 1024):
        super().__init__()
        self.comm = comm
        self.store_sz = store_size
        self.queue = QueryCache()

    def run(self):
        while True:
            # client与server通信格式:(cmd, ts, key[, data]), cmd是push或pull, ts是时间戳, key是键, data可选(当cmd==push时必选)
            st = MPI.Status()
            cmd, ts, v = self.comm.Recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=st)
            if cmd == g.CMD_INC:
                key, data = v
                self.update(ts, key, data)
            elif cmd == g.CMD_PULL:
                key = v

    def update(self, ts, key, data):
        pass
