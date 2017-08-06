import re
import fileinput
import sys

## TODO: add arguments: Delta, file. 
    ## Translate file by delta. 
    
filename = r"simple.vmf"
# filename = r"notSimple.vmf"
regexp = r"\((.*?)\)"

def translate():
    for line in fileinput.input(files=(filename), inplace=True):
            planar = re.findall(regexp, line)
            if planar:
                # print("Current Line: ", fileinput.lineno(), file=sys.stderr)
                print('-' * 10, file=sys.stderr)
                for vertex in planar:
                    new = vertex.split(' ')
                    try:
                        new = list(map(int, new))
                    except ValueError:
                        sys.stderr.write("could not convert to integer")
                    try:
                        new[2] -= 64 # test value for now, make into argument
                    except:
                        sys.stderr.write("Not an array")

                    new = map(str, new)
                    new = ' '.join(new)
                    new = re.sub(r".*", r'(\g<0>)', new)
                    print("New: ", new, file=sys.stderr)
                    newVertex = re.sub(regexp, new, line.rstrip())
                    print('-' * 10, file=sys.stderr)

                print("Translated: ", newVertex, file=sys.stderr)

                print(newVertex)
            else:
                print(line.rstrip())
                

translate()