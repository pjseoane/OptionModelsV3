import numpy as np 
import math
import sys

#sys.path.append('C:/Users/pauli/Dropbox/Python/optionModels/Cython')
#sys.path.append('C:/Users/pseoane/Dropbox/Python/optionModels/Cython')

from scipy import stats

cimport numpy as np
cimport cython


cdef extern from "math.h" nogil:
    double exp(double)
    double sqrt(double)
    double pow (double,double)
    double fmax(double,double)
    double log (double)


def payoff(double underlying, double strike, int cp):
    return fmax((underlying-strike)*cp,0)


def driftCalc(contract,double rf,double h):
    return(1 if (contract=="F") else exp(rf*h))


def fillDerivativesArray(double prima,double delta,double gamma,double vega,double theta,double rho,double impVlt):
    cdef np.ndarray[np.double_t,ndim=1] derivatives=np.zeros(7)
    derivatives[0]=prima
    derivatives[1]=delta
    derivatives[2]=gamma
    derivatives[3]=vega
    derivatives[4]=theta
    derivatives[5]=rho
    derivatives[7]=impVlt
    return derivatives

def binomJRCY(contract="S",double underlying=100,double strike=100,double life_days=365,double vol=.30,double rf=0.03,int cp=-1,double div=0,int american=True, int steps=1000,int argument=6,double mktPrice=0):
    """ Price and option using the Jarrow-Rudd binomial model"""

    #Basic calculations
    cdef double h,u,d,drift,q,qx
    h= life_days/365/steps 
    u= exp((rf-0.5*pow(vol,2))*h+vol*sqrt(h))
    d= exp((rf-0.5*pow(vol,2))*h-vol*sqrt(h))
    drift=driftCalc(contract,rf,h)
    q=(drift-d)/(u-d)
    qx=1-q
    
    #Process the terminal stock price
    #Definicion Arreglos
    cdef np.ndarray[np.double_t,ndim=2] stkval=np.zeros((steps+1,steps+1))
    cdef np.ndarray[np.double_t,ndim=2] optval=np.zeros((steps+1,steps+1))
    
    cdef int i,j,m,cont
    cdef double accuracy,dif, impliedVol 

    stkval[0,0]=underlying
    
    for i in range (1, steps+1):
        stkval[i,0]=stkval[i-1,0]*u
        for j in range (1,i+1):
            stkval[i,j]=stkval[i-1,j-1]*d
    
    #Backward recursion for option price
    for j in range(steps+1):
        optval [steps,j]=fmax(0,payoff(stkval[steps,j],strike,cp))

    for m in range(steps):
        i=steps-m-1
        for j in range(i+1):
            optval[i,j]=(q*optval[i+1,j]+qx*optval[i+1,j+1])/drift

            if american:
                optval[i,j]=fmax(optval[i,j],payoff(stkval[i,j],strike,cp))
    def prima():
        return optval[0,0]

    def delta():
        return (optval[1, 1] - optval[1, 0]) / (stkval[1, 1] - stkval[1, 0])

    def gamma():
        return ((optval[2, 0] - optval[2, 1]) / (stkval[2, 0] - stkval[2, 1]) - (optval[2, 1] - optval[2, 2]) / (
                stkval[2, 1] - stkval[2, 2])) / ((stkval[2, 0] - stkval[2, 2]) / 2)
    def vega():
        return binomJRCY(contract, underlying, strike, life_days, vol + 0.01, rf, cp, div, american, steps,
                           0,0) - prima()

    def theta():
        return (optval[2, 1] - optval[0, 0]) / (2 * 365 * h)

    def rho():
        return binomJRCY(contract, underlying, strike, life_days, vol, rf+0.01, cp, div, american, steps,
                           0,0) - prima()

    def arr():
        return fillDerivativesArray(prima(), delta(), gamma(), vega(), theta(), rho(), ivVega())

    def ivVega():
        if mktPrice>0:
            accuracy=0.0001
            cont=0
            dif = mktPrice - prima()
            impliedVol = vol

            while (abs(dif) > accuracy and cont < 20 and mktPrice > 0 and impliedVol > 0.005):
                impliedVol += (dif / vega() / 100);
                dif = mktPrice - binomJRCY(contract, underlying, strike, life_days, impliedVol, rf, cp, div, american, steps, 0,0)
                cont += 1
                #vol=impliedVol  (#??para actualizar todas las greeks a la nueva vol
        else:
            impliedVol=vol
        return impliedVol

    switcher = {
        0: prima,
        1: delta,
        2: gamma,
        3: vega,
        4: theta,
        5: rho,
        6: arr,
        7: ivVega
    }
    func = switcher.get(argument, "Default Nothing")

    return func()

    """
    cdef double prima,delta,gamma,vega,theta,rho
    prima=optval[0,0]
    delta=(optval[1,1]-optval[1,0])/(stkval[1,1]-stkval[1,0])
    gamma=((optval[2,0]-optval[2,1])/(stkval[2,0]-stkval[2,1])-(optval[2,1]-optval[2,2])/(stkval[2,1]-stkval[2,2])) / ((stkval[2,0]-stkval[2,2])/2)
    vega=0
    theta=(optval[2,1]-optval[0,0])/(2*365*h)
    rho=0
    return fillDerivativesArray(prima,delta,gamma,vega,theta,rho)
    """
def binomCRR3CY(contract="S",double underlying=100,double strike=100,double life_days=365,double vol=.30,double rf=0.03,int cp=-1,double div=0,int american=True, int steps=1000):
    """ Price and option using the Coxx-Rubinstein model"""

    #Basic calculations
    cdef double h,u,d,drift,q,qx,z,assetAtNode,a,b,c,optionAtNode
    h=life_days/365/steps
    u= exp(vol*sqrt(h))
    d= exp(-vol*sqrt(h))
    drift=driftCalc(contract,rf,h)
    q=(drift-d)/(u-d)
    qx=1-q
    
    
    cdef int i,j 
    
    #declaracion de arrays
    cdef np.ndarray[np.double_t,ndim=1] optionsPrice=np.zeros((steps+1))
    
    #Fill array Boundary Conditions
    for i in range(0,steps+1):
        assetAtNode=underlying*pow(u,(steps-i))*pow(d,i)
        optionsPrice[i]=payoff(assetAtNode,strike,cp)
      
    # Rolling Backward
    for i in range(0,steps):
        if(i==steps-2):
            a=optionsPrice[0]
            b=optionsPrice[1]
            c=optionsPrice[2]
        for j in range(0, steps-i):
                optionAtNode=(q*optionsPrice[j]+qx*optionsPrice[j+1])/drift
                
                if (american==1):
                    assetAtNode=underlying*pow(u, steps-i-j-1)*pow(d,j)
                    optionsPrice[j]=fmax(payoff(assetAtNode,strike,cp),optionAtNode)
                else:
                    optionsPrice[j]=optionAtNode


    
    cdef double prima,delta,delta1,delta2,gamma,vega,theta,rho
    prima=optionsPrice[0]

    delta=(a-c)/(underlying*u*u-underlying*d*d)
    
    delta1=(a-b)/(underlying*u*u-underlying*u*d)
    delta2=(b-c)/(underlying*u*d-underlying*d*d)
    gamma=(delta1-delta2)/((underlying*u*u-underlying*d*d)/2)

    vega=0
    theta=(b-optionsPrice[0])/(2*h*365)
    rho=0

    return fillDerivativesArray(prima,delta,gamma,vega,theta,rho)
    
def binomCRR4CY(contract="S",double underlying=100,double strike=100,double life_days=365,double vol=.30,double rf=0.03,int cp=-1,double div=0,int american=True, int steps=1000):
    
    cdef double h,u,d,drift,q,qx
    #Basic calculations
    h=life_days/365/steps
    u= exp(vol*sqrt(h))
    d= exp(-vol*sqrt(h))
    drift=driftCalc(contract,rf,h)
    
    q=(drift-d)/(u-d)
    qx=1-q

    #Arrays for stock & options Tree
    #Process the terminal stock price
    #Definicion Arreglos
    cdef np.ndarray[np.double_t,ndim=2] stkval=np.zeros((steps+1,steps+1))
    cdef np.ndarray[np.double_t,ndim=2] optval=np.zeros((steps+1,steps+1))
    
    cdef int i,j,m

    stkval[0,0]=underlying
        
    for i in range (1, steps+1):
        stkval[i,0]=stkval[i-1,0]*u
        for j in range (1,i+1):
            stkval[i,j]=stkval[i-1,j-1]*d


    for j in range(steps+1):
        optval[steps,j]=fmax(0,payoff(stkval[steps,j],strike,cp))
    
    for m in range(steps):
        i=steps-m-1
        for j in range(i+1):
            optval[i,j]=(q*optval[i+1,j]+qx*optval[i+1,j+1])/drift

            if american:
                optval[i,j]=fmax(optval[i,j],payoff(stkval[i,j],strike,cp))

    cdef double prima,delta,gamma,vega,theta,rho
    prima=optval[0,0]
    delta=(optval[1,1]-optval[1,0])/(stkval[1,1]-stkval[1,0])
    gamma=((optval[2,0]-optval[2,1])/(stkval[2,0]-stkval[2,1])-(optval[2,1]-optval[2,2])/(stkval[2,1]-stkval[2,2])) / ((stkval[2,0]-stkval[2,2])/2)
    theta=(optval[2,1]-optval[0,0])/(2*365*h)
    vega=0
    rho=0

    return fillDerivativesArray(prima,delta,gamma,vega,theta,rho)
           
def blackScholesCY(contract="S",double underlying=100,double strike=100,double life_days=365,double vol=.30,double riskFree=0.03,int cp=-1,double div=0):
        
    cdef double dayYear=life_days/365
    cdef double q=div if (contract=="S") else riskFree
        
    cdef double d1 = (log(underlying / strike) + ((riskFree-q) + 0.5 * pow(vol, 2)) * dayYear) / (vol * sqrt(dayYear))
    cdef double d2 = d1 - vol * sqrt(dayYear)

    #gamma y vega son iguales para call y put
    cdef double gamma=stats.norm.pdf(d1) *exp(-riskFree*dayYear) / (underlying*vol*sqrt(dayYear))
    cdef double vega=underlying * sqrt(dayYear)*stats.norm.pdf(d1) / 100

    cdef double prima=cp * underlying * exp(-q * dayYear) * stats.norm.cdf(cp * d1) - cp * strike * exp(-riskFree * dayYear) * stats.norm.cdf(cp * d2)
    t=(0 if (cp==1) else 1)
                
    cdef double delta=exp(-q * dayYear)*(stats.norm.cdf(d1)-t)
        
    cdef double theta1=-(underlying*vol*stats.norm.pdf(d1)) / (2 * sqrt(dayYear))
    cdef double theta2=cp*strike*riskFree*exp(-riskFree * dayYear)*stats.norm.cdf(d2*cp)+cp*div*underlying*stats.norm.cdf(d1*cp)
    cdef double theta=(theta1 - theta2)  / 365
    cdef double rho=cp*strike*dayYear*exp(-riskFree * dayYear)*stats.norm.cdf(cp * d2)  / 100 #Hull pag 317
    
    return fillDerivativesArray(prima,delta,gamma,vega,theta,rho)