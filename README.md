# gwcat-data
Data from LIGO-Virgo gravitational wave detections, built from [Gravitational Wave Open Science Centre](https://www.gw-openscience.org/) and [GraceDB](https://gracedb.ligo.org/latest/). For usage see gwcat.cardiffgravity.org

### Data files (GWOSC + GraceDB):
 * [all data (JSON)](docs/data/gwosc_gracedb.json) (_includes parameter definitions and referece links_)
 * [all data (JSON, minified))](docs/data/gwosc_gracedb.min.json) (_includes parameter definitions and reference links_)
 * [data values only (JSON))](docs/data/data.json)
 * [Data parameters only (JSON))](docs/data/parameters.json)
 * [References/links only (JSON))](docs/data/links.json)
 * [data values (CSV)](docs/data/gwosc_gracedb.csv)
 * [Data parameters (CSV)](docs/data/parameters.csv)
 * [References/Links (CSV)](docs/data/links.csv)

### Sky localisation images:
 * Location: http://data.cardiffgravity.org/gwcat-data/data/png/\<filename\>
 * Filename formats for \<event\> (e.g. GW150914, S190510g etc.):
    * Mollweide: data/png/\<event\>_moll.png
        * (e.g. [data/png/S191105e_moll.png](data/png/S191105e_moll.png))
    * Mollweide (rotated to centre on peak location): data/png/\<event\>_moll_rot.png
        * (e.g. [data/png/S191105e_moll_rot.png](data/png/S191105e_moll_rot.png))
    * Cartesian fullsky: data/png/\<event\>_cart.png
        * (e.g. [data/png/S191105e_cart.png](data/png/S191105e_cart.png))
    * Cartesian fullsky (rotated to centre on peak location): data/png/\<event\>_cart_rot.png
        * (e.g. [data/png/S191105e_cart_rot.png](data/png/S191105e_cart_rot.png))
    * Cartesian zoomed onto peak location: data/png/\<event\>_cartzoom.png
        * (e.g. [data/png/S191105e_cartzoom.png](data/png/S191105e_cartzoom.png))
 * "Pretty" versions of images (NB these are under development, and may change style)
    * Mollweide (white background): data/png/\<event\>_moll_pretty.png
        * (e.g. [data/png/S191105e_moll_black.png](data/png/S191105e_moll_pretty.png))
    * Mollweide (black background): data/png/\<event\>_moll_pretty_black.png
        * (e.g. [data/png/S191105e_moll_black.png](data/png/S191105e_moll_pretty_black.png))
    * Cartesian zoomed on peak location (no border): data/png/\<event\>_cartzoom_pretty.png
        * (e.g. [data/png/S191105e_cartzoom_pretty.png](data/png/S191105e_cartzoom_pretty.png))
 * Thumnail of all images have .thumb.png extension
    * e.g. [data/png/S191105e_cartzoom.thumb.png](data/png/S191105e_cartzoom.thumb.png)
 * All images are in Equatorial (J2000) coordinates.

 
 
### High-res sky localisation images:
 * Galactic: http://data.cardiffgravity.org/gwcat-data/data/gravoscope/\<event\>_8192.png
   * e.g. [data/gravoscope/S191105e_8192.png](data/gravoscope/S191105e_8192.png)
 * Equatorial (J2000): http://data.cardiffgravity.org/gwcat-data/data/gravoscope/\<event\>_8192_eq.png
   * e.g. [data/gravoscope/S191105e_8192_eq.png](data/gravoscope/S191105e_8192_eq.png)
 * 8192x4096 px
 * grayscale image

### Dependencies
 * python>=3.6 (it almost certainly works in earlier versions of python3, and it may well work in python 2, possibly with minor changes)
 * Contains the submodule gwcatpy, which has the following dependencies:
    * LIGO-specific dependencies
      * pesummary
      * ligo.gracedb
    * Other community-developed dependencies:
      * astropy
      * healpy
      * matplotlib
      * pandas
      * h5py
      * astropy_healpix
      * numpy
      * scipy
      * requests
      * json
      * bs4
