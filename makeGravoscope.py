#!/Applications/anaconda3/anaconda3/bin/python3.6
import gwcat
import os
import argparse

parser=argparse.ArgumentParser(prog="makeGravoscope.py", description="Updates the gravoscope tiles")
parser.add_argument('-d','--datadir', dest='datadir', type=str, default='data/', help='directory in which data is stored')
parser.add_argument('-f','--forceupdate', dest='forceupdate', action='store_true', default=False, help='Force (re)download of files')
parser.add_argument('-v','--verbose', dest='verbose', action='store_true', default=False, help='Set to print more helpful text to the screen')

args=parser.parse_args()
verbose=args.verbose
forceupdate=args.forceupdate
dataDir=args.datadir

gc=gwcat.GWCat(fileIn=os.path.join(dataDir,'gwosc_gracedb.json'))
gc.makeGravoscopeTiles(overwrite=forceupdate,maxres=6,verbose=verbose)