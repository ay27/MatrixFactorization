# Created by ay27 at 16/3/19
import hashlib

import numpy as np

from ps import g
import copy


class VectorClock:
    """
    标准的向量时钟实现.
    combined函数: 将两个向量时钟按照对应时钟最大值进行合并, 结果存在本时钟内
    tick函数: 使某个时钟滴答走一步
    scope函数: 得到该向量最大值与最小值的差距
    """

    def __init__(self, clocks=None):
        if clocks is None:
            self._clock = np.array([0 for _ in range(g.client_num)])
        else:
            tmp = copy.deepcopy(clocks)
            self._clock = np.array(tmp)
        # self.min_v = 1234567890

    def combined(self, v):
        if len(v) != len(self._clock):
            raise AttributeError('can not combined, length is not equal')
        for ii in range(len(v)):
            self._clock[ii] = max(self._clock[ii], v[ii])
        # self._check()

    def tick(self, rank):
        self._clock[rank] += 1
        # self._check()

    def __len__(self):
        return len(self._clock)

    @property
    def min(self):
        minv = 123456789
        for v in self._clock:
            minv = min(minv, v)
        return minv
        # return self.min_v

    # def _check(self):
    #     for v in self._clock:
    #         if v < self.min_v:
    #             self.min_v = v

    def __getitem__(self, key):
        return self._clock[key]

    def __str__(self):
        return str(self._clock)


class NetPack:
    def __init__(self, cmd, key, value, vc, src, dest, tag):
        self.cmd = cmd
        self.key = key
        self.value = value
        self.vc = vc
        self.src = src
        self.dest = dest
        self.tag = tag
