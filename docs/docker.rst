Using the container
===================

This pages walks you though how to use the docker container and details some
pre-configured settings.

Conda environments
------------------

There are two pre-configured conda environments setup in the container -
:code:`iraf27` and :code:`py36`. To activate these conda environments run,

.. code::

    source activate iraf27

or

.. code::

    source activate py36

To deactivate run,

.. code::

    source deactivate

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

.. code::

    <path on your local machine>:<path in the container>

To see this volume you will have to start the container with the modified
docker compose file.
