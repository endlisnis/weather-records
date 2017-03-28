#/bin/python3
# -*- coding: utf-8 -*-

def valWithFlagScore(val, flag):
    scoreFlags = ['M', 'F', 'E', 'H', 'S', 'Y']
    if val is None:
        return 0
    for i, scoreFlag in enumerate(scoreFlags):
        if scoreFlag in flag:
            return i
    return len(scoreFlags)

def selectBestWithFlag(val1, flag1, val2, flag2):
    if val1 is None:
        return val2, flag2
    score1 = valWithFlagScore(val1, flag1)
    score2 = valWithFlagScore(val2, flag2)
    if score1 > score2:
        return val1, flag1
    if score2 > score1:
        return val2, flag2
    if val1 == val2 and flag1 == flag2:
        return val1, flag1
    if val1 == 0 and val2 == 0:
        if flag1 == 'T' and flag2 == '':
            return val1, flag1
        if flag1 == '' and flag2 == 'T':
            return val2, flag2
    import pudb; pu.db
    raise BaseException(repr(val1)+repr(flag1)+repr(val2)+repr(flag2))

def selectBest(val1, val2):
    if val1 is None:
        return val2
    if val2 is None:
        return val1
    if val1 == val2:
        return val1
    import pudb; pu.db
    raise BaseException(repr(val1)+repr(val2))
