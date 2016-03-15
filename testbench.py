# Created by ay27 at 16/3/14
import unittest
import numpy as np


def EuclideanDistance(A, B):
    if isinstance(A, float) or isinstance(A, int):
        return pow(A-B, 2)
    if A.shape != B.shape:
        raise AttributeError('shape of A is not equal to B')
    shape = A.shape
    sum = 0
    for ii in range(shape[0]):
        sum += EuclideanDistance(A[ii], B[ii])
    return sum


class MyTestCase(unittest.TestCase):
    def test_naive_mf(self):
        import naive_mf
        N = 10
        M = 15
        K = 5
        R = np.random.rand(N, M)*10
        P = np.random.rand(N, K)
        Q = np.random.rand(K, M)
        nP, nQ = naive_mf.naive_mf(R, P, Q, K, steps=2000)
        nR = np.dot(nP, nQ)
        # print(EuclideanDistance(R, nR))

if __name__ == '__main__':
    unittest.main()
