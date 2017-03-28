import types, time
from __future__ import print_function

gridInterval = 5

psfile = None

# page is 66x51

xrange = [999999999999,0]
yrange = [999999999999,0]

xscale = [1,2]
yscale = [30,1]

def updateRange(x, y):
    for i in ((x,xrange), (y,yrange)):
	i[1][0] = min(i[1][0], i[0])
	i[1][1] = max(i[1][1], i[0])

def linear(val, scale):
    return scale[0] + val * scale[1]

def header(title, creator):
    global psfile
    psfile = file(title, 'wb')
    print >> psfile, "%!PS-Adobe-2.0"
    print >> psfile, "%%%%Title: %s" % title
    print >> psfile, "%%%%Creator: %s" % creator
    print >> psfile, "%%CreationDate: %s" % time.asctime()
    print >> psfile, "%%DocumentFonts: (atend)"
    print >> psfile, "%%Orientation: Landscape"
    print >> psfile, "%%Pages: 1"
    print >> psfile, "%%EndComments"
    print >> psfile, "%%BeginProlog"
    print >> psfile, "%%EndProlog"
    print >> psfile, "%%Page: 1 1"
    print >> psfile, "90 rotate"
    print >> psfile, "0 -615 translate"
    print >> psfile, "12 12 scale"
    print >> psfile, ".2 setlinewidth"
    print >> psfile, "1 setlinejoin"
    print >> psfile, "1 setlinecap"
    print >> psfile, "/Times-Roman findfont"
    print >> psfile, "1 scalefont"
    print >> psfile, "setfont"


class Line():
    def __init__(self, linelist, colour, dash):
	self.linelist = []
	for index in range(len(linelist)):
	    point = linelist[index]

	    if point == None or (type(point) == types.TupleType and point[1] == None):
		continue

	    if type(point) == types.FloatType:
		self.linelist.append((index, point));
	    else:
		self.linelist.append(point)
	    updateRange(self.linelist[-1][0], self.linelist[-1][1])

	self.colour = colour
	self.dash = dash

    def plot(self):
	print >> psfile, "newpath"
	print >> psfile, "%s setrgbcolor" % self.colour
	print >> psfile, "%s setdash" % self.dash

	command = "moveto"

	for index in range(len(self.linelist)):
	    point = self.linelist[index]

	    print >> psfile, "%f %f %s" % (linear(point[0], xscale), linear(point[1], yscale), command)
	    command = "lineto"

	print >> psfile, "stroke"

class Text():
    def __init__(self, text, x, y, colour):
	self.x = x
	self.y = y
	self.text = text
	self.colour = colour

    def plot(self):
	print >> psfile, "%s setrgbcolor" % self.colour
	print >> psfile, "newpath"
	print >> psfile, "%f %f moveto" % (linear(self.x, xscale), linear(self.y, yscale))
	print >> psfile, "(%s) show" % self.text


lines = []

def updateScale():
    # page is 66x51
    print xrange, yrange
    xpage = [3,62]
    ypage = [1,50]

    xscale[1] = float(xpage[1]-xpage[0])/(xrange[1]-xrange[0])
    xscale[0] = xpage[0] - xscale[1]*xrange[0]

    yscale[1] = float(ypage[1]-ypage[0])/(yrange[1]-yrange[0])
    yscale[0] = ypage[0] - yscale[1]*yrange[0]

def plotline(linelist, colour = "0 0 0", dash="[] 0", front=0):
    line = Line(linelist, colour, dash)

    if front:
	lines.insert(0, line)
    else:
	lines.append(line)

def printText(x, y, text, colour = "0 0 0"):
    lines.append(Text(text, x, y, colour))

def showPage():
    updateScale()

    for y in range(int(yrange[0] / gridInterval) * gridInterval,
		   int(yrange[1] / gridInterval + 1) * gridInterval,
		   gridInterval):
	plotline( [(xrange[0], y), (xrange[1], y)], colour="0.7 0.7 0.7", dash="[0.2 0.5] 0", front=1)
	printText(xrange[0]-1, y, '%d' % y)
	printText(xrange[1]+1, y, '%d' % y)

    for line in lines:
	line.plot()
    print >> psfile, "showpage"

def trailer():
    print >> psfile, "%%Trailer"
    print >> psfile, "%%DocumentFonts: Helvetica"
    #print xrange, yrange
    #print xscale, yscale
