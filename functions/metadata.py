import re

def get_scan_number(s):
    s = str(s)
    s = re.search('(?<=scan)\d{4}', s)
    if s is not None:
        return int(s.group(0))
    else:
        return -1
    
    
def get_rep(x, reps_per_spot=1):
    scan = get_scan_number(x)
    return (scan % reps_per_spot) + 1