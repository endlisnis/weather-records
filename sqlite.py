import sqlite3
conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS temperatures')
c.execute('CREATE TABLE temperatures (date text PRIMARY KEY, temperature real)')
for i in range(100000):
    c.execute('INSERT INTO temperatures VALUES ("2016-01-{}", 4.5)'.format(i))
#c.execute('REPLACE INTO temperatures VALUES ("2016-01-01", 4.6)')
c.execute('SELECT * FROM temperatures')
tuple(c)
