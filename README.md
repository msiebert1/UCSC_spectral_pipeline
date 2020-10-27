UCSC Spectral Reduction Pipeline
==============

This is the 0.1 version of a quicklook spectral reduction pipeline. It has been tested extensively on Kast and LRIS spectral images (SOAR still in development). 

The pipeline is a collection of python scripts (pre_reduction_dev.py, QUICKLOOK.py, and cal.py), utilising an implementation of IRAF called, not surprisingly, pyRAF. It is heavily influenced from Stefano Valenti's work on similar pipelines for NNT (EFOSC) and LCO (FLOYDS) pipelines.

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

     ```task disp='<your_iraf_directory>/disp.cl'```

- For the flux calibration portion of the pipline make sure you have a python 3 environment. This can be 
created with a command like:

    ```conda create -n py36 python=3.6 anaconda```
  
------------

The pipeline includes 3 folders with the relevant scripts, and this readme file:

- Spectral_reduction. This includes the scripts + functions, used in the
pipeline. There may be some left-over functions from other codes, or
functions that are not called at all. In time, this will be corrected.
Moreover, there is a folder called trunk, where the archival files, used in the pipeline are included.
- Extra_files. This includes 2 plots with emission arc lines for KAST,
for your convenience, and the disp.cl file, for which we will mention later on.
- Test_data. Contains arcs (b1003, r1003), flats (b1020-b1030, r1020-r1030), and science frames 
(b1064, r1073-r1075).

-----------

The 3 main parts to this pipeline are pre-reduction, extraction, and flux calibration. Each of
the files specified below need to be made executable:

1) Pre-reduction (pre_reduction_dev.py)
- IMPORTANT: requires the iraf27 env
- Starts with folder containing raw arcs, flats, and science frames.
- Overscan correction, trimming, master arcs, master flats, and object folder organizing
- A "pre_reduced" directory is created containing these new calibration files and 
folders for individual targets.
- Recommended procedure:
	- run pre_reduction_dev.py, this will create a configuration file and attempt to organize files by category
	- edit the custom_config.json file manually (rsubl custom_config.json), correct any mistakes that the pipeline makes in file classification
	- run pre_reduction_dev.py -c custom_config.json --make-arc --make-flat (or to use archival cals, pre_reduction_dev.py -c custom_config.json -q)
		- include --red-amp-bad if LRIS bottom amplifier broken
	- when prompted to edit the response file, enter "p" to fit and replace preset regions of the response

2) Extraction (QUICKLOOK.py -i -a -c)
- IMPORTANT: requires the iraf27 env
- Move to a target folder created in step 1 and run this script.
- Cosmic ray removal (-c), using the python implementation of LACOS
- Define the wavelength solution using iraf identify (can use predefined master solution if it exists)
- Extract a spectrum using the apall task from IRAF
- Map the extracted spectrum with the calculated wavelength solution
- The same for the red arm
- If more than one red exposures are provided (normal), the images
are combined prior to reduction
- Creates "target_ex" directory containing the d*_ex.fits file used in flux calibration

3) Flux Calibration (cal.py)
- IMPORTANT: requires a python3 env
- Run cal.py in the same directory.
- Flux calibrates and telluric corrects the extracted spectrum from part 2.
- If you specified to use an archival flux calibration in part 2, then the relevant files have
been moved into this directory. Simply choose "n" when prompted to fit a flux or bstar.

