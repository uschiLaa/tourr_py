#general python imports first
import sys
import configparser

#r specific python imports
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
from rpy2.robjects.vectors import DataFrame

#load r packages we want to use
tourr = importr("tourr")
colorspace = importr("colorspace")
base = importr('base')

#get parameters from param file
params = configparser.ConfigParser( inline_comment_prefixes=( ';', ) )
params.read("parameter.ini")
inF = params.get("input","f")

#read input file into r dataframe
df = DataFrame.from_csvfile(inF)
#simple check that input format fits what we expect (only test number of columns here)
if df.ncol < 2:
	print("ERROR: need input in CSV format with at least 2 columns")
	sys.exit()

#sort points according to column defined by sort
sortCol = params.get("style","sort")
if sortCol in df.names:
        sortVec = base.order(df.rx2(sortCol))
        df = df.rx(sortVec,True)

#select columns to show
#here we assume the user knows which columns he is selecting, i.e. they should all be numeric
try:
	selCols = [int(x) for x in params.get("options","showCols").split(",")]
	selCols = robjects.IntVector(selCols)
	dfShow = df.rx(selCols)
#if this fails we show all numeric columns
except:
	numCols = base.sapply(df, base.is_numeric)
	dfShow = df.rx(numCols)

#get color vector
colN = params.get("style","col")
if colN in df.names:
	colV = df.rx2(colN)				#first extract column from dataframe
	colV = base.as_integer(base.factor(colV))	#some reformatting so we get values 1, 2, ...
	nCol = base.length(base.unique(colV))		#number of colors we need to select from palette
	pal = colorspace.rainbow_hcl(nCol)		#defining color palette
	col = pal.rx(colV)				#defining color vector
else: col = "black"					#if colors not set by user keep default

#get pch number/vector
pch = params.get("style","pch")
#if pch is an integer, we use this style for all points
try:
	pch = int(pch)
#otherwise pch should be column name, column containing integer values of the individual pch for each point
except:
	pch = df.rx2(pch)


tourr.animate_xy(dfShow, col=col, pch=pch)

