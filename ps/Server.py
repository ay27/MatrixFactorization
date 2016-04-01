# Created by ay27 at 16/3/17

import multiprocessing as mp
from mpi4py import MPI
import numpy as np

from ps import g
from ps import util
from ps.util import VectorClock, Store


class QueryQueue:
    def __init__(self):
        self.queue = dict()

    def insert(self, key, pack, st):
        self.queue[key] = (pack, st)

    def remove(self, key):
        self.queue.pop(key)

    def get(self, key):
        return self.queue.get(key)

    def inner(self):
        return self.queue


class Server:
    def __init__(self, comm, ps_comm):
        self.log_file = open('../log/log_S%d.log' % comm.Get_rank(), 'w')
        self.log('server init')
        self.comm = comm
        self.ps_comm = ps_comm
        self.store = Store()
        self.query = QueryQueue()
        self.my_rank = self.comm.Get_rank()
        if self.my_rank == g.EXPT_MACHINE:
            self.expt = dict()
        self.status = [True for _ in range(g.client_num)]
        self.STOP = False
        self.log('init finish')
        self.clocks = VectorClock()
        self.run()

    def run(self):
        self.log('server run')
        self.log(self.STOP)
        while not self.STOP:
            # self.log('server waiting')
            st = MPI.Status()
            pack = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=st)
            if not isinstance(pack, dict):
                if pack == g.CMD_STOP_THE_WORLD:
                    print('stop the world %d' % self.my_rank)
                    break
            if pack.get('cmd') == g.CMD_INC:
                value_buf = np.empty(g.K, dtype=float)
                self.comm.Recv(value_buf, source=st.source, tag=st.tag + 1)
                self._do_inc(util.Unpack(pack, value_buf))

            elif pack.get('cmd') == g.CMD_PULL:
                self._do_pull(util.Unpack(pack), st)

            elif pack.get('cmd') == g.CMD_EXPT:
                vc_buf = np.empty(g.client_num, dtype=int)
                self.comm.Recv(vc_buf, source=st.source, tag=st.tag+1)
                self._do_expt(util.Unpack(pack, None, VectorClock(vc_buf)))

            elif pack.get('cmd') == g.CMD_STOP:
                self._do_stop(util.Unpack(pack))
            else:
                continue
        MPI.Finalize()

    def _do_inc(self, pack):
        value = self.store.get(pack.key)
        if value is None:
            self.store[pack.key] = pack.value
        else:
            self.store[pack.key] = pack.value + value

    def _do_pull(self, pack, st):
        if self.clocks[pack.src] - self.clocks.get_min() > g.STALE:
            print('block %d' % pack.src)
            self.query.insert(pack.key, pack, st)
            return
        value = self.store.get(pack.key)
        self.comm.Send([value, MPI.FLOAT], dest=st.source, tag=st.tag)
        self.comm.Send([self.clocks.inner, MPI.INT], dest=st.source, tag=st.tag + 1)

    def _do_expt(self, pack):
        src = pack.src
        value = pack.key
        row = self.expt.get(src)
        # print('expt %d %f' % (src, value))
        if row is None:
            self.expt[src] = [value]
        else:
            self.expt[src].append(value)
        # update server clocks
        self.clocks = util.merge(self.clocks, pack.vc)
        self.scan_query()

    def _do_stop(self, pack):
        src = pack.src
        self.status[src] = False
        for ii in range(g.client_num):
            if self.status[ii]:
                return
        self.write_result()
        for ii in range(g.client_num, g.client_num + g.ps_num):
            self.comm.send(g.CMD_STOP_THE_WORLD, dest=ii, tag=ii)

    def write_result(self):
        print('write result')
        self.expt[0] = np.array(self.expt[0])
        for jj in range(1, g.client_num):
            self.expt[0] += np.array(self.expt[jj])
        f = open('../log/result%d.txt' % self.my_rank, 'w')
        f.write(str(self.expt[0]))

    def log(self, msg):
        # print('server %s' % msg)
        self.log_file.write('%s\n' % msg)

    def scan_query(self):
        for key, (pack, st) in list(self.query.inner().items()):
            if self.clocks[pack.src] - self.clocks.get_min() <= g.STALE:
                print('waitup %d' % pack.src)
                value = self.store.get(pack.key)
                self.comm.Send([value, MPI.FLOAT], dest=st.source, tag=st.tag)
                self.comm.Send([self.clocks.inner, MPI.INT], dest=st.source, tag=st.tag + 1)

                self.query.remove(key)
