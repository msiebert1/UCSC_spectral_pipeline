Using the pipeline
==================

The 3 main parts to this pipeline are pre-reduction, extraction, and flux
calibration. Each of the files specified below need to be made executable:

Pre-reduction
-------------

(pre_reduction_dev.py)

* Starts with folder containing raw arcs, flats, and science frames.
* Overscan correction, trimming, master arcs, master flats, and object folder
  organizing
* A "pre_reduced" directory is created containing these new calibration files
  and folders for individual targets.

Recommended procedure:

1. run pre_reduction_dev.py, this will create a configuration file and attempt
   to organize files by category
2. edit the custom_config.json file manually (rsubl custom_config.json), correct
   any mistakes that the pipeline makes in file classification
3. run pre_reduction_dev.py -c custom_config.json --make-arc --make-flat
   (or to use archival cals, pre_reduction_dev.py -c custom_config.json -q)
   include --red-amp-bad if LRIS bottom amplifier broken when prompted to edit
   the response file, enter "p" to fit and replace preset regions of the response

Extraction
----------

(QUICKLOOK.py -i -a -c)

* Move to a target folder created in step 1 and run this script.
* Cosmic ray removal (-c), using the python implementation of LACOS
* Define the wavelength solution using iraf identify (can use predefined master
  solution if it exists)
* Extract a spectrum using the apall task from IRAF
* Map the extracted spectrum with the calculated wavelength solution
* The same for the red arm
* If more than one red exposures are provided (normal), the images are combined
  prior to reduction Creates "target_ex" directory containing the d*_ex.fits file
  used in flux calibration

Flux Calibration
----------------

(cal.py)

* Run cal.py in the same directory.
* Flux calibrates and telluric corrects the extracted spectrum from part 2.
* If you specified to use an archival flux calibration in part 2, then the
  relevant files have been moved into this directory. Simply choose "n" when
  prompted to fit a flux or bstar.
