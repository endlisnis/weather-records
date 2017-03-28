import daily
import datetime as dt

springEquinoxes = '''
1950	Mar 20	11:35 pm EST	Jun 21	7:36 pm EDT	Sep 23	10:44 am EDT	Dec 22	5:13 am EST
1951	Mar 21	5:26 am EST	Jun 22	1:25 am EDT	Sep 23	4:37 pm EDT	Dec 22	11:00 am EST
1952	Mar 20	11:14 am EST	Jun 21	7:13 am EDT	Sep 22	10:24 pm EDT	Dec 21	4:43 pm EST
1953	Mar 20	5:01 pm EST	Jun 21	1:00 pm EDT	Sep 23	4:06 am EDT	Dec 21	10:31 pm EST
1954	Mar 20	10:53 pm EST	Jun 21	6:54 pm EDT	Sep 23	9:55 am EDT	Dec 22	4:24 am EST
1955	Mar 21	4:35 am EST	Jun 22	12:31 am EDT	Sep 23	3:41 pm EDT	Dec 22	10:11 am EST
1956	Mar 20	10:20 am EST	Jun 21	6:24 am EDT	Sep 22	9:35 pm EDT	Dec 21	3:59 pm EST
1957	Mar 20	4:16 pm EST	Jun 21	12:20 pm EDT	Sep 23	3:26 am EDT	Dec 21	9:49 pm EST
1958	Mar 20	10:06 pm EST	Jun 21	5:57 pm EDT	Sep 23	9:09 am EDT	Dec 22	3:40 am EST
1959	Mar 21	3:54 am EST	Jun 21	11:50 pm EDT	Sep 23	3:08 pm EDT	Dec 22	9:34 am EST
1960	Mar 20	9:43 am EST	Jun 21	5:42 am EDT	Sep 22	8:59 pm EDT	Dec 21	3:26 pm EST
1961	Mar 20	3:32 pm EST	Jun 21	11:30 am EDT	Sep 23	2:42 am EDT	Dec 21	9:19 pm EST
1962	Mar 20	9:30 pm EST	Jun 21	5:24 pm EDT	Sep 23	8:35 am EDT	Dec 22	3:15 am EST
1963	Mar 21	3:20 am EST	Jun 21	11:04 pm EDT	Sep 23	2:23 pm EDT	Dec 22	9:02 am EST
1964	Mar 20	9:10 am EST	Jun 21	4:57 am EDT	Sep 22	8:17 pm EDT	Dec 21	2:50 pm EST
1965	Mar 20	3:05 pm EST	Jun 21	10:56 am EDT	Sep 23	2:06 am EDT	Dec 21	8:40 pm EST
1966	Mar 20	8:53 pm EST	Jun 21	4:33 pm EDT	Sep 23	7:43 am EDT	Dec 22	2:28 am EST
1967	Mar 21	2:37 am EST	Jun 21	10:23 pm EDT	Sep 23	1:38 pm EDT	Dec 22	8:16 am EST
1968	Mar 20	8:22 am EST	Jun 21	4:13 am EDT	Sep 22	7:26 pm EDT	Dec 21	2:00 pm EST
1969	Mar 20	2:08 pm EST	Jun 21	9:55 am EDT	Sep 23	1:07 am EDT	Dec 21	7:44 pm EST
1970	Mar 20	7:56 pm EST	Jun 21	3:43 pm EDT	Sep 23	6:59 am EDT	Dec 22	1:36 am EST
1971	Mar 21	1:38 am EST	Jun 21	9:20 pm EDT	Sep 23	12:45 pm EDT	Dec 22	7:24 am EST
1972	Mar 20	7:22 am EST	Jun 21	3:06 am EDT	Sep 22	6:33 pm EDT	Dec 21	1:13 pm EST
1973	Mar 20	1:12 pm EST	Jun 21	9:01 am EDT	Sep 23	12:21 am EDT	Dec 21	7:08 pm EST
1974	Mar 20	7:07 pm EST	Jun 21	2:38 pm EDT	Sep 23	5:58 am EDT	Dec 22	12:56 am EST
1975	Mar 21	12:57 am EST	Jun 21	8:26 pm EDT	Sep 23	11:55 am EDT	Dec 22	6:46 am EST
1976	Mar 20	6:50 am EST	Jun 21	2:24 am EDT	Sep 22	5:48 pm EDT	Dec 21	12:35 pm EST
1977	Mar 20	12:42 pm EST	Jun 21	8:14 am EDT	Sep 22	11:29 pm EDT	Dec 21	6:23 pm EST
1978	Mar 20	6:33 pm EST	Jun 21	2:10 pm EDT	Sep 23	5:26 am EDT	Dec 22	12:21 am EST
1979	Mar 21	12:22 am EST	Jun 21	7:56 pm EDT	Sep 23	11:16 am EDT	Dec 22	6:10 am EST
1980	Mar 20	6:10 am EST	Jun 21	1:47 am EDT	Sep 22	5:09 pm EDT	Dec 21	11:56 am EST
1981	Mar 20	12:03 pm EST	Jun 21	7:45 am EDT	Sep 22	11:05 pm EDT	Dec 21	5:51 pm EST
1982	Mar 20	5:56 pm EST	Jun 21	1:23 pm EDT	Sep 23	4:46 am EDT	Dec 21	11:38 pm EST
1983	Mar 20	11:39 pm EST	Jun 21	7:09 pm EDT	Sep 23	10:42 am EDT	Dec 22	5:30 am EST
1984	Mar 20	5:24 am EST	Jun 21	1:02 am EDT	Sep 22	4:33 pm EDT	Dec 21	11:23 am EST
1985	Mar 20	11:14 am EST	Jun 21	6:44 am EDT	Sep 22	10:08 pm EDT	Dec 21	5:08 pm EST
1986	Mar 20	5:03 pm EST	Jun 21	12:30 pm EDT	Sep 23	3:59 am EDT	Dec 21	11:02 pm EST
1987	Mar 20	10:52 pm EST	Jun 21	6:11 pm EDT	Sep 23	9:45 am EDT	Dec 22	4:46 am EST
1988	Mar 20	4:39 am EST	Jun 20	11:57 pm EDT	Sep 22	3:29 pm EDT	Dec 21	10:28 am EST
1989	Mar 20	10:28 am EST	Jun 21	5:53 am EDT	Sep 22	9:20 pm EDT	Dec 21	4:22 pm EST
1990	Mar 20	4:19 pm EST	Jun 21	11:33 am EDT	Sep 23	2:56 am EDT	Dec 21	10:07 pm EST
1991	Mar 20	10:02 pm EST	Jun 21	5:19 pm EDT	Sep 23	8:48 am EDT	Dec 22	3:54 am EST
1992	Mar 20	3:48 am EST	Jun 20	11:14 pm EDT	Sep 22	2:43 pm EDT	Dec 21	9:43 am EST
1993	Mar 20	9:41 am EST	Jun 21	5:00 am EDT	Sep 22	8:22 pm EDT	Dec 21	3:26 pm EST
1994	Mar 20	3:28 pm EST	Jun 21	10:48 am EDT	Sep 23	2:19 am EDT	Dec 21	9:23 pm EST
1995	Mar 20	9:14 pm EST	Jun 21	4:34 pm EDT	Sep 23	8:13 am EDT	Dec 22	3:17 am EST
1996	Mar 20	3:03 am EST	Jun 20	10:24 pm EDT	Sep 22	2:00 pm EDT	Dec 21	9:06 am EST
1997	Mar 20	8:55 am EST	Jun 21	4:20 am EDT	Sep 22	7:56 pm EDT	Dec 21	3:07 pm EST
1998	Mar 20	2:55 pm EST	Jun 21	10:03 am EDT	Sep 23	1:37 am EDT	Dec 21	8:56 pm EST
1999	Mar 20	8:46 pm EST	Jun 21	3:49 pm EDT	Sep 23	7:31 am EDT	Dec 22	2:44 am EST
2000	Mar 20	2:35 am EST	Jun 20	9:48 pm EDT	Sep 22	1:28 pm EDT	Dec 21	8:37 am EST
2001	Mar 20	8:31 am EST	Jun 21	3:38 am EDT	Sep 22	7:04 pm EDT	Dec 21	2:21 pm EST
2002	Mar 20	2:16 pm EST	Jun 21	9:24 am EDT	Sep 23	12:55 am EDT	Dec 21	8:14 pm EST
2003	Mar 20	8:00 pm EST	Jun 21	3:10 pm EDT	Sep 23	6:47 am EDT	Dec 22	2:04 am EST
2004	Mar 20	1:49 am EST	Jun 20	8:57 pm EDT	Sep 22	12:30 pm EDT	Dec 21	7:42 am EST
2005	Mar 20	7:34 am EST	Jun 21	2:46 am EDT	Sep 22	6:23 pm EDT	Dec 21	1:35 pm EST
2006	Mar 20	1:25 pm EST	Jun 21	8:26 am EDT	Sep 23	12:03 am EDT	Dec 21	7:22 pm EST
2007	Mar 20	8:07 pm EDT	Jun 21	2:06 pm EDT	Sep 23	5:51 am EDT	Dec 22	1:08 am EST
2008	Mar 20	1:48 am EDT	Jun 20	7:59 pm EDT	Sep 22	11:44 am EDT	Dec 21	7:04 am EST
2009	Mar 20	7:44 am EDT	Jun 21	1:46 am EDT	Sep 22	5:19 pm EDT	Dec 21	12:47 pm EST
2010	Mar 20	1:32 pm EDT	Jun 21	7:28 am EDT	Sep 22	11:09 pm EDT	Dec 21	6:38 pm EST
2011	Mar 20	7:21 pm EDT	Jun 21	1:17 pm EDT	Sep 23	5:05 am EDT	Dec 22	12:30 am EST
2012	Mar 20	1:15 am EDT	Jun 20	7:09 pm EDT	Sep 22	10:49 am EDT	Dec 21	6:12 am EST
2013	Mar 20	7:02 am EDT	Jun 21	1:04 am EDT	Sep 22	4:44 pm EDT	Dec 21	12:11 pm EST
2014	Mar 20	12:57 pm EDT	Jun 21	6:51 am EDT	Sep 22	10:29 pm EDT	Dec 21	6:03 pm EST
2015	Mar 20	6:45 pm EDT	Jun 21	12:38 pm EDT	Sep 23	4:20 am EDT	Dec 21	11:48 pm EST
2016	Mar 20	12:30 am EDT	Jun 20	6:34 pm EDT	Sep 22	10:21 am EDT	Dec 21	5:44 am EST'''.strip()
#2017	Mar 20	6:29 am EDT	Jun 21	12:24 am EDT	Sep 22	4:02 pm EDT	Dec 21	11:28 am EST'''.strip()

data = daily.load('ottawa')
maxAndYear = []
minAndYear = []
for line in springEquinoxes.split('\n'):
    tokens = line.split()
    year = int(tokens[0])
    dayOfMonth = int(tokens[2])
    day = dt.date(year, 3, dayOfMonth)
    maxAndYear.append( (data[day].MAX_TEMP, year) )
    minAndYear.append( (data[day].MIN_TEMP, year) )
    #print(day, data[day].MAX_TEMP)
print(sorted(maxAndYear))
print(sorted(minAndYear))
