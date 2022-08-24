Using the container
===================

This pages walks you though how to use the docker container and details some
pre-configured settings.

Running the pipeline
--------------------

To run a pipeline script run:

.. code:: None

    python3 ${PIPELINE}/<name_of_script>.py


Volumes
-------

Volumes allow the docker container to see files (and live edits) on your local
system.

By default the container has the ucsc_spectral_pipeline repository, where
you launched the container from, mapped into :code:`/home/ucsc_spectral_pipeline/`
in the container.

Also by default the container has the :code:`/home/ucsc_spectral_pipeline/extra_files/disp.cl`
mapped to :code:`/home/iraf/disp.cl` in the container.

You might want to mount your own volumes in the container. For example you may
need the container to see a data directory on your local machine. To add this volume,
you need to add a volume to the :code:`ucsc_spectra_pipeline_latest` service in
:code:`docker/docker-compose.yml` file. The syntax is,

.. code:: None

    <path on your local machine>:<path in the container>

To see this volume you will have to start the container with the modified
docker compose file.

Running pyraf
-------------

To run pyraf in the container,

.. code:: None

    pyraf

You should see the pyraf GUI. If you get an "cannot find X display error", stop
the container and run "xhost +" on your local machine.