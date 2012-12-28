#!/usr/bin/python3

import subprocess
import sqlite3

subprocess.call(['./setup.py'])
subprocess.call(['rm', 'pres'])

db = sqlite3.connect('data.sql')
cur = db.cursor()
r = next(cur.execute('SELECT min(rowid), max(rowid) FROM periods'))
low = r[0]-1
high = r[1]
cur.close()

for i in range(low,high):
    subprocess.call(['./period.py', str(i)])

subprocess.call(['./plot.py'])
