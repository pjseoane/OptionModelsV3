#import math
from scipy import stats
import math
#from optionModels.commonFuncs import fillDerivativesArray as fd
import optionModels.commonFuncs as cf


def blackScholes(contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=-1, div=0,valueToFind=6,mktValue=0):
    dayYear = life_days / 365
    q = div if (contract == "S") else riskFree

    d1 = (math.log(underlying / strike) + ((riskFree - q) + 0.5 * math.pow(vol, 2)) * dayYear) / (
                vol * math.sqrt(dayYear))
    d2 = d1 - vol * math.sqrt(dayYear)
    vega=underlying * math.sqrt(dayYear) * stats.norm.pdf(d1) / 100

    # gamma y vega son iguales para call y put
    gamma=stats.norm.pdf(d1) * math.exp(-riskFree * dayYear) / (underlying * vol * math.sqrt(dayYear))

    prima=cp * underlying * math.exp(-q * dayYear) * stats.norm.cdf(cp * d1) - cp * strike * math.exp(
        -riskFree * dayYear) * stats.norm.cdf(cp * d2)

    t = (0 if (cp == 1) else 1)

    delta=math.exp(-q * dayYear) * (stats.norm.cdf(d1) - t)

    theta1 = -(underlying * vol * stats.norm.pdf(d1)) / (2 * math.sqrt(dayYear))
    theta2 = cp * strike * riskFree * math.exp(-riskFree * dayYear) * stats.norm.cdf(
        d2 * cp) + cp * div * underlying * stats.norm.cdf(d1 * cp)


    theta= (theta1 - theta2) / 365

    rho=cp * strike * dayYear * math.exp(-riskFree * dayYear) * stats.norm.cdf(cp * d2) / 100  # Hull pag 317

    if (valueToFind==0):
        return prima
    else:
        impliedVol = vol
        cont = 0

        if mktValue>0:
            accuracy=0.0001
            dif = mktValue - prima
            #impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                impliedVol += (dif / vega / 100)
                dif = mktValue - blackScholes(contract, underlying, strike, life_days, impliedVol, riskFree, cp, div,0,0)
                cont += 1
                #vol=impliedVol  #??para actualizar todas las greeks a la nueva vol
        return cf.fillDerivativesArray(prima, delta, gamma, vega, theta, rho, impliedVol, cont)



if __name__=='__main__':
    print('__main__')
    print(blackScholes())
else:
    print("Nombre de modelo:",__name__)

