# Created by ay27 at 16/3/25
import subprocess
import matplotlib.pyplot as plt
import g

TASK_NUM = g.client_num + g.ps_num
TASK_FILE = 'launcher.py'
# 'mpirun --mca btl_tcp_if_include eth0 -hostfile hostfile -n %d /home/ay27/anaconda3/bin/python3 %s' % (TASK_NUM, TASK_FILE)
CMD_RUN_MPI_TASK = 'mpirun -n %d python3.5 %s' % (TASK_NUM, TASK_FILE)

if __name__ == '__main__':
    p = subprocess.Popen(CMD_RUN_MPI_TASK, shell=True)
    p.communicate()

    # tmp = []
    # raw = ''
    # with open('log/result4.txt') as f:
    #     for line in f:
    #         raw += line
    #     tmp = eval(raw)
    # tmp.remove(tmp[0])
    # plt.plot(range(len(tmp)), tmp, 'r')
    # plt.show()
