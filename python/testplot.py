import matplotlib.pyplot as plot
import healpy as hp
import gwcat

plot.ion()
# map=hp.read_map('data/fits/S190519bj_bayestar.fits.gz')
map=gwcat.plotloc.makePlot(ev='S190519bj',proj='moll',plotcont=False,smooth=0,zoomlim=None,rotmap=False,verbose=True,cbg='w')
gwcat.plotloc.makePlot(ev='S190519bj',mapIn=map,proj='moll',plotcont=False,smooth=0,zoomlim=None,rotmap=False,verbose=True,cbg='w',RAcen=180)
gwcat.plotloc.makePlot(ev='S190519bj',proj='moll',plotcont=False,smooth=0,zoomlim=None,rotmap=False,verbose=True,cbg='w',RAcen=180,grid=True)
gwcat.plotloc.makePlot(ev='S190519bj',mapIn=map,proj='moll',plotcont=False,smooth=0,zoomlim=None,rotmap=True,verbose=True,cbg='w')