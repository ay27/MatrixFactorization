# Created by ay27 at 16/3/17

import multiprocessing as mp
from mpi4py import MPI
from ps import g
from ps.util import NetPack


class Store:
    class Row:
        def __init__(self, key, value, vc):
            self.key= key
            self.value = value
            self.vc = vc

    def __init__(self):
        self._store = dict()

    def get(self, key):
        return self._store.get(key)

    def inc(self, key, value, vc):
        row = self._store.get(key)
        if row is None:
            self._store[key] = self.Row(key, value, vc)
        else:
            row.value += value
            row.vc.combined(vc)


class QueryQueue:
    def __init__(self):
        self.queue = list()

    def insert(self, pack_st):
        self.queue.append(pack_st)

    def remove(self, pack_st):
        self.queue.remove(pack_st)

    def __iter__(self):
        return iter(self.queue)


class Server(mp.Process):
    def __init__(self, comm):
        super().__init__()
        self.comm = comm
        self.store = Store()
        self.query = QueryQueue()

    def run(self):
        while True:
            st = MPI.Status()
            pack = self.comm.Recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=st)
            if not isinstance(pack, NetPack):
                continue
            if pack.cmd == g.CMD_INC:
                self.store.inc(pack.key, pack.value, pack.vc)
            elif pack.cmd == g.CMD_PULL:
                row = self.store.get(pack.key)
                if row is None:
                    self.query.insert((pack, st))
                else:
                    r_pack = NetPack(pack.cmd, pack.key, row.value, row.vc, pack.src, pack.dest, pack.tag)
                    self.comm.Send(r_pack, dest=st.source, tag=st.tag)
            else:
                continue
