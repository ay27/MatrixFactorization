# Created by ay27 at 16/3/14
import copy
import time
import unittest

import matplotlib.pyplot as plt
import numpy as np


def load_data():
    with open('../data/9x9_3blocks') as file:
        tmp = []
        for line in file:
            words = line.split()
            tmp.append([int(words[0]), int(words[1]), float(words[2])])
    return tmp


log_file = open('../log/naive_result.txt', 'w')


def log(msg):
    log_file.write('%s\n' % msg)


def EuclideanDistance(A, B):
    if isinstance(A, float) or isinstance(A, int):
        return pow(A - B, 2)
    if A.shape != B.shape:
        raise AttributeError('shape of A is not equal to B')
    shape = A.shape
    sum = 0
    for ii in range(shape[0]):
        for jj in range(shape[1]):
            sum += pow(A[ii][jj] - B[ii][jj], 2)
    return sum


class MyTestCase(unittest.TestCase):
    def test_naive_mf(self):
        from learn import naive_mf
        N = 50
        M = 100
        K = 20
        steps = 200
        RR = np.random.rand(N, M) * 10
        PP = np.random.rand(N, K)
        QQ = np.random.rand(K, M)
        st = time.time()
        nP, nQ, ee1 = naive_mf.naive_mf(copy.deepcopy(RR), copy.deepcopy(PP), copy.deepcopy(QQ), K, steps=steps)
        print('ok1')
        nP, nQ, ee2 = naive_mf.naive_mf1(RR, PP, QQ, K, steps=steps)
        plt.plot(list(range(len(ee1))), ee1, 'r-')
        plt.plot(list(range(len(ee2))), ee2, 'b*')
        plt.show()
        nR = np.dot(nP, nQ)
        print('naive mf: steps = %d, time = %f' % (steps, time.time() - st))
        # print(EuclideanDistance(R, nR))

    def test_sparse_mf(self):
        from learn import naive_mf
        sparse_R = load_data()
        N = 9
        M = 9
        K = 4
        steps = 5000
        P = np.random.rand(N, K)
        Q = np.random.rand(K, M)
        st = time.time()
        nP, nQ = naive_mf.naive_sparse_mf(log, sparse_R, P, Q, K, steps, 0.002, 0.02)
        nR = np.dot(nP, nQ)
        log('naive sparse mf: steps = %d, time = %f' % (steps, time.time() - st))


if __name__ == '__main__':
    unittest.main()
