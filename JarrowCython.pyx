
""" Para llamar a este modulo desde otro file usar:
import sys
sys.path.append('C:/Users/pauli/Dropbox/Python/optionModelsDEF')
esto coloca a ese path en el sistema

"""
import math

#import pyximport
#import numpy as np
pyximport.install(setup_args=dict(include_dirs=[numpy.get_include()]))
#import numpy as np

cimport numpy as np
cimport cython

cdef extern from "math.h" nogil:
    double exp(double)
    double sqrt(double)
    double pow (double,double)
    double fmax(double,double)


def jarrowRuddCy(contract, double s, double k,double t,double v,double rf,double cp, double div, int am=False, int n=100,int valueToFind=0,double mktValue=0):
    """ Price and option using the Jarrow-Rudd binomial model

    s: initial stock price
    k: strike preice
    t: expiration time in days
    v: volatility
    rf: risk-free rate
    cp: +1/-1 for call/put
    am: True/False for American/European
    n: binomial steps
    """
    cdef double h,u,d,drift,q,qx
    cdef int i,j,m,cont
    cdef np.ndarray[np.double_t,ndim=2] stkval=np.zeros((n+1,n+1))
    cdef np.ndarray[np.double_t,ndim=2] optval=np.zeros((n+1,n+1))
    cdef np.ndarray[np.double_t,ndim=1] derivatives=np.zeros(10)
    cdef double prima,vega,accuracy,dif,impliedVol

    #Basic calculations
    h= t/365/n 
    u= math.exp((rf-0.5*math.pow(v,2))*h+v*math.sqrt(h))
    d= math.exp((rf-0.5*math.pow(v,2))*h-v*math.sqrt(h))

    drift=1 if (contract=="F") else math.exp(rf*h)

    
    q=(drift-d)/(u-d)
    qx =1-q

    def payoff(double und,double strk):
        return fmax((und-strk)*cp,0)

    #Process the terminal stock pricederi
    stkval[0,0]=s
    for i in range (1, n+1):
        stkval[i,0]=stkval[i-1,0]*u
        for j in range (1,i+1):
            stkval[i,j]=stkval[i-1,j-1]*d
    
    #Backward recursion for option price
    for j in range(n+1):
        optval[n,j]=fmax(0,payoff(stkval[n,j],k))

    for m in range(n):
        i=n-m-1
        for j in range(i+1):
            optval[i,j]=(q*optval[i+1,j]+qx*optval[i+1,j+1])/drift

            if am==1:
                optval[i,j]=fmax(optval[i,j],payoff(stkval[i,j],k))

    if (valueToFind==0):
        return (optval[0,0])
    else:
        prima=optval[0,0]
        vega=jarrowRuddCy(contract, s, k, t, v + 0.01, rf, cp, div,am, n, 0) - prima

        derivatives[0]=prima #prima
        derivatives[1]=(optval[1,1]-optval[1,0])/(stkval[1,1]-stkval[1,0]) #delta
        derivatives[2]=((optval[2,0]-optval[2,1])/(stkval[2,0]-stkval[2,1])-(optval[2,1]-optval[2,2])/(stkval[2,1]-stkval[2,2])) / ((stkval[2,0]-stkval[2,2])/2) #gamma
        derivatives[3]=(vega)  # vega
        derivatives[4]=(optval[2,1]-optval[0,0])/(2*365*h) #theta
        derivatives[5]=(jarrowRuddCy(contract, s, k, t, v, rf+0.01, cp, div,am, n, 0,0) - prima) # rho

        if mktValue > 0:
            accuracy = 0.0001
            cont = 0
            dif = mktValue - prima
            impliedVol = v

            while (abs(dif) > accuracy and cont < 20 and impliedVol > 0.005):
                impliedVol += (dif / vega / 100)
                dif = mktValue - jarrowRuddCy(contract, s, k, t, impliedVol, rf, cp, div,am, n, 0, 0)
                cont += 1
                    # vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
        else:
            impliedVol = v
        derivatives[6]=impliedVol
        derivatives[7]=cont

    return derivatives

