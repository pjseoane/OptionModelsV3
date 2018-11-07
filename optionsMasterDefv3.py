"""
Linea 1, Branch2
"""
import math
import sys

import numpy as np
from scipy import stats

sys.path.append('C:/Users/pauli/Dropbox/Python/optionModelsDEF')
sys.path.append('C:/Users/pseoane/Dropbox/Python/optionModelsDEF')

def payoff(underlying, strike, cp):
    return max((underlying - strike) * cp, 0)

def driftCalc(contract, rf, h):
    return (1 if (contract == "F") else math.exp(rf * h))

def fillDerivativesArray(prima, delta, gamma, vega, theta, rho,impVlt,cont):
    derivatives = np.zeros(10)
    derivatives[0] = prima
    derivatives[1] = delta
    derivatives[2] = gamma
    derivatives[3] = vega
    derivatives[4] = theta
    derivatives[5] = rho
    derivatives[6]=  impVlt
    derivatives[7]=  cont
    return derivatives

def binomJRv2(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
            steps=1000,valueToFind=6,mktValue=0):
    """ Price and option using the Jarrow-Rudd binomial model"""


    # Basic calculations
    h = life_days / 365 / steps
    u = math.exp((rf - 0.5 * math.pow(vol, 2)) * h + vol * math.sqrt(h))
    d = math.exp((rf - 0.5 * math.pow(vol, 2)) * h - vol * math.sqrt(h))

    drift = driftCalc(contract, rf, h)

    q = (drift - d) / (u - d)
    qx = 1 - q

    # Process the terminal stock price
    stkval = np.zeros((steps + 1, steps + 1))
    optval = np.zeros((steps + 1, steps + 1))
    stkval[0, 0] = underlying

    for i in range(1, steps + 1):
        stkval[i, 0] = stkval[i - 1, 0] * u
        for j in range(1, i + 1):
            stkval[i, j] = stkval[i - 1, j - 1] * d

    # Backward recursion for option price
    for j in range(steps + 1):
        optval[steps, j] = max(0, payoff(stkval[steps, j], strike, cp))

    for m in range(steps):
        i = steps - m - 1
        for j in range(i + 1):
            optval[i, j] = (q * optval[i + 1, j] + qx * optval[i + 1, j + 1]) / drift

            if american:
                optval[i, j] = max(optval[i, j], payoff(stkval[i, j], strike, cp))

    if (valueToFind==0):
        return (optval[0,0])
    else:
        prima=optval[0,0]
        delta=(optval[1,1]-optval[1,0])/(stkval[1,1]-stkval[1,0])
        vega=binomJRv2(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div,american, steps, 0,0) - prima
        gamma=((optval[2,0]-optval[2,1])/(stkval[2,0]-stkval[2,1])-(optval[2,1]-optval[2,2])/(stkval[2,1]-stkval[2,2])) / ((stkval[2,0]-stkval[2,2])/2)
        theta=(optval[2,1]-optval[0,0])/(2*365*h)
        rho=binomJRv2(contract, underlying, strike, life_days, vol, rf+0.01, cp, div,american, steps, 0,0) - prima

        cont = 0
        impliedVol = vol
        if mktValue > 0:
            accuracy = 0.0001
            #cont = 0
            dif = mktValue - prima
            #impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                impliedVol += (dif / vega / 100)
                dif = mktValue - binomJRv2(contract, underlying, strike, life_days, impliedVol, rf, cp, div,american, steps, 0,0)
                cont += 1
                    # vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
        #else:
        #    impliedVol = vol
        return fillDerivativesArray(prima,delta,gamma,vega,theta,rho,impliedVol,cont)


def binomCRR3v2(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
                steps=1000, valueToFind=6,mktValue=0):
    optionsPrice = np.zeros((steps + 1))

    # Basic calculations
    h = life_days / 365 / steps
    u = math.exp(vol * math.sqrt(h))   #upFactor
    d = math.exp(-vol * math.sqrt(h))  #DownFactor
    drift = driftCalc(contract, rf, h)

    q = (drift - d) / (u - d)
    qx = 1 - q

    # Fill array Boundary Conditions
    for i in range(0, steps + 1):
        assetAtNode = underlying * math.pow(u, (steps - i)) * pow(d, i)
        optionsPrice[i] = payoff(assetAtNode, strike, cp)

    # Rolling Backward
    for i in range(0, steps):
        if (i == steps - 2):
            a = optionsPrice[0]
            b = optionsPrice[1]
            c = optionsPrice[2]
        for j in range(0, steps - i):
            optionAtNode = (q * optionsPrice[j] + qx * optionsPrice[j + 1]) / drift
            optionsPrice[j] = optionAtNode #test

            if (american == 1):
                assetAtNode = underlying * math.pow(u, steps - i - j - 1) * math.pow(d, j)
                optionsPrice[j] = max(payoff(assetAtNode, strike, cp), optionAtNode)
           # else:
            #    optionsPrice[j] = optionAtNode

    if (valueToFind==0):
        return (optionsPrice[0])
    else:
        prima = optionsPrice[0]
        delta = (a - c) / (underlying * u * u - underlying * d * d)
        delta1 = (a - b) / (underlying * u * u - underlying * u * d)
        delta2 = (b - c) / (underlying * u * d - underlying * d * d)
        gamma= (delta1 - delta2) / ((underlying * u * u - underlying * d * d) / 2)
        vega = binomCRR3v2(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div, american, steps, 0,
                           0) - prima

        theta = (b - optionsPrice[0]) / (2 * h * 365)
        rho = binomCRR3v2(contract, underlying, strike, life_days, vol, rf+0.01, cp, div, american, steps, 0,
                           0) - prima
        cont = 0
        impliedVol = vol

        if mktValue > 0:
            accuracy = 0.0001
            #cont = 0
            dif = mktValue - prima
            #impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                impliedVol += (dif / vega / 100)
                dif = mktValue - binomCRR3v2(contract, underlying, strike, life_days, impliedVol, rf, cp, div,american, steps, 0,0)
                cont += 1
                    # vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
        #else:
        #    impliedVol = vol
        return fillDerivativesArray(prima,delta,gamma,vega,theta,rho,impliedVol,cont)


def binomCRR4v2(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
              steps=1000,valueToFind=6,mktValue=0):

    # Basic calculations
    h = life_days / 365 / steps
    u = math.exp(vol * math.sqrt(h))
    d = math.exp(-vol * math.sqrt(h))
    drift = driftCalc(contract, rf, h)

    p = (drift - d) / (u - d)
    px = 1 - p

    # Arrays for stock & options Tree
    stkval = np.zeros((steps + 1, steps + 1))
    optval = np.zeros((steps + 1, steps + 1))

    stkval[0, 0] = underlying

    for i in range(1, steps + 1):
        stkval[i, 0] = stkval[i - 1, 0] * u
        for j in range(1, i + 1):
            stkval[i, j] = stkval[i - 1, j - 1] * d

    for j in range(steps + 1):
        optval[steps, j] = max(0, payoff(stkval[steps, j], strike, cp))

    for m in range(steps):
        i = steps - m - 1
        for j in range(i + 1):
            optval[i, j] = (p * optval[i + 1, j] + px * optval[i + 1, j + 1]) / drift

            if american:
                optval[i, j] = max(optval[i, j], payoff(stkval[i, j], strike, cp))

    if (valueToFind==0):
        return (optval[0,0])
    else:
        prima = optval[0,0]
        delta = (optval[1, 1] - optval[1, 0]) / (stkval[1, 1] - stkval[1, 0])
        gamma= ((optval[2, 0] - optval[2, 1]) / (stkval[2, 0] - stkval[2, 1]) - (optval[2, 1] - optval[2, 2]) / (
                stkval[2, 1] - stkval[2, 2])) / ((stkval[2, 0] - stkval[2, 2]) / 2)

        vega = binomCRR4v2(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div, american, steps, 0,
                           0) - prima

        theta = (optval[2, 1] - optval[0, 0]) / (2 * 365 * h)
        rho = binomCRR4v2(contract, underlying, strike, life_days, vol, rf+0.01, cp, div, american, steps, 0,
                           0) - prima
        cont = 0
        impliedVol = vol

        if mktValue > 0:
            accuracy = 0.0001
            #cont = 0
            dif = mktValue - prima
            #impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                impliedVol += (dif / vega / 100)
                dif = mktValue - binomCRR4v2(contract, underlying, strike, life_days, impliedVol, rf, cp, div,american, steps, 0,0)
                cont += 1

        return fillDerivativesArray(prima,delta,gamma,vega,theta,rho,impliedVol,cont)


def blackScholesv2(contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=-1, div=0,valueToFind=6,mktValue=0):
    dayYear = life_days / 365
    q = div if (contract == "S") else riskFree

    d1 = (math.log(underlying / strike) + ((riskFree - q) + 0.5 * math.pow(vol, 2)) * dayYear) / (
                vol * math.sqrt(dayYear))
    d2 = d1 - vol * math.sqrt(dayYear)
    vega=underlying * math.sqrt(dayYear) * stats.norm.pdf(d1) / 100

    # gamma y vega son iguales para call y put
    gamma=stats.norm.pdf(d1) * math.exp(-riskFree * dayYear) / (underlying * vol * math.sqrt(dayYear))

    prima=cp * underlying * math.exp(-q * dayYear) * stats.norm.cdf(cp * d1) - cp * strike * math.exp(
        -riskFree * dayYear) * stats.norm.cdf(cp * d2)

    t = (0 if (cp == 1) else 1)

    delta=math.exp(-q * dayYear) * (stats.norm.cdf(d1) - t)

    theta1 = -(underlying * vol * stats.norm.pdf(d1)) / (2 * math.sqrt(dayYear))
    theta2 = cp * strike * riskFree * math.exp(-riskFree * dayYear) * stats.norm.cdf(
        d2 * cp) + cp * div * underlying * stats.norm.cdf(d1 * cp)


    theta= (theta1 - theta2) / 365

    rho=cp * strike * dayYear * math.exp(-riskFree * dayYear) * stats.norm.cdf(cp * d2) / 100  # Hull pag 317

    if (valueToFind==0):
        return prima
    else:
        impliedVol = vol
        cont = 0

        if mktValue>0:
            accuracy=0.0001
            dif = mktValue - prima
            #impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                impliedVol += (dif / vega / 100)
                dif = mktValue - blackScholesv2(contract, underlying, strike, life_days, impliedVol, riskFree, cp, div,0,0)
                cont += 1
                #vol=impliedVol  #??para actualizar todas las greeks a la nueva vol
        return fillDerivativesArray(prima, delta, gamma, vega, theta, rho, impliedVol, cont)


def biseccion(func, min, max, accuracy, maxIterations):
    count = 0
    mid = (min + max) / 2
    dif = func(mid)

    while (abs(dif) > accuracy and count < maxIterations):
        if (dif >= 0):
            max = mid
        else:
            min = mid
            mid = (min + max) / 2
            dif = func(mid)

            count += 1

        return (mid)
