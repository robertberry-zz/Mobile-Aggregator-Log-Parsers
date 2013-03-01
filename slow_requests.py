#!/usr/bin/env python

import re
import fileinput

from collections import defaultdict

request_re = re.compile(r'''
    \S+\s\S+                                         # Skip date columns
    \s\S+\s\S+                                       # Skip thread name columns
    \s\S+\s+                                         # Skip log level column
    c\.g\.m\.endpoints\.EndpointUrls\$\s-\srequest   # Logging class
    \s
    (\S+)                                            # The URL
    \s
    completed\sin
    \s
    (\d+)                                            # Request time 
''', re.X)

stat_fns = (
    len,
    lambda rs: sum(rs) / float(len(rs)),
    max,
    min
)

def make_stats(times):
    return [f(times) for f in stat_fns]

def requests(lines):
    for line in lines:
        match = request_re.match(line)
        if match:
            url, time = match.groups()
            yield (url, int(time))

def request_times(requests):
    times = defaultdict(list)
    
    for request, time in requests:
        times[request].append(time)

    return times

def request_stats(request_times):
    return [(url, make_stats(times)) for url, times in request_times.items()]

def main():
    stats = request_stats(request_times(requests(fileinput.input())))

    for url, stats in sorted(stats, key=lambda s: s[1][1]):
        print "%100s %10d %10d %10d %10d" % (url, stats[0], stats[1], stats[2], stats[3])

if __name__ == '__main__':
    main()
