from rpy2.robjects.packages import importr
utils = importr('utils')
utils.chooseCRANmirror(ind=5)
utils.install_packages('tourr')
