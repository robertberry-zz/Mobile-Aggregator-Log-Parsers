#!/usr/bin/env python

import sys
import fileinput
import re
import dateutil.parser as date_parser
import matplotlib

from pylab import *

is_homepage = re.compile(r"^([^,]+).*EndpointUrls.* completed in (\d+) ms")

def homepage_requests(lines):
    request_times = []

    for line in lines:
        match = is_homepage.search(line)

        if match:
            date = match.group(1)

            request_times.append((date_parser.parse(date), int(match.group(2))))

    return request_times

def draw_graph(requests, t):
    xlabel("Time (minutes)")
    ylabel("Request times")

    title(t)

    xvals = [r[0] for r in requests]
    yvals = [r[1] for r in requests]

    matplotlib.pyplot.scatter(xvals, yvals)
    matplotlib.pyplot.show()

def main():
    requests = homepage_requests(fileinput.input())
    draw_graph(requests, "Request times for XL3")

if __name__ == "__main__": main()
