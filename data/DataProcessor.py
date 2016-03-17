# Created by ay27 at 16/3/15


def _count(data):
    N = 0
    M = 0
    for row in data:
        N = max(N, row[0])
        M = max(M, row[1])
    return N, M


def read_data(file_path):
    tmp = []
    with open(file_path, 'r') as file:
        for line in file:
            tmp.append([float(word) for word in line.split()])
    N, M = _count(tmp)
    return N, M, tmp

# def write_data(tmp, file_path):
#     with open(file_path, 'w') as file:
#         for row in tmp:
#             file.write('%d %d %d\n' % (row[0], row[1], row[3]))
#
#
# if __name__ == '__main__':
#     N, M, tmp = read_data('movie_718user_all.txt')
#     write_data(tmp, 'movie_data_718.txt')
