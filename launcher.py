# Created by ay27 at 16/3/17
import csv

import numpy as np
from mpi4py import MPI
from MF import d_mf

from Server import Server
import g


def load_data(rank):
    with open('data/9x9_3blocks') as file:
        for ii in range(rank * 27):
            file.readline()
        tmp = []
        for ii in range(27):
            row = file.readline().split()
            tmp.append([int(row[0]), int(row[1]), float(row[2])])
    return tmp
    # with open('data/output1/data_%d.csv' % rank) as file:
    #     tmp = []
    #     reader = csv.reader(file)
    #     for row in reader:
    #         tmp.append([int(float(row[0])), int(float(row[1])), int(float(row[2]))])
    # return tmp


if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    group = comm.group
    # make a group for ps
    ps_group = group.Range_excl([(0, g.client_num - 1, 1)])
    ps_comm = comm.Create(ps_group)
    ps_group.Free()
    # make a group for worker
    wk_group = group.Range_incl([(0, g.client_num - 1, 1)])
    wk_comm = comm.Create(wk_group)
    wk_group.Free()

    print('rank = %d' % rank)
    print('g.client_num = %d' % g.client_num)
    o_t = MPI.Wtime()
    if rank >= g.client_num:
        print('server')
        ser = Server(comm, ps_comm)
    else:
        print('client')
        local_data = load_data(rank)
        o_t = MPI.Wtime()
        d_mf(comm, wk_comm, local_data, np.random.rand(len(local_data), g.K), g.K, 500, 0.002, 0.02)
    print('finish %d, elapsed time = %f' % (rank, MPI.Wtime() - o_t))
