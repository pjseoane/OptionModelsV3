import math

from scipy import stats

from optionModelsClasses import cOption as cOpt


class cBlackScholes(cOpt.cOption):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=-1, div=0,
                 mktValue=0):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, mktValue)


        self.calc()

    def calc(self):
        q = self.div if (self.contract == "S") else self.riskFree

        d1 = (math.log(self.underlying / self.strike) + (
                (self.riskFree - q) + 0.5 * math.pow(self.vol, 2)) * self.dayYear) / (self.vol * math.sqrt(self.dayYear))
        d2 = d1 - self.vol * math.sqrt(self.dayYear)

        # gamma y vega son iguales para call y put
        self.gamma = stats.norm.pdf(d1) * math.exp(-self.riskFree * self.dayYear) / (
                self.underlying * self.vol * math.sqrt(self.dayYear))
        self.vega = self.underlying * math.sqrt(self.dayYear) * stats.norm.pdf(d1) / 100

        self.prima = self.cp * self.underlying * math.exp(-q * self.dayYear) * stats.norm.cdf(
            self.cp * d1) - self.cp * self.strike * math.exp(-self.riskFree * self.dayYear) * stats.norm.cdf(
            self.cp * d2)

        t = (0 if (self.cp == 1) else 1)

        self.delta = math.exp(-q * self.dayYear) * (stats.norm.cdf(d1) - t)

        theta1 = -(self.underlying * self.vol * stats.norm.pdf(d1)) / (2 * math.sqrt(self.dayYear))
        theta2 = self.cp * self.strike * self.riskFree * math.exp(-self.riskFree * self.dayYear) * stats.norm.cdf(
            d2 * self.cp) + self.cp * self.div * self.underlying * stats.norm.cdf(d1 * self.cp)
        self.theta = (theta1 - theta2) / 365
        self.rho = self.cp * self.strike * self.dayYear * math.exp(-self.riskFree * self.dayYear) * stats.norm.cdf(
            self.cp * d2) / 100  # Hull pag 317

        self.arr = self.fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho, 0, 0)



    def impliedVol(self):
        impliedVol = self.vol
        if self.mktValue > 0:  # Calculo de implied Vlts
            difToModel = lambda vlt: self.mktValue - cBlackScholes(self.contract, self.underlying, self.strike,
                                                                   self.life_days, vlt, self.riskFree, self.cp,
                                                                   self.div, 0).prima
            impliedVol = self.ivVega(difToModel, self.vol, self.vega, 0.0001, 20)
        return impliedVol




if __name__ == '__main__':
    print('__main__')
    # a=cBlackScholes('S',100, 100, 365,0.30, .03,  1, 0)
    # a = cBlackScholes()
    a = cBlackScholes("S", 100, 100, 365, 0.3, .03, -1, 0, 11)
    print("Modelo BlackScholes prima:\n", a.prima)
    print("Modelo BlackScholes arr:\n", a.arr)
    print("Modelo BlackScholes iv:\n", a.impliedVol())


else:
    print("Nombre de modelo:", __name__)
