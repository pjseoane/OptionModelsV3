import math
#import numpy as np

from optionModelsClasses import cBinomialMask as cBinom

class cBinomJRV2(cBinom.cBinomMask):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0
                 , american=True, steps=100, mktValue=0):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, american, steps,mktValue)

        self.calc()

    def calc(self):

        drift = self.drift()
        u = math.exp((self.riskFree - 0.5 * math.pow(self.vol, 2)) * self.h + self.vol * math.sqrt(self.h))
        d = math.exp((self.riskFree - 0.5 * math.pow(self.vol, 2)) * self.h - self.vol * math.sqrt(self.h))
        p = (drift - d) / (u - d)  # px=(1-p)

        self.stkval = self.buildUnderlyingTree(u, d)
        self.optval = self.buildOptionTree(p, drift, self.cp)

        self.prima = self.optval[0, 0]
        self.delta = (self.optval[1, 1] - self.optval[1, 0]) / (self.stkval[1, 1] - self.stkval[1, 0])
        self.gamma = ((self.optval[2, 0] - self.optval[2, 1]) / (self.stkval[2, 0] - self.stkval[2, 1]) - (
                    self.optval[2, 1] - self.optval[2, 2]) / (self.stkval[2, 1] - self.stkval[2, 2])) / (
                                 (self.stkval[2, 0] - self.stkval[2, 2]) / 2)
        self.theta = (self.optval[2, 1] - self.optval[0, 0]) / (2 * 365 * self.h)

        self.vega = 0
        self.rho = 0

        if self.mktValue > -1:
            self.vega = cBinomJRV2(self.contract, self.underlying, self.strike, self.life_days, self.vol + 0.01,
                                 self.riskFree, self.cp, self.div, self.american, self.steps, -1).prima - self.prima
            self.rho = cBinomJRV2(self.contract, self.underlying, self.strike, self.life_days, self.vol,
                                self.riskFree + 0.01, self.cp, self.div, self.american, self.steps,
                                -1).prima - self.prima

        self.arr = self.fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho, 0, 0)

    def impVol(self):
        return self.impliedVol(cBinomJRV2,self.vega,0.0001)


if __name__ == '__main__':
    print('__main__')

    a = cBinomJRV2("S", 100, 100, 365, 0.3, .03, -1, 0, True, 100,10)
    print("Modelo Jarrow Rudd V2 prima:\n", a.prima)
    print("Modelo Jarrow Rudd V2 arr:\n", a.arr)
    print("Modelo Jarrow Rudd V2 iv:\n", a.impVol())


else:
    print("Nombre de modelo:", __name__)

