Using the container
===================

This pages walks you though how to use the docker container and details some
pre-configured settings.

Environment file
----------------

The docker container should run out of the box with the env/env.public environment
file. However, you may want to use your own env file e.g., if you want to map
data on your local machine to the container.

To do this, first make a copy of the env.public file and call it env. In the base
directory run

.. code:: None

    cp env/env.public env/env

The env file is now your personal environment file and will be ignored by git.
Make sure you change the :code:`PATH_TO_ENV` to ../env/env so docker can find it.
Then to run the docker container with your personal env file,

.. code:: None

    bash run.sh

Volumes
-------

Volumes allow the docker container to see files (and live edits) on your local
system.

By default the container has the ucsc_spectral_pipeline repository, where
you launched the container from, mapped into :code:`/home/ucsc_spectral_pipeline/`
in the container.

Also by default the container has the :code:`ucsc_spectral_pipeline/extra_files/disp.cl`
mapped to :code:`/etc/iraf/disp.cl` in the container, and :code:`ucsc_spectral_pipeline/login.cl`
is mapped to :code:`/etc/iraf/login.cl` in the container.

You might want to mount your own data volumes in the container. To do this set
the :code:`DATA_VOLUME` variable in your env file to the path on your local machine
container the data. This data will then be available in the docker container at
:code:`/home/data/`.

Running the pipeline
--------------------

To run a pipeline script run when in the container.

.. code:: None

    python3 ${PIPELINE}/<name_of_script>.py

Running pyraf
-------------

To run pyraf in the container,

.. code:: None

    pyraf

You should see the pyraf GUI. If you get an "cannot find X display error", stop
the container and run "xhost +localhost" on your machine.