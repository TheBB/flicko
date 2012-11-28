#!/usr/bin/python3

import time

from numpy import *
from scipy.stats import norm
from math import log
import scipy.optimize as opt

class Player:
    pass

def new_dev(old_dev):
    return old_dev

def update_noplay(player):
    pass

def update(player, opps, W, L):

    if len(opps) == 0:
        update_noplay(player)

    tot_catrating = 0
    categories = []
    for j in range(0,len(opps)):
        if opps[j].cat not in categories:
            categories.append(opps[j].cat)
            tot_catrating += player.cat_rating[opps[j].cat]

    N = len(categories)

    mu = zeros(len(opps))
    s = zeros(len(opps))
    q = zeros((len(opps), N))
    p = zeros((len(opps), N+1))
    q[:,0] = 1
    p[:,0] = 1
    for j in range(0,len(opps)):
        opp = opps[j]
        mu[j] = 2*(opp.rating + opp.cat_rating[player.cat])
        s[j] = sqrt(1 + opp.dev**2 + opp.cat_dev[player.cat]**2)
        if categories.index(opp.cat) < N - 1:
            q[j,1+categories.index(opp.cat)] = 1
        else:
            q[j,1:] = -1
        p[j,1+categories.index(opp.cat)] = 1

    def make_cats(x):
        cats = zeros(N)
        if N > 1:
            cats[:-1] = x[1:]
            cats[-1] = tot_catrating - sum(x[1:])
        else:
            cats = [tot_catrating]
        return cats

    def logL(x):
        ret = 0
        cats = make_cats(x)
        for j in range(0,len(opps)):
            t = x[0] + cats[categories.index(opps[j].cat)]
            Phi = norm.cdf(t, loc=mu[j], scale=s[j])
            ret += W[j]*log(Phi) + L[j]*log(1-Phi)
        return -ret

    def DlogL(x):
        ret = zeros(N)
        cats = make_cats(x)
        for j in range(0,len(opps)):
            t = x[0] + cats[categories.index(opps[j].cat)]
            phi = norm.pdf(t, loc=mu[j], scale=s[j])
            Phi = norm.cdf(t, loc=mu[j], scale=s[j])
            ret += (W[j]/Phi - L[j]/(1-Phi))*phi * q[j,:]
        return -ret

    def D2logL(x):
        ret = zeros((N,N))
        cats = make_cats(x)
        for j in range(0,len(opps)):
            t = x[0] + cats[categories.index(opps[j].cat)]
            phi = norm.pdf(t, loc=mu[j], scale=s[j])
            Phi = norm.cdf(t, loc=mu[j], scale=s[j])
            val = -(W[j]/Phi**2 + L[j]/(1-Phi)**2) * phi**2
            val -= (W[j]/Phi - L[j]/(1-Phi))*phi*(t-mu[j])/s[j]**2
            ret += val * outer(q[j,:], q[j,:])
        return -ret

    def D2logLmod(x,cats):
        ret = zeros((N+1,N+1))
        for j in range(0,len(opps)):
            t = x + cats[categories.index(opps[j].cat)]
            phi = norm.pdf(t, loc=mu[j], scale=s[j])
            Phi = norm.cdf(t, loc=mu[j], scale=s[j])
            val = -(W[j]/Phi**2 + L[j]/(1-Phi)**2) * phi**2
            val -= (W[j]/Phi - L[j]/(1-Phi))*phi*(t-mu[j])/s[j]**2
            ret += val * outer(p[j,:], p[j,:])
        return -ret

    x = zeros(N)
    x[0] = player.rating
    for c in range(0,len(categories)-1):
        x[1+c] = player.cat_rating[categories[c]]

    ret = opt.fmin_bfgs(logL, x, fprime=DlogL, full_output=True, disp=False)
    if ret[6] > 0:
        print('Unable to converge')
        return False
    x = ret[0]

    if N == 1:
        x = [x]

    gen_mod = x[0]
    cat_mod = make_cats(x)
    dev = sqrt(1/diag(D2logLmod(x[0], make_cats(x))))
    gen_dev = dev[0]
    cat_dev = dev[1:]

    player.new_dev = sqrt(1/(1/player.dev**2 + 1/gen_dev**2))
    player.new_rating = (player.rating/player.dev**2 + gen_mod/gen_dev**2) *\
            player.new_dev**2

    player.new_cat_dev = [0] * len(player.cat_dev)
    player.new_cat_rating = [0] * len(player.cat_rating)
    for c in range(0,len(player.cat_dev)):
        if c in categories:
            i = categories.index(c)
            player.new_cat_dev[c] = sqrt(1/(1/player.cat_dev[c]**2 +\
                                            1/cat_dev[i]**2))
            player.new_cat_rating[c] = (player.cat_rating[c]/player.cat_dev[c]**2 +\
                    cat_mod[c]/cat_dev[c]**2) * player.new_cat_dev[c]**2
        else:
            player.new_cat_dev[c] = new_dev(player.cat_dev[i])
            player.new_cat_rating[c] = player.cat_rating[c]

    m = mean(player.new_cat_rating)
    player.new_cat_rating -= m

p = Player()
p.rating = 0
p.cat_rating = [0, 0, 0]
p.dev = 1
p.cat_dev = [1, 1, 1]
p.cat = 0

opps = []

q = Player()
q.rating = 0
q.cat_rating = [0, 0, 0]
q.dev = 1
q.cat_dev = [1, 1, 1]
q.cat = 0
opps += [q]

q = Player()
q.rating = 0
q.cat_rating = [0, 0, 0]
q.dev = 1
q.cat_dev = [1, 1, 1]
q.cat = 1
opps += [q]

q = Player()
q.rating = 0
q.cat_rating = [0, 0, 0]
q.dev = 1
q.cat_dev = [1, 1, 1]
q.cat = 2
opps += [q]

t = time.clock()
for i in range(0,300):
    update(p, opps, [3, 3, 3], [1, 3, 3])
t = time.clock() - t
print('{t:.2f}'.format(t=t))

#print(p.new_rating)
#print(p.new_cat_rating)
#print(p.new_dev)
#print(p.new_cat_dev)
