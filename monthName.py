import time

def monthName(month, long=False):
    if long:
        return time.strftime("%B", (2008, month, 1, 0, 0, 0, 0, 0, 0))
    return time.strftime("%b", (2008, month, 1, 0, 0, 0, 0, 0, 0))
