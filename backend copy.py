import csv

#Reads every item in a csv file.
#file:  csv file name.
def print_rows(file):
    with open(file, newline='') as fd:
        f_reader = csv.reader(fd, delimiter=',')

        print('\t'.join(next(f_reader)))

        for row in f_reader:
            print('\t\t'.join(row))
    return

#Reads a specified row in a csv file.
#file:  csv file name.
#n:     Row number.
def print_row(file, n):
    with open(file, newline='') as fd:
        f_reader = csv.reader(fd, delimiter=',')

        for i in range(n):
            next(f_reader)
        
        print('\t\t'.join(next(f_reader)))

    return

#Appends an entry to the end of a given csv file.
#file:      csv file name.
#*values:   Any number of values to be placed in the columns.
def add_row(file, *values):
    with open(file, newline='') as fd:
        reader = csv.reader(fd, delimiter=',')
        length = len(next(reader))

    with open(file, 'a', newline='') as fd:
        reader = csv.reader(fd, delimiter=',')

        new = '\n'

        if(len(values) != length):
            print('Number of entries does not match')
            return

        for value in values:
            new = new + str(value)
            if(value != values[-1]):
                new = new + ','
        
        fd.write(new)
    return

#Appends an entry to the end of a given csv file (given as a series of lists).
#file:      csv file name.
#*items:    Any number of items to be appended into the csv file. 
#           Remember to only use the same number of columns per entry.
def add_rows(file, *items):
    for item in items:
        add_row(file, *item)

#Deletes one or several rows in a given csv file.
#file:  csv file name.
#n:     Row to delete.
def del_row(file, *n):
    for i in n:
        if(i <= 0):
            print('invalid entry')
            return

    with open(file, newline='') as fd:
        f_dict_reader = csv.DictReader(fd)
        items = []
        for rows in f_dict_reader:
            items.append(rows)

    remove = []

    for i in n:
        remove.append(items[i-1])
    
    items = [x for x in items if x not in remove]
    
    with open(file, 'w', newline ='') as fd:
        f_writer = csv.writer(fd)
        f_writer.writerow(items[0])
        for item in items:
            f_writer.writerow(item.values())
    return

print('All entries:')
print_rows('iris.csv')

a = 5
print('\nEntry on row ' + str(a) + ':')
print_row('iris.csv', a)

#add_item('iris.csv', 1, 2, 3, 4, 'bepis')
#add_items('iris.csv', [1, 2, 3, 4, 'bepis'], [5, 6, 7, 8, 'bepis2'])

#del_row('iris.csv', 1, 2, 3)
