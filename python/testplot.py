import matplotlib.pyplot as plot
import healpy as hp
import gwcat

plot.ion()
# map=hp.read_map('data/fits/S190519bj_bayestar.fits.gz')
map=gwcat.plotloc.makePlot(ev='S190519bj',proj='moll',plotcont=False,smooth=0,zoomlim=None,rotmap=False,verbose=True,cbg='w',dirData='../data/fits/',addCredit=True,addLogos=True)
gwcat.plotloc.makePlot(ev='S190519bj',mapIn=map,proj='cart',plotcont=False,smooth=0,zoomlim=None,rotmap=False,verbose=True,cbg='w',RAcen=180,dirData='../data/fits/',addCredit=True,addLogos=True)
gwcat.plotloc.makePlot(ev='S190519bj',proj='cart',plotcont=False,smooth=0,zoomlim=0.8,rotmap=True,verbose=True,cbg='w',grid=False,dirData='../data/fits/',addCredit=True,addLogos=True)
# gwcat.plotloc.makePlot(ev='S190519bj',mapIn=map,proj='moll',plotcont=False,smooth=0,zoomlim=None,rotmap=True,verbose=True,cbg='w',dirData='../data/fits/')