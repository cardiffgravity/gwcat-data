import gwcat
import json
import os
import argparse

parser=argparse.ArgumentParser(prog="updatecat.py", description="Updates the gwcat-data database")
parser.add_argument('-u','--update', dest='update', action='store_true', default=False, help='Update from GWOSC and GraceDB source')
parser.add_argument('-d','--datadir', dest='datadir', type=str, default='data/', help='directory in which data is stored')
args=parser.parse_args()
dataDir=args.datadir
update=args.update

if update==True:
    gc=gwcat.GWCat(fileIn=os.path.join(dataDir,'events.json'),dataDir=dataDir)
    # gdb=json.load(open(os.path.join(dataDir,'gracedb.json')))
    # gwoscdata=json.load(open(os.path.join(dataDir,'gwosc.json')))
    gwoscdata=gwcat.gwosc.getGwosc(verbose=True,export=True,dirOut=dataDir)
    gdb=gwcat.gracedb.getSuperevents(verbose=True,export=True,dirOut=dataDir)
    json.dump(gwoscdata,open(os.path.join(dataDir,'gwosc.min.json'),'w'))
    json.dump(gdb,open(os.path.join(dataDir,'gracedb.min.json'),'w'))
    print('importing GWOSC...')
    gc.importGwosc(gwoscdata,verbose=False)
    print('importing GraceDB...')
    gc.importGraceDB(gdb,verbose=False)
else:
    print('importing from local file')
    gc=gwcat.GWCat(fileIn=os.path.join(dataDir,'gwosc_gracedb.json'),dataDir=dataDir)
gc.updateMaps(verbose=False)
gc.plotMapPngs(verbose=True,overwrite=False)

# export library
gc.exportJson(os.path.join(dataDir,'gwosc_gracedb.json'))
gcdat=json.load(open(os.path.join(dataDir,'gwosc_gracedb.json')))
# create minified version of json file
json.dump(gcdat,open(os.path.join(dataDir,'gwosc_gracedb.min.json'),'w'))
# convert json files to jsonp
gwcat.json2jsonp(os.path.join(dataDir,'gwosc_gracedb.json'),os.path.join(dataDir,'gwosc_gracedb.jsonp'))
gwcat.json2jsonp(os.path.join(dataDir,'gwosc_gracedb.min.json'),os.path.join(dataDir,'gwosc_gracedb.min.jsonp'))