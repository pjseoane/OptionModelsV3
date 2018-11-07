import numpy as np


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
