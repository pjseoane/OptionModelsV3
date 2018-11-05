import math
import numpy as np
import optionModels.commonFuncs as cf






def binomJRv4(contract="S", underlying=100, strike=100, life_days=365, vol=.30, rf=0.03, cp=-1, div=0, american=True,
            steps=100,valueToFind=6,mktValue=11):
    """ Price and option using the Jarrow-Rudd binomial model"""


    # Basic calculations
    h = life_days / 365 / steps
    u = math.exp((rf - 0.5 * math.pow(vol, 2)) * h + vol * math.sqrt(h))
    d = math.exp((rf - 0.5 * math.pow(vol, 2)) * h - vol * math.sqrt(h))

    drift = cf.driftCalc(contract, rf, h)

    q = (drift - d) / (u - d)
    qx = 1 - q

    # Process the terminal stock price
    stkval = np.zeros((steps + 1, steps + 1))
    optval = np.zeros((steps + 1, steps + 1))
    stkval[0, 0] = underlying

    for i in range(1, steps + 1):
        stkval[i, 0] = stkval[i - 1, 0] * u
        for j in range(1, i + 1):
            stkval[i, j] = stkval[i - 1, j - 1] * d

    # Backward recursion for option price
    for j in range(steps + 1):
        optval[steps, j] = max(0, cf.payoff(stkval[steps, j], strike, cp))

    for m in range(steps):
        i = steps - m - 1
        for j in range(i + 1):
            optval[i, j] = (q * optval[i + 1, j] + qx * optval[i + 1, j + 1]) / drift

            if american:
                optval[i, j] = max(optval[i, j], cf.payoff(stkval[i, j], strike, cp))

    if (valueToFind==0):
        return (optval[0,0])
    else:
        prima=optval[0,0]
        delta=(optval[1,1]-optval[1,0])/(stkval[1,1]-stkval[1,0])
        vega=binomJRv4(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div,american, steps, 0,0) - prima
        gamma=((optval[2,0]-optval[2,1])/(stkval[2,0]-stkval[2,1])-(optval[2,1]-optval[2,2])/(stkval[2,1]-stkval[2,2])) / ((stkval[2,0]-stkval[2,2])/2)
        theta=(optval[2,1]-optval[0,0])/(2*365*h)
        rho=binomJRv4(contract, underlying, strike, life_days, vol, rf+0.01, cp, div,american, steps, 0,0) - prima

        diftoModel1 = lambda vlt: mktValue - binomJRv4(contract, underlying, strike, life_days, vlt, rf, cp, div,
                                                         american, steps, 0, 0)

        diftoModel2= lambda vlt: mktValue-binomJRv4(contract, underlying, strike, life_days, vlt, rf, cp, div,
                                                         american, steps, 0, 0)

        if(prima<=mktValue):
            mini=vol
            maxi=vol*3
        else:
            mini=0
            maxi=vol

        impliedVol2=cf.biseccion(diftoModel2,mini,maxi,0.0001,50)
        impliedVol1=cf.ivVega(diftoModel1,vega,0.0001)

        #Calculo de impVlt
        cont = 0
        impliedVol = vol
        if mktValue > 0:

            accuracy = 0.0001
            #cont = 0
            dif = mktValue - prima
            #impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                impliedVol += (dif / vega / 100)
                #dif = mktValue - binomJRv4(contract, underlying, strike, life_days, impliedVol, rf, cp, div,american, steps, 0,0)
                dif=difference(binomJRv4,impliedVol)
                cont += 1


        return cf.fillDerivativesArray(prima,delta,gamma,vega,theta,rho,impliedVol2,impliedVol)

if __name__ == '__main__':
    print('__main__')
    print("Modelo binomJRv4 :\n", binomJRv4())

else:
        print("Nombre de modelo:", __name__)

