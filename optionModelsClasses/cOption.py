import numpy as np
import math


class cOption:

    def __init__(self, contract, underlying, strike, life_days, vol, riskFree, cp, div, mktValue=0):
        self.contract = contract
        if (contract=='F'):
            div=0

        self.dayYear = life_days / 365
        self.underlying = underlying*math.exp(-div*self.dayYear)
        self.strike = strike
        self.life_days=life_days

        self.vol = vol
        self.riskFree = riskFree
        self.cp = cp  # 1 for call -1 for put
        self.div = div
        self.mktValue = mktValue

    def payoff(self, underlying, strike, cp):
        return max((underlying - strike) * cp, 0)

    def fillDerivativesArray(self, prima, delta, gamma, vega, theta, rho, impVlt, cont):
        derivatives = np.zeros(10)
        derivatives[0] = prima
        derivatives[1] = delta
        derivatives[2] = gamma
        derivatives[3] = vega
        derivatives[4] = theta
        derivatives[5] = rho
        derivatives[6] = impVlt
        derivatives[7] = cont
        return derivatives

    def ivVega(self, func, vol, vega, accuracy, maxIterations):
        cont = 0
        impliedVol = vol
        dif = func(vol)
        while (abs(dif) > accuracy and cont < maxIterations and impliedVol > 0.001):
            impliedVol += (dif / vega / 100)
            dif = func(impliedVol)
            cont += 1
        #return cont
        return impliedVol

    def biseccion(self, model, min, max, accuracy, maxIterations):
        count = 1
        mid = (min + max) / 2
        dif = model(mid)

        while (abs(dif) > accuracy and count < maxIterations):
            if (dif <= 0):
                max = mid
            else:
                min = mid

            mid = (min + max) / 2
            dif = model(mid)

            count += 1

        #return count
        return (mid)