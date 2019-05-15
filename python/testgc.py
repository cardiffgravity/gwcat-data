import gwcat
import json

gc=gwcat.GWCat(fileIn='../data/events.json')
gdb=json.load(open('../data/gracedb.json'))
gwoscdata=json.load(open('../data/gwosc.json'))
# gwoscdata=gwcat.gwosc.getGwosc(verbose=True,export=True,dirOut='../data')
# gdb=gwcat.gracedb.getSuperevents(verbose=True,export=True,dirOut='../data')
json.dump(gwoscdata,open('../data/gwosc.min.json','w'))
json.dump(gdb,open('../data/gracedb.min.json','w'))
gc.importGwosc(gwoscdata,verbose=False)
gc.importGraceDB(gdb,verbose=False)

gc.exportJson('../data/gwosc_gracedb.json')
gcdat=json.load(open('../data/gwosc_gracedb.json'))
json.dump(gcdat,open('../data/gwosc_gracedb.min.json','w'))
gwcat.json2jsonp('../data/gwosc_gracedb.json','../data/gwosc_gracedb.jsonp')
gwcat.json2jsonp('../data/gwosc_gracedb.min.json','../data/gwosc_gracedb.min.jsonp')