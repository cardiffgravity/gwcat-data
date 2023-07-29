# gwcat-data
Data from LIGO-Virgo gravitational wave detections, built from [Gravitational Wave Open Science Centre](https://www.gw-openscience.org/) and [GraceDB](https://gracedb.ligo.org/latest/). For usage see gwcat.cardiffgravity.org

### Data files (GWOSC + GraceDB):
 * [all data (JSON)](data/gwosc_gracedb.json) (_includes parameter definitions and referece links_)
 * [all data (JSON, minified))](data/gwosc_gracedb.min.json) (_includes parameter definitions and reference links_)
 * [data values only (JSON))](data/data.json)
 * [Data parameters only (JSON))](data/parameters.json)
 * [References/links only (JSON))](data/links.json)
 * [data values (CSV)](data/gwosc_gracedb.csv)
 * [Data parameters (CSV)](data/parameters.csv)
 * [References/Links (CSV)](data/links.csv)

### Sky localisation images:
 * Location: https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/\<filename\>
 * Filename formats for \<event\> (e.g. GW150914, S190510g etc.):
    * Mollweide: \<event\>_moll.png
        * (e.g. [S191105e_moll.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_moll.png))
    * Mollweide (rotated to centre on peak location): \<event\>_moll_rot.png
        * (e.g. [S191105e_moll_rot.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_moll_rot.png))
    * Cartesian fullsky: \<event\>_cart.png
        * (e.g. [S191105e_cart.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_cart.png))
    * Cartesian fullsky (rotated to centre on peak location): \<event\>_cart_rot.png
        * (e.g. [S191105e_cart_rot.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_cart_rot.png))
    * Cartesian zoomed onto peak location: \<event\>_cartzoom.png
        * (e.g. [S191105e_cartzoom.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_cartzoom.png))
 * "Pretty" versions of images (NB these are under development, and may change style)
    * Mollweide (white background): \<event\>_moll_pretty.png
        * (e.g. [S191105e_moll_black.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_moll_pretty.png))
    * Mollweide (black background): \<event\>_moll_pretty_black.png
        * (e.g. [S191105e_moll_black.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_moll_pretty_black.png))
    * Cartesian zoomed on peak location (no border): \<event\>_cartzoom_pretty.png
        * (e.g. [S191105e_cartzoom_pretty.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_cartzoom_pretty.png))
 * Thumnail of all images have .thumb.png extension
    * (e.g. [S191105e_cartzoom.thumb.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/png/S191105e_cartzoom.thumb.png))
 * All images are in Equatorial (J2000) coordinates.

 
 
### High-res sky localisation images:
 * Galactic: https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/gravoscope/\<event\>_8192.png
   * e.g. [S191105e_8192.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/gravoscope/S191105e_8192.png)
 * Equatorial (J2000): https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/gravoscope/\<event\>_8192_eq.png
   * e.g. [S191105e_8192_eq.png](https://ligo.gravity.cf.ac.uk/~chris.north/gwcat-data/data/gravoscope/S191105e_8192_eq.png)
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
