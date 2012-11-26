#!/usr/bin/python3

from numpy import *

class Player:
    pass

def update(player, opponents, wins, losses):

    mu = zeros(len(opponents))
    s = zeros(len(opponents))
    pd = zeros(len(opponents))
    D_delta = zeros((len(opponents), 1+len(player.cat_rating)))
    D_delta[:,0] = 1
    for j in range(0,len(opponents)):
        opp = opponents[j]
        mu[j] = (opp.rating - sqrt(3) * opp.cat_rating[player.cat]) / sqrt(6)
        s[j] = sqrt((1/6*opp.dev**2 + 1/2*opp.cat_dev[player.cat]**2 + 1/9*pi)*3/pi**2)
        pd[j] = opp.rating + opp.cat_rating[player.cat]
        D_delta[j,opp.cat+1] = 1

    delta = lambda x,j: x[0] + x[opponents[j].cat+1] - pd[j]
    l = lambda x,j: 1/(1 + exp(-(delta(x,j)+mu[j])/s[j]))
    w = lambda x,j: 1/(1 + exp( (delta(x,j)+mu[j])/s[j]))
    g = lambda y: y**2 * 1/(1/y-1)

    def Dlog(x):
        ret = zeros(1+len(player.cat_rating))
        for j in range(0,len(opponents)):
            ret += (losses[j]*l(x,j) - wins[j]*w(x,j)) * D_delta[j,:] / s[j]
        return ret

    def D2log(x):
        ret = zeros((1+len(player.cat_rating), 1+len(player.cat_rating)))
        for j in range(0,len(opponents)):
            ret += (losses[j]*g(l(x,j)) - wins[j]*g(w(x,j))) *\
                    outer(D_delta[j,:],D_delta[j,:]) / s[j]**2
        return ret

    x = zeros(1+len(player.cat_rating))
    x[0] = player.rating
    for c in range(0,len(player.cat_rating)):
        x[c+1] = player.cat_rating[c]

    for i in range(0,5):
        D = Dlog(x)
        D2 = D2log(x)
        (q,residues,rank,s) = linalg.lstsq(D2,D)
        x = x - 1e-2*q
        print(x)

p = Player()
p.rating = 0
p.dev = 10
p.cat_rating = [0, 0, 0]
p.cat_dev = [10, 10, 10]
p.cat = 0

q = Player()
q.rating = 0
q.dev = 10
q.cat_rating = [0, 0, 0]
q.cat_dev = [10, 10, 10]
q.cat = 0

update(p, [q], [3], [1])
