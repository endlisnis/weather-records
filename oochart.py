#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pyoo
desktop = pyoo.Desktop('localhost', 2002)
doc = desktop.create_spreadsheet()
sheet = doc.sheets[0]

a = '''1873 146.1
1874 292.6
1875 231.9
1876 293.4
1877 171.3
1879 185.8
1880 165.8
1881 114.9
1883 162.5
1884 199.2
1885 122.2
1886 203.7
1887 258.6
1888 166.0
1889 119.3
1890 105.4
1891 172.2
1892 174.6
1893 185.4
1894 219.4
1895 208.1
1896 176.0
1897 100.4
1898 187.6
1899 137.4
1900 96.1
1901 190.4
1902 221.1
1903 198.8
1904 219.4
1905 188.3
1906 102.5
1907 131.3
1908 222.4
1909 194.2
1910 101.0
1911 165.5
1912 138.7
1913 189.8
1914 152.0
1915 178.9
1916 172.3
1917 190.0
1918 228.6
1919 130.7
1920 153.4
1921 113.1
1922 172.4
1923 161.9
1924 174.5
1925 115.2
1926 111.1
1927 201.9
1928 147.2
1929 103.8
1930 136.4
1931 132.6
1932 85.7
1933 96.6
1934 213.1
1935 140.9
1936 125.8
1937 80.2
1938 98.6
1939 129.8
1940 118.8
1941 189.3
1942 139.8
1943 219.2
1944 108.1
1945 202.7
1946 124.2
1947 194.7
1948 100.1
1949 137.2
1950 124.5
1951 151.5
1952 181.6
1953 90.0
1954 131.2
1955 174.6
1956 108.2
1957 129.7
1958 123.8
1959 182.0
1960 199.6
1961 86.2
1962 102.3
1963 126.5
1964 93.3
1965 150.5
1966 194.5
1967 181.1
1968 172.5
1969 162.2
1970 169.4
1971 305.3
1972 207.9
1973 192.2
1974 147.0
1975 143.8
1976 141.0
1977 139.8
1978 199.6
1979 192.5
1980 93.9
1981 147.0
1982 149.3
1983 72.8
1984 193.2
1985 160.9
1986 118.7
1987 133.2
1988 171.6
1989 148.0
1990 186.2
1991 148.0
1992 157.0
1993 171.0
1994 149.7
1995 129.7
1996 229.9
1997 177.6
1998 187.2
1999 129.0
2000 137.8
2001 199.8
2002 104.6
2003 140.0
2004 114.6
2005 129.5
2006 177.1
2007 83.4
2008 305.0
2009 214.4
2010 90.6
2011 103.7
2012 79.7
2013 179.8
2014 186.8
2015 146.0
2016 135.5'''
b = a.split('\n')

for index, row in enumerate(b):
    (year, val) = row.split()
    year = int(year)
    val = float(val)
    #sheet[0,0].value = 1
    sheet[index,0].value = year
    sheet[index,1].value = val

chart = sheet.charts.create('My Chart', sheet[0:30, 3:10], sheet[0:len(b), 0:1])
