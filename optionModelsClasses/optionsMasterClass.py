import math
from math import exp, sqrt

import numpy as np
# import pydotplus as pydot
from scipy import stats


class cOption:

    def __init__(self, contract, underlying, strike, life_days, vol, riskFree, cp, div):
        self.contract = contract
        self.underlying = underlying
        self.strike = strike
        self.dayYear = life_days / 365
        self.vol = vol
        self.riskFree = riskFree
        self.cp = cp  # 1 for call -1 for put
        self.div = div

    def payoff(self, und, strk):
        return max((und - strk) * self.cp, 0)

    def calc(self):
        # TODO c/modelo implementa el calculo y termina llamando a fillDerivativesArray
        self.fillDerivativesArray(0, 0, 0, 0, 0, 0)
        return self.derivatives

    def fillDerivativesArray(self, prima, delta, gamma, vega, theta, rho):
        self.derivatives = np.zeros(6)
        self.derivatives[0] = prima
        self.derivatives[1] = delta
        self.derivatives[2] = gamma
        self.derivatives[3] = vega
        self.derivatives[4] = theta
        self.derivatives[5] = rho
        return self.derivatives

    # def impliedVlt(self, mktPrice, accuracy):


class cBlackScholes(cOption):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div)

        self.derivatives = self.calc()

    def calc(self):
        dayYear = self.dayYear
        q = self.div if (self.contract == "S") else self.riskFree

        d1 = (math.log(self.underlying / self.strike) + (
                    (self.riskFree - q) + 0.5 * math.pow(self.vol, 2)) * dayYear) / (self.vol * math.sqrt(dayYear))
        d2 = d1 - self.vol * math.sqrt(dayYear)

        # gamma y vega son iguales para call y put
        self.gamma = stats.norm.pdf(d1) * math.exp(-self.riskFree * dayYear) / (
                    self.underlying * self.vol * math.sqrt(dayYear))
        self.vega = self.underlying * math.sqrt(dayYear) * stats.norm.pdf(d1) / 100

        self.prima = self.cp * self.underlying * math.exp(-q * dayYear) * stats.norm.cdf(
            self.cp * d1) - self.cp * self.strike * math.exp(-self.riskFree * dayYear) * stats.norm.cdf(
            self.cp * d2)

        t = (0 if (self.cp == 1) else 1)

        self.delta = math.exp(-q * dayYear) * (stats.norm.cdf(d1) - t)

        theta1 = -(self.underlying * self.vol * stats.norm.pdf(d1)) / (2 * math.sqrt(dayYear))
        theta2 = self.cp * self.strike * self.riskFree * math.exp(-self.riskFree * dayYear) * stats.norm.cdf(
            d2 * self.cp) + self.cp * self.div * self.underlying * stats.norm.cdf(d1 * self.cp)
        self.theta = (theta1 - theta2) / 365
        self.rho = self.cp * self.strike * dayYear * math.exp(-self.riskFree * dayYear) * stats.norm.cdf(
            self.cp * d2) / 100  # Hull pag 317

        return super().fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho)


class cBinomialMask(cOption):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0,
                 american=True, steps=100):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div)

        self.american = american
        self.steps = steps
        self.h = self.dayYear / self.steps  # interv

        self.derivatives = self.calc()

    def drift(self):
        return (1 if (self.contract == "F") else math.exp(self.riskFree * self.h))

    def calc(self):
        # mask function definirla para cada implementacion
        # TODO cada modelo implementa
        super().fillDerivativesArray(0, 0, 0, 0, 0, 0)
        return self.derivatives


class cBinomCRR3(cBinomialMask):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0,
                 american=True, steps=100):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, american, steps)

        self.derivatives = self.calc()

    def calc(self):

        # Basic calculations

        drift = self.drift()
        u = exp(self.vol * sqrt(self.h))
        d = exp(-self.vol * sqrt(self.h))
        p = (drift - d) / (u - d)
        px = (1 - p)

        # Boundary Conditions
        optionsPrice = np.zeros(self.steps + 1)
        for i in range(0, self.steps + 1):
            assetAtNode = self.underlying * pow(u, (self.steps - i)) * pow(d, i)
            optionsPrice[i] = (super().payoff(assetAtNode, self.strike))

        # Resolving tree backwards
        for i in range(0, self.steps):
            if (i == self.steps - 2):
                a = optionsPrice[0]
                b = optionsPrice[1]
                c = optionsPrice[2]

            for j in range(0, self.steps - i):
                optionAtNode = (p * optionsPrice[j] + px * optionsPrice[j + 1]) / drift  # *z

                if (self.american):
                    assetAtNode = self.underlying * pow(u, self.steps - i - j - 1) * pow(d, j)
                    optionsPrice[j] = max(super().payoff(assetAtNode, self.strike), optionAtNode)
                else:
                    optionsPrice[j] = optionAtNode

        self.prima = (optionsPrice[0])
        self.delta = (a - c) / (self.underlying * u * u - self.underlying * d * d)

        delta1 = (a - b) / (self.underlying * u * u - self.underlying * u * d)
        delta2 = (b - c) / (self.underlying * u * d - self.underlying * d * d)
        self.gamma = ((delta1 - delta2) / ((self.underlying * u * u - self.underlying * d * d) / 2))
        self.vega = 0
        self.theta = (b - optionsPrice[0]) / (2 * self.h * 365)
        self.rho = 0
        return super().fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho)


class cBinomJR(cBinomialMask):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0,
                 american=True, steps=100):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, american, steps)

        self.derivatives = self.calc()

    def buildUnderlyingTree(self, u, d):

        undval = np.zeros((self.steps + 1, self.steps + 1))
        undval[0, 0] = self.underlying

        for i in range(1, self.steps + 1):
            undval[i, 0] = undval[i - 1, 0] * u
            for j in range(1, i + 1):
                undval[i, j] = undval[i - 1, j - 1] * d
        return undval

    def buildOptionTree(self, p, drift):
        opttree = np.zeros((self.steps + 1, self.steps + 1))

        px = 1 - p
        for j in range(self.steps + 1):
            opttree[self.steps, j] = max(0, self.payoff(self.stkval[self.steps, j], self.strike))

        for m in range(self.steps):
            i = self.steps - m - 1
            for j in range(i + 1):
                opttree[i, j] = (p * opttree[i + 1, j] + px * opttree[i + 1, j + 1]) / drift

                if self.american:
                    opttree[i, j] = max(opttree[i, j], self.payoff(self.stkval[i, j], self.strike))
        return opttree

    def calc(self):
        # Basic calculations

        drift = self.drift()
        u = exp((self.riskFree - 0.5 * pow(self.vol, 2)) * self.h + self.vol * sqrt(self.h))
        d = exp((self.riskFree - 0.5 * pow(self.vol, 2)) * self.h - self.vol * sqrt(self.h))
        p = (drift - d) / (u - d)
        # px=(1-p)

        # ------
        self.stkval = self.buildUnderlyingTree(u, d)
        self.optval = self.buildOptionTree(p, drift)
        # -----

        self.prima = self.optval[0, 0]
        self.delta = (self.optval[1, 1] - self.optval[1, 0]) / (self.stkval[1, 1] - self.stkval[1, 0])
        self.gamma = ((self.optval[2, 0] - self.optval[2, 1]) / (self.stkval[2, 0] - self.stkval[2, 1]) - (
                    self.optval[2, 1] - self.optval[2, 2]) / (self.stkval[2, 1] - self.stkval[2, 2])) / (
                                 (self.stkval[2, 0] - self.stkval[2, 2]) / 2)
        self.theta = (self.optval[2, 1] - self.optval[0, 0]) / (2 * 365 * self.h)
        self.vega = 0
        self.rho = 0

        return super().fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho)


class cBinomCRR4(cBinomJR):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0,
                 american=True, steps=100):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, american, steps)

        self.derivatives = self.calc()

    def calc(self):
        # Basic calculations
        drift = self.drift()
        u = exp(self.vol * sqrt(self.h))
        d = exp(-self.vol * sqrt(self.h))
        p = (drift - d) / (u - d)
        # px=(1-p)

        self.stkval = super().buildUnderlyingTree(u, d)
        self.optval = super().buildOptionTree(p, drift)

        self.prima = self.optval[0, 0]
        self.delta = (self.optval[1, 1] - self.optval[1, 0]) / (self.stkval[1, 1] - self.stkval[1, 0])
        self.gamma = ((self.optval[2, 0] - self.optval[2, 1]) / (self.stkval[2, 0] - self.stkval[2, 1]) - (
                    self.optval[2, 1] - self.optval[2, 2]) / (self.stkval[2, 1] - self.stkval[2, 2])) / (
                                 (self.stkval[2, 0] - self.stkval[2, 2]) / 2)
        self.theta = (self.optval[2, 1] - self.optval[0, 0]) / (2 * 365 * self.h)
        self.vega = 0
        self.rho = 0
        return super().fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho)
