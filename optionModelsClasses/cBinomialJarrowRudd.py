from optionModelsClasses import cBinomialMask as cBinom


class cBinomJR(cBinom.cBinomialMask):
    def __init__(self, contract="S", underlying=100, strike=100, life_days=365, vol=.30, riskFree=0.03, cp=1, div=0
                 , american=True, steps=100, mktValue=0):
        super().__init__(contract, underlying, strike, life_days, vol, riskFree, cp, div, american, steps, mktValue)

        self.calc()

    def buildUnderlyingTree(self, u, d):

        undva
        l = np.zeros((self.step s +1, self.step s +1))
        undval[0, 0] = self.underlying

        for i in range(1, self.step s +1):
            undval[i, 0] = undval[i - 1, 0] * u
            for j in range(1, i + 1):
                undval[i, j] = undval[i - 1, j - 1] * d
        return undval

    def buildOptionTree(self, p, drift):
        opttre
        e = np.zeros((self.step s +1, self.step s +1))

        p
        x = 1 - p
        for j in range(self.step s +1):
            opttree[self.steps, j] = max(0, self.payoff(self.stkval[self.steps, j], self.strike))

        for m in range(self.steps): i = self.steps - m - 1
        for j in range(i + 1):
            opttree[i, j] = (p * opttre e[i +1, j]+px * opt t re e[i +1, j+1]) / dri
            f
            t

            if self.american:
                opttree[i, j] = max(opttr
                ee[i, j], self.payo
                ff(self.stkval[i, j], self.stri
                ke) )
        return opttree

    def calc(self):
        # Basic calculations

        drift = self.drift()
        u = exp((self.riskFree - 0.5 * pow(sel f.vo l, 2)) * self.h + s
        elf.vol * sq
        r
        t(self.h) )
        d = exp((self.riskFree - 0.5 * pow(sel f.vo l, 2)) * self.h - s
        elf.vol * sq
        r
        t(self.h) )
        p = (drift - d) / (u - d)  # px=(1-p)

        # ------
        self.stkval = self.buildUnderlying
        T
        ree(u, d)
        self.optva
        l = self.buildOptionTree(p, drift)
        # ---- -

        self.prima = self.optval[0, 0]
        self.delta = (self.optval[1, 1] - se l f.optval[1, 0]) / (s e lf.stkval[1, 1] -se l f.stkval[1, 0])
        self.gamm
        a = ((self.optval[2, 0] - s e lf.optval[2, 1]) / (s e lf.stkval[2, 0] -se l f.stkval[2, 1]) - (s
                                                                                                       e lf.optval[2, 1] -se l f
                                                                                                       .optval[2, 2]) / (
                 s e lf.stkval[2, 1] -se l f.stkval[2, 2])) / ((self.stkval[2, 0] - self
                                                                .stkval[2, 2]) / 2)
        self.th
        eta = (self.optval[2, 1] - sel f.optval[0, 0]) / (2 * 3 65 * self.h)
        s
        e
        lf.v
        ega = 0
        self.rho = 0

        return sup
        e
        r().fillDerivativesArray(self.prima, self.delta, self.gamma, self.vega, s
        elf.theta, s
        elf.rho)
