# Created by ay27 at 16/3/17
import multiprocessing as mp
import hashlib

from ps import g


class Client(mp.Process):
    """
    cache 格式:[ts, key, data], ts是int型时间戳, key是str型键
    cache是一个环装结构,当cache满后,从头开始写.因为ts的关系,cache是以ts递增保存的,故查找时只需沿一个方向扫描即可
    client与server通信格式:(cmd, ts, key[, data]), cmd是push或pull, ts是时间戳, key是键, data可选(当cmd==push时必选)
    """

    __magic_num = 3454756789

    def __init__(self, comm, ps_num, stale=1, cache_size=1024 * 1000):
        super().__init__()
        self.comm = comm
        self.ps_num = ps_num
        self.stale = stale
        self.cache_sz = cache_size
        # ts默认值设置为一个很小的负数,避免在cache查找时判断错误
        self.cache = list(map(lambda x: [-12345678, 0, 0], range(cache_size)))
        self.cache_flag = 0
        self.route_map = dict()
        self.left_p, self.right_p = mp.Pipe()

    # 根据key的md5值划分服务器, 相同的key总能分配到同一个服务器
    # TODO 需要测试这种划分方式是否均衡
    def _find_route(self, key):
        dest = self.route_map.get(key)
        if dest is None:
            dest = int(hashlib.md5(key.encode()).hexdigest(), 16) % self.ps_num
            self.route_map[key] = dest
        return dest

    def pull(self, ts, key):
        self.left_p.send('%s %d %s' % (g.CMD_PULL, ts, key))
        return self.left_p.recv()

    def inc(self, ts, key, value):
        self.left_p.send('%s %d %s' % (g.CMD_INC, ts, key))
        self.left_p.send(value)

    def clock(self, source_rank, ):

    # 同一个ts和key应该总能生成同一个tag
    def _gen_tag(self, ts, key):
        return int(hashlib.md5(('%d%s' % (ts, key)).encode()).hexdigest(), 16) % Client.__magic_num

    def run(self):
        while True:
            cmd, ts, key = self.right_p.recv().split()
            dest = self._find_route(key)
            tag = self._gen_tag(ts, key)
            if cmd == g.CMD_PULL:
                ii = self.cache_flag
                while self.cache[ii][0] >= ts - self.stale and self.cache[ii][1] != key:
                    ii -= 1
                    if ii == -1:
                        ii = self.cache_sz - 1
                if self.cache[ii][0] < ts - self.stale:
                    self.comm.Send((cmd, [ts, key]), dest=dest, tag=tag)
                    r_ts, r_key, r_data = self.comm.Recv(source=dest, tag=tag)
                    self.right_p.send(r_data)
                    self.cache_it(r_ts, r_key, r_data)
                    continue
                # cache命中
                if self.cache[ii][1] == key:
                    self.right_p.send(self.cache[ii][2])
                    continue
            elif cmd == g.CMD_INC:
                data = self.right_p.recv()
                self.comm.Send((cmd, [ts, key, data]), dest=dest, tag=tag)
                # cache it
                self.cache_it(ts, key, data)
            else:
                raise AttributeError('cmd must be inc or pull')

    def cache_it(self, ts, key, data):
        self.cache[self.cache_flag] = [ts, key, data]
        self.cache_flag += 1
        # cache是一个环
        if self.cache_flag == self.cache_sz:
            self.cache_flag = 0
