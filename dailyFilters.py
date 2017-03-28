#!/usr/bin/python3
import daily

class DayFilter():
    pass

class Avg(DayFilter):
    def __init__(self, field1, field2, title):
        self.field1 = field1
        self.field2 = field2
        self.title = title

    def __call__(self, fields):
        r1 = fields[self.field1.index]
        r2 = fields[self.field2.index]
        if r1 is None or r2 is None:
            return None
        return (r1 + r2) / 2

    @property
    def name(self):
        return "AVG[%s,%s]" % (self.field1.name, self.field2.name)

    @property
    def units(self):
        return self.field1.units

    @property
    def precision(self):
        return self.field1.monthlyPrecision

    @property
    def englishName(self):
        return self.title

class FractionVal(DayFilter):
    __slots__ = ('field', 'title', 'skipIncomplete')
    def __init__(self, field, title, skipIncomplete=False):
        self.field = field
        self.title = title
        self.skipIncomplete = skipIncomplete
    #
    def __call__(self, fields):
        r = fields[self.field.index]
        flags = fields[self.field.index+1]
        if r is None or (self.skipIncomplete and 'I' in flags):
            return None
        return r
    #
    @property
    def name(self):
        return self.field.name
    #
    @property
    def units(self):
        return self.field.units
    @property
    def unit(self):
        return self.field.units
    @property
    def precision(self):
        return self.field.monthlyPrecision
    @property
    def englishName(self):
        return self.title

class ExprVal(DayFilter):
    __slots__ = ('expr', 'title', 'name',
                 'unit', 'units', 'precision',
                 'field', 'description')
    def __init__(self, expr, title, name,
                 unit, units, precision,
                 field, description
    ):
        self.expr = expr
        self.title = title
        self.name = name
        self.unit = unit
        self.units = units
        self.precision = precision
        self.field = field
        self.description = description
    #
    def __call__(self, fields):
        r = fields.eval(self.expr)
        return r

    @property
    def englishName(self):
        return self.title
