# Created by ay27 at 16/3/17
import copy
import multiprocessing as mp
import hashlib
from random import randint

from mpi4py import MPI
import numpy as np

from ps import g
from ps.util import pack, VectorClock


def find_road(key):
    return int(hashlib.md5(str(key).encode()).hexdigest(), 16) % g.ps_num + g.client_num


def gen_tag():
    return randint(1, 102400)


class Cache:
    def __init__(self):
        self.store = dict()

    def insert(self, key, value, vc):
        self.store[key] = (value, vc)

    def query(self, key):
        return self.store.get(key)


class Client:
    def __init__(self, comm, wk_comm):
        self.comm = comm
        self.wk_comm = wk_comm
        self.cache = Cache()
        self.log_file = open('../log/log_C%d.txt' % comm.Get_rank(), 'w')

    def pull(self, rank, key):
        self.log('pull %d %d' % (rank, key))
        dest = find_road(key)
        tag = gen_tag()
        self.comm.send(obj=pack(g.CMD_PULL, key, rank, dest, tag), dest=dest, tag=tag)
        self.comm.Send([VectorClock().inner, MPI.INT], dest=dest, tag=tag+1)
        value_buf = np.empty(g.K, dtype=float)
        vc_buf = np.empty(g.client_num, dtype=int)
        self.comm.Recv(value_buf, source=dest, tag=tag)
        self.comm.Recv(vc_buf, source=dest, tag=tag+1)
        return value_buf

    def inc(self, rank, key, value):
        self.log('inc %d %d %s' % (rank, key, str(value)))
        dest = find_road(key)
        tag = gen_tag()
        self.comm.send(obj=pack(g.CMD_INC, key, rank, dest, tag), dest=dest, tag=tag)
        self.comm.Send([value, MPI.FLOAT], dest=dest, tag=tag + 1)
        self.comm.Send([VectorClock().inner, MPI.INT], dest=dest, tag=tag+2)

    def clock(self, rank, expt):
        self.log('clock %d %f' % (rank, expt))
        dest = g.EXPT_MACHINE
        tag = rank
        self.comm.send(obj=pack(g.CMD_EXPT, expt, rank, 0, tag), dest=dest, tag=tag)
        self.wk_comm.barrier()

    def stop(self, rank):
        self.log('stop %d' % rank)
        dest = g.EXPT_MACHINE
        tag = rank
        self.comm.send(obj=pack(g.CMD_STOP, None, rank, dest, tag), dest=dest, tag=tag)

    def log(self, msg):
        self.log_file.write('%s\n' % msg)
