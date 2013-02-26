#!/usr/bin/env python

import sys
import fileinput
import re
import dateutil.parser as date_parser
import matplotlib
import datetime

from pylab import *
from collections import defaultdict

request_colours = {
    "DISCUSSION": ('b', '^'),
    "CONTENT-API": ('g', '^'),
    "OPTA": ('r', '^'),
    "PUSHY-GALORE": ('c', '^'),
    "TWITTER": ('m', '^'),
    "URBAN-AIRSHIP": ('y', '^'),
    "ZEITGEIST": ('k', '^')
}

request_types = request_colours.keys()

http_client_metric = re.compile(r"""
    ^([^,]+),\d+               # The time string
    \s
    \[[^\]]*\]                 # Name of the thread pool
    \s
    \[[^\]]*\]                 # ID of the thread
    \s
    \S+                        # Log level 
    \s\s
    (\S+)                      # Name of the logger
    \s-\s
    \S+                        # The URI
    \s
    completed\sin\s(\d+)\sms$  # Time
""", re.X)

def requests(lines):
    for line in lines:
        match = http_client_metric.match(line)

        if match:
            (finished, request_type, request_time) = match.groups()

            if request_type not in request_types:
                continue

            request_time = int(request_time)
            finished = date_parser.parse(finished)
            started = finished - datetime.timedelta(milliseconds=request_time)

            yield (request_type, started, request_time)

def draw_graph(requests):
    xlabel("Time")
    ylabel("Request times (milliseconds)")
    title("Apache HttpClient requests")

    requests_by_type = defaultdict(lambda: ([], []))

    for r in requests:
        (typ, started, lasted) = r
        requests_by_type[typ][0].append(started)
        requests_by_type[typ][1].append(lasted)

    for typ in request_types:
        if typ in requests_by_type:
            requests = requests_by_type[typ]
            matplotlib.pyplot.scatter(requests[0], requests[1], \
                                          c=request_colours[typ][0], \
                                          marker=request_colours[typ][1])

    matplotlib.pyplot.show()
    
def main():
    draw_graph(requests(fileinput.input()))

if __name__ == "__main__": main()
