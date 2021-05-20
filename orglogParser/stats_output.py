import re
from click import echo
from .outputs import label

ms_pattern = "\d*\.\d*ms"
duration_re = "(duration=)(?={})".format(ms_pattern)

peculiars = []
durations = []

def stats_output(search_results):
    duration_stats(search_results)

    echo( label("Results", len(search_results)) )
    if len(durations):
        echo("")
        echo( label("Clean Durations", len(durations)) )
        echo( label("Average Duration", f"{average(durations)} ms") )
        echo("")

    if len(peculiars):
        error_report()
        echo("")

def duration_stats(log_events):
    duration_events = [ev for ev in log_events if "duration=" in ev]

    for ev in duration_events:
        inspect_duration(ev)

def inspect_duration(log_event):
    if not re.search(duration_re, log_event):
        peculiars.append(log_event)
        return

    [ durations.append(float(str[:-2]))
        for str in re.findall(ms_pattern, log_event)]

def error_report():
    echo( label("UnPattern Events", len(peculiars)) )
    for event in peculiars:
        echo(f"\t{event}")

def average(numbers):
    return round((sum(numbers))/len(numbers), 3)
