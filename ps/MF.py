# Created by ay27 at 16/3/22
import numpy
from ps.Client import Client


def d_mf(comm, client, my_rank, local_data, local_P, k, steps=500, alpha=0.0002, beta=0.02):
    zeros = numpy.zeros(k)
    for row in local_data:
        client.inc(my_rank, row[1]-1, zeros)
    local_Q = dict()
    e = 0
    for step in range(steps):
        client.clock(my_rank, e)
        local_Q.clear()
        for row in local_data:
            ii = row[0]-1
            jj = row[1]-1
            value = row[2]
            q = local_Q.get(jj)
            if q is None:
                q = local_Q[jj] = client.pull(my_rank, jj)
            eij = value - numpy.dot(local_P[ii, :], q)
            local_P[ii] += alpha * (2 * eij * q - beta * local_P[ii])
            client.inc(my_rank, jj, alpha * (2 * eij * local_P[ii] - beta * q))
        e = 0
        for row in local_data:
            q = local_Q.get(row[1]-1)
            e += pow(row[2] - numpy.dot(local_P[row[0] - 1, :], q), 2)
    return
