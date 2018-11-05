
import math
import numpy as np
import optionModels.commonFuncs as cf


def binomCRR3(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0,
                    american=True,
                    steps=100, valueToFind=6, mktValue=0):
        optionsPrice = np.zeros((steps + 1))

        # Basic calculations
        h = life_days / 365 / steps
        u = math.exp(vol * math.sqrt(h))  # upFactor
        d = math.exp(-vol * math.sqrt(h))  # DownFactor
        drift = cf.driftCalc(contract, rf, h)

        q = (drift - d) / (u - d)
        qx = 1 - q

        # Fill array Boundary Conditions
        for i in range(0, steps + 1):
            assetAtNode = underlying * math.pow(u, (steps - i)) * pow(d, i)
            optionsPrice[i] = cf.payoff(assetAtNode, strike, cp)

        # Rolling Backward
        for i in range(0, steps):
            if (i == steps - 2):
                a = optionsPrice[0]
                b = optionsPrice[1]
                c = optionsPrice[2]
            for j in range(0, steps - i):
                optionAtNode = (q * optionsPrice[j] + qx * optionsPrice[j + 1]) / drift
                optionsPrice[j] = optionAtNode  # test

                if (american == 1):
                    assetAtNode = underlying * math.pow(u, steps - i - j - 1) * math.pow(d, j)
                    optionsPrice[j] = max(cf.payoff(assetAtNode, strike, cp), optionAtNode)
            # else:
            #    optionsPrice[j] = optionAtNode

        if (valueToFind == 0):
            return (optionsPrice[0])
        else:
            prima = optionsPrice[0]
            delta = (a - c) / (underlying * u * u - underlying * d * d)
            delta1 = (a - b) / (underlying * u * u - underlying * u * d)
            delta2 = (b - c) / (underlying * u * d - underlying * d * d)
            gamma = (delta1 - delta2) / ((underlying * u * u - underlying * d * d) / 2)
            vega = binomCRR3(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div, american, steps, 0,
                               0) - prima

            theta = (b - optionsPrice[0]) / (2 * h * 365)
            rho = binomCRR3(contract, underlying, strike, life_days, vol, rf + 0.01, cp, div, american, steps, 0,
                              0) - prima
            cont = 0
            impliedVol = vol

            if mktValue > 0:
                accuracy = 0.0001
                # cont = 0
                dif = mktValue - prima
                # impliedVol = vol

                while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                    impliedVol += (dif / vega / 100)
                    dif = mktValue - binomCRR3(contract, underlying, strike, life_days, impliedVol, rf, cp, div,
                                                 american, steps, 0, 0)
                    cont += 1
                    # vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
            # else:
            #    impliedVol = vol
            return cf.fillDerivativesArray(prima, delta, gamma, vega, theta, rho, impliedVol, cont)


if __name__=='__main__':
    print('__main__')
    print(binomCRR3())

else:
    print("Nombre de modelo:",__name__)