# Created by ay27 at 16/3/25
import subprocess
from ps import g

TASK_NUM = g.client_num+g.ps_num
TASK_FILE = 'launcher.py'
CMD_RUN_MPI_TASK = 'mpirun -np %d python3 %s' % (TASK_NUM, TASK_FILE)

if __name__ == '__main__':
    p = subprocess.Popen(CMD_RUN_MPI_TASK, shell=True)
    p.communicate()