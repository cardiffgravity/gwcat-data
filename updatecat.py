#test update
statusFile='./status.log'
statF=open(statusFile,'w')
statF.write('pending\n')
statF.close()

import sys,os
sys.path.insert(0,os.path.join(os.getcwd(),'python'))

import gwcatpy
import json
import argparse
import ciecplib

parser=argparse.ArgumentParser(prog="updatecat.py", description="Updates the gwcat-data database")
parser.add_argument('-u','--update', dest='update', action='store_true', default=False, help='Update from GWOSC and GraceDB source')
parser.add_argument('-v','--verbose', dest='verbose', action='store_true', default=False, help='Set to print more helpful text to the screen')
parser.add_argument('-o','--overwrite', dest='overwrite', action='store_true', default=False, help='Regenerate and overwrite image files')
parser.add_argument('-f','--forceupdate', dest='forceupdate', action='store_true', default=False, help='Force (re)download of files')
parser.add_argument('-s','--skymaps', dest='skymaps', action='store_true', default=False, help='Plot skymaps')
parser.add_argument('-m','--forcemap', dest='forcemap', action='store_true', default=False, help='Force (re)download of fits files')
parser.add_argument('-5','--forceh5', dest='forceh5', action='store_true', default=False, help='Force (re)extraction of HDF files')
parser.add_argument('-g','--gravoscope', dest='gravoscope', action='store_true', default=False, help='Update Gravoscope tiles')
parser.add_argument('-w','--waveforms', dest='waveforms', action='store_true', default=False, help='Update Waveforms')
parser.add_argument('--manual', dest='manual', action='store_true', default=False, help='Read in manual data')
parser.add_argument('-d','--datadir', dest='datadir', type=str, default='data/', help='directory in which data is stored')
parser.add_argument('-l','--datelim', dest='datelim', type=float, default=999, help='number of days to go back in time')
parser.add_argument('-b','--baseurl', dest='baseurl', type=str, default='https://ligo.gravity.cf.ac.uk/~chris.north/LVC/gwcat-data-dev/', help='Base URL to prepend to relative links [Default=https://ligo.gravity.cf.ac.uk/~chris.north/LVC/gwcat-data-dev/]')
parser.add_argument('-t','--tilesurl', dest='tilesurl', type=str, default='https://ligo.gravity.cf.ac.uk/~chris.north/LVC/gwcat-data-dev/', help='Base URL to prepend to relative links for tiles [Default=https://ligo.gravity.cf.ac.uk/~chris.north/LVC/gwcat-data-dev/]')
parser.add_argument('--log',dest='logfile',type=str, default='logs/gdb_updates.log', help='File to output GraceDB logs to. [Default=logs/gdb_updates.log]')
parser.add_argument('--gracedb',dest='gracedb',action='store_true', default=False, help='Set to include GraceDB load')
parser.add_argument('--skipgracedb',dest='skipgracedb',action='store_true', default=False, help='Set to skip GraceDB load')
parser.add_argument('--devMode',dest='devMode',action='store_true', default=False, help='Set to use dev mode (requires LVK login)')
parser.add_argument('--skiph5',dest='skiph5',action='store_true', default=False, help='Set to skip using H5 files')
args=parser.parse_args()
dataDir=args.datadir
update=args.update
verbose=args.verbose
forceupdate=args.forceupdate
forcemap=args.forcemap
forceh5=args.forceh5
overwrite=args.overwrite
baseurl=args.baseurl
tilesurl=args.tilesurl
gravoscope=args.gravoscope
waveforms=args.waveforms
datelim=args.datelim
logfile=args.logfile
skipgracedb=args.skipgracedb
gracedb=args.gracedb
skiph5=args.skiph5
skymaps=args.skymaps
devMode=args.devMode

if devMode:
    mode='dev'
    sess=ciecplib.Session("LIGO")
else:
    mode=None
    sess=None

fileIn=os.path.join(dataDir,'gwosc_gracedb.json')

print('\n\n*****\nImporting from local file\n*****\n\n')
gc=gwcatpy.GWCat(fileIn=fileIn,dataDir=dataDir,mode=mode,baseurl=baseurl)

if update==True:

    print('\n\n*****\nReading GWTC...\n*****\n\n')
    gwtcdata=gwcatpy.gwosc.getGWTC(export=True,dirOut=dataDir,verbose=verbose,devMode=devMode,catalog='GWTC',sess=sess)
    print('\n\n*****\nImporting GWTC...\n*****\n\n')
    gc.importGWTC(gwtcdata,verbose=verbose, devMode=devMode,catalog='GWTC',forceOverwrite=forceupdate)
    
    print('\n\n*****\nReading GWTC-3-marginal...\n*****\n\n')
    gwtc3margdata=gwcatpy.gwosc.getGWTC(export=True,dirOut=dataDir,verbose=verbose,devMode=devMode,catalog='GWTC-3-marginal',sess=sess)
    print('\n\n*****\nImporting GWTC-3-marginal...\n*****\n\n')
    gc.importGWTC(gwtc3margdata,verbose=verbose, devMode=devMode,catalog='GWTC-3-marginal',forceOverwrite=True)
    
    print('\n\n*****\nReading GWTC-2.1-marginal...\n*****\n\n')
    gwtc21margdata=gwcatpy.gwosc.getGWTC(export=True,dirOut=dataDir,verbose=verbose,devMode=devMode,catalog='GWTC-2.1-marginal',sess=sess)
    print('\n\n*****\nImporting GWTC-2.1-marginal...\n*****\n\n')
    gc.importGWTC(gwtc21margdata,verbose=verbose, devMode=devMode,catalog='GWTC-2.1-marginal',forceOverwrite=True)
    
    print('\n\n*****\nReading GWTC-1-marginal...\n*****\n\n')
    gwtc1margdata=gwcatpy.gwosc.getGWTC(export=True,dirOut=dataDir,verbose=verbose,devMode=devMode,catalog='GWTC-1-marginal',sess=sess)
    print('\n\n*****\nImporting GWTC-1-marginal...\n*****\n\n')
    gc.importGWTC(gwtc1margdata,verbose=verbose, devMode=devMode,catalog='GWTC-1-marginal',forceOverwrite=True)
    
    knownEvents=gc.getTimestamps()
    
    json.dump(gwtcdata,open(os.path.join(dataDir,'gwtc.min.json'),'w'))
    if gracedb:
        print('\n\n*****\nReading GraceDB...\n*****\n\n')
        gdb=gwcatpy.gracedb.getSuperevents(export=True,dirOut=dataDir,verbose=verbose,
        knownEvents=knownEvents,forceUpdate=forceupdate,datelim=datelim,logFile=logfile)
        json.dump(gdb,open(os.path.join(dataDir,'gracedb.min.json'),'w'))
                    
        print('\n\n*****\nimporting GraceDB...\n*****\n\n')
        gc.importGraceDB(gdb,verbose=verbose,forceUpdate=forceupdate)
        
    print('\n\n*****\nmatching GraceDB entries...\n*****\n\n')
    gc.matchGraceDB(verbose=verbose)
    print('\n\n*****\nremoving unnecessary GraceDB candidates\n*****\n\n')
    gc.removeCandidates(verbose=verbose)
    
    print('\n\n*****\nAdding manual references...\n*****\n\n')    
    gc.addRefs(verbose=verbose)

    if skiph5:
        print('\n\n*****\Skipping getting data from H5\n*****\n\n')
    else:
        print('\n\n*****\nUpdating data from H5\n*****\n\n')
        gc.updateH5(verbose=verbose,forceUpdate=forceupdate,forceUpdateData=forceh5)

    print('\n\n*****\nsetting precision...\n*****\n\n')
    gc.setPrecision(extraprec=1,verbose=verbose)

    print('\n\n*****\nUpdating maps\n*****\n\n')
    gc.updateMaps(verbose=verbose,forceUpdate=forcemap)
    

else:
    print('importing from local file')
    gc=gwcatpy.GWCat(fileIn=fileIn,dataDir=dataDir,mode=mode)

    
logfileMaps=logfile+'_maps'
if skymaps:
    print('\n\n*****\nPlotting maps\n*****\n\n')
    gc.plotMapPngs(verbose=verbose,overwrite=overwrite,logFile=logfileMaps)
else:
    if os.path.exists(logfileMaps):
        os.remove(logfileMaps)
        print('Removing log file: {}'.format(logfileMaps))
        fM=open(logfileMaps,'w')
        fM.close()

if gravoscope:
    print('\n\n*****\nUpdating gravoscope\n*****\n\n')
    gc.makeGravoscopeTiles(verbose=verbose,maxres=6,tilesurl=tilesurl)

if waveforms:
    print('\n\n*****\nUpdating waveforms\n*****\n\n')
    gc.makeWaveforms(verbose=verbose,overwrite=overwrite)

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
