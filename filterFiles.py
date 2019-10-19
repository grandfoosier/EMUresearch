import re

def filterList(name_in, name_out):
    with open(name_in, 'r') as file_in, open(name_out, 'w') as file_out:
        for line in file_in:
            left = line.rfind('~') + 1; right = line.find('.py ')
            if left == 0: left = line.rfind('[') + 1
            if not exclude(line[left: right]): file_out.write(line)

def exclude(func_name):
    return re.match('.*test.*', func_name)

if __name__ == '__main__':
    filterList('paths_full.txt', 'paths_filtered.txt')
