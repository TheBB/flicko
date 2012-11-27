#!/usr/bin/python3

import time

from numpy import *
from scipy.stats import norm
from math import log
import scipy.optimize as opt

class Player:
    pass

def update(player, opps, W, L):

    mu = zeros(len(opps))
    s = zeros(len(opps))
    q = zeros((len(opps), len(player.cat_rating)))
    q[:,0] = 1
    for j in range(0,len(opps)):
        opp = opps[j]
        mu[j] = 2*(opp.rating + opp.cat_rating[player.cat])
        s[j] = sqrt(1 + opp.dev**2 + opp.cat_dev[player.cat]**2)
        if opp.cat < len(player.cat_rating) - 1:
            q[j,opp.cat+1] = 1
        else:
            q[j,1:] = -1

    def make_cats(x):
        cats = zeros(len(x))
        cats[:-1] = x[1:]
        cats[-1] = 1 - sum(x)
        return cats

    def logL(x):
        ret = 0
        cats = make_cats(x)
        for j in range(0,len(opps)):
            t = x[0] + cats[opps[j].cat]
            Phi = norm.cdf(t, loc=mu[j], scale=s[j])
            ret += W[j]*log(Phi) + L[j]*log(1-Phi)
        return -ret

    def DlogL(x):
        ret = zeros(len(x))
        cats = make_cats(x)
        for j in range(0,len(opps)):
            t = x[0] + cats[opps[j].cat]
            phi = norm.pdf(t, loc=mu[j], scale=s[j])
            Phi = norm.cdf(t, loc=mu[j], scale=s[j])
            ret += (W[j]/Phi - L[j]/(1-Phi))*phi * q[j,:]
        return -ret

    def D2logL(x):
        ret = zeros((len(x),len(x)))
        cats = make_cats(x)
        for j in range(0,len(opps)):
            t = x[0] + cats[opps[j].cat]
            phi = norm.pdf(t, loc=mu[j], scale=s[j])
            Phi = norm.cdf(t, loc=mu[j], scale=s[j])
            val = -(W[j]/Phi**2 + L[j]/(1-Phi)**2) * phi**2
            val -= (W[j]/Phi - L[j]/(1-Phi))*phi*(t-mu[j])/s[j]**2
            ret += val * outer(q[j,:], q[j,:])
        return -ret

    x = zeros(len(player.cat_rating))
    x[0] = player.rating
    for c in range(0,len(player.cat_rating)-1):
        x[1+c] = player.cat_rating[c]

    if False:
        start = time.clock()
        for i in range(0,100):
            opt.fmin(logL, x, disp=False)
        end = time.clock()
        print('Downhill simplex: {t:.2f} seconds.'.format(t=end-start))

        start = time.clock()
        for i in range(0,100):
            opt.fmin_powell(logL, x, disp=False)
        end = time.clock()
        print('Powell: {t:.2f} seconds.'.format(t=end-start))

        start = time.clock()
        for i in range(0,100):
            opt.fmin_cg(logL, x, fprime=DlogL, disp=False)
        end = time.clock()
        print('CG: {t:.2f} seconds.'.format(t=end-start))

        start = time.clock()
        for i in range(0,100):
            opt.fmin_bfgs(logL, x, fprime=DlogL, disp=False)
        end = time.clock()
        print('BFGS: {t:.2f} seconds.'.format(t=end-start))

        start = time.clock()
        for i in range(0,100):
            opt.fmin_ncg(logL, x, fprime=DlogL, fhess=D2logL, disp=False)
        end = time.clock()
        print('Newton-CG: {t:.2f} seconds.'.format(t=end-start))

    x = opt.fmin_bfgs(logL, x, fprime=DlogL, disp=True)
    print(x)
    #print(D2logL(x))
    #print(linalg.det(D2logL(x)))

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

#q = Player()
#q.rating = 10
#q.cat_rating = [0, 0, 0]
#q.dev = 1
#q.cat_dev = [1, 1, 1]
#q.cat = 1
#opps += [q]

update(p, opps, [3, 3], [1, 3])
