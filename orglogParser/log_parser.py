import re

milliSecond_re = "ms=\d*.\d*|\d*\.\d*ms"
duration_re = "(duration=)(?={})".format(milliSecond_re)

kiloPascal_re = "kPa=\.*.\d*\.\d*"

class LogParser:
    def __init__(self, raw_events):
        self.entries = [LogEntry(i, ev) for i,ev in enumerate(raw_events)]
        self.baseline_inflations = BaselineInflations(raw_events)

        if len(self.baseline_inflations):
            #test_idx = 43
            #self.baseline_inflations.test_output(test_idx)
            pass

class LogEntry:
    def __init__(self, idx, line_item):
        if 'duration=' in line_item:
            self.duration = Duration(line_item)
            #print(self.duration.test_str)

class Duration:
    def __init__(self, line_item):
        expected_pattern = duration_re

        if not re.search(expected_pattern, line_item):
            self.value = 'UNPATTERN'
            self.unpattern = True
            self.test_str = 'Found an unpattern'
        else:
            time = Time(line_item)
            self.float = time.float
            self.stringify = time.stringify
            self.test_str = time.test_str

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

    def test_output(self, test_idx):
        test_obj = self[test_idx]
        print(test_obj.test_str)
        print(test_obj.start)
        print(test_obj.end)
        #for step in test_obj.steps:
        #    print(step.completed.test_str)
        #    print(step.delta.test_str_abs)
        #    print(step.delta.test_str_pct)
        #for ev in test_obj.log_events:
        #    print(ev)

        #for reading in test_obj.pressure_readings:
        #    if hasattr(reading, 'delta'):
        #        print(reading.pressure.stringify)
        #        print(reading.delta.test_str_abs)
        #        print(reading.delta.test_str_pct)
        #        print("")

class BaselineInflation:
    def __init__(self, log_events):
        self.test_str = f"BL Inflate Event of: {len(log_events)} entries"
        #self.log_events = log_events # <-- use to output all

        self.start = log_events.pop(0)
        self.end = log_events.pop(-1)

        self.pressure_readings = PressureReadings(log_events)
        self.steps = InflationSteps(log_events)

        self.test_str = f"took {len(self.steps)} to reach baseline"

class InflationSteps(list):
    def __init__(self, log_events):
        super().__init__(self)

        prog = re.compile("Inflating")
        for i,ev in enumerate(log_events):
            if prog.search(ev):
                self.append( InflationStep(log_events[i:i+2]) )

class InflationStep:
    def __init__(self, events):
        self.inflating = Time(events[0])
        self.completed = Time(events[1])
        self.delta = Delta(self.completed.float, self.inflating.float, 'ms')

        self.inflating.test_str = f"Set {self.inflating.test_str}"
        self.completed.test_str = f"Actual {self.completed.test_str}"

class PressureReadings(list):
    def __init__(self, log_events):
        super().__init__(self)

        prog = re.compile('pressure sensor', re.IGNORECASE)
        for ev in log_events:
             if prog.search(ev):
                 self.append( PressureSensorData(ev) )

        self.iterate_deltas()

    def iterate_deltas(self):
        for i,reading in enumerate(self):
            if i:
                reading.set_delta(self[i-1].pressure)

class PressureSensorData:
    def __init__(self, line_item):
        self.pressure = Pressure(line_item)
        self.time = Time(line_item)
        self.test_str = f"Pressure Sensor Read:\n{self.pressure.test_str}\n{self.time.test_str}"

    def set_delta(self, relative):
        self.delta = Delta(self.pressure.float, relative.float, 'kPa')

class Pressure:
    def __init__(self, line_item):
        prog=re.compile("[^=kPa]")
        raw_data = re.findall(kiloPascal_re, line_item)[0]
        self.float = float(''.join(prog.findall(raw_data) ))
        self.stringify = f"{self.float} kPa"
        self.test_str = f"Pressure: {self.stringify}"

class Time:
    def __init__(self, line_item):
        raw_data = re.findall(milliSecond_re, line_item)[0]
        self.float = float(''.join(re.findall("[^ms={}]", raw_data)))
        self.stringify = f"{self.float} ms"
        self.test_str = f"Duration: {self.stringify}"

class Delta:
    def __init__(self, a, b, unit=None):
        self.absolute = round(abs(float(b)- float(a)), 3)
        self.pct = round(abs(self.absolute/a)*100, 3)

        if unit:
            self.stringify(unit)

    def stringify(self, unit):
        self.str_absolute = f"{self.absolute} {unit}"
        self.str_pct = f"{self.pct} %"
        self.test_str_abs = f"Delta (abs): {self.str_absolute}"
        self.test_str_pct = f"Delta (pct): {self.str_pct}"
