# Created by ay27 at 16/3/25
import csv

with open('data/output1/data_%d.csv' % 0) as file:
    tmp = []
    reader = csv.reader(file)
    for row in reader:
        tmp.append([int(float(row[0])), int(float(row[1])), int(float(row[2]))])
    print(tmp)
