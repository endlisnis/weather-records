import collections

def dictFromArgs(**kwargs):
    return kwargs

def namedtuple_with_defaults(typename, field_names, default_values=None):
    T = collections.namedtuple(typename, field_names)
    if default_values is None:
        prototype = (None,) * len(T._fields)
    elif isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T
