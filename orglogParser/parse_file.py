
def parse_file(path, search_string=""):
    def _filter(log_entry):
        if not search_string or search_string in log_entry:
            return log_entry

    with open(path) as f:
        log_entry = f.readlines()
        return [le.strip() for le in log_entry if _filter(le)]
