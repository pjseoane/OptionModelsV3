#Este modelo anda OK 7 Nov 2018

import math
import numpy as np

from optionModelsClasses import cOption as cOpt
#2

class cBinomJR(cOpt.cOption):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0
                 , american=True, steps=100, mktValue=0):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, mktValue)

        self.american = american
        self.steps = steps
        self.h = self.dayYear / self.steps
        self.calc()

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


    def calc(self):
        # Basic calculations

        drift = self.drift()
        u = math.exp((self.riskFree - 0.5 * math.pow(self.vol, 2)) * self.h + self.vol * math.sqrt(self.h) )
        d = math.exp((self.riskFree - 0.5 * math.pow(self.vol, 2)) * self.h - self.vol * math.sqrt(self.h) )
        p = (drift - d) / (u - d)  # px=(1-p)

        # ------
        "arma los trees con las funciones que estan en cBinomial Mask"
        self.stkval = self.buildUnderlyingTree(u,d)
        self.optval = self.buildOptionTree(p, drift,self.cp)
        # ---- -

        self.prima = self.optval[0, 0]
        self.delta = (self.optval[1, 1] - self.optval[1, 0]) / (self.stkval[1, 1] -self.stkval[1, 0])
        self.gamma = ((self.optval[2, 0] - self.optval[2, 1]) / (self.stkval[2, 0] -self.stkval[2, 1]) - (self.optval[2, 1] -self.optval[2, 2]) / (self.stkval[2, 1] -self.stkval[2, 2])) / ((self.stkval[2, 0] - self.stkval[2, 2]) / 2)
        self.theta = (self.optval[2, 1] - self.optval[0, 0]) / (2 * 365 * self.h)

        self.vega = 0
        self.rho = 0

        if self.mktValue > -1:
            self.vega = cBinomJR(self.contract, self.underlying, self.strike, self.life_days, self.vol + 0.01, self.riskFree, self.cp, self.div,self.american, self.steps, -1).prima - self.prima
            self.rho =  cBinomJR(self.contract, self.underlying, self.strike, self.life_days, self.vol, self.riskFree+0.01, self.cp, self.div,self.american, self.steps, -1).prima- self.prima


        self.arr=self.fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho, 0,0)

    def impliedVol(self):
        #return self.mktValue

        impliedVol = self.vol
        if self.mktValue > 0 and self.vega>0 :  # Calculo de implied Vlts
            difToModel = lambda vlt: self.mktValue - cBinomJR(self.contract, self.underlying, self.strike,
                                                                       self.life_days, vlt, self.riskFree, self.cp,
                                                                       self.div, self.american,self.steps, 0).prima
            impliedVol = self.ivVega(difToModel, self.vol, self.vega, 0.0001, 20)
        return impliedVol


if __name__ == '__main__':
    print('__main__')

    a = cBinomJR("S", 100, 100, 365, 0.3, .03, -1, 0, True, 100,10)
    print("Modelo Jarrow Rudd prima:\n", a.prima)
    print("Modelo Jarrow Rudd arr:\n", a.arr)
    print("Modelo Jarrow Rudd iv:\n", a.impliedVol())


else:
    print("Nombre de modelo:", __name__)
