Install
=======

These instructions have been tested for macOS with an intel chip.

Install the Docker desktop app
-------------------------------

The first step is to install the docker desktop application, which can be found
`here <https://docs.docker.com/get-docker/>`_ for mac, windows, and linux.
Running the pipeline with docker means that you won't have to install pipeline
dependencies locally.

Install and configure XQuarts
-----------------------------

You are going to need XQuartx to see IRAF GUI output.

1. Install XQuartz: https://www.xquartz.org/ (Tested with XQuarts 2.8.2)

2. Launch XQuartz. Under the XQuartz menu, select Preferences

3. Go to the security tab and ensure "Allow connections from network clients" is checked.

4. Restart your computer

Running the spectral pipeline
-----------------------------

Clone the pipline repository.

..  code::

    git clone https://github.com/astrophpeter/UCSC_spectral_pipeline

Download the most recent docker image.

..  code::

    docker pull ghcr.io/astrophpeter/ucsc_spectral_pipeline:latest

Run the start up script. While in the base directory,

..  code:: None

    bash run.sh

This script enables the docker container to forward to your machine so you can see the
IRAF GUI, and starts the pipeline container with your :code:`env/env` file.

Once in the container, you can run pipeline tasks with the required installs present.
See :doc:`here <docker>` for details on using the pipeline container.

Stopping the container
----------------------

It is important when you are finished using the docker container that you stop it
properly. This enables it to be started easily again.

To exit the container run,

.. code:: None

    exit

Then make sure you stop the container running and close your machine to local
host connections by running,

.. code:: None

    bash down.sh

in the base directory. Happy reducing!

Archival Native install
-----------------------

.. warning::

    These instructions are here for archival purposes only, we do not recommend
    you install the pipeline this way. It will be difficult, you have been warned.

Installation of the pipeline.

* Via anaconda, install astroconda. More info on https://astroconda.readthedocs.io/en/latest/
* Make sure you include the iraf environment, https://astroconda.readthedocs.io/en/latest/installation.html
* After that, just in case, check if you have pyraf, numpy, astropy and pylab.
* Clone the repository

     ```git clone https://github.com/msiebert1/UCSC_spectral_pipeline.git```

* In your ~/.bashrc file (or your ~/.bash_profile for Mac people), add the following lines:

     ```export UCSC_SPECPIPE=<the new directory just created by git>```

     ```export PATH=$UCSC_SPECPIPE/spectral_reduction:$PATH```

* Copy the disp.cl file (located in the extra_files folder) into your iraf folder
(this was hopefully created when you installed astroconda). If you cannot find it,
copy the disp.cl file into ~/iraf and run mkiraf in that directory.

* At the end of your iraf login.cl file, add the following line with the appropriate path:

     ```task disp='<your_iraf_directory>/disp.cl'```

* For the flux calibration portion of the pipline make sure you have a python 3 environment. This can be
created with a command like:

    ```conda create -n py36 python=3.6 anaconda```



