import re

kiloPascal_re = "(?<=kPa=).\d*.\d*|\d*.\d*(?= kPa)"
milliSecond_re = "(?<=ms=).\d*\.\d*|(?<=ms=)\d*|(?<=duration=)\d*\.\d*"
duration_re = "(duration=)(?={})".format(milliSecond_re)

class LogParser:
    def __init__(self, raw_events):
        self.entries = [LogEntry(i, ev) for i,ev in enumerate(raw_events)]
        self.baseline_inflations = BaselineInflations(raw_events)
        self.layer_inflations = LayerInflationEvents(raw_events)

        if len(self.baseline_inflations):
            #test_idx = 43
            #self.baseline_inflations.test_output(test_idx)
            pass

        if len(self.layer_inflations):
            test_idx = 37
            self.layer_inflations[test_idx].test_output(test_idx)

        InstanceBlocks(raw_events)

class InstanceBlocks:
    def __init__(self, log_events):
        prog_enter = re.compile('instance enter')
        prog_ent_val = re.compile('(?<=instance enter).*')
        prog_eval = re.compile('instance evaluate')
        prog_eval_val = re.compile('(?<=instance evaluate).*')
        prog_leave = re.compile('instance leave')
        prog_leave_val = re.compile('(?<=instance leave).*')

        ent_events = [
            prog_ent_val.search(ev) for ev in log_events
            if prog_enter.search(ev)
        ]

        eval_events = [
            prog_eval_val.search(ev) for ev in log_events
            if prog_eval.search(ev)
        ]

        exit_events = [
            prog_leave_val.search(ev) for ev in log_events
            if prog_leave.search(ev)
        ]

        #for ev in exit_events:
         #  print(ev.group(0))
        print(f"Instance Enter: {len(ent_events)}")
        print(f"Instance Eval: {len(eval_events)}")
        print(f"Instance Exit: {len(exit_events)}")

class LayerInflationEvents(list):
    def __init__(self, log_events):
        super().__init__(self)
        prog_pre = re.compile('Pre-inflation pressure:')
        prog_post = re.compile('Post-inflation pressure:')
        prog_set = re.compile('Inflating')
        prog_end = re.compile('Actual inflation time')
        for i,ev in enumerate(log_events):
            if prog_pre.search(ev):
                inflate_start = ev
                inflate_end = next(ln for ln in log_events[i:] if prog_post.search(ln))
                inflate_set = next(ln for ln in log_events[i:] if prog_set.search(ln))
                inflate_time = next(ln for ln in log_events[i:] if prog_end.search(ln))
                self.append( LayerInflation(inflate_start, inflate_end, inflate_set, inflate_time))
        print(f"Pneumatic Separation Events: {len(self)}")

        #def iterate_deltas(self): <-- tbd: write to iterate for rate of change
        #    for i,liEvent in enumerate(self):
        #        if i:
        #            reading.set_delta(self[i-1].pressure)

class LayerInflation:
    def __init__(self, start_line, end_line, time_set, time_actual):
        self.start_pressure = Pressure(start_line)
        self.end_pressure = Pressure(end_line)
        self.step = InflationStep([time_set, time_actual])
        self.delta = Delta(self.start_pressure.float, self.end_pressure.float, 'kPa')

    def test_output(self, idx):
        print(f"Log Data for separation event {idx}")
        print(f"Start {self.start_pressure.test_str}")
        print(f"End {self.end_pressure.test_str}")
        print(self.delta.test_str_abs)
        print(self.step.inflating.test_str)
        print(self.step.completed.test_str)
        print("")

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
    def __init__(self, log_events):
        super().__init__(self)
        start_msg = "Inflating to baseline..."
        end_msg = "Inflated to baseline: "

        starts = [i for i,ev in enumerate(log_events) if re.search(start_msg, ev)]
        ends = [i for i,ev in enumerate(log_events) if re.search(end_msg, ev)]

        if len(starts) and len(ends):
            # hard code fix for log sample data starting mid-cycle
            if ends[0] < starts[0]: del ends[0]

            start_ends = zip(starts, ends)

            for ev in start_ends:
                if not ev[0] < ev[1]:
                    print(f"ERROR: {ev}")
                else:
                    self.append( BaselineInflation(log_events[ev[0]:ev[1]+1]) )

    def test_output(self, test_idx):
        test_obj = self[test_idx]
        print(test_obj.test_str)
        print(test_obj.start)
        print(test_obj.end)
        for step in test_obj.steps:
            print(step.completed.test_str)
            print(step.delta.test_str_abs)
            print(step.delta.test_str_pct)
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
        prog=re.compile(kiloPascal_re)
        raw_data = prog.search(line_item)[0]
        self.float = float(raw_data)
        self.stringify = f"{self.float} kPa"
        self.test_str = f"Pressure: {self.stringify}"

class Time:
    def __init__(self, line_item):
        prog = re.compile(milliSecond_re)
        raw_data = prog.search(line_item)[0]
        self.float = float(raw_data)
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
