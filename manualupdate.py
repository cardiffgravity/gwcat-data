#!/Applications/anaconda3/anaconda3/bin/python3.6
#test update
import gwcat
import json
import os
# import argparse

# ARGUMENTS LISTED FOR CONVENIENCE
# parser=argparse.ArgumentParser(prog="updatecat.py", description="Updates the gwcat-data database")
# parser.add_argument('-u','--update', dest='update', action='store_true', default=False, help='Update from GWOSC and GraceDB source')
# parser.add_argument('-v','--verbose', dest='verbose', action='store_true', default=False, help='Set to print more helpful text to the screen')
# parser.add_argument('-o','--overwrite', dest='overwrite', action='store_true', default=False, help='Regenerate and overwrite image files')
# parser.add_argument('-f','--forceupdate', dest='forceupdate', action='store_true', default=False, help='Force (re)download of files')
# parser.add_argument('-m','--forcemap', dest='forcemap', action='store_true', default=False, help='Force (re)download of fits files')
# parser.add_argument('-g','--gravoscope', dest='gravoscope', action='store_true', default=False, help='Update Gravoscope tiles')
# parser.add_argument('-d','--datadir', dest='datadir', type=str, default='data/', help='directory in which data is stored')
# parser.add_argument('-b','--baseurl', dest='baseurl', type=str, default='https://data.cardiffgravity.org/gwcat-data/', help='Base URL to prepend to relative links [Default=https://data.cardiffgravity.org/gwcat-data/]')
# args=parser.parse_args()

dataDir='data/'
update=True
verbose=True
forceupdate=False
forcemap=False
overwrite=False
baseurl='https://data.cardiffgravity.org/gwcat-data/'
gravoscope=True

if update==True:
    gc=gwcat.GWCat(fileIn=os.path.join(dataDir,'gwosc_gracedb.json'),dataDir=dataDir,baseurl=baseurl,verbose=verbose)
    gdb=json.load(open(os.path.join(dataDir,'gracedb.json')))
    gwoscdata=json.load(open(os.path.join(dataDir,'gwosc.json')))
    knownEvents=gc.getTimestamps()

    gwoscdata=gwcat.gwosc.getGwosc(export=True,dirOut=dataDir,verbose=verbose)
    gdb=gwcat.gracedb.getSuperevents(export=True,dirOut=dataDir,verbose=verbose,
        knownEvents=knownEvents,forceUpdate=forceupdate)
    json.dump(gwoscdata,open(os.path.join(dataDir,'gwosc.min.json'),'w'))
    json.dump(gdb,open(os.path.join(dataDir,'gracedb.min.json'),'w'))


    print('importing GWOSC...')
    gc.importGwosc(gwoscdata,verbose=verbose)
    print('importing GraceDB...')
    gc.importGraceDB(gdb,verbose=verbose,forceUpdate=forceupdate)
else:
    print('importing from local file')
    gc=gwcat.GWCat(fileIn=os.path.join(dataDir,'gwosc_gracedb.json'),dataDir=dataDir)

gc.updateMaps(verbose=verbose,forceUpdate=forcemap)
gc.plotMapPngs(verbose=verbose,overwrite=overwrite)

if gravoscope:
    print('Updating gravoscope')
    gc.makeGravoscopeTiles(verbose=True,maxres=6)


# export library
gc.exportJson(os.path.join(dataDir,'gwosc_gracedb.json'))
gcdat=json.load(open(os.path.join(dataDir,'gwosc_gracedb.json')))
# create minified version of json file
json.dump(gcdat,open(os.path.join(dataDir,'gwosc_gracedb.min.json'),'w'))
# convert json files to jsonp
gwcat.json2jsonp(os.path.join(dataDir,'gwosc_gracedb.json'),os.path.join(dataDir,'gwosc_gracedb.jsonp'))
gwcat.json2jsonp(os.path.join(dataDir,'gwosc_gracedb.min.json'),os.path.join(dataDir,'gwosc_gracedb.min.jsonp'))

