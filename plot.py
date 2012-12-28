#!/usr/bin/python

import sqlite3
from scipy.stats import norm
import numpy
from math import floor, sqrt
import pylab
import params

nsl = 15

class Match:
    pass

db = sqlite3.connect('data.sql')
cur = db.cursor()

res = cur.execute('''SELECT p1.name, p2.name, p1.race, p2.race, m.sa, m.sb,
                  r1.rating, r1.ratingvp, r1.ratingvt, r1.ratingvz,
                  r1.dev, r1.devvp, r1.devvt, r1.devvz,
                  r2.rating, r2.ratingvp, r2.ratingvt, r2.ratingvz,
                  r2.dev, r2.devvp, r2.devvt, r2.devvz
                  FROM matches AS m, ratings AS r1, ratings AS r2,
                  players AS p1, players AS p2 
                  WHERE r1.player=m.pa AND r2.player=m.pb AND
                  r1.period=m.period-1 AND r2.period=m.period-1 AND
                  p1.rowid=m.pa AND p2.rowid=m.pb AND m.period>=0''')

matches = []
for r in res:
    if r[4] + r[5] == 0:
        continue

    m = Match()
    m.paname = r[0]
    m.pbname = r[1]
    m.parace = ['P','T','Z'].index(r[2])
    m.pbrace = ['P','T','Z'].index(r[3])
    m.pascore = r[4]
    m.pbscore = r[5]
    m.parating = r[6] + r[7+m.pbrace]
    m.pbrating = r[14] + r[15+m.parace]
    m.padev = r[10]**2 + r[11+m.pbrace]**2
    m.pbdev = r[18]**2 + r[19+m.parace]**2
    matches.append(m)

cur.close()

table_w = [0]*nsl
table_l = [0]*nsl
games = 0

for m in matches:
    #prob = norm.cdf(m.parating-m.pbrating, scale=sqrt(1+m.padev+m.pbdev))
    prob = norm.cdf(1.00*(m.parating-m.pbrating), scale=1)
    act = float(m.pascore) / float(m.pascore + m.pbscore)

    if prob < 0.5:
        p = 1-prob
        (na,nb) = (m.pbscore, m.pascore)
    else:
        p = prob
        (na,nb) = (m.pascore, m.pbscore)
    S = int(floor((p-0.5)*nsl))

    table_w[S] += na
    table_l[S] += nb
    games += na + nb

    if False:
        q = ('{na: >15} ({ra:<+7.4f}) {sa: >2}-{sb: <2} ({rb:<+7.4f}) {nb: <15}' +\
             '{prob:5.2f}% {act:6.2f}% {s: >2}').\
                format(na=m.paname, nb=m.pbname, ra=m.parating, rb=m.pbrating,\
                       sa=m.pascore, sb=m.pbscore, prob=100*prob, act=100*act,\
                       s=S)
        print(q)

table_g = [float(table_w[i]+table_l[i]) for i in range(0,len(table_w))\
           if table_w[i] > 0 and table_l[i] > 0]
zones = []
fracs = []
slw = float(50)/nsl
for i in range(0,nsl):
    if table_w[i] + table_l[i] == 0:
        continue

    zones.append(50.0+slw*(i+0.5))
    fracs.append(float(table_w[i]) / float(table_w[i] + table_l[i]))
    print('{zone:5.2f}%: {frac:6.2f}% ({n})'.format(zone=zones[-1],\
                                                    frac=100*fracs[-1],\
                                                    n=table_g[i]))

I = 0
while I < len(table_g) and table_g[I] > 0:
    I += 1
M = max(table_g)

a = numpy.polynomial.polynomial.polyfit(zones[0:I],[100*f for f in fracs][0:I]\
                                        ,1,w=table_g[0:I])
p1, = pylab.plot(zones, [100*f for f in fracs], '#000000', marker='o', linewidth=2)
p2, = pylab.plot(zones, zones, '#ff0000', linestyle='--')
p3, = pylab.plot([zones[0],zones[-1]], [a[0]+a[1]*zones[0],a[0]+a[1]*zones[-1]],\
                 '#0000ff', linestyle='--')
pylab.axis([50,80,50,80])
pylab.grid()
pylab.xlabel('Predicted winrate')
pylab.ylabel('Actual winrate')

ax = pylab.twinx()
ax.set_ylabel('Games')
p4, = ax.plot(zones, table_g, '#000000', linestyle='--')

pylab.legend([p2,p3,p4], ['ideal','fitted','games'], loc=8)
pylab.title('decay=%.2f init=%.2f floor=%.2f period=%i' % (params.var_decay,\
           params.init_dev, params.min_dev, params.per_length))

pylab.show()
