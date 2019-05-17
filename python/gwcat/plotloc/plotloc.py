from ligo.gracedb.rest import GraceDb
import json
import healpy as hp
import numpy as np
import requests
import os
from matplotlib import pyplot as plot
from matplotlib import cm
from astropy.io import fits
# print ('plotloc file',__file__,os.path.dirname(__file__))
# plot.ion()

def getSuperevents(verbose=False):
    # get events list from GraceDB
    superevents=[]
    service_url = 'https://gracedb.ligo.org/api/'
    if verbose: print('Retrieving GraceDB data from {}'.format(service_url))
    client = GraceDb(service_url,force_noauth=True)
    events = client.superevents('far < 1.0e-4')
    results=[]
    for event in events:
        ev = event['superevent_id']
        results.append(ev)
    return results

def getSuperevent(ev,verbose=False):
    # get event properties from GraceDB
    service_url = 'https://gracedb.ligo.org/api/'
    client = GraceDb(service_url,force_noauth=True)
    evreq=client.superevent(ev)
    event=json.loads(evreq.read())
    if verbose: print('getting files for {}'.format(ev))
    freq=client.files(ev)
    files=json.loads(freq.read())
    event['files'] = files

    mapsrch=['LALInference1','LALInference','bayestar1','bayestar']
    mapFound=False
    m=0
    while not mapFound and m<len(mapsrch):
        mapfile='{}.fits.gz'.format(mapsrch[m])
        if mapfile in files:
            event['mapfile']=[mapfile,event['files'][mapfile]]
            mapFound=True
            # if verbose: print('  found {}'.format(mapfile))
        m+=1
    return event

def getMapFile(urlIn,dirOut='data/',fileOut='',verbose=True,overwrite=False):
    # download map file from GraceDB (if not already present)
    if fileOut=='':
        fileOut='skyloc.fits'.format()
    fOut=os.path.join(dirOut,fileOut)
    # check if file exists
    fExists=os.path.isfile(fOut)
    if fExists:
        if overwrite:
            if verbose:print('Overwriting file: {}'.format(fOut))
        else:
            if verbose:print('File already exists: {}'.format(fOut))
            return()
    if verbose:print('Downloading file from {}'.format(urlIn))
    mapreq=requests.get(urlIn)
    if verbose: print('status code:',mapreq.status_code)
    if verbose: print('Saving file to {}'.format(fOut))
    f=open(fOut, 'wb')
    f.write(mapreq.content)
    f.close()
    return(mapreq.status_code)

# def loadConst():
#     fConst='const/constellations.json'
#     fConstBounds='const/constellations.bounds.json'
#     fConstLines='const/constellations.lines.json'
#     const=json.load(open(fConst))
#     cBounds=json.load(open(fConstBounds))
#     cLines=json.load(open(fConstLines))
#     return(const,cBounds,cLines)

def getConstBounds(fIn=None,verbose=False):
    # get constellation boundaries from file
    if not fIn:
        fIn=os.path.join(os.path.dirname(__file__),'constdata/constellations.bounds.json')
    cBounds=json.load(open(fIn))['features']
    const={}
    for c in cBounds:
        coords=c['geometry']['coordinates'][0]
        ra=[]
        dec=[]
        for xy in coords:
            ra.append(xy[0])
            dec.append(xy[1])
        ra.append(coords[0][0])
        dec.append(coords[0][1])
        const[c['id']]={'coord':coords,'ra':ra,'dec':dec}
    return(const)

def plotConstBounds(color='w',alpha=1,verbose=False):
    # plot constellation boundaries
    cb=getConstBounds(verbose=verbose)
    for c in cb:
        const=cb[c]
        nra=len(const['ra'])
        for i in range(nra-1):
            line=hp.projplot(const['ra'][i:i+2],const['dec'][i:i+2],lonlat=True,color=color,linewidth=1,alpha=alpha)
            if len(line)>1:
                # catch lines that don't plot properly
                # print(c,i,nra,len(line))
                # for l in range(len(line)):
                #     print(l,line[l].get_xydata())
                xy0=line[1].get_xydata()[0]
                xy1=line[2].get_xydata()[0]
                if np.sign(xy0[0])==np.sign(xy1[0]):
                    plot.plot([xy0[0],xy1[0]],[xy0[1],xy1[1]],color=color,linewidth=1,alpha=alpha)
                # else:
                #     print('***')


def getConstLines(fIn=None,verbose=False):
    # get constellation lines from files
    if not fIn:
        fIn=os.path.join(os.path.dirname(__file__),'constdata/constellations.lines.json')
    cLines=json.load(open(fIn))['features']
    const={}
    for c in cLines:
        coords=c['geometry']['coordinates']
        ra=[]
        dec=[]
        for i in range(len(coords)):
            ra.append([])
            dec.append([])
            for xy in coords[i]:
                ra[i].append(xy[0])
                dec[i].append(xy[1])
        const[c['id']]={'coord':coords,'ra':ra,'dec':dec}
    return(const)

def plotConstLines(color='y',colorstars='y',alpha=1,plotstars=True,verbose=False):
    # plot constellation lines
    cb=getConstLines(verbose=verbose)
    for c in cb:
        const=cb[c]
        # if verbose:print('plotting {}:'.format(c),const['ra'],const['dec'])
        for i in range(len(const['ra'])):
            hp.projplot(const['ra'][i],const['dec'][i],lonlat=True,color=color,linewidth=1,alpha=alpha)
            if plotstars:
                hp.projplot(const['ra'][i],const['dec'][i],'o',lonlat=True,color=colorstars,markersize=2,alpha=alpha)
    return

def getConstLabs(fIn=None,verbose=False):
    # get constellation labels from input file
    if not fIn:
        fIn=os.path.join(os.path.dirname(__file__),'constdata/constellations.json')
    constellations=json.load(open(fIn))['features']
    const={}
    for c in constellations:
        const[c['id']]={}
        for p in c['properties']:
            const[c['id']][p]=c['properties'][p]
            const[c['id']]['coord']=c['geometry']['coordinates']
    return(const)

def plotConstLabs(color='w',alpha=1,verbose=False,radeclim=None,maxdist=None,plotcentre=[0,0]):
    # plot constellation labels, restricted to RA/Dec range if set
    if not radeclim:
        radeclim=[-180,180,-90,90]
    if maxdist==None:
        print('setting maxdist to 180')
        maxdist=180
        limplot=False
    else:
        limplot=True
    if plotcentre==None:
        plotcentre=[0,0]
    cl=getConstLabs(verbose=verbose)
    for c in cl:
        const=cl[c]
        ra=const['coord'][0]
        dec=const['coord'][1]
        angdist=hp.rotator.angdist([ra,dec],plotcentre,lonlat=True)*180/np.pi
        angdist=np.min([angdist[0],90])
        # if ra>radeclim[0] and ra<radeclim[1] and dec>radeclim[2] and dec<radeclim[3]:
        if not limplot or angdist<maxdist:
            # point is in range
            # print(ra,dec,angdist,maxdist)
            # if verbose:print('printing {:s} [{:.2f},{:2f} : {:2f}<{:.2f}]'.format(const['name'],ra,dec,angdist,maxdist))
            hp.projtext(ra,dec,const['name'],lonlat=True,color=color,alpha=alpha,ha='center',va='center')
        # elif verbose:print('not printing {:s} [{:.2f},{:2f} : {:2f}>{:.2f}]'.format(const['name'],ra,dec,angdist,maxdist))
    return

def smoothMap(map,fwhm=None,verbose=False):
    # smooth map do specified FWHM
    if fwhm==None:
        fwhm=1
    fwhmrad=fwhm*np.pi/180
    if verbose: print('smoothing map by {} deg ({:.2f} radians)'.format(fwhm,fwhmrad))
    mapsm=hp.smoothing(map,fwhm=fwhmrad)
    return(mapsm)

def readMap(fileIn,dirIn='data/',smooth=0,overwrite=False,verbose=False):
    # read in map file, and smooth if requested
    # writes out smoothed file to disc
    if smooth==0:
        map=hp.read_map(os.path.join(dirIn,fileIn))
        return(map)
    else:
        smoothFile=os.path.join(dirIn,fileIn.split('.fits')[0]+'_sm{}.fits'.format(smooth))
        fwhmrad=smooth*np.pi/180
        fExists=os.path.isfile(smoothFile)
        if fExists:
            if not overwrite:
                if verbose:print('Loading file: {}'.format(smoothFile))
                mapsm=hp.read_map(smoothFile)
                return(mapsm)
        else:
            map=hp.read_map(os.path.join(dirIn,fileIn))
            if verbose: print('smoothing map by {} deg ({:.2f} radians)'.format(smooth,fwhmrad))
            mapsm=hp.smoothing(map,fwhm=fwhmrad)
            if verbose:print('Writing smoothed file: {}'.format(smoothFile))
            hp.write_map(smoothFile,mapsm)
            return(mapsm)

def getProbMap(map,prob=0.9,verbose=False):
    # get map of area > prob
    # returns area and area within limit
    mapP=np.ones_like(map)
    # mapP[::]=hp.UNSEEN
    nside=hp.get_nside(map)
    pixarea=hp.nside2pixarea(nside,degrees=True)
    isort=np.argsort(map)[::-1]
    probtot=0
    foundP=False
    i=0
    while not foundP:
        # print(i,isort[i],map[isort[i]])
        probtot += map[isort[i]]
        if probtot>prob:
            if not foundP:
                iP=i
                if verbose: print('{} pixels in {:d}% area'.format(i,int(prob*100)))
                foundP=True
        i += 1
        mapP[isort[i]]=probtot
    areaP=(iP+1)*pixarea

    if verbose: print('{:d}% area={:d} deg^2'.format(int(prob*100),int(areaP)))

    return(mapP,areaP)

def getArea(maptot,prob=0.9,verbose=False):
    npix=len(np.where(maptot<=prob)[0])
    pixarea=hp.nside2pixarea(hp.get_nside(maptot),degrees=True)
    areaP=npix*pixarea
    if verbose: print('{:d}% area={:d} deg^2'.format(int(prob*100),int(areaP)))
    return(areaP)

def getRaDecRange(map,lim=0.5,ltype='max',border=0,verbose=False):
    # get RA/Dec limits of all pixels which satisfy criteria
    # returns min(RA), max(RA), min(Dec), max(Dec)
    if ltype=='max':
        # get all pixels less than limit
        pixlim=np.where(map<lim)[0]
    elif ltype=='min':
        # get all pixels greater than limit
        pixlim=np.where(map>lim)[0]
    # convert HP pixels to RA/Dec
    nside=hp.get_nside(map)
    ra,dec=hp.pix2ang(nside, pixlim, lonlat=True)
    # keep in range [-180,180]
    ra=np.where(ra>180,ra-360,ra)
    # find minima
    decMin=np.min(dec)
    decMax=np.max(dec)
    raMin=np.min(ra)
    raMax=np.max(ra)
    # if raMax-raMin > 359:
    #     # crosses meridian
    #     # ra=np.where(ra>180,ra-360,ra)
    #     raMin=np.min(ra)
    #     raMax=np.max(ra)

    # get ra/dec of peak of map
    raPeak,decPeak=getPeak(map,getmin=True,verbose=verbose)
    # calculate angular distance to corners/edges of map and find max distance
    maxdist=0
    for ra in [raMin,raMax,np.mean([raMin,raMax])]:
        for dec in [decMin,decMax,np.mean([decMin,decMax])]:
            dist=hp.rotator.angdist([ra,dec],[raPeak,decPeak],lonlat=True)
            maxdist=np.max([dist,maxdist])
    maxdist=np.min([maxdist*180./np.pi,90])

    if verbose: print('RA range=[{:.1f},{:.1f}] ; Dec range=[{:.1f},{:.1f}]'.format(raMin,raMax,decMin,decMax))
    if verbose: print('maximum angular distance: {:.1f}'.format(maxdist))
    return([raMin,raMax,decMin,decMax,maxdist])

def makeGrid(radecLim,nX=4096,nY=2048,verbose=False):
    # make RA/Dec grid over spcified RA/Dec area
    # returns x,y coords of grid
    raMin,raMax,decMin,decMax,maxdist=radecLim

    # get grid of RA, Dec within range
    xxAll=np.arange(-180,180,360/nX)+0.5
    yyAll=np.arange(-90,90,180/nY)+0.5

    # restrict to RA/Dec range
    xx=xxAll[np.where((xxAll<=raMax) & (xxAll>=raMin))]
    yy=yyAll[np.where((yyAll<=decMax) & (yyAll>=decMin))]
    # if len(np.where(xx>180)[0]):
    #     xx2=np.zeros_like(xx)
    #     no180=len(np.where(xx>180)[0])
    #     xx2[0:no180]=xx[np.where(xx>180)]-360
    #     xx2[no180:]=xx[np.where(xx<=180)]
    if verbose: print('Created {} x {} grid'.format(len(xx),len(yy)))

    return(xx,yy)

def map2grid(map,xx,yy,verbose=False):
    # transform map to x-y grid
    # returns map regridded onto grid
    if verbose: print('Populating grid...')
    nside=hp.get_nside(map)
    nX=len(xx)
    nY=len(yy)
    zz=np.zeros((nY,nX))
    zz[::]=np.nan
    for i in range(nX):
        x=xx[i]
        for j in range(nY):
            y=yy[j]
            ipix=hp.ang2pix(nside,x,y,lonlat=True)
            zz[j,i]=map[ipix]

    return(zz)

def getContLines(xx,yy,zz,level=0.9,ax=None,verbose=False):
    # get contour lines and return as RA/Dec points
    if ax==None:
        ax=plot.gca()
    if verbose:print('Getting contour lines for level:',level)
    cont=ax.contour(xx,yy,zz,levels=level,alpha=0)
    coll=cont.collections[0]
    segs=coll.get_segments()
    # nseg=len(segs)
    raCont=[]
    decCont=[]
    ns=0
    ncp=0
    for seg in segs:
        raCont.append([])
        decCont.append([])
        for s in range(len(seg)):
            raCont[ns].append(seg[s][0])
            decCont[ns].append(seg[s][1])
            ncp+=1
        ns+=1
    if verbose:print('Calculate {} points in contour'.format(ncp))

    return(raCont,decCont,cont)

def plotMap(map,proj='moll',fig=None,pmax=None,pmin=None,rot=None,cmap=None,cbg=None,verbose=False,half_sky=False,zoomrng=None,title=None):
    # plot map based on options specified
    if not cmap:
        cmap=cm.gray
    if not cbg:
        cmap.set_under('w')
        cmap.set_over('w')
        cmap.set_bad('w')
    else:
        cmap.set_under(cbg)
        cmap.set_over(cbg)
        cmap.set_bad(cbg)
    if fig==None:
        if proj=='cart' and zoomrng!=None:
            figsize=(10,10)
        else:
            figsize=(20,10)
        fig=plot.figure(figsize=figsize)

    if proj=='cart':
        if zoomrng==None:
            # plot full-sky Cartesian view (rotated to centre if specified)
            fig=hp.cartview(map,cmap=cmap,max=pmax,min=pmin,cbar=False,rot=rot,fig=fig.number,title=title)
        else:
            # get the centre of the plot averate of the ra and dec limits
            ramean,decmean=getPeak(map,verbose=verbose)
            maxdist=np.min([zoomrng[4],90])
            rarng=[-maxdist,maxdist]
            decrng=[-maxdist,maxdist]
            #
            # ramean=np.mean(zoomrng[0:1])
            # decmean=np.mean(zoomrng[2:3])
            # # calculate RA/Dec ranges from centre and add 10deg border around edge
            # rawid=zoomrng[1]-zoomrng[0]
            # decht=zoomrng[3]-zoomrng[2]
            # rarng=[np.max([zoomrng[0]-ramean-10,-180]),np.min([zoomrng[1]-ramean+10,180])]
            # decrng=[np.max([zoomrng[2]-decmean-10,-90]),np.min([zoomrng[3]-decmean+10,90])]
            # ralim=[rarng[0]+ramean,rarng[1]+ramean]
            # declim=[decrng[0]+decmean,decrng[1]+decmean]


            # plot Cartesian view centred and zoomed on RA/Dec range
            fig=hp.cartview(map,cmap=cmap,max=pmax,min=pmin,cbar=False,rot=[ramean,decmean],fig=fig.number,
                lonra=rarng,latra=decrng,title=title)
    elif proj=='moll':
        # plot full-sky Mollweide view (rotated to centre if specified)
        fig=hp.mollview(map,cmap=cmap,max=pmax,min=pmin,cbar=False,rot=rot,fig=fig.number,title=title)
    elif proj=='orth':
        # plot full-sky Mollweide view (rotated to centre if specified)
        fig=hp.orthview(map,cmap=cmap,max=pmax,min=pmin,cbar=False,rot=rot,half_sky=half_sky,fig=fig.number,title=title)
    elif proj=='gnom':
        fig=hp.gnomview(map,cmap=cmap,max=pmax,min=pmin,cbar=False,rot=rot,half_sky=half_sky,fig=fig.number,title=title)
    else:
        print('unknown projection:',proj)
    return fig

def getPeak(map,verbose=False,getmin=False):
    # get RA/Dec of peak
    # set getmin to find minimum of map, otherwise fint max [default=max]
    # returns RA and Dec
    if getmin:
        iPeak=np.argmin(map)
        pval=np.min(map)
    else:
        iPeak=np.argmax(map)
        pval=np.max(map)
    ns=hp.get_nside(map)
    raPeak,decPeak=hp.pix2ang(ns,iPeak,lonlat=True)
    if verbose: print('peak [{:.2f}] found at ({:.2f},{:.2f})'.format(pval,raPeak,decPeak))
    return(raPeak,decPeak)

def plotLab(map,txt,color='r',verbose=False):
    # plot label at Peak of map
    # Depracated
    raPeak,decPeak=getPeak(map,verbose=verbose)
    hp.projtext(raPeak,decPeak,txt,lonlat=True,color=color)
    return

def plotContours(map,level=0.9,color='w',alpha=0.5,linestyle='-',linewidth=2,verbose=False):
    # plot contours of map
    if verbose:print('plotting contours for level:',level)
    radec95=getRaDecRange(map,lim=0.92,ltype='max',verbose=verbose)
    xx95,yy95=makeGrid(radec95,verbose=verbose)
    zz95=map2grid(map,xx95,yy95,verbose=verbose)
    raCont,decCont,cont=getContLines(xx95,yy95,zz95,level=level,verbose=verbose)
    nseg=len(raCont)
    for s in range(nseg):
        hp.projplot(raCont[s],decCont[s],lonlat=True,color=color,alpha=alpha,linestyle=linestyle,linewidth=linewidth)
    return(cont)


def makePlot(ev='S190412m',mapIn=None,proj='moll',plotcont=False,smooth=0.5,zoomlim=0.92,rotmap=True,half_sky=False,pngOut=None,verbose=False,cbg=None,dirData='data/',minzoom=10,pngSize=3000,thumbOut=None,thumbSize=300,title=None):
    # ev: superevent ID [default='S190412m']
    # proj: projection (moll=Mollweide [Default], cart=Cartesian)
    # plotcont: set to plot contours (default=True)
    # smooth: degrees to smooth probability densith map to get contours. 0=no smoothing. [Default=0.5deg]
    # zoomlim: probability to zoom map in to (cartview only). Default=0.92
    # rotmap: rotate map to centre on peak value [Default=False]
    # half_sky: only show half the sky (orthographic only)
    # pngOut: filename to export to PNG [Default=None -> no export]
    # pngSize: width of output image [default=3000px]
    # thumbOut: filename to export to thumbnail PNG [Default=None -> no export]
    # thumbSize: width of output image [default=100px]
    # verbose: plot more text [Default=False]
    # cbg: background colour [Default=black]
    # dirData: directory to load files from [Default= 'data/']
    # minzoom: minimum map radius, in degrees (proj=cart & zoomlim!=None only) [Default=10]
    # title: Title to plot on image (optional string) [Default = <ev>]
    if type(mapIn)==type(None):
        event=getSuperevent(ev,verbose=verbose)
        event['mapfile_local']=fileOut='{}_{}'.format(ev,event['mapfile'][0])
        getMapFile(event['mapfile'][1],fileOut=event['mapfile_local'],verbose=verbose)
        map=readMap(event['mapfile_local'],smooth=smooth,verbose=verbose,dirIn=dirData)
    elif type(mapIn)==str:
        map=readMap(mapIn,smooth=smooth,verbose=verbose,dirIn=dirData)
    else:
        map=mapIn
    maptot,area95=getProbMap(map,0.95,verbose=verbose)

    if title==None:
        title=ev

    blankmap=np.zeros_like(maptot)
    if rotmap:
        raPeak,decPeak=getPeak(map,verbose=verbose)
        rot=[raPeak,decPeak]
    else:
        rot=None
    if minzoom==None:
        minzoom=180
    if proj=='cart' and zoomlim!=None:
        radeczoom=getRaDecRange(maptot,lim=zoomlim,ltype='max',verbose=verbose)
        # apply min zoom
        if radeczoom[4] < minzoom:
            print('setting min zoom [{}->{}]'.format(radeczoom[4],minzoom))
            radeczoom[4]=minzoom
        maxdist=radeczoom[4]
        # print('zoom range',radeczoom)
        # radeclab=getRaDecRange(maptot,lim=zoomlim,ltype='min',verbose=verbose,border=0)
        # ralim=[radeclab[0],radeclab[1]]
        # declim=[radeclab[2],radeclab[3]]
    else:
        radeczoom=None
        maxdist=None
        ralim=[-180,180]
        declim=[-90,90]
    # print (radec95)
    fig=plotMap(map,cmap=cm.hot,proj=proj,rot=rot,verbose=verbose,zoomrng=radeczoom,title=title,half_sky=half_sky,cbg=cbg)

    if plotcont:
        cont90=plotContours(maptot,level=0.9,color='w',alpha=0.5,linestyle='-',linewidth=2,verbose=verbose)

    if proj=='cart' and zoomlim!=None:
        alphaLab=1
    else:
        alphaLab=0.5
    plotConstBounds(color=(0.5,0.5,0.5),verbose=verbose,alpha=0.5)
    plotConstLabs(color=(0,0.7,0.7),verbose=verbose,alpha=alphaLab,maxdist=maxdist,plotcentre=rot)
    plotConstLines(color=(0,0.7,0.7),verbose=verbose,alpha=0.5)

    if pngOut:
        plot.savefig(pngOut,dpi=pngSize/10)
    if thumbOut:
        plot.savefig(thumbOut,dpi=thumbSize/10)

    return map

###########################
def plotall():
    evs=['S190421ar']
    evs=[]
    try:
        evs[0]
    except:
        evs=getSuperevents()
    print ('plotting {} event(s):'.format(len(evs)),evs)
    # dirData='../data/'
    for ev in evs:
        map=makePlot(ev=ev,proj='cart',plotcont=False,smooth=0.5,zoomlim=0.8,rotmap=True,verbose=True,
            pngOut='png/{}_cartzoom.png'.format(ev))
        makePlot(ev=ev,mapIn=map,proj='cart',plotcont=False,smooth=0.5,zoomlim=None,rotmap=False,verbose=True,pngOut='png/{}_cart.png'.format(ev))
        makePlot(ev=ev,mapIn=map,proj='moll',plotcont=False,smooth=0.5,zoomlim=None,rotmap=False,verbose=True,pngOut='png/{}_moll.png'.format(ev),cbg='w')
        # map = makePlot(ev=ev,proj='orth',plotcont=False,smooth=0.5,zoomlim=None,rotmap=True,half_sky=True,verbose=True,pngOut='png/{}_orth.png'.format(ev))
    plot.show()


