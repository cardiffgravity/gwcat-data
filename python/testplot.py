import matplotlib.pyplot as plot
import matplotlib.cm as cm
import healpy as hp
import numpy as np
import gwcat
import os

plot.ioff()
ev='S190519bj'

map=hp.read_map('../data/fits/S190519bj_bayestar.fits.gz')

# map=gwcat.plotloc.makePlot(ev=ev,proj='moll',plotcont=False,smooth=0,zoomlim=None,rotmap=False,verbose=True,cbg='w',dirData='../data/fits/',addCredit=True,addLogos=True)
# gwcat.plotloc.makePlot(ev=ev,mapIn=map,proj='cart',plotcont=False,smooth=0,zoomlim=None,rotmap=False,verbose=True,cbg='w',RAcen=180,dirData='../data/fits/',addCredit=True,addLogos=True)
# gwcat.plotloc.makePlot(ev=ev,proj='cart',plotcont=False,smooth=0,zoomlim=0.8,rotmap=True,verbose=True,cbg='w',grid=False,dirData='../data/fits/',addCredit=True,addLogos=True)

pngOut='../data/gravoscope/{}_gravoscope_8192.png'.format(ev)
gwcat.plotloc.plotGravoscope(mapIn=map,pngOut=pngOut,verbose=True,res=8)
# gwcat.plotloc.plotGravoscope(mapIn=map,pngOut='../data/gravoscope/{}_gravoscope_4096.png'.format(ev),
#     verbose=True,res=4)

# cutterfile=os.path.join('gwcat/plotloc','cutter.pl')
#
# command='perl {} cutter.pl file="{}" minzoom=3 maxzoom=6 ext="png"'.format(cutterfile,pngOut)

# os.system('perl {} cutter.pl file="{}" minzoom=3 maxzoom=7 ext="png"'.format(cutterfile,pngOut))
# # gwcat.plotloc.makePlot(ev='S190519bj',mapIn=map,proj='moll',plotcont=False,smooth=0,zoomlim=None,rotmap=True,verbose=True,cbg='w',dirData='../data/fits/')