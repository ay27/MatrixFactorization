# Created by ay27 at 16/3/17
import multiprocessing as mp
import hashlib
from ps import g
import numpy as np

from ps.util import VectorClock, NetPack


class Cache:
    class Row:
        def __init__(self, key, value, vc):
            self.key = key
            self.vc = vc
            self.value = value

    def __init__(self):
        self._store = dict()
        self.not_flush = list()

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value, vc):
        self._store[key] = Cache.Row(key, value, vc)

    def inc(self, key, value, vc):
        _row = self._store.get(key)
        if _row is None:
            self._store[key] = Cache.Row(key, value, vc)
        else:
            self._store[key].value += value
        self.not_flush.append(key)

    def flush(self):
        self.not_flush.clear()


class RoadMap:
    def __init__(self):
        self._map = dict()

    def get(self, key):
        return self._map.get(key)

    def find_road(self, key):
        dest = self._map.get(key)
        if dest is None:
            dest = int(hashlib.md5(str(key).encode()).hexdigest(), 16) % g.ps_num
            self._map[key] = dest
        return dest


class Client(mp.Process):
    def __init__(self, comm):
        super().__init__()
        self.comm = comm
        self.cache = Cache()
        self.cache_tail = 0
        self.route_map = RoadMap()
        self.outer, self.inner = mp.Pipe()
        # 每一个worker的时钟
        self.clocks = np.array([0 for _ in range(g.client_num)])

    def pull(self, rank, key):
        self.outer.send((g.CMD_PULL, rank, key))
        g.log('pull %d %d' % (rank, key))
        return self.outer.recv()

    def inc(self, rank, key, value):
        self.outer.send((g.CMD_INC, rank, key))
        g.log('inc %d %d' % (rank, key))
        self.outer.send(value)

    def clock(self, rank, expt):
        self.clocks[rank] += 1
        self.outer.send((g.CMD_FLUSH, rank, 0))
        self.outer.send((g.CMD_EXPT, rank, expt))
        g.log('clock %d %f' % (rank, expt))

    def stop(self, rank):
        g.log('stop %d' % rank)
        self.outer.send((g.CMD_STOP, rank, 0))

    def run(self):
        while True:
            # key is string when arrive here
            cmd, rank, key = self.inner.recv()
            if cmd == g.CMD_PULL:
                self._do_pull(rank, key)
            elif cmd == g.CMD_INC:
                self._do_inc(rank, key)
            elif cmd == g.CMD_FLUSH:
                self._do_flush(rank)
            elif cmd == g.CMD_EXPT:
                self._do_expt(rank, key)
            elif cmd == g.CMD_STOP:
                self._do_stop(rank)
            else:
                raise AttributeError('cmd must be inc or pull')

    def _do_pull(self, rank, key):
        g.log('do pull %d %d' % (rank, key))
        row = self.cache.get(key)
        if row is None or row.vc[rank] - g.STALE > row.vc.min:
            value = self._remote_pull(rank, key)
            self.inner.send(value)
        else:
            self.inner.send(row.value)

    def _do_inc(self, rank, key):
        value = self.inner.recv()
        self.cache.inc(key, value, VectorClock(self.clocks))

    def _do_flush(self, rank):
        for key in self.cache.not_flush:
            self._remote_inc(rank, self.cache.get(key))
        self.cache.flush()

    def _do_expt(self, rank, expt):
        self._remote_expt(rank, expt)

    def _do_stop(self, rank):
        self._remote_stop(rank)

    def _remote_pull(self, rank, key, vc=None):
        dest = self.route_map.find_road(key)
        tag = self._gen_tag(rank, key)
        if vc is not None:
            g.log('remote pull %d %d %d %d %s' % (rank, key, dest, tag, vc))
        else:
            g.log('remote pull %d %d %d %d' % (rank, key, dest, tag))
        self.comm.Bsend(NetPack(g.CMD_PULL, key, None, vc, rank, dest, tag), dest=dest, tag=tag)
        pack = self.comm.recv(source=dest, tag=tag)
        # cache it
        self.cache.set(key, pack.value, pack.vc)
        return pack.value

    def _remote_inc(self, rank, cache_row):
        key = cache_row.key
        dest = self.route_map.find_road(key)
        tag = self._gen_tag(rank, key)
        g.log('remote inc %d %d %d %d %s' % (rank, key, dest, tag, cache_row.vc))
        self.comm.isend(obj=NetPack(g.CMD_INC, key, cache_row.value, cache_row.vc, rank, dest, tag), dest=dest, tag=tag)

    def _remote_expt(self, rank, expt):
        dest = g.EXPT_MACHINE
        tag = rank
        g.log('remote expt %d %d %d %f' % (rank, dest, tag, expt))
        self.comm.isend(obj=NetPack(g.CMD_EXPT, None, expt, None, rank, 0, tag), dest=dest, tag=tag)

    def _remote_stop(self, rank):
        dest = g.EXPT_MACHINE
        tag = rank
        g.log('remote stop %d %d %d' % (rank, dest, tag))
        self.comm.isend(obj=NetPack(g.CMD_STOP, None, None, None, rank, dest, tag), dest=dest, tag=tag)

    __magic_num = 34547567

    @staticmethod
    def _gen_tag(rank, key):
        return int(hashlib.md5(('%d%s' % (rank, key)).encode()).hexdigest(), 16) % Client.__magic_num
