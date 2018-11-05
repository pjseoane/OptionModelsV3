import numpy as np
import math
def payoff(underlying, strike, cp):
    return max((underlying - strike) * cp, 0)

def driftCalc(contract, rf, h):
    return (1 if (contract == "F") else math.exp(rf * h))

def fillDerivativesArray(prima, delta, gamma, vega, theta, rho,impVlt,cont):
    derivatives = np.zeros(10)
    derivatives[0] = prima
    derivatives[1] = delta
    derivatives[2] = gamma
    derivatives[3] = vega
    derivatives[4] = theta
    derivatives[5] = rho
    derivatives[6]=  impVlt
    derivatives[7]=  cont
    return derivatives
