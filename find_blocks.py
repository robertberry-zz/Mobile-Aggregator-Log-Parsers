#!/usr/bin/env python

import re
import fileinput

def blocked_at(lines):
    is_block = re.compile(r'BLOCKED \(on object monitor\)')
    position = re.compile(r'\s+at (\S+)')
    
    read_position = False

    for line in lines:
        if read_position:
            match = position.match(line)
            read_position = False

            if match:
                yield match.group(1)
        elif is_block.search(line):
            read_position = True

def main():
    for line in blocked_at(fileinput.input()):
        print line

if __name__ == '__main__':
    main()
