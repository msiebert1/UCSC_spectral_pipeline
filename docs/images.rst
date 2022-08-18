Adding new packages
===================

You may need to install further dependencies in the container for your analysis
to work. You can do this when in the container, but these installs will not
be saved the next time you want to run the container. To permanently add new installs,
which other people can use as well, you need to alter :code:`docker/Dockerfile`.

Once you have altered the dockerfile locally, to see these new changes you
have to run

.. code::

    docker compose run ucsc_spectral_pipeline_local

This uses your local docker file to build an image instead of just pulling the
latest image from the `Github container registry <https://github.com/astrophpeter/UCSC_spectral_pipeline/pkgs/container/ucsc_spectral_pipeline>`_

Once you are happy with the new dockerfile, if you push you changes to github,
a new updated image is built automatically using github actions and will be able
to be used by running,

.. code::

    docker compose ucsc_spectral_pipeline_latest

