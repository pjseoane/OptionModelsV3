#Binom Americam + BSEuropean - Binom European


import optionModelsDEF.binomialJarrowRuddv4 as binomJR
import optionModelsDEF.blackScholesModel as bs
import optionModelsDEF.commonFuncs as cf


def binomCV(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
            steps=100,valueToFind=6,mktValue=10):

    amOpt=binomJR.binomJRv4(contract, underlying, strike, life_days, vol, rf, cp, div, True, steps,valueToFind,mktValue)
    bsOpt=bs.blackScholes(contract, underlying, strike, life_days, vol, rf, cp, div)
    euOpt=binomJR.binomJRv4(contract, underlying, strike, life_days, vol, rf, cp, div, False, steps,valueToFind,mktValue)

    if (valueToFind==0):
        return amOpt + bsOpt[0] - euOpt
    else:
        prima=amOpt[0]+bsOpt[0]-euOpt[0]
        delta=amOpt[1]+bsOpt[1]-euOpt[1]
        gamma=amOpt[2]+bsOpt[2]-euOpt[2]
        vega=amOpt[3]+bsOpt[3]-euOpt[3]
        theta=amOpt[4]+bsOpt[4]-euOpt[4]
        rho=amOpt[5]+bsOpt[5]-euOpt[5]


    impliedVol = vol
    if mktValue > 0:  # Calculo de implied Vlts
        difToModel = lambda vlt: mktValue - binomCV(contract, underlying, strike, life_days, vlt, rf, cp, div,
                                                      american, steps, 0, 0)
        impliedVol = cf.ivVega(difToModel, vol, vega, 0.0001, 20)

    return cf.fillDerivativesArray(prima, delta, gamma, vega, theta, rho, impliedVol,0)


if __name__ == '__main__':
    print('__main__')
    print("Modelo binom CV :\n", binomCV())

else:
    print("Nombre de binom CV:", __name__)
