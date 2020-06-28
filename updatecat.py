#test update
statusFile='./status.log'
statF=open(statusFile,'w')
statF.write('pending\n')
statF.close()

import sys,os
import argparse

parser=argparse.ArgumentParser(prog="updatecat.py", description="Updates the gwcat-data database")
parser.add_argument('--codedir', dest='codedir', type=str, default='python', help='directory in which dev code is stored')
parser.add_argument('-u','--update', dest='update', action='store_true', default=False, help='Update from GWOSC and GraceDB source')
parser.add_argument('-v','--verbose', dest='verbose', action='store_true', default=False, help='Set to print more helpful text to the screen')
parser.add_argument('-o','--overwrite', dest='overwrite', action='store_true', default=False, help='Regenerate and overwrite image files')
parser.add_argument('-f','--forceupdate', dest='forceupdate', action='store_true', default=False, help='Force (re)download of files')
parser.add_argument('-s','--skymaps', dest='skymaps', action='store_true', default=False, help='Plot skymaps')
parser.add_argument('-m','--forcemap', dest='forcemap', action='store_true', default=False, help='Force (re)download of fits files')
parser.add_argument('-g','--gravoscope', dest='gravoscope', action='store_true', default=False, help='Update Waveforms')
parser.add_argument('-w','--waveforms', dest='waveforms', action='store_true', default=False, help='Update Gravoscope tiles')
parser.add_argument('--manual', dest='manual', action='store_true', default=False, help='Read in manual data')
parser.add_argument('-d','--datadir', dest='datadir', type=str, default='data/', help='directory in which data is stored')
parser.add_argument('-l','--datelim', dest='datelim', type=float, default=999, help='number of days to go back in time')
parser.add_argument('-b','--baseurl', dest='baseurl', type=str, default='https://data.cardiffgravity.org/gwcat-data/', help='Base URL to prepend to relative links [Default=https://data.cardiffgravity.org/gwcat-data/]')
parser.add_argument('-t','--tilesurl', dest='tilesurl', type=str, default='https://gravity.astro.cf.ac.uk/gwcat-data/', help='Base URL to prepend to relative links for tiles [Default=https://ligo.gravity.cf.ac.uk/chris.north/gwcat-data/]')
parser.add_argument('--log',dest='logfile',type=str, default='logs/gdb_updates.log', help='File to output GraceDB logs to. [Default=logs/gdb_updates.log]')
parser.add_argument('--skipgracedb',dest='skipgracedb',action='store_true', default=False, help='Set to skip GraceDB load')
args=parser.parse_args()
dataDir=args.datadir
codedir=args.codedir
update=args.update
verbose=args.verbose
forceupdate=args.forceupdate
forcemap=args.forcemap
overwrite=args.overwrite
baseurl=args.baseurl
tilesurl=args.tilesurl
gravoscope=args.gravoscope
waveforms=args.waveforms
datelim=args.datelim
logfile=args.logfile
skymaps=args.skymaps
skipgracedb=args.skipgracedb

if os.getcwd().split('/')[-1]=='python':
    relDir='../'
else:
    relDir='./'
sys.path.insert(0,os.path.join(relDir,codedir))

import gwcatpy
import json

if update==True:
    gc=gwcatpy.GWCat(fileIn=os.path.join(dataDir,'gwosc_gracedb.json'),
        dataDir=dataDir,baseurl=baseurl,verbose=verbose)
    gdb=json.load(open(os.path.join(dataDir,'gracedb.json')))
    gwoscdata=json.load(open(os.path.join(dataDir,'gwtc1.json')))
    knownEvents=gc.getTimestamps()

    mandata=gwcatpy.getManual(export=True,dirOut=dataDir,verbose=verbose)
    if not skipgracedb:
        gdb=gwcatpy.gracedb.getSuperevents(export=True,dirOut=dataDir,verbose=verbose,
            knownEvents=knownEvents,forceUpdate=forceupdate,datelim=datelim,logFile=logfile)
    gwtc1data=gwcatpy.gwosc.getGWTC1(export=True,dirOut=dataDir,verbose=verbose)
    json.dump(gwtc1data,open(os.path.join(dataDir,'gwtc1.min.json'),'w'))
    json.dump(gdb,open(os.path.join(dataDir,'gracedb.min.json'),'w'))

    print('importing Manual Data...')
    gc.importManual(mandata,verbose=verbose)
    print('importing GWTC1...')
    gc.importGWTC1(gwtc1data,verbose=verbose)
    print('importing GraceDB...')
    gc.importGraceDB(gdb,verbose=verbose,forceUpdate=forceupdate)
    print('updating data from H5 files...')
    gc.updateH5(verbose=verbose,forceUpdate=False)
    print('setting precision...')
    gc.setPrecision(extraprec=1,verbose=verbose)
    print('matching GraceDB entries')
    gc.matchGraceDB(verbose=verbose)
    print('removing unnecessary GraceDB candidates')
    gc.removeCandidates(verbose=verbose)
    print('adding references')
    gc.addrefs(verbose=verbose)

else:
    print('importing from local file')
    gc=gwcatpy.GWCat(fileIn=os.path.join(dataDir,'gwosc_gracedb.json'),dataDir=dataDir)

gc.updateMaps(verbose=verbose,forceUpdate=forcemap)
logfileMaps=logfile+'_maps'
if skymaps:
    print('Plotting Skymaps')
    gc.plotMapPngs(verbose=verbose,overwrite=overwrite,logFile=logfileMaps)
else:
    if os.path.exists(logfileMaps):
        os.remove(logfileMaps)
        print('Removing log file: {}'.format(logfileMaps))
        fM=open(logfileMaps,'w')
        fM.close()

if gravoscope:
    print('Updating gravoscope')
    gc.makeGravoscopeTiles(verbose=True,maxres=6,tilesurl=tilesurl)

if waveforms:
    print('Updating waveforms')
    gc.makeWaveforms(verbose=True,overwrite=False)


# export library
gc.exportJson(os.path.join(dataDir,'gwosc_gracedb.json'))
gcdat=json.load(open(os.path.join(dataDir,'gwosc_gracedb.json')))
# create minified version of json file
json.dump(gcdat,open(os.path.join(dataDir,'gwosc_gracedb.min.json'),'w'))
# convert json files to jsonp
gwcatpy.json2jsonp(os.path.join(dataDir,'gwosc_gracedb.json'),os.path.join(dataDir,'gwosc_gracedb.jsonp'))
gwcatpy.json2jsonp(os.path.join(dataDir,'gwosc_gracedb.min.json'),os.path.join(dataDir,'gwosc_gracedb.min.jsonp'))

#export data to CSV files
gc.exportCSV(os.path.join(dataDir,'gwosc_gracedb.csv'),verbose=True,dictfileout=os.path.join(dataDir,'parameters.csv'))

statF=open(statusFile,'w')
statF.write('success\n')
statF.close()
