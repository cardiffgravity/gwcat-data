import os
from ligo.gracedb.rest import GraceDb
from numpy import argmax
import json
import requests
from bs4 import BeautifulSoup
from astropy.time import Time
from astropy import units as un

def gracedb2cat(gdb,verbose=False):
    catOut={}
    linksOut={}
    if 'data' in gdb:
        gdbIn=gdb['data']
    else:
        gdbIn=gdb
    for g in gdbIn:
        if verbose: print('importing GraceDB event {}'.format(g))
        catOut[g]={}
        linksOut[g]=[]
        if 'superevent_id' in gdbIn[g]: catOut[g]['name']=gdbIn[g]['superevent_id']
        catOut[g]['obsrun']={'best':'O3'}
        catOut[g]['detType']={'best':'Candidate'}
        catOut[g]['conf']={'best':'Candidate'}
        if 't_0' in gdbIn[g]:
            catOut[g]['GPS']={'best':gdbIn[g]['t_0']}
            dtIn=Time(gdbIn[g]['t_0'],format='gps')
            dtOut=Time(dtIn,format='iso').isot
            catOut[g]['UTC']={'best':dtOut}
        if 'far' in gdbIn[g]:
            catOut[g]['FAR']={'best':gdbIn[g]['far']*un.year.to('s')}
        if 'hdr' in gdbIn[g]:
            hdr=gdbIn[g]['hdr']
            if 'DISTMEAN' in hdr and 'DISTSTD' in hdr:
                catOut[g]['DL']={
                    'best':float(hdr['DISTMEAN']['value']),
                    'err':[-float(hdr['DISTSTD']['value']),float(hdr['DISTSTD']['value'])]
                }
            # if 'DATE' in hdr:

        if 'xml' in gdbIn[g]:
            xml=gdbIn[g]['xml']
            if 'Instruments' in xml:
                instOut=''
                inst=xml['Instruments']
                if inst.find('H1')>=0: instOut=instOut+'H'
                if inst.find('L1')>=0: instOut=instOut+'L'
                if inst.find('V1')>=0: instOut=instOut+'V'
                catOut[g]['net']={'best':instOut}
            if 'Classification' in xml:
                catOut[g]['objType']={'prob':{}}
                bestObjType=''
                bestProb=0
                for t in xml['Classification']:
                    prob=float(xml['Classification'][t])
                    catOut[g]['objType']['prob'][t]=prob
                    if prob > bestProb:
                        bestObjType=t
                        bestProb=float(xml['Classification'][t])
                catOut[g]['objType']['best']=bestObjType
        if 'meta' in gdbIn[g]:
            catOut[g]['meta']=gdbIn[g]['meta']
        # update links
        if 'links' in gdbIn[g]:
            if 'self' in gdbIn[g]['links']:
                opendata={'url':gdbIn[g]['links']['self'],
                    'text':'GraceDB data',
                    'type':'open-data'}
                linksOut[g].append(opendata)
        if 'mapfile' in gdbIn[g]:
            skymap={'url':gdbIn[g]['mapfile'][1],
                'text':'Sky Map',
                'type':'skymap'}
            linksOut[g].append(skymap)

    return {'data':catOut,'links':linksOut}

def getSuperevents(export=False,dirOut=None,fileOut=None,indent=2,verbose=False):

    service_url = 'https://gracedb.ligo.org/api/'
    if verbose: print('Retrieving GraceDB data from {}'.format(service_url))
    client = GraceDb(service_url,force_noauth=True)

    # Retrieve an iterator for events matching a query.
    events = client.superevents('far < 1.0e-4')
    # if verbose: print('retrieved {} events'.format(len(events)))
    # For each event in the search results, add the graceid
    # and chirp mass to a dictionary.
    results = {}
    links = {}
    for event in events:
        sid = event['superevent_id']
        results[sid]=event
        if verbose: print('getting files for {}'.format(sid))
        freq=client.files(sid)
        files=json.loads(freq.read())
        results[sid]['files']=files
        xmln=[]
        xmlf=[]
        for f in files:
            if f.find('.xml')>0 and f.find(',0')<0:
                xmln.append(f.split('-')[1])
                xmlf.append(f)
        results[sid]['xmlfile']=[xmlf[argmax(xmln)],results[sid]['files'][xmlf[argmax(xmln)]]]

        # get map and html files
        mapsrch=['LALInference1','LALInference','bayestar1','bayestar']
        htmlsrch2=['bayestar1','bayestar']
        mapFound=False
        m=0
        while not mapFound and m<len(mapsrch):
            mapfile='{}.fits.gz'.format(mapsrch[m])
            if mapfile in files:
                results[sid]['mapfile']=[mapfile,results[sid]['files'][mapfile]]
                mapFound=True
                # if verbose: print('  found {}'.format(mapfile))
            m+=1
        htmlFound=False
        h=0
        while not htmlFound and h<len(mapsrch):
            htmlfile='{}.html'.format(mapsrch[h])
            if htmlfile in files:
                results[sid]['htmlfile']=[htmlfile,results[sid]['files'][htmlfile]]
                htmlFound=True
                # if verbose: print('  found {}'.format(htmlfile))
            h+=1
        html2Found=False
        h2=0
        while not html2Found and h2<len(htmlsrch2):
            htmlfile2='{}.html'.format(htmlsrch2[h2])
            if htmlfile2 in files:
                results[sid]['htmlfile2']=[htmlfile2,results[sid]['files'][htmlfile2]]
                html2Found=True
                # if verbose: print('  found {}'.format(htmlfile2))
            h2+=1
        # if 'LALInference1.fits' in files:
        #     results[sid]['mapfile']=['LALInference1.fits',results[sid]['files']['LALInference1.fits']]
        # elif 'bayestar.fits' in files:
        #     results[sid]['mapfile']=['bayestar.fits',results[sid]['files']['bayestar.fits']]
        # if 'LALInference1.html' in files:
            # results[sid]['htmlfile']=['LALInference1.html',results[sid]['files']['LALInference1.html']]
        # elif 'bayestar.html' in files:
            # results[sid]['htmlfile']=['bayestar.html',results[sid]['files']['bayestar.html']]

        # parse HTML
        hdr={}
        if verbose: print('  parsing {}'.format(results[sid]['htmlfile'][0]))
        htmlurl=results[sid]['htmlfile'][1]
        htmlreq=requests.get(htmlurl)
        soup=BeautifulSoup(htmlreq.text,'html.parser')
        trs=soup.find_all('tr')
        for tr in trs:
            tds=tr.find_all('td')
            if len(tds)>2:
                hdr[tds[0].text]={
                    'value':tds[1].text,
                    'src':results[sid]['htmlfile'][0]}
                if len(tds)>=3:
                    hdr[tds[0].text]['comment']=tds[2].text

        # parse HTML2
        if 'htmlfile2' in results[sid]:
            if verbose: print('  parsing {}'.format(results[sid]['htmlfile2'][0]))
            htmlurl2=results[sid]['htmlfile2'][1]
            htmlreq2=requests.get(htmlurl2)
            soup2=BeautifulSoup(htmlreq2.text,'html.parser')
            trs2=soup2.find_all('tr')
            for tr in trs2:
                tds=tr.find_all('td')
                if len(tds)>2:
                    if not tds[0].text in hdr:
                        hdr[tds[0].text]={
                            'value':tds[1].text,
                            'src':results[sid]['htmlfile2'][0]}
                        if len(tds)>=3:
                            hdr[tds[0].text]['comment']=tds[2].text
        results[sid]['hdr']=hdr

        # parse XML
        xml={}
        if verbose: print('  parsing {}'.format(results[sid]['xmlfile'][0]))
        xmlurl=results[sid]['xmlfile'][1]
        xmlreq=requests.get(xmlurl)
        soup=BeautifulSoup(xmlreq.text,'lxml')
        params=soup.what.find_all('param',recursive=False)
        for p in params:
            xml[p.attrs['name']]=p.attrs['value']
        groups=soup.what.find_all('group',recursive=False)
        for g in groups:
            gt=g.attrs['type']
            xml[gt]={}
            gparams=g.find_all('param',recursice=False)
            for gp in gparams:
                xml[gt][gp.attrs['name']]=gp.attrs['value']
        results[sid]['xml']=xml

        # create meta data
        results[sid]['meta']={'retrieved':Time.now().isot,'src':service_url}
        # if 'DATE' in results[sid]['hdr']:
        #     results[sid]['meta']['mapdatesrc']=Time(results[sid]['hdr']['DATE']['value']).isot
        #     # results[sid]['meta']['mapdatesrc']=Time(results[sid]['hdr']['DATE']['value']).isot
        cdate=' '.join(results[sid]['created'].split(' ')[0:2])
        results[sid]['meta']['created_date']=Time(cdate).isot

    if verbose: print('Retrieved data for {} events'.format(len(results)))

    cat={'meta':{'retrieved':Time.now().isot,'src':service_url},'data':results}

    if export:
        if dirOut==None:
            dirOut='../../data/'
        if fileOut==None:
            fileOut='gracedb.json'
        if verbose: print('Exporting to {}'.format(os.path.join(dirOut,fileOut)))
        fOut=open(os.path.join(dirOut,fileOut),'w')
        json.dump(cat,fOut,indent=indent)
        fOut.close()



    return(cat)

def getMap(sid,fileout=None,dirOut=None,getLAL=False):
    if getLAL:
        filename = 'bayestar.fits'
    else:
        filename = 'LALInference.fits'
    if fileout==None:
        outFilename = '{}_{}'.format(sid,filename)
    if dirOut==None:
        dirOut='../../data/'
    print('downloading {} for superevent {}'.format(filename,sid))
    clFits=GraceDbBasic(service_url)
    fout=open(os.path.join(dirOut,outFilename),'wb')
    r = clFits.files(sid,filename)
    fout.write(r.read())
    fout.close()