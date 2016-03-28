# Created by ay27 at 16/3/28

f = open('log.log', 'w')


def log(string):
    f.write('%s\n' % string)
