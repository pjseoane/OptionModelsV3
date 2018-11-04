import numpy as np 
import math

""" Para llamar a este modulo desde otro file usar:
import sys
sys.path.append('C:/Users/pauli/Dropbox/Python/OptionModels')
esto coloca a ese path en el sistema

"""

def jarrowRudd(contract,s,k,t,v,rf,cp,div,am=True, n=100,valueToFind=0,mktValue=0):
    """ Price and option using the Jarrow-Rudd binomial model

    s: initial stock price
    k: strike price
    t: expiration time in days
    v: volatility
    rf: risk-free rate
    cp: +1/-1 for call/put
    am: True/False for American/European
    n: binomial steps
    """

    #Basic calculations
    h= t/365/n 
    u= math.exp((rf-0.5*math.pow(v,2))*h+v*math.sqrt(h))
    d= math.exp((rf-0.5*math.pow(v,2))*h-v*math.sqrt(h))
    
    drift= 1 if(contract=="F") else (math.exp(rf*h))
    
    #if (contract=="F"):
    #    drift=1
    #else:
    #    drift=math.exp(rf*h)
    q=(drift-d)/(u-d)
    qx=1-q

    def payoff(underlying,strike):
        return max((underlying-strike)*cp,0)

    
    #Process the terminal stock price
    stkval=np.zeros((n+1,n+1))
    optval=np.zeros((n+1,n+1))
    derivatives=[]
    stkval[0,0]=s
    
    for i in range (1, n+1):
        stkval[i,0]=stkval[i-1,0]*u
        for j in range (1,i+1):
            stkval[i,j]=stkval[i-1,j-1]*d
    
    #Backward recursion for option price
    for j in range(n+1):
        optval [n,j]=max(0,payoff(stkval[n,j],k))

    for m in range(n):
        i=n-m-1
        for j in range(i+1):
            optval[i,j]=(q*optval[i+1,j]+qx*optval[i+1,j+1])/drift

            if am:
                optval[i,j]=max(optval[i,j],payoff(stkval[i,j],k))

    if (valueToFind==0):
        return (optval[0,0])
    else:
        prima=optval[0,0]
        vega=jarrowRudd(contract, s, k, t, v + 0.01, rf, cp, div,am, n, 0) - prima

        derivatives.append(prima) #prima
        derivatives.append((optval[1,1]-optval[1,0])/(stkval[1,1]-stkval[1,0])) #delta
        derivatives.append(((optval[2,0]-optval[2,1])/(stkval[2,0]-stkval[2,1])-(optval[2,1]-optval[2,2])/(stkval[2,1]-stkval[2,2])) / ((stkval[2,0]-stkval[2,2])/2)) #gamma
        derivatives.append(vega)  # vega
        derivatives.append((optval[2,1]-optval[0,0])/(2*365*h)) #theta
        derivatives.append(jarrowRudd(contract, s, k, t, v, rf+0.01, cp, div,am, n, 0,0) - prima)  # rho

        if mktValue > 0:
            accuracy = 0.0001
            cont = 0
            dif = mktValue - prima
            impliedVol = v

            while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                impliedVol += (dif / vega / 100)
                dif = mktValue - jarrowRudd(contract, s, k, t, impliedVol, rf, cp, div,am, n, 0, 0)
                cont += 1
                    # vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
        else:
            impliedVol = v
        derivatives.append(impliedVol)

        return derivatives
    #return optval[0,0] 
