# Created by ay27 at 16/3/17
import hashlib
import multiprocessing as mp
from random import randint

import numpy as np
from mpi4py import MPI

import util
import g
from util import pack, VectorClock, Store


def find_road(key):
    return int(hashlib.md5(str(key).encode()).hexdigest(), 16) % g.ps_num + g.client_num


def gen_tag():
    return randint(1, 102400)


class Client(mp.Process):
    def __init__(self, comm, wk_comm):
        super().__init__()
        self.comm = comm
        self.wk_comm = wk_comm
        self.cache = Store()
        self.inner, self.outer = mp.Pipe()

    ####################################################################################################################
    # outer process
    def pull(self, rank, key):
        self.outer.send((g.CMD_PULL, rank, key))
        value = self.outer.recv()
        return value

    def inc(self, rank, key, value):
        self.outer.send((g.CMD_INC, rank, key, value))

    def clock(self, rank, expt):
        self.outer.send((g.CMD_CLOCK, rank, expt))

    def stop(self, rank):
        self.outer.send((g.CMD_STOP, rank))

    ####################################################################################################################

    def run(self):
        self.log_file = open('log/log_c%d.txt' % self.comm.Get_rank(), 'w')
        self.clock = VectorClock()
        while True:
            msg = self.inner.recv()
            if msg[0] == g.CMD_PULL:
                msg, rank, key = msg

                self.do_pull(rank, key)

            elif msg[0] == g.CMD_INC:
                cmd, rank, key, value = msg
                self.do_inc(rank, key, value)

            elif msg[0] == g.CMD_CLOCK:
                cmd, rank, expt = msg
                self.clock.tick(rank)
                self.do_clock(rank, expt)

            elif msg[0] == g.CMD_STOP:
                cmd, rank = msg
                self.do_stop(rank)
                break

    def log(self, msg):
        if self.log_file is None:
            return
        self.log_file.write('%s\n' % msg)

    def do_pull(self, rank, key):
        self.log('pull %d %d' % (rank, key))
        # read cache
        value = self.cache.get(key)
        if self.check_consistency(rank):
            if value is not None:
                self.inner.send(value)
                return
            else:
                tmp = np.zeros(g.K, dtype=np.float64)
                self.cache[key] = tmp
                self.inner.send(tmp)
                return

        dest = find_road(key)
        tag = gen_tag()
        self.comm.send(obj=pack(g.CMD_PULL, key, rank, dest, tag), dest=dest, tag=tag)
        value_buf = np.empty(g.K, dtype=np.float64)
        vc_buf = np.empty(g.client_num, dtype=np.int32)
        self.comm.Recv(value_buf, source=dest, tag=tag)
        self.comm.Recv(vc_buf, source=dest, tag=tag + 1)
        self.log('recv vc %s' % str(vc_buf))

        # cache it and update local clocks
        self.cache[key] = value_buf
        self.clock = util.merge(self.clock, vc_buf)
        self.log('local clocks %s' % str(self.clock.inner))
        self.inner.send(value_buf)

    def do_inc(self, rank, key, value):
        self.log('inc %d %d %s' % (rank, key, str(value)))
        # update cache
        v = self.cache.get(key)
        if v is None:
            self.cache[key] = value
        else:
            self.cache[key] += value

        dest = find_road(key)
        tag = gen_tag()
        self.comm.send(obj=pack(g.CMD_INC, key, rank, dest, tag), dest=dest, tag=tag)
        self.comm.Send([value, MPI.FLOAT], dest=dest, tag=tag + 1)

    def do_clock(self, rank, expt):
        self.log('clock %d %f' % (rank, expt))
        dest = g.EXPT_MACHINE
        tag = rank
        self.comm.send(obj=pack(g.CMD_EXPT, expt, rank, 0, tag), dest=dest, tag=tag)
        self.comm.Send([self.clock.inner, MPI.INT], dest=dest, tag=tag + 1)
        self.log('clock %s' % str(self.clock.inner))
        # self.wk_comm.barrier()

    def do_stop(self, rank):
        self.log('stop %d' % rank)
        dest = g.EXPT_MACHINE
        tag = rank
        self.comm.send(obj=pack(g.CMD_STOP, None, rank, dest, tag), dest=dest, tag=tag)

    def check_consistency(self, rank):
        return self.clock[rank] - self.clock.get_min() <= g.STALE
