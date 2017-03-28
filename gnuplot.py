# -*- coding: utf-8 -*-
from __future__ import print_function
import os, fractions

lineTypes = {"solid": -1,
             "dotted": 2}

def linetype(colour=None, width=1, type = 'solid'):
    if colour != None:
        ret = 'lc rgb "%s" lw %f dashtype %s' % (colour, width, type)
    else:
        lineTypeV = lineTypes[type]
        ret = "lt %d lw %f" % (lineTypeV, width)
    return ret

def filltype(colour=None):
    if colour == None:
        ret = 'fs solid 1.0'
    else:
        ret = 'fc rgb "%s" fs solid 1.0 noborder' % (colour)
    return ret

def axisText(val):
    return {1:"", 2:"2"}[val]

class Line():
    def __init__(self, title, lineData, lineColour=None, lineWidth=1,
                 lineType='solid', plot='linespoints', pointType=7, smooth=False):
        self.title = title
        self.lineData = lineData
        self.lineColour = lineColour
        self.lineWidth = lineWidth
        self.lineType = lineType
        self.plot = plot
        self.pointType = pointType
        self.smooth = smooth

def stringifyValue(val):
    if isinstance(val, fractions.Fraction):
        return '%f' % val
    return str(val)

def emptyStringIfNone(value):
    if value != None:
        return str(value)
    return ''

def replaceSymbols(string):
    #print repr(string), repr("°"), repr('^o')
    return string.replace("°", '^o')

class PopenWithDebug():
    def __init__(self, program, debugOutName):
        self.pipe = os.popen(program, 'w')
        self.debug = open(debugOutName, 'w')
    def write(self, data):
        self.pipe.write(data)
        self.debug.write(data)
    def close(self):
        self.pipe.close()
        self.debug.close()

class Plot():
    #__slots__=()
    def __init__(self, psPath, xaxis=1, yaxis=1, output='svg'):
        self.fname = "%s.%s" % (psPath, output)
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.lines = []
        self.output = output

    def open(self,
             xtics=None, xticsRotate=0, xticsFont=None,
             ytics=None,
             ylabel=None, xlabel=None,
             margins=[6,8,2,5],
             legend=None,
             title=None,
             ymin=None, ymax=None,
             xmin=None, xmax=None,
             grid=None,
             boxWidth=.75):
        fnameDir, fnameBase = self.fname.rsplit('/',1)
        debugFname = '%s/.debug/%s.txt' % (fnameDir, fnameBase)
        self.gnuplot = PopenWithDebug('~/bin/gnuplot', debugFname)

        if self.output == 'ps':
            self.gnuplot.write('set terminal postscript color enhanced\n')
        else:
            self.gnuplot.write('set terminal %s size 1024,768\n' % self.output)

        #self.gnuplot.write('set terminal svn\n')
        self.gnuplot.write('set output "%s"\n' % (self.fname))
        if xtics != None or xticsRotate != 0 or xticsFont != None:
            rotate = ""
            if xticsRotate != 0:
                rotate = "rotate %d" % xticsRotate

            labels = ""
            if xtics != None:
                labels = "(%s)" % ', '.join(xtics)

            font = ""
            if xticsFont != None:
                font = 'font "%s"' % xticsFont

            self.gnuplot.write('set xtics %s %s %s\n' % (rotate, labels, font))
        if ylabel != None:
            self.gnuplot.write('set y%slabel "%s"\n' % (axisText(self.yaxis), replaceSymbols(ylabel)))
        if xlabel != None:
            self.gnuplot.write('set x%slabel "%s"\n' % (axisText(self.xaxis), replaceSymbols(xlabel)))


        yticLabels = ''
        if ytics != None:
            yticLabels = "(%s)" % ', '.join(ytics)
        self.gnuplot.write('unset y%stics\n' % axisText(3-self.yaxis))
        self.gnuplot.write('set y%stics %s\n' % (axisText(self.yaxis), yticLabels))
        if legend:
            self.gnuplot.write('set key %s\n' % legend)
        if title:
            self.write('set title "%s"\n' % title)
        self.gnuplot.write('set lmargin %.1f\n' % margins[0])
        self.gnuplot.write('set rmargin %.1f\n' % margins[1])
        self.gnuplot.write('set tmargin %.1f\n' % margins[2])
        self.gnuplot.write('set bmargin %.1f\n' % margins[3])

        if ymin != None or ymax != None:
            self.write('set y%srange [%s:%s]\n' % (('', '2')[self.yaxis-1], emptyStringIfNone(ymin), emptyStringIfNone(ymax)))

        if xmin != None or xmax != None:
            self.write('set x%srange [%s:%s]\n' % (('', '2')[self.xaxis-1], emptyStringIfNone(xmin), emptyStringIfNone(xmax)))
        self.write('set boxwidth %f\n' % boxWidth)
        self.write('set style fill solid 1.00 border -1\n')
        if grid != None:
            self.write('set grid %s\n' % grid)
        else:
            self.write('set grid noxtics front\n')

    def write(self, data):
        self.gnuplot.write(data)

    def addLine(self, line):
        self.lines.append(line)

    def plot(self):
        commandArgs = []
        for line in self.lines:
            plotStr = "'-'"
            if line.title != None:
                plotStr += " title '%s'" % line.title
            plotStr += " axes x%dy%d" % (self.xaxis, self.yaxis)
            if line.plot != None:
                if line.smooth:
                    plotStr += " smooth bezier"
                plotStr += " with %s" % line.plot

            if line.plot in ("lines", 'linespoints'):
                plotStr += ' ' + linetype(line.lineColour, line.lineWidth, line.lineType)
            elif line.plot in ('filledcurves', 'boxes'):
            #elif line.plot == 'filledcurves':
                plotStr += ' ' + filltype(line.lineColour)


            if line.pointType != None and line.plot in ('points', 'linespoints'):
                plotStr += ' pointtype %s' % line.pointType

            commandArgs.append(plotStr)
        self.write('plot ' + ', '.join(commandArgs) + '\n')

        for line in self.lines:
            for dataPoint in line.lineData:
                if dataPoint != None:
                    if type(dataPoint) in (type([]),type(())):
                        self.write('%s\n' % ' '.join([stringifyValue(data) for data in dataPoint]))
                    else:
                        self.write('%s\n' % dataPoint)
            self.write('e\n')


    def close(self):
        assert(self.gnuplot.close() == None)
