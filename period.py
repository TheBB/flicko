#!/usr/bin/python3

import atexit
import sqlite3
import sys

from flicko import *
from numpy import *
import progressbar

class Player:
    pass

if len(sys.argv) > 1:
    period = int(sys.argv[1])
else:
    period = 0

if len(sys.argv) > 2:
    initdev = float(sys.argv[2])
else:
    initdev = 0.3

db = sqlite3.connect('data.sql')
cur = db.cursor()
atexit.register(lambda: cur.close())

nrepeats = 0
nnew = 0
nmatches = 0
players = dict()
res = cur.execute('''SELECT DISTINCT p.rowid, p.race FROM players AS p, matches
                  AS m WHERE (m.pa = p.rowid OR m.pb = p.rowid) AND m.period =
                  :per''', {'per': period})
for r in res:
    p = Player()
    p.c = ['P','T','Z'].index(r[1])
    p.oppr = []
    p.opps = []
    p.oppc = []
    p.W = []
    p.L = []
    p.id = r[0]
    players[r[0]] = p

for id in players:
    ratres = cur.execute('''SELECT * FROM ratings WHERE player=:id AND
                         period=:per''', {'id': id, 'per': period-1})
    p = players[id]
    try:
        rat = next(ratres)
        p.r = array(rat[2:6])
        p.s = array(rat[6:10])
        nrepeats += 1
    except:
        p.r = zeros(4)
        p.s = initdev * ones(4)
        nnew += 1

res = cur.execute('''SELECT * FROM matches WHERE period=:per''', {'per': period})
for r in res:
    pa = players[r[1]]
    pb = players[r[2]]
    
    pa.oppr.append(list(pb.r))
    pa.opps.append(list(pb.s))
    pa.oppc.append(pb.c)
    pa.W.append(r[3])
    pa.L.append(r[4])

    pb.oppr.append(list(pa.r))
    pb.opps.append(list(pa.s))
    pb.oppc.append(pa.c)
    pb.W.append(r[4])
    pb.L.append(r[3])

    nmatches += 1

for id in players:
    p = players[id]
    p.oppr = array(p.oppr)
    p.opps = array(p.opps)
    p.oppc = array(p.oppc)
    p.W = array(p.W)
    p.L = array(p.L)

if len(players) > 0:
    progress = progressbar.ProgressBar(len(players), exp='Updating ratings')
    num = 0
    for id in players:
        progress.update_time(num)
        num += 1
        print(progress.dyn_str())

        p = players[id]
        R = update(p.r, p.s, p.c, p.oppr, p.opps, p.oppc, p.W, p.L, str(p.id))

        if R == None:
            p.newr = p.r
            p.news = p.s
        else:
            p.newr = R[0]
            p.news = R[1]

    progress.update_time(len(players))
    print(progress.dyn_str())
    print('')

num = next(cur.execute('''SELECT count(*) FROM players, ratings WHERE
                       players.rowid=ratings.player AND
                       ratings.period=:per''', {'per': period-1}))[0]
if num > 0:
    progress = progressbar.ProgressBar(num, exp='Decaying ratings')
    n = 0
    res = cur.execute('''SELECT * FROM ratings WHERE period=:per''',\
                      {'per': period-1})
    storeres = []
    for r in res:
        storeres.append(r)

    for r in storeres:
        progress.update_time(n)
        n += 1
        print(progress.dyn_str())

        if r[0] in players.keys():
            continue

        (k, news) = update([], array(r[6:10]), [], [], [], [], [], [], str(r[0]))

        cur.execute('''INSERT INTO ratings VALUES (:id, :per, :r, :rp, :rt,
                    :rz, :d, :dp, :dt, :dz)''',\
                    {'id': r[0], 'per': period, 'r': r[2], 'rp': r[3],\
                     'rt': r[4], 'rz': r[5], 'd': news[0], 'dp': news[1],\
                     'dt': news[2], 'dz': news[3]})

    progress.update_time(num)
    print(progress.dyn_str())
    print('')

for id in players:
    p = players[id]

    cur.execute('''INSERT INTO ratings VALUES (:id, :per, :r, :rp, :rt,
                :rz, :d, :dp, :dt, :dz)''',\
                {'id': id, 'per': period,\
                 'r': p.newr[0], 'rp': p.newr[1], 'rt': p.newr[2], 'rz': p.newr[3],\
                 'd': p.news[0], 'dp': p.news[1], 'dt': p.news[2], 'dz': p.news[3]})

res = cur.execute('SELECT start, end FROM periods WHERE rowid=:period',\
                  {'period': period+1})
res = next(res)

t = 'Period ' + str(period+1) + ': ' + res[0] + ' to ' + res[1]
print(t)
a = str(nrepeats) + ' returning and ' + str(nnew) + ' new players played ' +\
        str(nmatches) + ' matches.'
print(a)
t += '\n' + a + '\n'

top = []
bottom = []
res = cur.execute('''SELECT p.name, r.rating FROM players as p, ratings as r
                  WHERE p.rowid=r.player AND r.period=:period ORDER BY r.rating
                  DESC LIMIT 10''', {'period': period})
for r in res:
    top.append((r[0], r[1]))

for i in range(0,10):
    a = '{n:>2}. {name: <15} '.format(n=i+1, name=top[i][0])
    t += '\n' + a

    a = '{r:<2.4f}'.format(r=top[i][1])
    t += a

t += '\n\n'
with open('pres','a') as f:
    f.write(t)

db.commit()
