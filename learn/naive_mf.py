# Created by ay27 at 16/3/14
import numpy


def naive_mf(R, P, Q, K, steps=500, alpha=0.0002, beta=0.02):
    # transform Q for calculate convenience
    Q = Q.T
    ee = []
    for step in range(steps):
        print(step)
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - numpy.dot(P[i, :], Q[j, :])
                    P[i] += alpha * (2 * eij * Q[j] - beta * P[i])
                    Q[j] += alpha * (2 * eij * P[i] - beta * Q[j])
                    # for k in range(K):
                    #     P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                    #     Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
                    # eR = numpy.dot(P, Q.T)

        # for i in range(len(R)):
        #     for j in range(len(R[i])):
        #         if R[i][j] > 0:
        #             eij = R[i][j] - numpy.dot(P[i, :], Q[j, :])
        #             Q[j] += alpha * (2 * eij * P[i] - beta * Q[j])
        e = 0
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    e += pow(R[i][j] - numpy.dot(P[i, :], Q[j, :]), 2)
                    # for k in range(K):
                    #     e += (beta / 2) * (pow(P[i][k], 2) + pow(Q[j][k], 2))
                    # print(e)
        ee.append(e)
        if e < 0.001:
            break
    return P, Q.T, ee


def naive_sparse_mf(log, sparse_R, P, Q, K, steps=500, alpha=0.0002, beta=0.02):
    Q = Q.T
    for step in range(steps):
        for row in sparse_R:
            ii = row[0]-1
            jj = row[1]-1
            value = row[2]
            eij = value - numpy.dot(P[ii, :], Q[jj, :])
            P[ii] += alpha * (2 * eij * Q[jj] - beta * P[ii])
            Q[jj] += alpha * (2 * eij * P[ii] - beta * Q[jj])
        e = 0
        for row in sparse_R:
            if abs(row[2] - 0.0) > 0.00001:
                e += pow(row[2] - numpy.dot(P[row[0]-1, :], Q[row[1]-1, :]), 2)
        log(e)
        if e < 0.001:
            break
    return P, Q.T


def naive_mf1(R, P, Q, K, steps=500, alpha=0.0002, beta=0.02):
    # transform Q for calculate convenience
    Q = Q.T
    ee = []
    for step in range(steps):
        print(step)
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - numpy.dot(P[i, :], Q[j, :])
                    P[i] += alpha * (2 * eij * Q[j] - beta * P[i])
                    # Q[j] += alpha * (2 * eij * P[i] - beta * Q[j])
                    # for k in range(K):
                    #     P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                    #     Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
                    # eR = numpy.dot(P, Q.T)

        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - numpy.dot(P[i, :], Q[j, :])
                    Q[j] += alpha * (2 * eij * P[i] - beta * Q[j])
        e = 0
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    e += pow(R[i][j] - numpy.dot(P[i, :], Q[j, :]), 2)
                    # for k in range(K):
                    #     e += (beta / 2) * (pow(P[i][k], 2) + pow(Q[j][k], 2))
                    # print(e)
        ee.append(e)
        if e < 0.001:
            break
    return P, Q.T, ee
