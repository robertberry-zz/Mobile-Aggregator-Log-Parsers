#!/usr/bin/env python

import sys
import argparse
import fileinput
import dateutil.parser as date_parser
import fileinput
import re

from collections import defaultdict

BASE_FILENAME = "out"

line_matcher = re.compile(r'''
    ^(\S+\s\S+),\S+         # date string
    \s
    \[(\S*)\]               # thread pool
    \s
    \[(\S*)\]               # thread ID
    \s
    (\S+)                   # log level
    \s\s
    (\S+)                   # class name
    \s-\s
    (.*)                    # message
''', re.X)

request = re.compile(r'request (\S+) completed in (\d+) ms')
outbound_request = re.compile(r'\S+ completed in (\d+) ms')

class LogLine(object):
    def __init__(self, time, thread_pool, thread_id, log_level, class_name, \
                     message):
        self.time = time
        self.thread_pool = thread_pool
        self.thread_id = thread_id
        self.log_level = log_level
        self.class_name = class_name
        self.message = message

    @property
    def request_id(self):
        return (self.thread_pool, self.thread_id)

class RequestProfile(object):
    def __init__(self, url, request_time, outbound_times):
        self.url = url
        self.request_time = request_time
        self.outbound_times = outbound_times

def ftrue(x):
    return True

def fand(f, g):
    lambda x: f(x) and g(x)

def log_lines(f):
    for line in f:
        match = line_matcher.match(line)

        if match:
            groups = match.groups()
            yield LogLine(date_parser.parse(groups[0]), *groups[1:])

def outbound_times(lines):
    thread_outbound_times = defaultdict(lambda: defaultdict(list))
    request_profiles = []

    for line in lines:
        match = outbound_request.match(line.message)

        if match:
            thread_outbound_times[(line.request_id)][line.class_name]\
                .append(int(match.group(1)))
        else:
            match = request.match(line.message)

            if match:
                request_profiles.append(RequestProfile(match.group(1), \
                                                           int(match.group(2)), \
                                                           thread_outbound_times[line.request_id]))
                # in case thread is reused
                thread_outbound_times[line.request_id] = list()

    return request_profiles

def aggregate_profiles(profiles, extract):
    by_class = defaultdict(list)

    for profile in profiles:
        for k, times in profile.outbound_times.items():
            v = extract(profile, times)
            if v is not None:
                by_class[k].append(v)

    return by_class

def main():
    parser = argparse.ArgumentParser(description="Find % request time doing " + \
                                         "synchronous loads")
    parser.add_argument('--start', help='only process requests after this ' + \
                            'date time')
    parser.add_argument('--end', help='only process requests before this ' + \
                            'date time')
    parser.add_argument('--min_time', help='only process requests that ' + \
                            'take at least this long', type=int, default=1)
    args = parser.parse_args()

    f = ftrue

    if args.start:
        start = date_parser.parse(args.start)
        f = fand(f, lambda line: line.time >= start)

    if args.end:
        end = date_parser.parse(args.end)
        f = fand(f, lambda line: line.time <= end)

    lines = (l for l in log_lines(sys.stdin) if f(l))

    profiles = outbound_times(lines)

    min_time = max(1, args.min_time)

    def percent_of_request(profile, times):
        if profile.request_time > min_time:
            return 100 * sum(times) / float(profile.request_time)
        else:
            return None

    aggregated = aggregate_profiles(profiles, percent_of_request)

    for klass, results in aggregated.items():
        fp = open("%s_%s" % (BASE_FILENAME, klass), "w")

        for result in results:
            fp.write("%s\n" % result)

        fp.close()

if __name__ == '__main__':
    main()
