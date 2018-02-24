UCSC Spectral Reduction Pipeline
==============

This is the 0.1 version of a quicklook spectral reduction pipeline. For now, it works on KAST spectral images, the plan is to include every longslit spectral instrument.

The pipeline is a python script called QUICKLOOK.py, utilising an implementation of IRAF called, not surprisingly, pyRAF. It is heavily influenced from Stefano Valenti's work on similar pipelines for NNT (EFOSC) and LCO (FLOYDS) pipelines. For a small description, type:

QUICKLOOK.py -h

In order for the pipeline to work, collect in a folder the science files (for KAST, these are b****.fits and r****.fits for the blue and red arm, respectively), plus a set of arcs (for KAST, these are again on the form of b****.fits and r****.fits. It works for 2 arcsec slit arcs, which, if everything during the night went well, they are probably b1003.fits and r1003.fits)

The recommended syntax is 

QUICKLOOK.py -i -c

You can add the option -a if you want to identify the arcs of the night by yourself, instead of comparing them with the archival ones.

-------------

Installation of the pipeline.

- Via anaconda, install astroconda. More info on https://astroconda.readthedocs.io/en/latest/
- Make sure you include the iraf environment, https://astroconda.readthedocs.io/en/latest/installation.html
- After that, just in case, check if you have pyraf, numpy, astropy and pylab.
- Clone the repository

     ```git clone https://github.com/msiebert1/UCSC_spectral_pipeline.git```

- In your ~/.bashrc file (or your ~/.bash_profile for Mac people), add the following lines:

     ```export UCSC_SPECPIPE=<the new directory just created by git>```

     ```export PATH=$UCSC_SPECPIPE/spectral_reduction:$PATH```

- Copy the disp.cl file (located in the extra_files folder) into your iraf folder
(this was hopefully created when you installed astroconda). If you cannot find it,
copy the disp.cl file into ~/iraf and run mkiraf in that directory.
- At the end of your iraf login.cl file, add the following line with the appropriate path:

     ```disp='<your_iraf_directory>/disp.cl'```

- in the folder "$UCSC_SPECPIPE/test_data" run the following command and
follow the prompts.  If all goes well - and if you interactively 
move the red aperture so that it's not centered on the galaxy - 
you will get a SN spectrum of 2018pj!

     ```QUICKLOOK.py -i -c```

  
------------

The pipeline includes 3 folders with the relevant scripts, and this readme file:

- Spectral_reduction. This includes the scripts + functions, used in the
pipeline. There may be some left-over functions from other codes, or
functions that are not called at all. In time, this will be corrected.
Moreover, there is a folder called trunk, where the archival files, used in the pipeline are included.
- Extra_files. This includes 2 plots with emission arc lines for KAST,
for your convenience, and the disp.cl file, for which we will mention later on.
- Test_data. This includes 4 files: b1063.fits and r1085.fits are
blue and red exposures of SN 2018pj, a normal type Ia, and b1003.fits
and r1003.fits, a set of blue and red arcs. When I run the pipeline
for these exposures, I type QUICKLOOK.py -c, so cosmic removal, no
interactive extraction and only comparison with the archival arcs, I
get a nice merged spectrum at ~14.5 seconds. Keep in mind that in the
non-interactive case, the spectrum is not correct: the automated iraf
extraction algorithm picks the galaxy instead of the SN at the red part.

-----------

The pipeline will :

- Identify which files are science and which are arcs, for each spectrograph's arm
- Start from the blue arm
- Overscan correction and trimming, for pre-defined regions of the CCD
- Dark and Flat correction, from biases and dome flats taken on 02/06/2018
- Cosmic ray removal, using the python implementation of LACOS
- Compare the night's arcs with a set of already wavelength
identified arcs (tbb1070.ms.fit) from 02/06/2018, calculating a new set of wavelength solution
- (commented out for now, since I am still testing it) Determine
an extra wavelength corrections from sky lines
- Extract a spectrum using the apall task from IRAF
- Map the extracted spectrum with the calculated wavelength solution
- Calibrate the extracted, wavelength solved spectrum with a sensitivity
function from Feige34, taken on 02/06/2018
- The same for the red arm
- If more than one red exposures are provided (normal), the images
are combined prior to reduction
- The red arm arcs fits file is tbr1103.ms.fits
- The red sensitivity function is from BD262606, taken on 02/06/2018
- The blue and red arm are merged to a single spectrum

------------

The pipeline produces:

- A folder with the name of the supernova, that contains 3 ascii
files (blue, red, merged) and 6 fits files (2D spectrum, extracted
1D spectrum and flux-calibrated 1D spectrum, for each arm)
- A folder named database, that contains files regarding the aperture
(ap*) and wavelength solutions (id*). This specific file is used by IRAF
- A png file with the plot of the extracted, wavelength solved, flux
calibrated and merged spectrum

Keep in mind that the script copies at the working folder several
files, but in the end, everything that is not needed is deleted.

