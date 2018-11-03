import numpy as np
import math
#from math import sqrt, exp


def driftCalc(contract, rf, h):
    return (1 if (contract == "F") else math.exp(rf * h))

def payoffFunc(und, strk, cp):
    return max((und - strk) * cp, 0)

def binomCRR5(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
                steps=100, argument=6,mktPrice=0):

    #optionsPrice = np.zeros((steps + 1))

    # Basic calculations
    h = life_days / 365 / steps
    u = math.exp(vol * math.sqrt(h))   #upFactor
    d = math.exp(-vol * math.sqrt(h))  #DownFactor
    drift = driftCalc(contract, rf, h)

    q = (drift - d) / (u - d)
    qx = 1 - q

    # build undTree
    undTree = []
    for i in range(0, steps + 1):
        # Number of prices per period
        period_prices = []
        for j in range(i + 1):
            up_factor_repeat = i - j
            down_factor_repeat = j

            values = np.append(np.repeat(u, up_factor_repeat), np.repeat(d, down_factor_repeat))
            assetAtNode = values.prod() * underlying
            period_prices.append(assetAtNode)
        undTree.append(period_prices)

    opArray = undTree.copy()

    # Boundary Condition
    for i in range(steps + 1):
        opArray[steps][i] = payoffFunc(undTree[steps][i], strike, cp)

    for i in range(steps - 1, -1, -1):
        for j in range(len(opArray[i])):
            opAtNode = (opArray[i + 1][j + 1] * qx + opArray[i + 1][j] * q) / drift

            if (american == 1):
                opAtNode = max(payoffFunc(undTree[i][j], strike, cp), opAtNode)

            opArray[i][j] = opAtNode
        # print(opArray[i])
        # print("opArray Final :",opArray)

    #def prima():
    #return 11.11
    return opArray[0][0]
