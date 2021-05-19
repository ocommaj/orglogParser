from click import echo
from .outputs import label

def stats_output(search_results):
    count = len(search_results)
    echo( label("Count", count) )
