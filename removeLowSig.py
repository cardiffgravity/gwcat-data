import os
import numpy as np
import gwcatpy

dataDir='data/'
fileIn=os.path.join(dataDir,'gwosc_gracedb.json')
gc=gwcatpy.GWCat(fileIn=fileIn)

inclist=[]
tlist=[]
for ev in gc.data:
    cat=gc.getParameter(ev,'catalog')
    sig=gc.getValue(ev,'Significance','best')
    time=gc.getValue(ev,'GPS','best')
    print(ev,cat,sig)
    if sig != 'Low':
        inclist.append(ev)
        tlist.append(time)
    # if sig=='Highgc.data.pop(ev)
    # if ev in gc.links:
    #     gc.links.pop(ev)

tlist=np.array(tlist)
inclist=np.array(inclist)
order=np.argsort(tlist)

orderlist=inclist[order]

dataOut={}
linksOut={}
for i in orderlist:
    print(i)
    dataOut[i]=gc.data[i]
    linksOut[i]=gc.links[i]

gc.data=dataOut
gc.links=linksOut

# export library
gc.exportJson(os.path.join(dataDir,'gwosc_gracedb.json'))
# gcdat=json.load(open(os.path.join(dataDir,'gwosc_gracedb.json')))
# # create minified version of json file
# json.dump(gcdat,open(os.path.join(dataDir,'gwosc_gracedb.min.json'),'w'))
# # convert json files to jsonp
# gwcatpy.json2jsonp(os.path.join(dataDir,'gwosc_gracedb.json'),os.path.join(dataDir,'gwosc_gracedb.jsonp'))
# gwcatpy.json2jsonp(os.path.join(dataDir,'gwosc_gracedb.min.json'),os.path.join(dataDir,'gwosc_gracedb.min.jsonp'))

# #export data to CSV files
# gc.exportCSV(os.path.join(dataDir,'gwosc_gracedb.csv'),verbose=True,dictfileout=os.path.join(dataDir,'parameters.csv'),linksfileout=os.path.join(dataDir,'links.csv'))