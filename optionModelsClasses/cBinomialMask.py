import math
import numpy as np
from optionModelsClasses import cOption as cOpt
#2

class cBinomMask(cOpt.cOption):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0.05
                 , american=True, steps=100, mktValue=0):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, mktValue)

        self.american = american
        self.steps = steps
        self.mktValue=mktValue
        self.h = self.dayYear / self.steps
        self.z= math.exp(-self.riskFree * self.h)

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

    def buildOptionTree(self, p, cp):
            optTree = np.zeros((self.steps + 1, self.steps + 1))

            px = 1 - p
            for j in range(self.steps + 1):
                optTree[self.steps, j] = max(0, self.payoff(self.undval[self.steps, j], self.strike, cp))

            for m in range(self.steps):
                i = self.steps - m - 1
                for j in range(i + 1):
                    optTree[i, j] = (p * optTree[i + 1, j] + px * optTree[i + 1, j + 1]) * self.z #/ drift

                    if self.american:
                        optTree[i, j] = max(optTree[i, j], self.payoff(self.undval[i, j], self.strike, cp))


            return optTree


    def impliedVolV(self,model,vega,accuracy):
        impliedVol = self.vol
        if self.mktValue > 0 and vega>0 :  # Calculo de implied Vlts
            difToModel = lambda vlt: self.mktValue - model(self.contract, self.underlying, self.strike,
                                                                       self.life_days, vlt, self.riskFree, self.cp,
                                                                       self.div, self.american,self.steps, 0).prima
            impliedVol = self.ivVega(difToModel, self.vol, vega, accuracy, 20)
        return impliedVol


    def impliedVolB(self, model, teorica, accuracy):
        impliedVol = self.vol
        if self.mktValue > 0:
            difToModel = lambda vlt: self.mktValue - model(self.contract, self.underlying, self.strike,
                                                       self.life_days, vlt, self.riskFree, self.cp,
                                                       self.div, self.american, self.steps, 0).prima
            if(teorica<=self.mktValue):
                        mini=self.vol
                        maxi=self.vol*3
            else:
                        mini=0
                        maxi=self.vol

            return self.biseccion(difToModel,mini,maxi,accuracy,50)
        return impliedVol

