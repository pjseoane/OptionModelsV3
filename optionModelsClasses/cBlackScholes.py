import math

from scipy import stats

from optionModelsClasses import cOption as cO


class cBlackScholes(cO.cOption):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=-1, div=0):
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

        self.arr = self.fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, self.theta, self.rho, 0, 0)


if __name__ == '__main__':
    print('__main__')
    # a=cBlackScholes('S',100, 100, 365,0.30, .03,  1, 0)
    a = cBlackScholes()
    # option = cOpt(100, 100, 0.03, .30, 100, 1, 1)
    print("Modelo BlackScholes :\n", a.prima, a.arr)
else:
    print("Nombre de modelo:", __name__)
