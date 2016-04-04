# Created by ay27 at 16/3/30
import numpy
from mpi4py import MPI

from Client import Client

f = open('log/mf.log', 'w')


def log(msg):
    f.write('%s\n' % msg)


def d_mf(comm, wk_comm, local_data, local_P, k, steps=500, alpha=0.0002, beta=0.02):
    zeros = numpy.zeros(k)
    client = Client(comm, wk_comm)
    client.start()
    my_rank = comm.Get_rank()
    for row in local_data:
        client.inc(my_rank, row[1] - 1, zeros)
    local_Q = dict()
    e = 0
    for step in range(steps):
        print('rank %d, iter=%d' % (my_rank, step))
        client.clock(my_rank, e)
        local_Q.clear()
        for row in local_data:
            # 需要减去偏移值
            ii = int(row[0] - local_data[0][0])
            jj = int(row[1] - 1)
            value = float(row[2])
            q = local_Q.get(jj)
            if q is None:
                q = local_Q[jj] = client.pull(my_rank, jj)
            log('%d %d %f %s' % (ii, jj, value, str(q)))
            eij = value - numpy.dot(local_P[ii], q)
            local_P[ii] += alpha * (2 * eij * q - beta * local_P[ii])
        for row in local_data:
            ii = int(row[0] - local_data[0][0])
            jj = int(row[1] - 1)
            value = float(row[2])
            q = local_Q.get(jj)
            eij = value - numpy.dot(local_P[ii], q)
            client.inc(my_rank, jj, alpha * (2 * eij * local_P[ii] - beta * q))

        e = 0.0
        for row in local_data:
            ii = row[0] - local_data[0][0]
            jj = row[1] - 1
            value = row[2]
            if abs(value - 0.0) > 0.000001:
                e += pow(numpy.dot(local_P[ii], local_Q[jj]) - value, 2)
    client.stop(my_rank)
    MPI.Finalize()
    return
