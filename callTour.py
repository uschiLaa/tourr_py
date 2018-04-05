#general python imports first
import sys, os
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

#selecting tour type between grand and little tour
tourType = params.get("options","tourType")
if not tourType in ["grand", "little"]:
	print("WARNING: Unknown tour type selected, defaulting to grand tour")
	tourType = "grand"
if tourType == "grand":
	tour = tourr.grand_tour()
else:
	tour = tourr.little_tour()

#rescaling or not?
rescale = params.getboolean("options","rescale")

#display setting
disp = tourr.display_xy(col=col, pch=pch)

#need to convert dataframe to matrix for animation
mat = base.as_matrix(dfShow)

#decide if displaying output or saving gif
saveGIF = (params.get("output","out")=="GIF")
if saveGIF:
	#try to load moviepy
	try:
		import moviepy.editor as mpy
	except:
		print("ERROR: Need to install moviepy to save GIF output.")
		sys.exit()
	#first check that nProj is integer
	try:
		nProj = int(params.get("output","nProj"))
	except:
		print("WARNING: nProj must be integer number, defaulting to 10")
		nProj = 10
	#check that output name makes sense
	outName = params.get("output","n")
	if not outName.split(".")[1] == "gif":
		outName = outName.split(".")[0]+".gif"
		print("WARNING: Output filename should have extension '.gif', using output filename %s" %outName)
	#check that fps is int
	try:
		fps = int(params.get("output","fps"))
	except:
		print("WARNING: fps must be given as integer, defaulting to 10")
		fps = 10
	#now we can generate the GIF
	#check if temp directory exists, create if not
	if not os.path.isdir('temp/'): os.mkdir('temp/')
	#clean temp directory
	os.system("rm temp/*")
	#start by saving png output
	tourr.render(mat, tour, disp, 'png', "temp/temp-%03d.png", rescale=rescale, frames=nProj)
	#get all output png files
	pngL = os.listdir("temp")
	pngL.sort()
	pngL = ["temp/"+ x for x in pngL]
	clip = mpy.ImageSequenceClip(pngL, fps=fps)
	clip.write_gif(outName, fps=fps)

else:
	#otherwise display tour on default graphic device with infinite number of bases (close window to terminate)
	#FIXME can I suppress error messages when closing?
	tourr.animate(mat, tour_path= tour, display=disp, rescale=rescale)

