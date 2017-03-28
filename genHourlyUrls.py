#!/usr/bin/python3
# -*- coding: utf-8 -*-

#import datetime, time, sys

#for hourdiff in range(1,24):
#   hourtime = datetime.datetime.utcfromtimestamp(time.time()-hourdiff*3600)
#   hourstring = ( '%04d%02d%02d%02d'
#                  % (hourtime.year, hourtime.month, hourtime.day, hourtime.hour) )
#   print hourstring

import urllib.request, sys, re, os

def main(province):
   directory = "http://dd.weatheroffice.ec.gc.ca/observations/xml/%s/hourly/" % province
   f = urllib.request.urlopen(directory)
   myfile = f.read().decode()

   xmlFilenames = []
   for line in myfile.split('\n'):
      match = re.search('>(hourly.*_e.xml)<', line)
      if match != None:
         #print match.groups()[0]
         xmlFilenames.append(match.groups()[0])
   xmlFilenames = xmlFilenames[-48:]


   try:
      os.mkdir(province)
   except OSError as err:
      if err.errno != 17: #exists
         raise

   localFiles = os.listdir(province)
   for localFile in localFiles:
      if localFile not in xmlFilenames:
         localPath = '%s/%s' % (province, localFile)
         print("Removing old file '%s'" % localPath, file=sys.stderr)
         os.unlink( localPath )

   return ' '.join([os.path.join(province, x) for x in xmlFilenames])

if __name__=='__main__':
   print(main(sys.argv[1]))
