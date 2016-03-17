# Created by ay27 at 16/3/17
import multiprocessing as mp
import hashlib


class NetWork(mp.Process):
    """
    cache 格式:[ts, key, data], ts是int型时间戳, key是str型键
    client与server通信格式:(cmd, ts, key[, data]), cmd是push或pull, ts是时间戳, key是键, data可选(当cmd==push时必选)
    """

    __magic_num = 3454756789

    def __init__(self, comm, ps_num, stale=1, cache_size=1024 * 1000, route_map_size=1024 * 1000):
        super().__init__()
        self.comm = comm
        self.ps_num = ps_num
        self.stale = stale
        self.cache_sz = cache_size
        self.route_map_ze = route_map_size
        manager = mp.Manager()
        self.cache = manager.list(range(cache_size))
        self.cache_flag = 0
        self.route_map = manager.dict()
        self.left_p, self.right_p = mp.Pipe()
        NetWork._pipe = mp.Pipe()

    def _find_route(self, key):
        dest = self.route_map.get(key)
        if dest is None:
            dest = int(hashlib.md5(key.encode()).hexdigest(), 16) % self.ps_num
            self.route_map[key] = dest
        return dest

    def pull(self, ts, key):
        self.left_p.send('pull %d %s' % (ts, key))
        return self.left_p.recv()

    def push(self, ts, key, value):
        self.left_p.send('push %d %s' % (ts, key))
        self.left_p.send(value)

    def _gen_tag(self, ts, key):
        return int(hashlib.md5(('%d%s' % (ts, key)).encode()).hexdigest(), 16) % NetWork.__magic_num

    def run(self):
        while True:
            cmd, ts, key = self.right_p.recv().split()
            dest = self._find_route(key)
            tag = self._gen_tag(ts, key)
            if cmd == 'pull':
                ii = self.cache_flag
                while ii >= 0 and self.cache[ii][0] >= ts - self.stale and self.cache[ii][1] != key:
                    ii -= 1
                if ii < 0 or self.cache[ii][0] < ts - self.stale:
                    self.comm.send((cmd, [ts, key]), dest=dest, tag=tag)
                    r_ts, r_key, r_data = self.comm.recv(source=dest, tag=tag)
                    self.right_p.send(r_data)
                    # cache it
                    self.cache[self.cache_flag] = [r_ts, r_key, r_data]
                    continue
                # cache命中
                if self.cache[ii][1] == key:
                    self.right_p.send(self.cache[ii][2])
                    continue
            elif cmd == 'push':
                data = self.right_p.recv()
                self.comm.send((cmd, [ts, key, data]), dest=dest, tag=tag)
