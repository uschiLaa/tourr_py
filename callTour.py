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

#select columns to show
try:
	selCols = [int(x) for x in params.get("options","showCols").split(",")]
	selCols = robjects.IntVector(selCols)
	dfShow = df.rx(selCols)
#if this fails we show all columns
#FIXME should not be df but only numeric columns
except: dfShow = df

#get color vector
colN = params.get("style","col")
if colN in df.names:
	colV = df.rx2(colN)				#first extract column from dataframe
	colV = base.as_integer(base.factor(colV))	#some reformatting so we get values 1, 2, ...
	nCol = base.length(base.unique(colV))		#number of colors we need to select from palette
	pal = colorspace.rainbow_hcl(nCol)		#defining color palette
	col = pal.rx(colV)				#defining color vector
else: col = "black"					#if colors not set by user keep default

tourr.animate_xy(dfShow, col=col)

