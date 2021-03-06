import math
#5

from optionModelsClasses import cBinomialMask as cBinom

class cBinomJRV2(cBinom.cBinomMask):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0.0
                 , american=True, steps=100, mktValue=10):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, american, steps,mktValue)

        self.calc()

    def calc(self):

        drift = self.drift()
        firstTerm = (self.riskFree - 0.5 * math.pow(self.vol, 2)) * self.h
        secondTerm= self.vol * math.sqrt(self.h)
        u = math.exp(firstTerm+secondTerm)
        d = math.exp(firstTerm-secondTerm)

        p = (drift - d) / (u - d)  # px=(1-p)

        self.stkval = self.buildUnderlyingTree(u, d)
        self.optval = self.buildOptionTree(p, self.cp)

        #Calculo los valores en cBinomialMask ?
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

    def impVolV(self,accuracy):
        return self.impliedVolV(cBinomJRV2, self.vega, accuracy)

    def impVolB(self,accuracy):
        return self.impliedVolB(cBinomJRV2, self.prima, accuracy)


if __name__ == '__main__':
    print('__main__')

    a = cBinomJRV2("F", 36000, 36000, 87, 0.14, .50, -1, 0.0, True, 200,850)
    print("Modelo Jarrow Rudd V2 prima:\n", a.prima)
    print("Modelo Jarrow Rudd V2 arr:\n", a.arr)
    print("Modelo Jarrow Rudd V2 ivVega:\n", a.impVolV(0.001))
    print("Modelo Jarrow Rudd V2 ivBiseccion:\n", a.impVolB(0.001))
    print("Para solo tener la ImpVlt:\n",cBinomJRV2("S", 100, 100, 365, 0.3, .03, -1, 0, True, 100,10).impVolV(0.001))


else:
    print("Nombre de modelo:", __name__)

