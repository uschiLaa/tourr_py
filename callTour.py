#general python imports first
import sys
import configparser

#r specific python imports
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
from rpy2.robjects.vectors import DataFrame

#load r packages we want to use
tourr = importr("tourr")

#get options, for now simple input file path being passed in as sys.argv[1]
#inF = sys.argv[1]

#get parameters from param file
params = configparser.ConfigParser( inline_comment_prefixes=( ';', ) )
params.read("parameter.ini")
inF = params.get("input","f")

#read input file into r dataframe
df = DataFrame.from_csvfile(inF)
if df.ncol < 2:
	print("ERROR: need input in CSV format with at least 2 columns")
	sys.exit()

tourr.animate(df)


#do more fancy stuff as
#getting column from dataframe: df.rx("colName") #want to use this e.g. for color, point style
#select subset from df: selectCols = robjects.StrVector(("rn1", "rn2")) #just give vector of column names
#then define new df simply as: subDf = df.rx(selectCols)
