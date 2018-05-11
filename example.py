#simple example of how to pass list into r and run tourr

##Header to import r and relevant packages
#r specific python imports
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
from rpy2.robjects.numpy2ri import numpy2ri
robjects.conversion.py2ri = numpy2ri
robjects.numpy2ri.activate()
from rpy2.robjects.vectors import DataFrame
#load r packages we want to use
tourr = importr("tourr")
colorspace = importr("colorspace")
base = importr('base')

##Header for python packages
import numpy as np


##build data in python
mean = np.zeros(4)
cov = [[2,1,0,0],[1,3,0,0],[0,0,1,1],[0,0,1,1]]
d = np.random.multivariate_normal(mean,cov,100)

nr,nc = d.shape
mat = robjects.r.matrix(d, nrow=nr, ncol=nc)
robjects.numpy2ri.deactivate()
#tourr animate only works if we assing colnames
mat.colnames = robjects.StrVector(("a","b","c","d"))
disp = tourr.display_xy()

tourr.animate(mat, tour_path= tourr.grand_tour(), display=disp)


