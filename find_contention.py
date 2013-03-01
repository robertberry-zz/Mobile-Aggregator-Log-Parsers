#!/usr/bin/env python

import re
import fileinput

def working_at(lines):
    is_block = re.compile(r'\s+java.lang.Thread.State:')
    position = re.compile(r'\s+at (\S+)')
    
    read_position = False

    for line in lines:
        if read_position:
            match = position.match(line)
            read_position = False

            if match:
                yield match.group(1)
        elif is_block.match(line):
            read_position = True

def main():
    for line in working_at(fileinput.input()):
        print line

if __name__ == '__main__':
    main()
