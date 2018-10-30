#Agregue esta linea y va por commit...
# 2da linea...222
#ok bajado de github, le agrego esta linea en la oficina
#voy a trar una notebook de dropbox
# en esta linea creo un pull request
# Este es branch1??
#linea 4
#linea 5, hago commit /pull req, pero no push
#line6 6, hago pull req y desp commit
#linea 7,commit y pull req
#linea 8, commit y pull req
#linea 9, solo push

import numpy as np
import math
import sys
from scipy import stats

sys.path.append('C:/Users/pauli/Dropbox/Python/OptionModels')
sys.path.append('C:/Users/pseoane/Dropbox/Python/OptionModels')

def payoff(underlying, strike, cp):
    return max((underlying - strike) * cp, 0)

def driftCalc(contract, rf, h):
    return (1 if (contract == "F") else math.exp(rf * h))

def fillDerivativesArray(prima, delta, gamma, vega, theta, rho,impVlt):
    derivatives = np.zeros(7)
    derivatives[0] = prima
    derivatives[1] = delta
    derivatives[2] = gamma
    derivatives[3] = vega
    derivatives[4] = theta
    derivatives[5] = rho
    derivatives[6]=  impVlt
    return derivatives

def binomJRv2(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
            steps=1000,argument=6,mktPrice=0):
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

    def prima():
        return optval[0, 0]

    def delta():
        return (optval[1, 1] - optval[1, 0]) / (stkval[1, 1] - stkval[1, 0])

    def gamma():
        return ((optval[2, 0] - optval[2, 1]) / (stkval[2, 0] - stkval[2, 1]) - (optval[2, 1] - optval[2, 2]) / (
                stkval[2, 1] - stkval[2, 2])) / ((stkval[2, 0] - stkval[2, 2]) / 2)
    def vega():
        return binomJRv2(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div, american, steps,
                           0,0) - prima()

    def theta():
        return (optval[2, 1] - optval[0, 0]) / (2 * 365 * h)

    def rho():
        return binomJRv2(contract, underlying, strike, life_days, vol, rf+0.01, cp, div, american, steps,
                           0,0) - prima()

    def arr():
        return fillDerivativesArray(prima(), delta(), gamma(), vega(), theta(), rho(), ivVega())

    def ivVega():
        if mktPrice>0:
            accuracy=0.0001
            cont=0
            dif = mktPrice - prima()
            impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and mktPrice > 0 and impliedVol > 0.005):
                impliedVol += (dif / vega() / 100);
                dif = mktPrice - binomJRv2(contract, underlying, strike, life_days, impliedVol, rf, cp, div, american, steps, 0,0)
                cont += 1
                #vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
        else:
            impliedVol=vol
        return impliedVol



    switcher = {
        0: prima,
        1: delta,
        2: gamma,
        3: vega,
        4: theta,
        5: rho,
        6: arr,
        7: ivVega
    }
    func = switcher.get(argument, "Default Nothing")

    return func()

def binomCRR3v2(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
                steps=1000, argument=6,mktPrice=0):
    optionsPrice = np.zeros((steps + 1))

    # Basic calculations
    h = life_days / 365 / steps
    u = math.exp(vol * math.sqrt(h))
    d = math.exp(-vol * math.sqrt(h))
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

            if (american == 1):
                assetAtNode = underlying * math.pow(u, steps - i - j - 1) * math.pow(d, j)
                optionsPrice[j] = max(payoff(assetAtNode, strike, cp), optionAtNode)
            else:
                optionsPrice[j] = optionAtNode


    def prima():
        return optionsPrice[0]

    def delta():
        return (a - c) / (underlying * u * u - underlying * d * d)

    def gamma():
        delta1 = (a - b) / (underlying * u * u - underlying * u * d)
        delta2 = (b - c) / (underlying * u * d - underlying * d * d)
        return (delta1 - delta2) / ((underlying * u * u - underlying * d * d) / 2)

    def vega():
        return binomCRR3v2(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div, american, steps,
                           0) - prima()

        # return -33.33

    def theta():
        return (b - optionsPrice[0]) / (2 * h * 365)

    def rho():
        return binomCRR3v2(contract, underlying, strike, life_days, vol,  rf+0.01, cp, div, american, steps,
                           0) - prima()
    def ivVega():
        if mktPrice>0:
            accuracy=0.0001
            cont=0
            dif = mktPrice - prima()
            impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and mktPrice > 0 and impliedVol > 0.005):
                impliedVol += (dif / vega() / 100);
                dif = mktPrice - binomCRR3v2(contract, underlying, strike, life_days, impliedVol, rf, cp, div, american, steps, 0,0)
                cont += 1
                #vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
        else:
            impliedVol=vol
        return impliedVol

    def arr():
        return fillDerivativesArray(prima(), delta(), gamma(), vega(), theta(), rho(),ivVega())

    switcher = {
        0: prima,
        1: delta,
        2: gamma,
        3: vega,
        4: theta,
        5: rho,
        6: arr,
        7: ivVega
    }
    func = switcher.get(argument, "Default Nothing")

    return func()

def binomCRR4v2(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
              steps=1000,argument=6,mktPrice=0):

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

    def prima():
        return optval[0, 0]
    def delta():
        return (optval[1, 1] - optval[1, 0]) / (stkval[1, 1] - stkval[1, 0])
    def gamma():
        return ((optval[2, 0] - optval[2, 1]) / (stkval[2, 0] - stkval[2, 1]) - (optval[2, 1] - optval[2, 2]) / (
                stkval[2, 1] - stkval[2, 2])) / ((stkval[2, 0] - stkval[2, 2]) / 2)
    def theta():
        return (optval[2, 1] - optval[0, 0]) / (2 * 365 * h)
    def vega():
        return binomCRR4v2(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div, american, steps,
                           0) - prima()
    def rho():
        return binomCRR4v2(contract, underlying, strike, life_days, vol, rf+0.01, cp, div, american, steps,
                           0) - prima()
    def ivVega():
        if mktPrice>0:
            accuracy=0.0001
            cont=0
            dif = mktPrice - prima()
            impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and mktPrice > 0 and impliedVol > 0.005):
                impliedVol += (dif / vega() / 100);
                dif = mktPrice - binomCRR4v2(contract, underlying, strike, life_days, impliedVol, rf, cp, div, american, steps, 0,0)
                cont += 1
                #vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
        else:
            impliedVol=vol
        return impliedVol

    def arr():
        return fillDerivativesArray(prima(), delta(), gamma(), vega(), theta(), rho(),ivVega())

    switcher = {
        0: prima,
        1: delta,
        2: gamma,
        3: vega,
        4: theta,
        5: rho,
        6: arr,
        7: ivVega
    }
    func = switcher.get(argument, "Default Nothing")

    return func()

def blackScholesv2(contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=-1, div=0,argument=6,mktPrice=0):
    dayYear = life_days / 365
    q = div if (contract == "S") else riskFree

    d1 = (math.log(underlying / strike) + ((riskFree - q) + 0.5 * math.pow(vol, 2)) * dayYear) / (
                vol * math.sqrt(dayYear))
    d2 = d1 - vol * math.sqrt(dayYear)
    veg=underlying * math.sqrt(dayYear) * stats.norm.pdf(d1) / 100

    # gamma y vega son iguales para call y put
    def gamma():
        return stats.norm.pdf(d1) * math.exp(-riskFree * dayYear) / (underlying * vol * math.sqrt(dayYear))

    def vega():
        return veg

    def prima():
        return cp * underlying * math.exp(-q * dayYear) * stats.norm.cdf(cp * d1) - cp * strike * math.exp(
        -riskFree * dayYear) * stats.norm.cdf(cp * d2)
    t = (0 if (cp == 1) else 1)

    def delta():
        return math.exp(-q * dayYear) * (stats.norm.cdf(d1) - t)

    theta1 = -(underlying * vol * stats.norm.pdf(d1)) / (2 * math.sqrt(dayYear))
    theta2 = cp * strike * riskFree * math.exp(-riskFree * dayYear) * stats.norm.cdf(
        d2 * cp) + cp * div * underlying * stats.norm.cdf(d1 * cp)


    def theta():
        return (theta1 - theta2) / 365

    def rho():
        return cp * strike * dayYear * math.exp(-riskFree * dayYear) * stats.norm.cdf(cp * d2) / 100  # Hull pag 317

    def ivVega():
        if mktPrice>0:
            accuracy=0.0001
            cont=0
            dif = mktPrice - prima()
            impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and mktPrice > 0 and impliedVol > 0.005):
                impliedVol += (dif / vega() / 100);
                dif = mktPrice - blackScholesv2(contract, underlying, strike, life_days, impliedVol, riskFree, cp, div,0,0)
                cont += 1
                #vol=impliedVol  #??para actualizar todas las greeks a la nueva vol
        else:
            impliedVol=vol
        return impliedVol



    def arr():
        return fillDerivativesArray(prima(), delta(), gamma(), vega(), theta(), rho(),ivVega())

    switcher = {
        0: prima,
        1: delta,
        2: gamma,
        3: vega,
        4: theta,
        5: rho,
        6: arr,
        7: ivVega
    }
    func = switcher.get(argument, "Default Nothing")

    return func()

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
