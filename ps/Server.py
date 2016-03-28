# Created by ay27 at 16/3/17

import multiprocessing as mp
from mpi4py import MPI
from ps import g
from ps.util import NetPack


class Store:
    class Row:
        def __init__(self, key, value, vc):
            self.key = key
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
        self.queue = dict()

    def insert(self, key, pack, st):
        self.queue[key] = (pack, st)

    def remove(self, key):
        self.queue.pop(key)

    def get(self, key):
        return self.queue.get(key)


class Server:
    def __init__(self, comm):
        self.log_file = open('log_S%d.log' % comm.Get_rank(), 'w')
        self.log('server init')
        self.comm = comm
        self.store = Store()
        self.query = QueryQueue()
        self.my_rank = self.comm.Get_rank()
        if self.my_rank == g.EXPT_MACHINE:
            self.expt = dict()
        self.status = [True for _ in range(g.client_num)]
        self.STOP = False
        self.log('init finish')
        self.run()

    def run(self):
        self.log('server run')
        self.log(self.STOP)
        while not self.STOP:
            self.log('server waiting')
            st = MPI.Status()
            pack = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=st)
            self.log('%d recv %d %d %s' % (self.my_rank, st.source, st.tag, pack.cmd))
            if not isinstance(pack, NetPack):
                continue
            if pack.cmd == g.CMD_INC:
                self._do_inc(pack)
            elif pack.cmd == g.CMD_PULL:
                self._do_pull(pack, st)
            elif pack.cmd == g.CMD_EXPT:
                self._do_expt(pack)
            elif pack.cmd == g.CMD_STOP:
                self._do_stop(pack)
            else:
                continue

    def scan_query(self, new_pack):
        pair = self.query.get(new_pack.key)
        if pair is None:
            return
        o_pack, st = pair
        vc = self.store.get(new_pack.key).vc
        if abs(o_pack.vc[o_pack.src] - vc.min) > g.STALE:
            return
        r_pack = NetPack(o_pack.cmd, o_pack.key, new_pack.value, vc, o_pack.src, o_pack.dest, o_pack.tag)
        self.comm.isend(r_pack, dest=st.source, tag=st.tag)

    def _do_inc(self, pack):
        self.store.inc(pack.key, pack.value, pack.vc)
        self.scan_query(pack)

    def _do_pull(self, pack, st):
        row = self.store.get(pack.key)
        if row is None:
            self.query.insert(pack.key, pack, st)
        else:
            r_pack = NetPack(pack.cmd, pack.key, row.value, row.vc, pack.src, pack.dest, pack.tag)
            self.comm.isend(r_pack, dest=st.source, tag=st.tag)

    def _do_expt(self, pack):
        src = pack.src
        value = pack.value
        row = self.expt.get(src)
        if row is None:
            self.expt[src] = [value]
        else:
            self.expt[src].append(value)

    def _do_stop(self, pack):
        src = pack.src
        self.status[src] = False
        for ii in range(g.client_num):
            if self.status[ii]:
                return
        self.write_result()
        self.STOP = True

    def write_result(self):
        for jj in range(1, len(self.expt[0])):
            self.expt[0] += self.expt[jj]
        f = open('result.txt', 'w')
        f.write(str(self.expt[0]))

    def log(self, msg):
        # print('server %s' % msg)
        self.log_file.write('%s\n' % msg)
