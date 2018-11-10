#asi se ejecuta un cython desde un .py
import pyximport, numpy
pyximport.install(setup_args=dict(include_dirs=[numpy.get_include()]))

from optionModelsCYTHON import jarrowCython as jrcy
a=jrcy.jarrowRuddCy("F",100,100,365,0.3,0.03,-1,0,True,100,6,0)
print(a)


