# Created by ay27 at 16/4/11

import matplotlib.pyplot as plt

C = ['r', 'g', 'b', 'y', 'c', 'k']
M = ['^', 'o', 'v', 'd', '+', '.']
cnt = ["multi-thread", "one thread"]
expts = ["/Users/ay27/Documents/mf_ps/mf_ps/expt.txt", "/Users/ay27/ClionProjects/mf_ps_no_thread/mf_ps_no_thread/expt.txt"]
times = ["/Users/ay27/Documents/mf_ps/mf_ps/times.txt", "/Users/ay27/ClionProjects/mf_ps_no_thread/mf_ps_no_thread/times.txt"]


def read_file(filename):
    tmp = []
    with open(filename) as f:
        for line in f:
            tmp.append(float(line))
    tmp.remove(tmp[0])
    return tmp

for ii in range(len(cnt)):
    x = read_file(times[ii])
    y = read_file(expts[ii])
    plt.plot(x, y, c=C[ii], marker=M[ii], markersize=12, linewidth=2.0, label=cnt[ii])

plt.legend()
plt.show()
