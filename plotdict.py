# -*- coding: utf-8 -*-
from reversedict import reverseDict
import gnuplot
import numpy

def plotdict(valueByYear, filename, chartTitle, yaxisLabel, thisYear,
             plotZeros=True, output='svg', ymin=None,
             showAverage=True):
    yearByValue = reverseDict(valueByYear)
    values = sorted(yearByValue.keys())
    #
    chartTicks = []
    chartDataOtherYears = []
    chartDataThisYear = []
    chartIndex = 0
    maxValue = max(values)

    if showAverage:
        recentYears = tuple(filter(lambda t: t in valueByYear, range(thisYear-30, thisYear)))
        recentValues = [valueByYear[t] for t in recentYears]
        recentAvg = sum(recentValues) / len(recentValues)
        recentStd = numpy.std(tuple(map(float, recentValues)))

    longestXTick = 0
    for value in values:
        # number of years with this value
        #print 'val="%s"' % value
        thiscount = len(yearByValue[value])
        #
        if plotZeros == False and value == 0:
            # We've been told to skip zeros, so we don't plot them
            continue

        for year in yearByValue[value]:
            if year == thisYear:
                chartDataThisYear.append((chartIndex, value, '# ' + str(year)))
            else:
                chartDataOtherYears.append((chartIndex, value, '# ' + str(year)))
            xtick = str(year)
            longestXTick = max(longestXTick, len(xtick))
            chartTicks.append('"{date}" {index}'.format(date=xtick, index=chartIndex))
            chartIndex += 1

    legend = 'on left'
    if maxValue < 0:
        legend = 'on right bottom'
    bmargin = 2+longestXTick//2

    plot = gnuplot.Plot(filename, yaxis=2, output=output)
    #
    #, xticsFont='Arial,10'
    plot.open(title=chartTitle,
              xtics=chartTicks, xticsRotate=90, xticsFont='Arial,20', legend=legend,
              margins=[6,8,2,bmargin],
              ylabel=yaxisLabel, ymin=ymin,
              xmin=-1, xmax=chartIndex)
    if showAverage:
        plot.addLine(gnuplot.Line('30-year 2*std-dev',  ((-1,recentAvg-recentStd*2),(chartIndex,recentAvg-recentStd*2),(chartIndex,recentAvg+recentStd*2),(-1,recentAvg+recentStd*2)), lineColour='#f1f1f1', plot='filledcurves'))
        plot.addLine(gnuplot.Line('30-year std-dev',  ((-1,recentAvg-recentStd),(chartIndex,recentAvg-recentStd),(chartIndex,recentAvg+recentStd),(-1,recentAvg+recentStd)), lineColour='#e3e3e3', plot='filledcurves'))
        plot.addLine(gnuplot.Line('30-year average', ((-1,recentAvg),(chartIndex,recentAvg)), lineColour='0x000000'))
    plot.addLine(gnuplot.Line('Other years', chartDataOtherYears, plot='boxes', lineColour='0x6495ED'))
    plot.addLine(gnuplot.Line('This year', chartDataThisYear, plot='boxes', lineColour='0x556B2F'))
    plot.plot()
    plot.close()
    return plot.fname
