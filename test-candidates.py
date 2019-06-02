#!/Applications/anaconda3/anaconda3/bin/python3.6
import gwcat
import json
import os

baseurl='https://data.cardiffgravity.org/gwcat-data/'
verbose=True
dataDir='data/'

gc=gwcat.GWCat(fileIn=os.path.join(dataDir,'gwosc_gracedb.json'),dataDir=dataDir,baseurl=baseurl,verbose=verbose)
knownEvents=gc.getTimestamps()

gwosctrig=gwcat.gwosc.getGwosc(export=True,dirOut=dataDir,verbose=verbose,triggers=True)

gc.importGwosc(gwosctrig,verbose=verbose)
gc.exportJson(os.path.join(dataDir,'gwosc-marginal.json'))