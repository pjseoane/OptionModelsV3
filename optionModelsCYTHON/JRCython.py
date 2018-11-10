#asi se ejecuta un cython desde un .py
import sys
sys.path.append('C:/Users/pauli/Dropbox/Python/OptionModels')
sys.path.append('C:/Users/pauli/Dropbox/Python/OptionModels/Cython')
#sys.path.append('C:/Users/pseoane/Dropbox/Python/OptionModels')
#sys.path.append('C:/Users/pseoane/Dropbox/Python/OptionModels/Cython')
sys.path.append('C:/Users/pauli/Documents/python/OptionModelsV3')



import pyximport, numpy
pyximport.install(setup_args=dict(include_dirs=[numpy.get_include()]))

from optionModelsCYTHON import jarrowCython as jrcy
a=jrcy.jarrowRuddCy("S",100,100,365,0.3,0.03,-1,0.0,True,100,6,0)
print("Array :",a)
print ("Prima",a[0])


