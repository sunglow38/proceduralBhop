import re
import fileinput
import sys

filefrom = r"copytest2.vmf"
fileto = r"copytest1.vmf"
# regex = r'\t\solid\\n\t\t\"id\"\s+\"\d+\"'
regex = r'\tsolid'

def copy():
    with open(fileto) as f:
        for line in f:
            # solid = re.findall(regex, line)
            if re.match(regex, line):
                print(line)
                # lines = [f.readline() for i in range(2)]
                # print(lines)
                # print('-' * 10)




copy()