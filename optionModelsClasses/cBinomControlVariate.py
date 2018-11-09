from optionModelsClasses import cBinomialMask as cBinom
from optionModelsClasses import cBinomJarrowRuddV2 as cJR
from optionModelsClasses import cBlackScholes as cBS

class cBinomCV(cBinom.cBinomMask):

    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0
                 , american=True, steps=100, mktValue=0):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, american, steps,mktValue)

        self.calc()

    def calc(self):
        #amOpt=self.arr
        amOpt= cJR.cBinomJRV2(self.contract, self.underlying, self.strike, self.life_days, self.vol, self.riskFree, self.cp, self.div, True, self.steps,self.mktValue)
        bsOpt= cBS.cBlackScholes(self.contract, self.underlying, self.strike, self.life_days, self.vol, self.riskFree, self.cp, self.div)
        euOpt= cJR.cBinomJRV2(self.contract, self.underlying, self.strike, self.life_days, self.vol, self.riskFree, self.cp, self.div, False, self.steps,self.mktValue)

        self.prima=amOpt.prima+bsOpt.prima-euOpt.prima
        self.delta=amOpt.delta+bsOpt.delta-euOpt.delta
        self.gamma=amOpt.gamma+bsOpt.gamma-euOpt.gamma
        self.vega=amOpt.vega+bsOpt.vega-euOpt.vega
        self.theta=amOpt.theta+bsOpt.theta-euOpt.theta
        self.rho=amOpt.rho+bsOpt.rho-euOpt.rho

        if self.mktValue > -1:
            self.vega = cBinomCV(self.contract, self.underlying, self.strike, self.life_days, self.vol + 0.01,
                                 self.riskFree, self.cp, self.div, self.american, self.steps, -1).prima - self.prima
            self.rho = cBinomCV(self.contract, self.underlying, self.strike, self.life_days, self.vol,
                                self.riskFree + 0.01, self.cp, self.div, self.american, self.steps,
                                -1).prima - self.prima

        self.arr = self.fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho, 0, 0)

    def impVolV(self,accuracy):
        return self.impliedVolV(cBinomCV,self.vega,accuracy)

    def impVolB(self,accuracy):
        return self.impliedVolB(cBinomCV, self.prima, accuracy)

if __name__ == '__main__':
    print('__main__')

    a = cBinomCV("S", 100, 100, 365, 0.3, .03, -1, 0, True, 100,0)
    print("Modelo Control Variate prima:\n", a.prima)
    print("Modelo Control Variate arr:\n", a.arr)
    print("Modelo Control Variate arr:\n", a.impVolV(0.001))
    print("Modelo Control Variate arr:\n", a.impVolB(0.001))


else:
    print("Nombre de modelo:", __name__)
