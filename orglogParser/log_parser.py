import re

ms_re = "\d*\.\d*ms"
duration_re = "(duration=)(?={})".format(ms_re)

class LogParser:
    def __init__(self, raw_events):
        self.entries = [LogEntry(i, ev) for i,ev in enumerate(raw_events)]

class LogEntry:
    def __init__(self, idx, line_item):
        print(f"SearchResult_LogEntry__{idx}")

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
