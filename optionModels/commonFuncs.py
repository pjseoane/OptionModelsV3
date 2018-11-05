import numpy as np
import math

#contingent_payoff = lambda st, k,cp: max((st - k)*cp, 0)

#ivVega=lambda model, accuracy, mktVal, prima,contract, underlying, strike, life_days, vol, rf, cp, div,american, steps:


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

def ivVega(func, vol, vega, accuracy,maxIterations):
    cont = 0
    impliedVol = vol
    dif=func(vol)
    while (abs(dif) > accuracy and cont < maxIterations and impliedVol > 0.001):
        impliedVol += (dif / vega / 100)
        dif = func(impliedVol)
        cont += 1

    return impliedVol

def biseccion(func, min, max, accuracy, maxIterations):
    count = 1
    mid = (min + max) / 2
    dif = func(mid)

    while (abs(dif) > accuracy and count < maxIterations):
        if (dif <= 0):
            max = mid
        else:
            min = mid

        mid = (min + max) / 2
        dif = func(mid)

        count += 1

    return (mid)