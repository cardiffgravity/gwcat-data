import json
import pandas as pd
import numpy as np
from astropy.time import Time
from astropy.io import fits
import healpy as hp
import os
import requests
from . import gwosc
from . import gracedb
from . import plotloc
# import gracedb
# import gwosc

def json2jsonp(fileIn,fileOut=None,verbose=True):
    if fileOut==None:
        fileOut=fileIn.replace('json','jsonp')
    if verbose:print('reading JSON from {}'.format(fileIn))
    if verbose:print('writing JSONP to {}'.format(fileOut))
    fIn=open(fileIn,'r')
    fOut=open(fileOut,'w')
    lines=fIn.readlines()
    lines[0]='catdata('+lines[0]
    lines[-1]=lines[-1]+');'
    for l in lines:
        fOut.write(l)
    fOut.close()

def compareElement(el1,el2,verbose=False):
    if type(el1)!=type(el2):
        # types are different
        if verbose: print('inconsistent types [{},{}]'.format(type(el1),type(el2)))
        return(False)
    elif type(el1)==dict and type(el2)==dict:
        for el in el1:
            if el in el2:
                # if verbose: print('Comparing elements {}'.format(el))
                return(compareElement(el1[el],el2[el],verbose=verbose))
            else:
                # if verbose: print('element {} not in dict 2'.format(el))
                return(False)
        for el in el2:
            if el not in el1:
                # if verbose: print('element {} not in dict 1'.format(el))
                return(False)
    else:
        try:
            # if verbose: print('Comparing elements {}'.format(el1))
            if el1==el2:
                # if verbose: print('{}=={}'.format(el1,el2))
                return(True)
            else:
                # if verbose: print('{}!={}'.format(el1,el2))
                return(False)
        except:
            print('ERROR: unable to compare [{} , {}] / [{},{}]'.format(el1,el2),type(el1),type(el2))
            return()

    return()

def dataframe2jsonEvent(evIn,params,verbose=False):
    # convert dataframe element to json
    evOut={}
    for p in range(len(params)):
        param=params[p]
        if verbose: print('Converting value {}'.format(param))
        if param in evIn:
            try:
                pv=evIn[param+'_valtype']
            except:
                if verbose: print('ERROR: No valtype found for {}'.format(param))
                pv=''
                pass
            try:
                np.isnan(pv)
                pass
            except:
                evOut[param]={}
            if pv=='value':
                evOut[param]['best']=evIn[param]
            elif pv=='bestfit':
                evOut[param]['best']=evIn[param]
                try:
                    evOut[param]['err']=[evIn[param+'_errp'],evIn[param+'_errm']]
                except:
                    if verbose: print('WARNING: no err found form {}'.format(param))
            elif pv=='range':
                try:
                    evOut[param]['lim']=[evIn[param+'_errp'],evIn[param+'_errm']]
                except:
                    if verbose: print('WARNING: no lim found form {}'.format(param))
            elif pv=='upper':
                evOut[param]['upper']=evIn[param]
            elif pv=='lower':
                evOut[param]['lower']=evIn[param]
            else:
                if verbose: print('ERROR: unknown type for {} [{}]'.format(param,pv))
    return(evOut)

class GWCat(object):
    def __init__(self,fileIn='../data/events.json',statusFile='status.json',dataDir='data/',verbose=False):
        """Initialise catalogue from input file
        Input: fileIn [string, OPTIONAL]: filename to read data from
        """
        self.dataDir=dataDir
        self.statusFile=os.path.join(dataDir,statusFile)
        self.getStatus()
        eventsIn=json.load(open(fileIn))
        self.data=eventsIn['data']
        self.datadict=eventsIn['datadict']
        self.cols=list(self.datadict.keys())
        self.links=eventsIn['links']
        self.json2dataframe(verbose=verbose)
        self.meta={'created':Time.now().isot}
        return

    def getEvent(self,ev):
        if ev in self.data:
            return(self.data[ev])
        else:
            return

    def getStatus(self):
        self.status=json.load(open(self.statusFile))
        return

    def saveStatus(self):
        json.dump(self.status,open(self.statusFile,'w'),indent=4)
        return

    def updateStatus(self,ev,statusIn=None,verbose=False):
        # check if it's in status
        if type(ev)!=str:
            print('ERROR: ev must be string object:',type(ev))
            return
        if statusIn==None:
            # get status from event data
            try:
                event=self.getEvent(ev)
                status=event['meta']
            except:
                print('ERROR: cannot find event {}'.format(ev))
                return
        elif type(statusIn)!=dict:
            print('ERROR: status must be dict object:',type(status))
            return
        else:
            if 'meta' in statusIn:
                status=statusIn['meta']
            else:
                status=statusIn
        for m in status:
            self.status[ev][m]=status[m]
        # if (event):
        #     if not ev in self.status:
        #         self.status[ev]={}
        #     if 'meta' in status:
        #         for m in event['meta']:
        #             self.status[ev][m]=event['meta'][m]
        if verbose:print('update status: {}'.format(ev))
        self.saveStatus()
        return

    def updateMapSrc(self,ev,verbose=False):
        lmap=self.getLink(ev,'skymap',verbose=verbose)
        if len(lmap)>1 and verbose:
            print('Warning: more than one skymap link for {}'.format(ev))
        if len(lmap)==0 and verbose:
            print('Warning: more than one skymap link for {}'.format(ev))
        if len(lmap)>0:
            l=lmap[0]
            tmpDir=os.path.join(self.dataDir,'tmp')
            try:
                hdr=fits.getheader(l['url'],ext=1)
                self.data[ev]['meta']['mapdatesrc']=hdr['DATE']
                self.data[ev]['meta']['mapurlsrc']=l['url']
                if verbose:print('Skymap loaded for {}:'.format(ev),l['url'])
            except:
                print('WARNING: Error loading skymap for {}:'.format(ev),l)

    def importGwosc(self,gwoscIn,verbose=False):
        catData=gwosc.gwosc2cat(gwoscIn)
        for g in catData['data']:
            self.data[g]=catData['data'][g]
            if g in catData['links']:
                for l in catData['links'][g]:
                    self.addLink(g,l,verbose=verbose)
            self.updateStatus(g,verbose=verbose)
        for ev in self.links:
            self.updateMapSrc(ev)
            self.updateStatus(ev,verbose=verbose)
        self.json2dataframe(verbose=verbose)
        self.meta['gwosc']=gwoscIn['meta']
        return

    def importGraceDB(self,gracedbIn,verbose=False):
        gdb=gracedb.gracedb2cat(gracedbIn['data'])
        for g in gdb['data']:
            self.data[g]=gdb['data'][g]
            for l in gdb['links'][g]:
                self.addLink(g,l,verbose=verbose)
            self.updateStatus(g)
        for ev in self.links:
            self.updateMapSrc(ev)
            self.updateStatus(ev,verbose=verbose)
        self.json2dataframe(verbose=verbose)
        self.meta['graceDB']=gracedbIn['meta']
        return

    def updateMaps(self,verbose=False,forceUpdate=False):
        for ev in self.events:
            # compare map creation dates
            try:
                mapdatelocal=Time(self.status[ev]['mapdatelocal'])
                mapdatesrc=Time(self.status[ev]['mapdatesrc'])
                if mapdatesrc>mapdatelocal:
                    updateMap=True
                else:
                    updateMap=False
            except:
                updateMap=True
            if updateMap or forceUpdate:
                self.getMap(ev,verbose=verbose)
                if verbose:print('Updating map for {}'.format(ev))
            else:
                if verbose:print('No update required for {}'.format(ev))

        return

    def getMap(self,ev,verbose=False):
        fitsDir=os.path.join(self.dataDir,'fits')
        if not os.path.exists(fitsDir):
            # create directory
            os.mkdir(fitsDir)
            print('Created directory: {}'.format(fitsDir))
        lmap=self.getLink(ev,'skymap')
        if len(lmap)==0:
            if verbose: print('ERROR: no skymap link for {}',format(ev))
            return
        if len(lmap)>1:
            if verbose: print('WARNING: more than one skymap link for {}',format(ev))
        url=lmap[0]['url']
        if verbose: print('Downloading skymap for {} from {}'.format(ev,url))
        mapreq=requests.get(url)
        if mapreq.ok:
            try:
                if url.find('.fits.gz')>=0:
                    fileext='fits.gz'
                else:
                    fileext='fits'
                fitsFile=os.path.join(fitsDir,'{}_skymap.{}'.format(ev,fileext))
                fOut=open(fitsFile,'wb')
                fOut.write(mapreq.content)
                fOut.close()
            except:
                print('ERROR: Problem loading/saving map:',mapreq.status_code)
                return mapreq
            try:
                hdr=fits.getheader(fitsFile,ext=1)
                stat={'mapurllocal':fitsFile,
                    'mapdatelocal':hdr['DATE']}
                self.updateStatus(ev,stat,verbose=verbose)
                return(hdr)
            except:
                print('ERROR: Problem opening fits file for {}:'.format(ev),fitsFile)
        else:
            print('ERROR: Problem loading map:',mapreq.status_code)
            return mapreq.status_code
        return

    def plotMapPngs(self,overwrite=False,verbose=False):
        pngDir=os.path.join(self.dataDir,'png')
        dataDir=os.path.join(self.dataDir,'fits')
        if not os.path.exists(pngDir):
            os.mkdir(pngDir)
        for ev in self.data:
            pngMoll=os.path.join(pngDir,'{}_moll.png'.format(ev))
            pngCartzoom=os.path.join(pngDir,'{}_cartzoom.png'.format(ev))
            pngCart=os.path.join(pngDir,'{}_cart.png'.format(ev))
            exCart=os.path.isfile(pngCart)
            exCartzoom=os.path.isfile(pngCartzoom)
            exMoll=os.path.isfile(pngMoll)
            if exCart and exMoll and exCartzoom and not overwrite:
                if verbose:print('all plots exist for {}'.format(ev))
            else:
                if not 'mapurllocal' in self.status[ev]:
                    self.getMap(ev,verbose=verbose)
                filename=self.status[ev]['mapurllocal']
                if verbose:print('plotting maps at {}'.format(filename))
                try:
                    map=hp.read_map(filename)
                    mapread=True
                except:
                    print('ERROR: problem reading map at {}'.format(filename))
                    mapread=False
                if mapread:
                    if not exCartzoom or overwrite:
                        if verbose:print('plotting Cartesian (zoomed) map to {}'.format(pngCartzoom))
                        plotloc.makePlot(ev=ev,mapIn=map,dirData=dataDir,
                            proj='cart',plotcont=False,smooth=0,zoomlim=0.8,rotmap=True,minzoom=20,
                            verbose=verbose,
                            pngOut=pngCartzoom)
                        self.addLink(ev,{'url':pngCartzoom,'text':'Skymap (Cartesian zoomed)','type':'skymap-plot'})
                    if not exCart or overwrite:
                        if verbose:print('plotting Cartesian (fullsky) map to {}'.format(pngCart))
                        plotloc.makePlot(ev=ev,mapIn=map,dirData=dataDir,
                            proj='cart',plotcont=False,smooth=0,zoomlim=None,
                            verbose=verbose,
                            pngOut=pngCart)
                        self.addLink(ev,{'url':pngCart,'text':'Skymap (Cartesian fullsky)','type':'skymap-plot'})
                    if not exMoll or overwrite:
                        if verbose:print('plotting Mollweide (fullsky) map to {}'.format(pngMoll))
                        plotloc.makePlot(ev=ev,mapIn=map,dirData=dataDir,
                            proj='moll',plotcont=False,smooth=0,zoomlim=None,
                            verbose=verbose,
                            pngOut=pngMoll)
                        self.addLink(ev,{'url':pngMoll,'text':'Skymap (Mollweide fullsky)','type':'skymap-plot'})

        return

    def getLink(self,ev,srchtxt,srchtype='type',verbose=False):
        if not ev in self.links:
            return []
        lOut=[]
        if len (self.links[ev])>0:
            for ol in range(len(self.links[ev])):
                if self.links[ev][ol][srchtype]==srchtxt:
                    lOut.append(self.links[ev][ol])
        if verbose:
            print('found {} links for {} with {}=={}'.format(len(lOut),ev,srchtype,srchtxt))
        return(lOut)

    def addLink(self,ev,link,replace=True,verbose=False):
        # replace: replace link with same type and text. (N.B. Always replace open-data links)
        if not ev in self.links:
            self.links[ev]=[]
        # ltype=link['type']
        exlink=None
        if verbose:print('adding {} link to {} [{}]'.format(link['type'],ev,link['url']))
        if len(self.links[ev])>0:
            for ol in range(len(self.links[ev])):
                oldlink=self.links[ev][ol]
                if replace==True:
                    # find link with same type and text
                    if oldlink['type']==link['type'] and oldlink['text']==link['text']:
                        exlink=ol
                    elif link['type']=='open-data' and oldlink['type']==link['type']:
                        # always remove open-data if it exists
                        if verbose:print('removing old {} link from {} [{}]'.format(ltype,g,self.links[ev][ol]['url']))
                        exlink=ol
        if (exlink):
            # replace link
            self.links[ev][exlink]=link
        else:
            # append new link
            self.links[ev].append(link)
        return

    def json2dataframe(self,verbose=False):
        """Convert dictionaries into pandas DataFrames
        data -> events
        datadict -> units
        links -> eventrefs
        Inputs:
            * None
        Outputs:
            * Tuple of DataFrames:
                - 0: events
                - 1: units
                - 2: eventlinks
        """

        # convert datadict into units DataFrame
        units=pd.DataFrame(self.datadict).transpose()
        self.units=units

        # convert data into events DataFrame
        data=self.data
        # if verbose:
        #     print(self.data)
        #     print(data)
        dataOut={}
        series={}
        for d in self.cols:
            if verbose:print('col:',d)
            dataOut[d]={}
            dataOut[d+'_valtype']={}
            dataOut[d+'_errp']={}
            dataOut[d+'_errm']={}
            for e in data:
                # if verbose:
                #     print('event',e,data[e])
                if d not in data[e]:
                    continue
                if 'best' in data[e][d]:
                    dataOut[d][e]=data[e][d]['best']
                    if 'err' in data[e][d]:
                        if data[e][d]['err']=='lowerbound':
                            dataOut[d][e]=data[e][d]['best']
                            dataOut[d+'_valtype'][e]='lower'
                        elif data[e][d]['err']=='upperbound':
                            dataOut[d][e]=data[e][d]['best']
                            dataOut[d+'_valtype'][e]='upper'
                        elif type(data[e][d]['err']) == list:
                            dataOut[d+'_valtype'][e]='bestfit'
                            dataOut[d+'_errp'][e]=np.max(data[e][d]['err'])
                            dataOut[d+'_errm'][e]=np.min(data[e][d]['err'])
                    else:
                        dataOut[d+'_valtype'][e]='value'
                elif 'lim' in data[e][d]:
                    dataOut[d+'_valtype'][e]='range'
                    dataOut[d+'_errp'][e]=data[e][d]['lim'][0]
                    dataOut[d+'_errm'][e]=data[e][d]['lim'][1]
                elif 'lower' in data[e][d]:
                    dataOut[d+'_valtype'][e]='lower'
                    dataOut[d][e]=data[e][d]['lower']
                elif 'upper' in data[e][d]:
                    dataOut[d][e]=data[e][d]['upper']
                    dataOut[d+'_valtype'][e]='upper'
        # convert to series
        for dOut in dataOut:
            series[dOut]=pd.Series(dataOut[dOut],index=dataOut[dOut].keys())
            # rows.append(d)
        # combine into DataFrame
        events=pd.DataFrame(series).T
        self.events=events

        # convert links into eventlinks DataFrame

        linksSeries=[]
        for ev in self.links:
            for l in range(len(self.links[ev])):
                link=self.links[ev][l]
                linkOut={'event':ev}
                for r in link:
                    linkOut[r]=link[r]
                # convert to series
                linksSeries.append(pd.Series(linkOut))
        # combine into DataFrame
        eventrefs=pd.DataFrame(linksSeries).T
        self.eventrefs=eventrefs

        return(events,units,eventrefs)

    def dataframe2json(self,dataIn,unitsIn,linksIn,mode,verbose=False):
        """Convert pandas DataFrame objects into dictionaries, merging with existing. Used to read from CSV files
        Inputs:
            * dataIn [dictionary]: data for events (merge with data)
            * unitsIn [dictionary]: units information (merge with datadict)
            * linksIn [dictionary]: links information (merge with links)
            * mode [string]: Mode to use:
                - "replace": Remove and replace entire dataset from imports
                - "update": Update existing data from imports
                - "append": Append new events/parameters, leave existing events/parameters unchanged
        Outputs:
            * Tuple of Dictionary:
                - 0: data
                - 1: datadict
                - 2: links
        """
        paramsIn=list(unitsIn.keys())
        eventsIn=list(dataIn.keys())

        # eventsInDict=dataIn.to_dict(orient='index')
        # unitsInDict=unitsIn.to_dict(orient='index')
        # linksInDict=linksIn.to_dict()

        if mode=='replace':
            # remove existing dataset
            if verbose:print('Removing existing data')
            for k in list(self.datadict.keys()):
                if verbose: print('Removing parameter {}'.format(k))
                self.datadict.pop(k,None)
            for k in list(self.data.keys()):
                if verbose: print('Removing event {}'.format(k))
                self.data.pop(k,None)
            for k in list(self.links.keys()):
                if verbose: print('Removing links {}'.format(k))
                self.links.pop(k,None)

        if verbose: print('\n*** Udating parameters ***')
        # create list of parameters
        for param in unitsIn:
            # check parameters are in current database
            if param not in self.datadict:
                if verbose: print('Adding parameter {}'.format(param))
                self.datadict[param]={}
                for k in unitsIn[param]:
                    try:
                        if np.isnan(unitsIn[param][k]):
                            continue
                    except:
                        pass
                    if not unitsIn[param][k]=='':
                        self.datadict[param][k]=unitsIn[param][k]
            elif mode=="append":
                # don't update existing parameter
                if verbose: print('Mode=append. Skipping parameter {}'.format(param))
                pass
            else:
                # replace existing parameter
                if verbose: print('Updating parameter {}'.format(param))
                self.datadict[param]={}
                for k in unitsIn[param]:
                    try:
                        if np.isnan(unitsIn[param][k]):
                            continue
                    except:
                        pass
                    if not unitsIn[param][k]=='':
                        self.datadict[param][k]=unitsIn[param][k]

        if verbose: print('\n*** Updating event data ***')
        # update events dictionary
        for ev in eventsIn:
            if ev not in self.data:
                # event is new
                if verbose: print('Adding event %s'%(ev))
                event=dataframe2jsonEvent(dataIn[ev],paramsIn,verbose=verbose)
                self.data[ev]=event
            else:
                # event exists in data
                if mode=="append":
                    # don't update existing events
                    if verbose: print('Mode=append. Skipping event {}'.format(ev))
                    pass
                else:
                    # update existing event
                    if verbose: print('Merging events {}'.format(ev))
                    event=dataframe2jsonEvent(dataIn[ev],paramsIn,verbose=verbose)
                    for el in event:
                        if el not in self.data[ev]:
                            if verbose: print ('Adding value {}'.format(el))
                            self.data[ev][el]=event[el]
                        else:
                            if verbose: print('Merging element {} for event {}'.format(el,ev))
                            if not compareElement(self.data[ev][el],event[el],verbose=verbose):
                                # if verbose: print('Updating value {}'.format(el))
                                self.data[ev][el]=event[el]
                            else:
                                pass
                                # if verbose: print('Keeping value {}'.format(el))
                    for el in list(self.data[ev].keys()):
                        if el not in event:
                            # element existed, but not in input.
                            if mode=='replace':
                                # Remove from dictionary
                                self.data[ev].pop(el,None)

        if verbose: print('\n*** Udating links ***')

        # get current links
        oldLinks=[]
        newLinks=[]
        skipLinks=[]
        for ev in self.links:
            oldLinks.append(ev)

        # update links
        for l in linksIn:
            link=linksIn[l]
            ev=link['event']
            if ev not in oldLinks and ev not in newLinks:
                # event is new in links
                if verbose: print('Adding links for event {}'.format(ev))
                self.links[ev]=[]

            if mode=="append":
                # don't update existing events
                if ev not in skipLinks:
                    if verbose: print('Skipping event {}'.format(ev))
                    skipLinks.append(ev)
                pass
            else:
                if ev not in newLinks:
                    # links haven't been replaced yet for this event
                    if verbose: print('Updating links for event {}'.format(ev))
                    self.links[ev]=[]
                    newLinks.append(ev)
                # add link to links-list for event
                newLink={}
                for key in link:
                    try:
                        if np.isnan(link[key]):
                            continue
                    except:
                        pass
                    if key!='event' and link[key]!='':
                        newLink[key]=link[key]
                self.links[ev].append(newLink)

        # put back into dataframe structures
        self.json2dataframe()

        return(self.data,self.datadict,self.links)


    def getValue(self,event,param,value):
        try:
            return self.data[event][param][value]
        except:
            print('Error finding value %s for parameter %s in event %s'%(value,param,event))
            return np.NaN

    def exportJson(self,fileout,dir='',verbose=False):
        """Export parameters, data and links to single JSON file
        Inputs:
            * fileout [string]: filename to write all data to
            * dir [string OPTIONAL]: directory to write files to. Default=''
        """
        alldata={'meta':self.meta,'datadict':self.datadict,'data':self.data,'links':self.links}
        if verbose: print('Writing data to JSON: {}'.format(os.path.join(dir,fileout)))
        json.dump(alldata,open(os.path.join(dir,fileout),'w'),indent=4)


        return()

    def exportCSV(self,datafileout,dictfileout=None,linksfileout=None,dir='',verbose=False):
        """Export data to CSV file(s)
        Inputs:
            * datafileout [string]: filename to write events data to
            * dictfileout [string, OPTIONAL]: filename to write data dictionary to. Default: do not export
            * linksfileout [string OPTIONAL]: filename to write references to. Default: to not export
            * dir [string OPTIONAL]: directory to write files to. Default=''
        """
        (dataframe,units,links) = self.json2dataframe(verbose=verbose)

        if verbose: print('Writing data to CSV: {}'.format(os.path.join(dir,datafileout)))
        dataframe.transpose().to_csv(os.path.join(dir,datafileout),encoding='utf8',index_label='Event')

        if dictfileout!=None:
            if verbose: print('Writing datadict to CSV: {}'.format(os.path.join(dir,dictfileout)))
            units.to_csv(os.path.join(dir,dictfileout),encoding='utf8',index_label='Parameter')

        if linksfileout!=None:
            if verbose: print('Writing links to CSV:{}'.format(os.path.join(dir,linksfileout)))
            links.transpose().to_csv(os.path.join(dir,linksfileout),encoding='utf8',index_label='Ref')

        return()

    def exportExcel(self,fileout,dir='',verbose=False):
        """Export datadict, events data and links to CSV file(s)
        Inputs:
            * fileout [string]: filename to write all data to
            * dir [string OPTIONAL]: directory to write files to. Default=''
        """
        (dataframe,units,links) = self.json2dataframe(verbose=verbose)

        writer=pd.ExcelWriter(os.path.join(dir,fileout),engine='xlsxwriter')

        if verbose: print('Writing data to Excel: {}'.format(os.path.join(dir,fileout)))
        dataframe.transpose().to_excel(writer,sheet_name='Events',encoding='utf8',index_label='Event')

        if verbose: print('Writing datadict to Excel: {}'.format(os.path.join(dir,fileout)))
        units.to_excel(writer,sheet_name='Parameters',encoding='utf8',index_label='Parameter')

        if verbose: print('Writing links to Excel:{}'.format(os.path.join(dir,fileout)))
        links.transpose().to_excel(writer,sheet_name='Links',encoding='utf8',index_label='Ref')

        writer.save()

        return()

    def importCSV(self,datafilein,dictfilein=None,linksfilein=None,dir='',mode=None,verbose=False):
        """Read CSV file of data and replace in database
        Inputs:
            * datafilein [string]: filename of events data file to read in
            * dictfilein [string, OPTIONAL]: filename of data dictionary to read in
            * linkfile [string OPTIONAL]: filename of references csv file to read in
            * dir [string OPTIONAL]: directory to read from. Default=''
            * mode [string, OPTIONAL]: import mode [replace,update,append]
                - replace: replace entire dataset with input data
                - update: update existing events and add new events [default]
                - append: add new events, leave existing events unchanged
        """

        # set mode to default if not set
        if mode==None:
            mode='update'

        # read CSV files
        if verbose: print('Reading data from {}'.format(os.path.join(dir,datafilein)))
        datain=pd.read_csv(os.path.join(dir,datafilein),index_col=0).to_dict(orient='index')
        if dictfilein!=None:
            if verbose: print('Reading data dict from {}'.format(os.path.join(dir,dictfilein)))
            unitsin=pd.read_csv(os.path.join(dir,dictfilein),index_col=0).to_dict(orient='index')
        else:
            unitsin=self.datadict
        if linksfilein!=None:
            if verbose: print('Reading links from {}'.format(os.path.join(dir,linksfilein)))
            linksin=pd.read_csv(os.path.join(dir,linksfilein),index_col=0).to_dict(orient='index')
        else:
            linksin=self.links

        # merge imports with existing
        self.dataframe2json(datain,unitsin,linksin,mode=mode,verbose=verbose)

        return()

    def importExcel(self,filein,dir='',sheet_events='Events',sheet_dict='Parameters',sheet_links='Links',mode='update',verbose=False):
        """Read Excel file of data and replace in database
        Inputs:
            * filein [string]: filename of data file to read in from
            * sheet_events [string, OPTIONAL]: sheet name for events data. Default="Events"
            * sheet_dict [string, OPTIONAL]: sheet name for parameters data. Default="Parameters"
            * sheet_links [string, OPTIONAL]: sheet name for links data. Default="Links"
            * dir [string OPTIONAL]: directory to read from. Default=''
            * mode [string, OPTIONAL]: import mode [replace,update,append]
                - replace: replace entire dataset with input data
                - update: update existing events and add new events [default]
                - append: add new events, leave existing events unchanged
        """

        # set mode to default if not set
        if mode==None:
            mode='update'

        # read Excel file
        if verbose: print('Reading data from {}'.format(os.path.join(dir,filein)))
        datain=pd.read_excel(os.path.join(dir,filein),sheet_name='Events',index_col=0).to_dict(orient='index')

        if verbose: print('Reading data dict from {}'.format(os.path.join(dir,filein)))
        unitsin=pd.read_excel(os.path.join(dir,filein),sheet_name='Parameters',index_col=0).to_dict(orient='index')

        if verbose: print('Reading links from {}'.format(os.path.join(dir,filein)))
        linksin=pd.read_excel(os.path.join(dir,filein),sheet_name='Links',index_col=0).to_dict(orient='index')


        # merge imports with existing
        self.dataframe2json(datain,unitsin,linksin,mode=mode,verbose=verbose)

        return()
