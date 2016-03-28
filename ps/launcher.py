# Created by ay27 at 16/3/17

# TODO load data, start mpi machine
import csv

from mpi4py import MPI
from ps import g
from ps.Client import Client
from ps.Server import Server
from ps.MF import d_mf
import numpy as np


def load_data(rank):
    with open('../data/output1/data_%d.csv' % rank) as file:
        tmp = []
        reader = csv.reader(file)
        for row in reader:
            tmp.append([int(float(row[0])), int(float(row[1])), int(float(row[2]))])
    return tmp


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

    if rank >= g.client_num:
        ser = Server(comm)
    else:
        local_data = load_data(rank)
        d_mf(comm, local_data, np.zeros((local_data[-1][0], g.K)), g.K, 10)
