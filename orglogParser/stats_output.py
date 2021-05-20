import re
from statistics import mean, stdev, NormalDist
from click import echo
import plotext as plt
from .outputs import label, err_label

ms_re = "\d*\.\d*ms"
duration_re = "(duration=)(?={})".format(ms_re)

peculiars = []

def stats_output(search_results):
    durations = duration_events(search_results)

    echo( label("Results", len(search_results)) )
    if len(durations):
        dur_stats = stats('Durations', durations)
        echo("")
        echo( label("Clean Durations", len(durations)) )
        echo( label("Average", f"{ dur_stats['mean'] } ms") )
        echo( label("Std Dev", f"{ dur_stats['stdev'] } ms") )
        echo("")
        dur_stats['plot']()
        echo("")

    if len(peculiars):
        error_report()
        echo("")

def duration_events(log_events):
    def inspect_duration(log_event):
        def _duration_float(log):
            return [ float(str[:-2]) for str in re.findall(ms_re, log) ][0]

        ev = log_event;
        if not re.search(duration_re, ev):
            peculiars.append(log_event)
            return

        return _duration_float(log_event)

    d_evts = [ev for ev in log_events if "duration=" in ev]
    durations = [ds for ds in [inspect_duration(ev) for ev in d_evts] if ds]
    return durations

def error_report():
    echo( err_label("UnPattern Events", len(peculiars)) )
    for event in peculiars:
        echo(f"\t{event}")

def stats(label_str, numbers):
    _nd = NormalDist.from_samples(numbers)
    _nd_Ys = [_nd.pdf(x) for x in numbers]

    mn = round(mean(numbers), 4)
    sd = round(stdev(numbers))

    def plot():
        plt.plot(numbers, _nd_Ys, line_color = "indigo")
        plt.figsize(60, 20)
        plt.title(label_str)
        plt.canvas_color('none') # <-inside plot bg
        plt.axes_color('none') # <-bg outside plot
        plt.ticks_color('teal') # <- axes lines & labels
        plt.show()


    return {
        "mean": mn,
        "stdev": sd,
        "plot": plot
        }
