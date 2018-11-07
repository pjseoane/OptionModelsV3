import math

import numpy as np

from optionModelsClasses import cOption as cOpt


class cBinomialMask(cOpt.cOption):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0,
                 american=True, steps=100, mktValue=0):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div,mktValue)

        self.american = american
        self.steps = steps
        self.h = self.dayYear / self.steps  # interv

        #self.derivatives = self.calc()

    def drift(self):
        return (1 if (self.contract == "F") else math.exp(self.riskFree * self.h))

    def buildUnderlyingTree(self, u, d):

        self.undval = np.zeros((self.steps + 1, self.steps + 1))
        self.undval[0, 0] = self.underlying

        for i in range(1, self.steps + 1):
            self.undval[i, 0] = self.undval[i - 1, 0] * u
            for j in range(1, i + 1):
                self.undval[i, j] = self.undval[i - 1, j - 1] * d
        return self.undval

    def buildOptionTree(self, p, drift,cp):
        opttree = np.zeros((self.steps + 1, self.steps + 1))

        px = 1 - p
        for j in range(self.steps + 1):
            opttree[self.steps, j] = max(0, self.payoff(self.undval[self.steps, j], self.strike,cp))

        for m in range(self.steps):
            i = self.steps - m - 1
            for j in range(i + 1):
                opttree[i, j] = (p * opttree[i + 1, j] + px * opttree[i + 1, j + 1]) / drift

                if self.american:
                    opttree[i, j] = max(opttree[i, j], self.payoff(self.undval[i, j], self.strike,cp))
        return opttree

