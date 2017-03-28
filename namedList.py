# -*- coding: utf-8 -*-
def namedList(name, members, verbose=False):
    memNames = [member.split('=')[0] for member in members]
    code = ""
    code += "class %s(list):\n" % name
    code += "    __slots__ = ()\n"
    code += ( "    _fields = ({})\n"
              .format(', '.join(['"'+a+'"' for a in memNames])))
    code += "    def __init__(self, %s):\n" % ', '.join(members)
    code += "        list.__init__(self, [%s])\n" % ', '.join(memNames)
    code += "    def __repr__(self):\n"
    code += "        return '%s(%s)' %% tuple(self)\n" % (name, ', '.join(['%s=%%r' % a for a in memNames]))
    for (index, member) in enumerate(memNames):
        code += "    @property\n"
        code += "    def %s(self):\n" % member
        code += "        return self[%d]\n" % index
        code += "    @%s.setter\n" % member
        code += "    def %s(self, value):\n" % member
        code += "        self[%d] = value\n" % index
    if verbose:
        print(code)
    exec(code)
    return eval(name)

def namedStruct(name, members, verbose=False):
    if type(members) is str:
        members = members.split()
    memNames = [member.split('=')[0] for member in members]
    code = ""
    code += "class %s():\n" % name
    code += "    __slots__ = ({})\n".format(', '.join(['"'+t+'"' for t in memNames]))
    code += "    def __init__(self, %s):\n" % ', '.join(members)
    for memName in memNames:
        code += "        self.%s = %s\n" % (memName, memName)
    code += "    def __repr__(self):\n"
    code += "        return '%s(%s)' %% (%s)\n" % (name, ', '.join(['%s=%%r' % a for a in memNames]), ', '.join(['self.' + a.split('=')[0] for a in memNames]))
    code += "    def __cmp__(self, other):\n"
    for memName in memNames:
        code += "        if not hasattr(other, '%s'):\n" % (memName)
        code += "            return 1\n"
        code += "        if self.%s != other.%s:\n" % (memName, memName)
        code += "            return self.%s.__cmp__(other.%s)\n" % (memName, memName)
    code += '        return 0\n'
    if verbose:
        print(code)
    exec(code)
    return eval(name)

def namedTupleDefaults(name, members, verbose=False):
    if type(members) is str:
        members = members.split()
    memNames = [member.split('=')[0] for member in members]
    code = ""
    code += 'from collections import namedtuple\n'
    code += '%s_noDefaults = namedtuple("%s_noDefaults", %s, verbose=%s)\n' % (name, name, memNames, verbose)
    code += "class %s(%s_noDefaults):\n" % (name, name)
    code += "    __slots__ = ()\n"
    #code += "    def __init__(self, %s):\n" % ', '.join(members)
    #code += '        %s_noDefaults.__init__(self, %s)\n' % (name, ', '.join(['%s = %s' % (a,a) for a in memNames]))
    code += "    def __new__(self, %s):\n" % ', '.join(members)
    code += '        %s_noDefaults.__new__(self, %s)\n' % (name, ', '.join(['%s = %s' % (a,a) for a in memNames]))
    code += name
    if verbose:
        print(code)
    exec(code)
    return eval(name)
