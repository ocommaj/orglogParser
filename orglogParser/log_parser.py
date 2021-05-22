import re

ms_re = "\d*\.\d*ms"
duration_re = "(duration=)(?={})".format(ms_re)

class LogParser:
    def __init__(self, raw_events):
        self.entries = [LogEntry(i, ev) for i,ev in enumerate(raw_events)]
        self.baseline_inflations = BaselineInflations(raw_events)

        if len(self.baseline_inflations):
            for ev in self.baseline_inflations[43].event_messages:
                print(ev)

class LogEntry:
    def __init__(self, idx, line_item):
        if 'duration=' in line_item:
            self.duration = Duration(line_item)
            print(f"Duration: {self.duration.value}")

class Duration:
    def __init__(self, line_item):
        expected_pattern = duration_re

        if not re.search(expected_pattern, line_item):
            self.value = 'UNPATTERN'
            self.unpattern = True
        else:
            self.stringify = re.findall(ms_re, line_item)[0]
            self.value = float(self.stringify[:-2])

class BaselineInflations(list):
    def __init__(self, events):
        super().__init__(self)
        start_msg = "Inflating to baseline..."
        end_msg = "Inflated to baseline: "

        starts = [i for i,ev in enumerate(events) if re.search(start_msg, ev)]
        ends = [i for i,ev in enumerate(events) if re.search(end_msg, ev)]
        if len(starts) and len(ends):
            # hard code fix for log sample data starting mid-cycle
            if ends[0] < starts[0]: del ends[0]

            start_ends = zip(starts, ends)

            for ev in start_ends:
                if not ev[0] < ev[1]:
                    print(f"ERROR: {ev}")
                else:
                    self.append( BaselineInflation(events[ev[0]:ev[1]+1]) )

class BaselineInflation:
    def __init__(self, event_messages):
        self.test_str = f"BL Inflate Event of: {len(event_messages)} entries"
        self.event_messages = event_messages
