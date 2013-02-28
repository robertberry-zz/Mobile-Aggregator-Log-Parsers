#!/usr/bin/env python

import fileinput
import dateutil.parser as date_parser
import fileinput
import re
import matplotlib.pyplot as pyplot

from pylab import *

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

class LogLine(object):
    def __init__(self, time, thread_pool, thread_id, log_level, class_name, \
                     message):
        self.time = time
        self.thread_pool = thread_pool
        self.thread_id = thread_id
        self.log_level = log_level
        self.class_name = class_name
        self.message = message

class Update(object):
    def __init__(self, klass, start, end):
        self.klass = klass
        self.start = start
        self.end = end

graph_line_colours = {
    "c.g.m.r.SectionFastContentItemStore": "r",
    "c.g.m.refdata.SectionQueryStore": "b",
    "c.g.m.refdata.DiscussionStore": "g",
    "c.g.m.r.football.opta.OptaLiveStore$": "c",
    "c.g.m.r.f.o.OptaVolatileStatsStore$": "m",
    "c.g.m.r.SectionSlowContentItemStore": "y"
}
        
update_start_messages = {
    "c.g.m.r.SectionFastContentItemStore": "### update",
    "c.g.m.refdata.SectionQueryStore": "### reloading...",
    "c.g.m.refdata.DiscussionStore": "Reloading...",
    "c.g.m.r.football.opta.OptaLiveStore$": "Reloading...",
    "c.g.m.r.f.o.OptaVolatileStatsStore$": "Reloading...",
    "c.g.m.r.SectionSlowContentItemStore": "### update"
}

update_classes = update_start_messages.keys()

def relevant_log_lines(f):
    return (l for l in log_lines(f) if l.class_name in update_classes)

# use relevant_log_lines - this loads too much into memory
def log_lines(f):
    for line in f:
        match = line_matcher.match(line)

        if match:
            groups = match.groups()
            yield LogLine(date_parser.parse(groups[0]), *groups[1:])

def update_lifespans(lines):
    update_threads = dict()

    for line in lines:
        if line.class_name in update_classes:
            if line.thread_pool in update_threads:
                update_threads[line.thread_pool].end = line.time
            elif update_start_messages[line.class_name] in line.message:
                update_threads[line.thread_pool] = Update(line.class_name, \
                                                              line.time, \
                                                              line.time + datetime.timedelta(seconds=1))

    # now figure out how many simultaneous updates occur at a time?
    updates = update_threads.values()

    assert len(updates) > 0, "No update events found"

    updates_begin = [(update.start, -1, update.klass) for update in \
                         updates]
    updates_end = [(update.end, 1, update.klass) for update in \
                       updates]
    events = sorted(updates_begin + updates_end)

    first_date = events[0][0] - datetime.timedelta(seconds=1)

    data_sets = dict((kls, ([first_date], [0])) for kls in update_classes)

    for time, update, klass in events:
        data_sets[klass][0].append(time)
        data_sets[klass][1].append(data_sets[klass][1][-1] - update)

    return data_sets

def draw_graph(lifespans):
    xlabel("Time")
    ylabel("Number of simultaneous updates")
    title("Mobile Aggregator simultaneous agent updates")

    for kls, dataset in lifespans.items():
        pyplot.plot(dataset[0], dataset[1], c=graph_line_colours[kls])

    pyplot.show()

def main():
    draw_graph(update_lifespans(relevant_log_lines(fileinput.input())))

if __name__ == '__main__':
    main()
