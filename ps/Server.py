# Created by ay27 at 16/3/17

import multiprocessing as mp
from mpi4py import MPI
from ps import g
from ps.util import NetPack


class Server(mp.Process):
    # store size default == 16GB
    def __init__(self, comm):
        super().__init__()
        self.comm = comm

    def run(self):
        while True:
            st = MPI.Status()
            pack = self.comm.Recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=st)
            if not isinstance(pack, NetPack):
                continue
            if pack.cmd == g.CMD_INC:



    def update(self, ts, key, data):
        pass
