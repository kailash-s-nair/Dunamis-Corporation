#This is a test

import csv

def read_items(file):
    with open(file, newline='') as fd:
        iris_reader = csv.reader(fd, delimiter=',', quotechar='|')

        print('\t'.join(next(iris_reader)))

        for row in iris_reader:
            print('\t\t'.join(row))
    return

def read_row(file, n):
    with open(file, newline='') as fd:
        iris_reader = csv.reader(fd, delimiter=',', quotechar='|')

        for i in range(n):
            next(iris_reader)
        
        print('\t\t'.join(next(iris_reader)))

    return

def add_item(file, s_length, s_width, p_length, p_width, species):
    with open(file, 'a', newline='') as fd:
        iris_reader = csv.reader(fd, delimiter=',', quotechar='|')

        new = str(s_length) + ',' + str(s_width) + ',' + str(p_length) + ',' + str(p_width) + ',' + species + '\n'

        fd.write('\n')
        fd.write(new)
    return

def del_item(file, n):
    if(n == 0):
        print('Do not attempt to delete the first row.')
        return

    i = 0
    items = []
    
    with open(file, newline='') as fd:
        iris_reader = csv.reader(fd, delimiter=',', quotechar='|')
        done = False
        for row in iris_reader:
            if(not done and i == n):
                done = True
            else:
                items.append(row)
            i = i+1
            

    with open(file, 'w', newline='') as fd:
        iris_writer = csv.writer(fd, delimiter=',', quotechar='|')
        for j in items:
            iris_writer.writerow(j)

    print(items)

    return

read_items('iris.csv')
read_row('iris.csv', 5)
add_item('iris.csv', 1, 2, 3, 4, 'bepis')
