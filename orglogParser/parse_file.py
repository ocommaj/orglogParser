
def parse_file(path, search_string=""):
    results = []
    with open(path) as f:
        lines = f.readlines()

        for line in lines:
            res = _check_search(line, search_string)
            if res:
                res = res.strip()
                results.append(res)
    return results

def _check_search(log_message, search_string):
    if not search_string or search_string in log_message:
        return log_message
