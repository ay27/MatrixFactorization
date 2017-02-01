# Created by ay27 at 16/3/14
import copy
import time
import unittest

import matplotlib.pyplot as plt
import numpy as np


def EuclideanDistance(A, B):
    if isinstance(A, float) or isinstance(A, int):
        return pow(A-B, 2)
    if A.shape != B.shape:
        raise AttributeError('shape of A is not equal to B')
    shape = A.shape
    sum = 0
    for ii in range(shape[0]):
        for jj in range(shape[1]):
            sum += pow(A[ii][jj]-B[ii][jj], 2)
    return sum


class MyTestCase(unittest.TestCase):
    def test_naive_mf(self):
        from learn import naive_mf
        N = 50
        M = 100
        K = 20
        steps = 200
        RR = np.random.rand(N, M)*10
        PP = np.random.rand(N, K)
        QQ= np.random.rand(K, M)
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
        from data.DataProcessor import read_data
        N, M, sparse_R = read_data('data/movie_data_718.txt')
        K = 20
        steps = 5
        P = np.random.rand(N, K)
        Q = np.random.rand(K, M)
        st = time.time()
        nP, nQ = naive_mf.naive_sparse_mf(sparse_R, P, Q, K, steps=steps)
        nR = np.dot(nP, nQ)
        print('naive sparse mf: steps = %d, time = %f' % (steps, time.time() - st))

if __name__ == '__main__':
    unittest.main()
