# Created by ay27 at 16/3/17

CMD_INC = 'inc'
CMD_PULL = 'pull'
CMD_FLUSH = 'flush'
CMD_EXPT = 'expt'
CMD_STOP = 'stop'

PROCESS_EVERY_MACHINE = 2
client_num = PROCESS_EVERY_MACHINE * 2
ps_num = PROCESS_EVERY_MACHINE * 1

STALE = 1

EXPT_MACHINE = client_num + ps_num - 1

K = 20
