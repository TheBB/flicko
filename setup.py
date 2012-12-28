#!/usr/bin/python3

from math import ceil
import sys
import atexit
import subprocess
import sqlite3

import params

subprocess.call(['cp', 'data_pristine.sql', 'data.sql'])
db = sqlite3.connect('data.sql')
cur = db.cursor()
atexit.register(lambda: cur.close())

cur.execute('ALTER TABLE matches ADD COLUMN period integer')
cur.execute('CREATE TABLE periods (start text, end text)')
db.commit()

start = next(cur.execute('''SELECT julianday(date) FROM matches 
                         ORDER BY date ASC LIMIT 1'''))[0]
end = next(cur.execute('''SELECT julianday(date) FROM matches ORDER BY date
                       DESC LIMIT 1'''))[0]
nperiods = ceil((end-start)/params.per_length)

for period in range(0,nperiods):
    cur.execute('''UPDATE matches SET period=:per WHERE 
                julianday(date)>=:pstart AND julianday(date)<:pend''',
                {'per': period, 'pstart': start, 'pend': start+params.per_length})
    cur.execute('''INSERT INTO periods VALUES (date(:start), date(:end-1))''',\
                {'start': start, 'end': start+params.per_length})
    start += params.per_length
db.commit()

cur.execute('''CREATE TABLE ratings (player integer, period integer, rating
            real, ratingvp real, ratingvt real, ratingvz real, dev real, devvp
           real, devvt real, devvz real)''')
db.commit()

res = cur.execute('SELECT rowid FROM players WHERE race=\'?\' OR race=\'R\'')
dels = []
for r in res:
    dels.append(r[0])
for d in dels:
    cur.execute('''DELETE FROM matches WHERE pa=:id OR pb=:id''', {'id': d})
cur.execute('DELETE FROM players WHERE race=\'?\' OR race=\'R\'')
db.commit()

print('Set up ' + str(nperiods) + ' periods (0-' + str(nperiods-1) + ')')
